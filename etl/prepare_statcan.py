#!/usr/bin/env python3
"""Prepare *candidate* beverage series for MySQL staging. Review codes before fact loads.

The text filter intentionally creates candidates, not an approved product classification.
Use --all-categories for source discovery when text filters miss relevant series.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import pandas as pd

try:
    from etl.common import TABLES, BEVERAGE_PATTERN, ALCOHOL_EXCLUSION, digest, period_info, series_columns
except ModuleNotFoundError:
    from common import TABLES, BEVERAGE_PATTERN, ALCOHOL_EXCLUSION, digest, period_info, series_columns

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ["row_hash", "source_id", "series_id", "period_key", "reference_period",
           "year", "period_grain", "category_label", "geography", "unit",
           "scalar_factor", "vector_id", "coordinate", "measure_value",
           "status_code", "dimensions_json"]

PREFERRED_CATEGORY = ("Products and product groups", "Commodities", "Commodity",
    "Products", "Product", "Food available", "Food group", "North American Industry "
    "Classification System (NAICS)", "Industry", "Components", "Goods and services")

def clean_num(raw: object) -> str:
    """Return a safe numeric string; missing/invalid values are loaded as SQL NULL."""
    s = str(raw).strip().replace(",", "")
    if not s or s.lower() in {"nan", "none", "..", "x", "f", "not available"}:
        return ""
    try:
        n = float(s)
        if not (float("-inf") < n < float("inf")):
            return ""
        return s
    except (ValueError, OverflowError):
        return ""

def pick_category(dimensions: dict) -> str:
    for key in PREFERRED_CATEGORY:
        if key in dimensions and dimensions[key]:
            return str(dimensions[key])
    return " | ".join(f"{k}: {v}" for k, v in dimensions.items())[:512]

def find_data_csv(raw_dir: Path, pid: str) -> Path:
    location = raw_dir / pid
    if not location.exists():
        raise FileNotFoundError(f"No raw data for {pid}. Run download_statcan.py")
    files = [p for p in location.glob("*.csv") if not p.name.lower().endswith("_meta.csv")
             and "metadata" not in p.name.lower()]
    exact = [p for p in files if p.stem == pid]
    if exact:
        return exact[0]
    if len(files) == 1:
        return files[0]
    raise ValueError(f"Ambiguous data CSVs for {pid}: {[str(x) for x in files]}")

def process_table(pid: str, raw_dir: Path, output_dir: Path,
                  all_categories: bool = False, chunksize: int = 50000) -> dict:
    source_file = find_data_csv(raw_dir, pid)
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{pid}_staging.csv"
    profile_path = output_dir / f"{pid}_profile.json"
    input_rows = selected = missing = 0
    categories: set[str] = set()
    granularities: dict[str, int] = {}
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for chunk in pd.read_csv(source_file, chunksize=chunksize, dtype=str,
                                 encoding="utf-8-sig", keep_default_na=False, low_memory=False):
            if not {"REF_DATE", "VALUE"}.issubset(set(chunk.columns)):
                raise ValueError(f"Source {source_file} missing REF_DATE or VALUE")
            extra_cols = series_columns(list(chunk.columns))
            for row in chunk.to_dict("records"):
                input_rows += 1
                period = period_info(row.get("REF_DATE", ""))
                if period is None or not 2020 <= period[3] <= 2025:
                    continue
                dimension_values = {k: str(row.get(k, "")) for k in extra_cols
                                    if str(row.get(k, "")).strip()}
                label = pick_category(dimension_values)
                text = " | ".join(dimension_values.values())
                if not all_categories and (not BEVERAGE_PATTERN.search(text) or ALCOHOL_EXCLUSION.search(text)):
                    continue
                period_key, period_ref, grain, year = period
                geography = str(row.get("GEO", ""))
                unit = str(row.get("UOM", ""))
                scalar = str(row.get("SCALAR_FACTOR", ""))
                vector = str(row.get("VECTOR", ""))
                coord = str(row.get("COORDINATE", ""))
                # VECTOR is the preferred identity for a series; dimensions are backup.
                identity = vector if vector else (coord if coord else dimension_values)
                series_id = digest([pid, identity, geography, unit, scalar])
                row_hash = digest([series_id, period_ref])
                value = clean_num(row.get("VALUE", ""))
                missing += not bool(value)
                categories.add(label)
                granularities[grain] = granularities.get(grain, 0) + 1
                writer.writerow({
                    "row_hash": row_hash, "source_id": pid, "series_id": series_id,
                    "period_key": period_key, "reference_period": period_ref, "year": year,
                    "period_grain": grain, "category_label": label[:512],
                    "geography": geography[:255], "unit": unit[:100],
                    "scalar_factor": scalar[:100], "vector_id": vector[:100],
                    "coordinate": coord[:255], "measure_value": value,
                    "status_code": str(row.get("STATUS", ""))[:50],
                    "dimensions_json": json.dumps(dimension_values, ensure_ascii=False,
                                                   sort_keys=True)})
                selected += 1
    result = {
        "pid": pid, "source_file": str(source_file), "output_file": str(out),
        "input_rows": input_rows, "candidate_rows_2020_2025": selected,
        "candidate_missing_value_rows": missing,
        "date_grains": granularities, "distinct_categories": len(categories),
        "sample_categories": sorted(categories)[:60],
        "category_selection": "all" if all_categories else "unreviewed_beverage_regex",
        "warning": "Rows are discovery candidates. Approve exact series after reviewing metadata."
    }
    profile_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", nargs="+", choices=TABLES.keys(),
                        default=["32100054"])
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed")
    parser.add_argument("--all-categories", action="store_true")
    parser.add_argument("--chunksize", type=int, default=50000)
    args = parser.parse_args()
    for pid in args.tables:
        print(json.dumps(process_table(pid, args.raw_dir, args.output_dir,
                                      args.all_categories, args.chunksize), indent=2))

if __name__ == "__main__":
    main()
