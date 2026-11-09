#!/usr/bin/env python3
"""Build unified five-code HS6 import/export fact and balance outputs.

Keeps original HS2202 and HS2201 outputs independently reproducible, then
combines their validated normalized rows. No source data is modified.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from etl.prepare_cimt_exports import ROOT, NORMALIZED_FIELDS, write_csv
from etl.prepare_cimt_trade import run as run_2202, aggregate, TOTAL_FIELDS, ANNUAL_FIELDS, PARTNER_FIELDS
from etl.prepare_cimt_2201 import run as run_2201

PREFIX="cimt_all"

def read_normalized(path: Path) -> list[dict]:
    with path.open(encoding="utf-8",newline="") as f:
        reader = csv.DictReader(f)
        if list(reader.fieldnames or []) != NORMALIZED_FIELDS:
            raise ValueError(f"Unexpected normalized columns in {path}")
        return list(reader)

def run(input_dir: Path, output_dir: Path) -> dict:
    a = run_2202(input_dir,output_dir)
    b = run_2201(input_dir,output_dir)
    records = (
        read_normalized(output_dir/"cimt_trade_normalized_2020_2025.csv") +
        read_normalized(output_dir/"cimt_2201_trade_normalized_2020_2025.csv")
    )
    keys = {(r["reference_period"],r["hs_code"],r["trade_flow"],
             r["partner_country"],r["partner_state"],r["clearance_geography"],
             r["quantity_unit"]) for r in records}
    if len(keys)!=len(records):
        raise ValueError("Duplicates after joining two verified HS source families")
    count_by_code_flow = {}
    for r in records:
        k=f'{r["hs_code"]}:{r["trade_flow"]}'
        count_by_code_flow[k]=count_by_code_flow.get(k,0)+1
    expected_codes={"220110","220190","220210","220291","220299"}
    if {r["hs_code"] for r in records} != expected_codes:
        raise ValueError("Incomplete expected HS6 codes")
    monthly=aggregate(records,("reference_period","hs_code"))
    annual=aggregate(records,("year","hs_code"),year_only=True)
    partner=aggregate(records,("year","hs_code","partner_country"),year_only=True)
    if len(monthly)!=360 or len(annual)!=30:
        raise ValueError("Expected 72 months times 5 codes and 6 years times 5 codes")
    write_csv(output_dir/f"{PREFIX}_trade_normalized_2020_2025.csv", NORMALIZED_FIELDS, records)
    write_csv(output_dir/f"{PREFIX}_trade_monthly_balances_2020_2025.csv", TOTAL_FIELDS, monthly)
    write_csv(output_dir/f"{PREFIX}_trade_annual_balances_2020_2025.csv", ANNUAL_FIELDS, annual)
    write_csv(output_dir/f"{PREFIX}_trade_annual_partner_2020_2025.csv", PARTNER_FIELDS, partner)
    profile={
        "source":"Statistics Canada CIMT app, user exports, accessed 2026-11-09",
        "total_rows":len(records),"hs2202_rows":a["all_observations"],
        "hs2201_rows":b["all_rows"],"month_hs_rows":len(monthly),
        "annual_hs_rows":len(annual),"annual_partner_rows":len(partner),
        "count_by_code_flow":count_by_code_flow,
        "warning":"HS220190 includes ice and snow. Exports are Total exports incl re-exports; not market size."
    }
    (output_dir/f"{PREFIX}_profile.json").write_text(json.dumps(profile,indent=2),encoding="utf-8")
    return profile

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-dir",type=Path,default=ROOT/"data/source_exports/cimt")
    p.add_argument("--output-dir",type=Path,default=ROOT/"data/processed")
    args=p.parse_args()
    print(json.dumps(run(args.input_dir,args.output_dir),indent=2))

if __name__=="__main__":
    main()
