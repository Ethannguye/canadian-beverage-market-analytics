#!/usr/bin/env python3
"""Normalize 4 original Canada HS2201 imports / Total exports files.

Outputs are a *separate* HS2201 data slice to preserve reproducibility of the
existing HS2202 tests and historical curated files. No fabricated observations.

HS220190 explicitly includes ice and snow; it is not exclusively bottled water.
Canada is the reporting geography; trade partners include US state-level rows.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from etl.prepare_cimt_exports import read_file, write_csv, NORMALIZED_FIELDS, ROOT, SOURCE_URL
from etl.prepare_cimt_trade import (
    read_total_exports, aggregate, TOTAL_FIELDS, ANNUAL_FIELDS, PARTNER_FIELDS
)

HS2201_IMPORT = {"2201.10": "I2201.10.csv", "2201.90": "I2201.90.csv"}
HS2201_EXPORT = {"2201.10": "E2201.10.csv", "2201.90": "E2201.90.csv"}
PREFIX = "cimt_2201"

def run(input_dir: Path, output_dir: Path) -> dict:
    all_rows = []
    code_counts = {}
    for hs, filename in HS2201_IMPORT.items():
        imports = read_file(input_dir / filename, hs)
        exports = read_total_exports(input_dir / HS2201_EXPORT[hs], hs)
        if len({r["reference_period"] for r in imports}) != 72:
            raise ValueError(f"Incomplete imports for {hs}")
        if len({r["reference_period"] for r in exports}) != 72:
            raise ValueError(f"Incomplete exports for {hs}")
        code_counts[hs] = {"imports": len(imports), "total_exports": len(exports)}
        all_rows.extend(imports)
        all_rows.extend(exports)

    # A row can recur in another flow; trade flow is part of the unique grain.
    keys = {(r["reference_period"],r["hs_code"],r["trade_flow"],
             r["partner_country"],r["partner_state"],r["clearance_geography"],
             r["quantity_unit"]) for r in all_rows}
    if len(keys) != len(all_rows):
        raise ValueError("Duplicate trade grain after merging HS2201 source exports")

    monthly = aggregate(all_rows, ("reference_period","hs_code"))
    annual = aggregate(all_rows, ("year","hs_code"),year_only=True)
    partner = aggregate(all_rows, ("year","hs_code","partner_country"),year_only=True)
    if len(monthly) != 144 or len(annual) != 12:
        raise ValueError(f"Unexpected HS2201 period coverage {len(monthly)}, {len(annual)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / f"{PREFIX}_trade_normalized_2020_2025.csv", NORMALIZED_FIELDS, all_rows)
    write_csv(output_dir / f"{PREFIX}_trade_monthly_balances_2020_2025.csv", TOTAL_FIELDS, monthly)
    write_csv(output_dir / f"{PREFIX}_trade_annual_balances_2020_2025.csv", ANNUAL_FIELDS, annual)
    write_csv(output_dir / f"{PREFIX}_trade_annual_partner_2020_2025.csv", PARTNER_FIELDS, partner)

    profile = {
        "source": SOURCE_URL,
        "scope": "Canada total, HS 220110 and HS 220190 imports and Total exports",
        "window": "2020-01 through 2025-12",
        "original_files": {**HS2201_IMPORT, **{f"Export:{k}":v for k,v in HS2201_EXPORT.items()}},
        "code_counts": code_counts, "all_rows": len(all_rows),
        "monthly_rows": len(monthly), "annual_rows": len(annual),
        "annual_country_rows": len(partner),
        "trade_value_unit": "CAD nominal, source dollars",
        "quantity_unit": "litres",
        "warnings": [
            "HS220190 includes ice and snow and other waters. Not bottled water exclusively.",
            "Total exports includes re-exports; not equivalent to Canadian production.",
            "US state breakdown is retained; state values are summed only in country totals.",
            "All four original files now have at least one recorded row in each of 72 months.",
            "No industry-wide market size should be inferred from these two headings."
        ]
    }
    (output_dir / f"{PREFIX}_profile.json").write_text(json.dumps(profile,indent=2), encoding="utf-8")
    return profile

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-dir", type=Path, default=ROOT/"data/source_exports/cimt")
    p.add_argument("--output-dir",type=Path,default=ROOT/"data/processed")
    args=p.parse_args()
    print(json.dumps(run(args.input_dir,args.output_dir),indent=2))

if __name__ == "__main__":
    main()
