#!/usr/bin/env python3
"""Download an official full-table Statistics Canada CSV ZIP and record provenance.

Example: python etl/download_statcan.py --tables 32100054
Never commit the large raw downloads to Git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import requests

try:
    from etl.common import TABLES, read_manifest
except ModuleNotFoundError:
    from common import TABLES, read_manifest

ROOT = Path(__file__).resolve().parents[1]
API = "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{pid}/en"

def safe_statcan_url(url: str) -> str:
    p = urlparse(url)
    if p.scheme != "https" or not (p.hostname == "statcan.gc.ca" or
                                    (p.hostname or "").endswith(".statcan.gc.ca")):
        raise ValueError(f"Untrusted download host: {p.hostname}")
    return url

def download_table(pid: str, raw_dir: Path, max_mb: int = 600, overwrite: bool = False) -> dict:
    if pid not in TABLES:
        raise ValueError(f"Unsupported table PID: {pid}")
    out = raw_dir / pid
    if out.exists() and any(out.glob("*.csv")) and not overwrite:
        return {"pid": pid, "state": "skipped_existing", "directory": str(out)}
    response = requests.get(API.format(pid=pid), timeout=60)
    response.raise_for_status()
    response_payload = response.json()
    if response_payload.get("status") != "SUCCESS":
        raise RuntimeError(f"WDS failed for {pid}: {response_payload}")
    url = safe_statcan_url(response_payload["object"])
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp:
        tmp = Path(temp.name)
    sha = hashlib.sha256()
    n_bytes = 0
    try:
        with requests.get(url, stream=True, timeout=(30, 180)) as transfer:
            transfer.raise_for_status()
            with tmp.open("wb") as dest:
                for block in transfer.iter_content(chunk_size=1024 * 1024):
                    if not block:
                        continue
                    n_bytes += len(block)
                    if n_bytes > max_mb * 1024 * 1024:
                        raise ValueError(f"{pid} exceeds {max_mb} MB; raise --max-mb intentionally")
                    sha.update(block)
                    dest.write(block)
        extracted = []
        with zipfile.ZipFile(tmp) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"Corrupt archive for {pid}")
            for member in archive.infolist():
                if member.is_dir() or not member.filename.lower().endswith(".csv"):
                    continue
                # Flatten archived paths to prevent path traversal.
                safe_name = Path(member.filename).name
                if not safe_name:
                    continue
                target = out / safe_name
                with archive.open(member) as src, target.open("wb") as dest:
                    shutil.copyfileobj(src, dest)
                extracted.append(safe_name)
        if not extracted:
            raise ValueError(f"{pid} downloaded but zip contained no CSV")
    finally:
        tmp.unlink(missing_ok=True)
    entry = {"pid": pid, "source": API.format(pid=pid), "download_url": url,
             "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
             "sha256_zip": sha.hexdigest(), "size_bytes": n_bytes,
             "files": extracted, "state": "downloaded"}
    manifest_path = raw_dir / "manifest.json"
    manifest = read_manifest(manifest_path)
    manifest["snapshots"].append(entry)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return entry

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", nargs="+", choices=TABLES.keys(),
                        default=["32100054"], help="One or more StatCan table PIDs")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--max-mb", type=int, default=600)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    for pid in args.tables:
        print(json.dumps(download_table(pid, args.raw_dir, args.max_mb, args.overwrite), indent=2))

if __name__ == "__main__":
    main()
