"""Shared helpers; all prepared source data remain observational (not modelled)."""
from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

TABLES = {
    "20100017": "retail_legacy",
    "20100080": "retail_new",
    "18100004": "cpi",
    "32100054": "availability",
    "16100048": "manufacturing",
    "12100176": "trade_industry",
}
BEVERAGE_PATTERN = re.compile(
    r"\b(?:beverages?|soft drinks?|carbonated|bottled water|"
    r"mineral water|drinking water|fruit juices?|vegetable juices?|"
    r"energy drinks?|sports drinks?|coffee|tea|non[- ]alcoholic|"
    r"soda|cola|soft drink and ice manufacturing)\b", re.I
)
# Preliminary safeguard only: final series inclusion requires a metadata audit.
ALCOHOL_EXCLUSION = re.compile(r"\bciders?\b|\bcoolers?\b|\bbeer\b|\bwine\b|\bspirits?\b|(?<!non-)\balcoholic\b|\bcannabis\b|\btobacco\b|\ball-items\b|\bretail commissions\b", re.I)
METADATA_COLUMNS = {
    "REF_DATE", "GEO", "DGUID", "UOM", "UOM_ID", "SCALAR_FACTOR",
    "SCALAR_ID", "VECTOR", "COORDINATE", "VALUE", "STATUS", "SYMBOL",
    "TERMINATED", "DECIMALS", "SOURCE", "RELEASE_DATE",
}

def period_info(value: object) -> tuple[int, str, str, int] | None:
    """(period_key, reference_period, grain, year); no invented month for annual/quarterly."""
    s = str(value).strip()
    year_match = re.fullmatch(r"(20\d{2})", s)
    if year_match:
        y = int(year_match.group(1))
        return y * 100, s, "annual", y
    month_match = re.fullmatch(r"(20\d{2})-(0[1-9]|1[0-2])(?:-\d{2})?", s)
    if month_match:
        y, month = map(int, month_match.groups())
        return y * 100 + month, s[:7], "monthly", y
    quarter_match = re.fullmatch(r"(20\d{2})-?Q([1-4])", s, re.I)
    if quarter_match:
        y, quarter = map(int, quarter_match.groups())
        return y * 100 + (quarter * 3), f"{y}-Q{quarter}", "quarterly", y
    return None

def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                  default=str, separators=(",", ":")).encode("utf-8")).hexdigest()

def series_columns(columns: list[str]) -> list[str]:
    return [c for c in columns if c.upper() not in METADATA_COLUMNS and
            c not in {"REF_DATE", "GEO"} and not c.startswith("Unnamed:")]

def read_manifest(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"snapshots": []}
