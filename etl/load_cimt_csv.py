#!/usr/bin/env python3
"""Load a HUMAN-VERIFIED, normalized CIMT export. No fake or auto-generated trade values.

See docs/cimt_export_guide.md for the mandatory columns and coverage checklist.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
import mysql.connector
try:
    from etl.common import period_info
    from etl.load_mysql import connection
except ModuleNotFoundError:
    from common import period_info
    from load_mysql import connection

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ("reference_period","hs_code","commodity_name","trade_flow",
           "partner_country","partner_state","clearance_geography","value_cad","quantity",
           "quantity_unit","source_note","classification_version")
HEADINGS = ("2009", "2201", "2202")

def validate(r: dict) -> dict:
    missing = [c for c in HEADERS if c not in r]
    if missing:
        raise ValueError(f"Missing CIMT columns: {missing}")
    period = period_info(r["reference_period"])
    if period is None or period[2] != "monthly" or not 2020 <= period[3] <= 2025:
        raise ValueError(f"Must be monthly date between 2020 and 2025: {r['reference_period']}")
    hs = r["hs_code"].strip()
    if not hs.isdigit() or not 4 <= len(hs) <= 10 or hs[:4] not in HEADINGS:
        raise ValueError(f"Not a validated beverage HS candidate: {hs}")
    flow = r["trade_flow"].strip().title()
    if flow not in ("Import", "Export"):
        raise ValueError(f"Invalid trade_flow: {flow}")
    for field in ("commodity_name","partner_country","partner_state","clearance_geography",
                  "source_note","classification_version"):
        if not r[field].strip():
            raise ValueError(f"Required field blank: {field}")
    try:
        val = Decimal(r["value_cad"].strip())
        qty = Decimal(r["quantity"].strip()) if r["quantity"].strip() else None
    except InvalidOperation as e:
        raise ValueError("Non-numeric monetary value or quantity") from e
    if not val.is_finite() or val < 0 or (qty is not None and (not qty.is_finite() or qty < 0)):
        raise ValueError("Negative or nonfinite values in trade data")
    if qty is not None and not r["quantity_unit"].strip():
        raise ValueError("quantity_unit is required when quantity is present")
    key = [period[1],hs,flow,r["partner_country"].strip(),
           r["partner_state"].strip(),r["clearance_geography"].strip(),r["quantity_unit"].strip()]
    row_id = hashlib.sha256(json.dumps(key,ensure_ascii=False).encode()).hexdigest()
    return {"id":row_id,"period":period,"hs":hs,"name":r["commodity_name"].strip(),
        "flow":flow,"partner":r["partner_country"].strip(), "state":r["partner_state"].strip(),
        "geo":r["clearance_geography"].strip(),"value":val,"quantity":qty,
        "quantity_unit":r["quantity_unit"].strip(),"source_note":r["source_note"].strip(),
        "version":r["classification_version"].strip()}

def import_file(path: Path, conn) -> int:
    seen: set[str] = set()
    count = 0
    cursor = conn.cursor()
    try:
        with path.open(encoding="utf-8-sig",newline="") as f:
            for line_num,raw in enumerate(csv.DictReader(f),start=2):
                row = validate(raw)
                if row["id"] in seen:
                    raise ValueError(f"Duplicate trade grain at CSV line {line_num}")
                seen.add(row["id"])
                p = row["period"]
                cursor.execute("""
                    INSERT INTO dim_period(reference_period,period_key,period_year,period_grain)
                    VALUES (%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE period_key=VALUES(period_key)
                """,(p[1],p[0],p[3],p[2]))
                cursor.execute("""
                    INSERT INTO dim_hs_product(hs_code,commodity_name,classification_version)
                    VALUES (%s,%s,%s)
                    ON DUPLICATE KEY UPDATE commodity_name=VALUES(commodity_name)
                """,(row["hs"],row["name"],row["version"]))
                cursor.execute("""
                    INSERT INTO fact_hs_trade
                    (trade_row_id,reference_period,hs_code,trade_flow,partner_country,partner_state,
                     clearance_geography,value_cad,quantity,quantity_unit,source_note)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE value_cad=VALUES(value_cad),
                        quantity=VALUES(quantity),source_note=VALUES(source_note)
                """,(row["id"],p[1],row["hs"],row["flow"],row["partner"],
                     row["state"],row["geo"],row["value"],row["quantity"],row["quantity_unit"],
                     row["source_note"]))
                count += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
    return count

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file",type=Path,
                        help="Normalized CSV based on original, verified CIMT export")
    args = parser.parse_args()
    with connection() as conn:
        count = import_file(args.file,conn)
    print(json.dumps({"rows_imported":count,"approved_hs_codes":0,
                      "warning":"Review HS codes before approving dim_hs_product."}))

if __name__ == "__main__":
    main()
