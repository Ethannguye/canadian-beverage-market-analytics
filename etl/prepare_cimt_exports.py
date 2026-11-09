"""Prepare official three HS6 IMPORT source files from CIMT into clean, audited observations.

No fabricated data. The first source line 'Imports' and trailing citation footer
are intentionally skipped. Preserve US partner-state detail to prevent silent collisions.
See docs/discovery_cimt_imports.md.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = {"2202.10": "2202.10.csv", "2202.91": "2202.91.csv", "2202.99": "2202.99.csv"}
SOURCE_URL = "https://www150.statcan.gc.ca/n1/pub/71-607-x/71-607-x2021004-eng.htm"
NORMALIZED_FIELDS = [
    "reference_period", "hs_code", "commodity_name", "trade_flow",
    "partner_country", "partner_state", "clearance_geography",
    "value_cad", "quantity", "quantity_unit", "source_note", "classification_version"
]
PARTNER_FIELDS = ["reference_period", "year", "hs_code", "partner_country",
    "value_cad", "quantity_litres", "source_rows"]
TOTAL_FIELDS = ["reference_period", "year", "hs_code", "value_cad",
    "quantity_litres", "source_rows"]
ANNUAL_FIELDS = ["year", "hs_code", "value_cad", "quantity_litres", "source_rows"]
ORIGINAL_FIELDS = ["Period", "Commodity", "Province", "Country", "State",
    "Value ($)", "Quantity", "Unit of measure"]

def decimal_nonnegative(value: str, field: str) -> Decimal:
    try:
        v = Decimal(value.replace(",", "").strip())
    except (InvalidOperation, AttributeError) as ex:
        raise ValueError(f"Invalid {field}: {value!r}") from ex
    if not v.is_finite() or v < 0:
        raise ValueError(f"Bad {field}: {value!r}")
    return v

def read_file(path: Path, expected_hs: str) -> list[dict]:
    out: list[dict] = []
    seen: set[tuple[str, ...]] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        title = next(reader, [])
        if title != ["Imports"]:
            raise ValueError(f"{path}: expected 'Imports' title, got {title}")
        header = next(reader, [])
        if header != ORIGINAL_FIELDS:
            raise ValueError(f"{path}: unexpected header {header}")
        for line_no, row in enumerate(reader, 3):
            # Original StatCan file ends with citation lines, not data.
            if not row or len(row) != 8 or not row[0].strip():
                if row and (row[0].startswith("How to cite:") or
                            row[0].startswith("Accessed date:") or
                            row[0].startswith("https://")):
                    continue
                if row and any(c.strip() for c in row):
                    raise ValueError(f"{path}:{line_no} non-data row: {row[:2]}")
                continue
            raw_date, label, geography, country, state, value, qty, unit = row
            if not label.startswith(expected_hs + " -"):
                raise ValueError(f"{path}:{line_no} unexpected code {label[:40]}")
            if geography != "Canada" or not country.strip():
                raise ValueError(f"{path}:{line_no} unexpected geography/partner")
            try:
                d = date.fromisoformat(raw_date)
            except ValueError as ex:
                raise ValueError(f"{path}:{line_no} invalid date {raw_date!r}") from ex
            if not (2020 <= d.year <= 2025 and d.day == 1):
                raise ValueError(f"{path}:{line_no} date outside monthly window")
            if unit != "Volume in litres":
                raise ValueError(f"{path}:{line_no} unexpected unit {unit!r}")
            money = decimal_nonnegative(value, "Value ($)")
            litres = decimal_nonnegative(qty, "Quantity")
            month = d.strftime("%Y-%m")
            state = state.strip() or "N/A"
            key = (month, expected_hs, geography, country, state, unit)
            if key in seen:
                raise ValueError(f"{path}:{line_no} duplicate grain {key}")
            seen.add(key)
            out.append(dict(zip(NORMALIZED_FIELDS, (
                month, expected_hs.replace(".", ""), label, "Import",
                country, state, geography, str(money), str(litres),
                "litres", f"CIMT export accessed 2026-11-09; {path.name}",
                "source-vintage-unverified"
            ))))
    months = {r["reference_period"] for r in out}
    if len(months) != 72 or min(months) != "2020-01" or max(months) != "2025-12":
        raise ValueError(f"{path}: incomplete 2020-2025 monthly coverage: {len(months)}")
    return out

def write_csv(path: Path, fields: list[str], records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

def run(input_dir: Path, output_dir: Path) -> dict:
    data: list[dict] = []
    counts = {}
    for code, filename in INPUTS.items():
        rows = read_file(input_dir / filename, code)
        counts[code] = len(rows)
        data.extend(rows)
    write_csv(output_dir / "cimt_imports_normalized_2020_2025.csv", NORMALIZED_FIELDS, data)
    by_month = defaultdict(lambda: [Decimal(0), Decimal(0), 0])
    by_partner = defaultdict(lambda: [Decimal(0), Decimal(0), 0])
    by_annual = defaultdict(lambda: [Decimal(0), Decimal(0), 0])
    for r in data:
        month = r["reference_period"]
        year = month[:4]
        code = r["hs_code"]
        value = Decimal(r["value_cad"])
        quantity = Decimal(r["quantity"])
        for key, d in (
            ((month, code), by_month),
            ((month, code, r["partner_country"]), by_partner),
            ((year, code), by_annual)
        ):
            item = d[key]
            item[0] += value
            item[1] += quantity
            item[2] += 1
    def render(key, totals, kind):
        value, quantity, n = totals
        if kind == "month":
            month, code = key
            return dict(reference_period=month, year=month[:4], hs_code=code,
                        value_cad=str(value), quantity_litres=str(quantity), source_rows=n)
        if kind == "partner":
            month, code, country = key
            return dict(reference_period=month, year=month[:4], hs_code=code,
                        partner_country=country, value_cad=str(value),
                        quantity_litres=str(quantity), source_rows=n)
        year, code = key
        return dict(year=year, hs_code=code, value_cad=str(value),
                    quantity_litres=str(quantity), source_rows=n)
    totals = [render(k, v, "month") for k,v in sorted(by_month.items())]
    partners = [render(k, v, "partner") for k,v in sorted(by_partner.items())]
    annual = [render(k, v, "annual") for k,v in sorted(by_annual.items())]
    write_csv(output_dir / "cimt_imports_monthly_totals_2020_2025.csv", TOTAL_FIELDS, totals)
    write_csv(output_dir / "cimt_imports_monthly_partner_2020_2025.csv", PARTNER_FIELDS, partners)
    write_csv(output_dir / "cimt_imports_annual_totals_2020_2025.csv", ANNUAL_FIELDS, annual)
    profile = {
        "source": SOURCE_URL,
        "scope": "imports, Canada total, HS6, all reported partners and US states, monthly 2020–2025",
        "observations": len(data), "counts_by_code": counts,
        "monthly_totals_rows": len(totals),
        "partner_month_rows": len(partners),
        "annual_rows": len(annual),
        "no_duplicate_natural_keys": True,
        "unit": "Canadian dollars and litres (as reported)",
        "notes": [
            "Partner country 'Canada' is an original source value, not a World total.",
            "US state records are distinct and summed to US country totals only for aggregates.",
            "2202.91 is non-alcoholic beer; segment separately from ordinary soft drinks.",
            "The three HS6 subheadings do not cover HS2201 or HS2009.",
            "Only imports are in these files; do not infer trade balance.",
            "HS vintage changes should be reviewed before long-term comparisons."
        ]
    }
    (output_dir / "cimt_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    return profile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "data/source_exports/cimt")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed")
    args = parser.parse_args()
    print(json.dumps(run(args.input_dir, args.output_dir), indent=2))

if __name__ == "__main__":
    main()
