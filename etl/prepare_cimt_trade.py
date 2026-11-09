#!/usr/bin/env python3
"""Build HS6 import/export analytical outputs from six unmodified CIMT exports.

Reads the three earlier import files and the three 'Total exports' files.
Includes partner *state* in record-level grain, sums state rows to country totals
only for partner aggregates, and never treats 'Country=Canada' as a World total.
All amounts are *nominal CAD*. No interpolated or invented observations.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
try:
    from etl.prepare_cimt_exports import (
        INPUTS, NORMALIZED_FIELDS, ORIGINAL_FIELDS, ROOT, SOURCE_URL,
        decimal_nonnegative, read_file, write_csv
    )
except ModuleNotFoundError:
    from prepare_cimt_exports import (
        INPUTS, NORMALIZED_FIELDS, ORIGINAL_FIELDS, ROOT, SOURCE_URL,
        decimal_nonnegative, read_file, write_csv
    )

EXPORT_INPUTS = {k: "E" + v for k,v in INPUTS.items()}
TOTAL_FIELDS = ["reference_period", "year", "hs_code", "imports_cad", "exports_cad",
                "trade_balance_cad", "imports_litres", "exports_litres", "import_rows", "export_rows"]
ANNUAL_FIELDS = ["year", "hs_code", "imports_cad", "exports_cad", "trade_balance_cad",
                 "imports_litres", "exports_litres", "import_rows", "export_rows"]
PARTNER_FIELDS = ["year", "hs_code", "partner_country", "imports_cad", "exports_cad",
                  "trade_balance_cad", "imports_litres", "exports_litres",
                  "import_rows", "export_rows"]

def read_total_exports(path: Path, code: str) -> list[dict]:
    """StatCan CSV: a 'Total exports' title, 8-column header, source rows, citation footer."""
    rows = []
    grain = set()
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        title = next(reader, [])
        if title != ["Total exports"]:
            raise ValueError(f"{path}: expected a Total exports dataset, got {title!r}")
        header = next(reader, [])
        if header != ORIGINAL_FIELDS:
            raise ValueError(f"{path}: unexpected columns {header!r}")
        for line_no, row in enumerate(reader, 3):
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) == 1 and (
                row[0].startswith("How to cite:") or
                row[0].startswith("https://") or
                row[0].startswith("Accessed date:")
            ):
                continue
            if len(row) != 8:
                raise ValueError(f"{path}:{line_no} unexpected row length {len(row)}")
            raw_date, desc, province, country, state, value, quantity, unit = row
            if not (desc.startswith(code + " -") or desc.startswith(code + ".00 -")):
                raise ValueError(f"{path}:{line_no} expected {code}, got {desc!r}")
            if province != "Canada" or not country.strip():
                raise ValueError(f"{path}:{line_no} invalid geography or partner")
            when = date.fromisoformat(raw_date)
            if when.day != 1 or not 2020 <= when.year <= 2025:
                raise ValueError(f"{path}:{line_no} date outside requested interval")
            if unit != "Volume in litres":
                raise ValueError(f"{path}:{line_no} unexpected quantity unit {unit!r}")
            money = decimal_nonnegative(value, "Value ($)")
            litres = decimal_nonnegative(quantity, "Quantity")
            month = when.strftime("%Y-%m")
            state = state.strip() or "N/A"
            key = (month, code, province, country, state, unit)
            if key in grain:
                raise ValueError(f"{path}:{line_no} duplicate source grain {key!r}")
            grain.add(key)
            rows.append(dict(zip(NORMALIZED_FIELDS, (
                month, code.replace(".", ""), desc, "Export", country,
                state, province, str(money), str(litres), "litres",
                f"CIMT Total exports accessed 2026-11-09; {path.name}",
                "source-vintage-unverified"
            ))))
    months = {r["reference_period"] for r in rows}
    if len(months) != 72 or min(months) != "2020-01" or max(months) != "2025-12":
        raise ValueError(f"{path}: expected all 72 months, got {len(months)}")
    return rows

def aggregate(records: list[dict], key_fields: tuple[str, ...], year_only: bool=False) -> list[dict]:
    amounts: dict[tuple, dict] = defaultdict(lambda: dict(
        imports_cad=Decimal(0), exports_cad=Decimal(0),
        imports_litres=Decimal(0), exports_litres=Decimal(0),
        import_rows=0, export_rows=0))
    for r in records:
        key = tuple((r["reference_period"][:4] if year_only and k=="year"
                     else r["reference_period"][:4] if k=="year"
                     else r[k]) for k in key_fields)
        item = amounts[key]
        side = "imports" if r["trade_flow"] == "Import" else "exports"
        item[f"{side}_cad"] += Decimal(r["value_cad"])
        item[f"{side}_litres"] += Decimal(r["quantity"])
        item["import_rows" if side == "imports" else "export_rows"] += 1
    output = []
    for key, a in sorted(amounts.items()):
        d = dict(zip(key_fields, key))
        if "reference_period" in d:
            d["year"] = d["reference_period"][:4]
        d.update({k:str(v) if isinstance(v,Decimal) else v for k,v in a.items()})
        d["trade_balance_cad"] = str(a["exports_cad"]-a["imports_cad"])
        output.append(d)
    return output

def run(source: Path, output: Path) -> dict:
    imports = []
    exports = []
    by_flow_code = {}
    for code, name in INPUTS.items():
        imported = read_file(source/name, code)
        exported = read_total_exports(source/EXPORT_INPUTS[code], code)
        imports.extend(imported)
        exports.extend(exported)
        by_flow_code[code] = dict(imports=len(imported), total_exports=len(exported))
    data = imports + exports
    if len({(r["reference_period"],r["hs_code"],r["trade_flow"],
             r["partner_country"],r["partner_state"],r["clearance_geography"],
             r["quantity_unit"]) for r in data}) != len(data):
        raise ValueError("Duplicate flow-month-HS-country-state rows after merge")
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output/"cimt_trade_normalized_2020_2025.csv", NORMALIZED_FIELDS,data)
    monthly = aggregate(data,("reference_period","hs_code"))
    annual = aggregate(data,("year","hs_code"),year_only=True)
    partners = aggregate(data,("year","hs_code","partner_country"),year_only=True)
    write_csv(output/"cimt_trade_monthly_balances_2020_2025.csv", TOTAL_FIELDS, monthly)
    write_csv(output/"cimt_trade_annual_balances_2020_2025.csv", ANNUAL_FIELDS, annual)
    write_csv(output/"cimt_trade_annual_partner_2020_2025.csv", PARTNER_FIELDS, partners)
    profile = {
        "source": SOURCE_URL, "date_range": "2020-01 to 2025-12",
        "import_rows": len(imports), "total_export_rows": len(exports),
        "all_observations": len(data), "by_hs": by_flow_code,
        "monthly_hs_rows": len(monthly), "annual_hs_rows": len(annual),
        "year_hs_partner_rows": len(partners),
        "source_trade_flow": "Total exports (includes domestic exports and re-exports)",
        "unit": "CAD nominal values; source quantity is litres",
        "limitations": [
            "Only HS 220210, 220291, 220299. Not entire Canadian beverage sector.",
            "Partner Canada in source Imports is not a World total.",
            "US state observations are separate and are summed once for USA aggregates.",
            "Annual figures sum actual monthly source rows. No extrapolated missing values.",
            "HS classification definitions/vintage may change; review before causal claims."
        ]
    }
    (output/"cimt_trade_profile.json").write_text(json.dumps(profile, indent=2),encoding="utf-8")
    return profile

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-dir",type=Path,default=ROOT/"data/source_exports/cimt")
    p.add_argument("--output-dir",type=Path,default=ROOT/"data/processed")
    args=p.parse_args()
    print(json.dumps(run(args.input_dir,args.output_dir),indent=2))

if __name__=="__main__":
    main()
