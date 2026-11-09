#!/usr/bin/env python3
"""Load candidate source staging into MySQL. Does NOT approve facts by itself."""
from __future__ import annotations
import argparse
import csv
import json
import os
from decimal import Decimal
from pathlib import Path
import mysql.connector
try:
    from etl.common import TABLES
except ModuleNotFoundError:
    from common import TABLES

ROOT = Path(__file__).resolve().parents[1]
STAGE_SQL = """
INSERT INTO stg_statcan_observation
(row_hash,source_id,series_id,period_key,reference_period,period_year,
 period_grain,category_label,geography,unit_label,scalar_factor,vector_id,
 coordinate,measure_value,status_code,dimensions_json)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
 measure_value=VALUES(measure_value),status_code=VALUES(status_code),
 dimensions_json=VALUES(dimensions_json)
"""
PERIOD_SQL = """
INSERT INTO dim_period(reference_period,period_key,period_year,period_grain)
VALUES (%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE period_key=VALUES(period_key),period_grain=VALUES(period_grain)
"""
SERIES_SQL = """
INSERT INTO dim_series
(series_id,source_id,category_label,geography,unit_label,scalar_factor,vector_id,
 coordinate,dimensions_json)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
 category_label=VALUES(category_label),dimensions_json=VALUES(dimensions_json)
-- Approval state intentionally preserved during reimports.
"""

def connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST","localhost"),
        port=int(os.getenv("MYSQL_PORT","3306")),
        database=os.getenv("MYSQL_DATABASE","canadian_beverage_market"),
        user=os.getenv("MYSQL_USER","root"),
        password=os.getenv("MYSQL_PASSWORD",""),
    )

def chunks(reader, size: int):
    chunk = []
    for row in reader:
        chunk.append(row)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

def upload_file(path: Path, conn, batch_size: int = 1000) -> int:
    if not path.exists():
        raise FileNotFoundError(path)
    count = 0
    cursor = conn.cursor()
    try:
        with path.open(encoding="utf-8",newline="") as f:
            for batch in chunks(csv.DictReader(f), batch_size):
                periods = {}
                series = {}
                observations = []
                for r in batch:
                    periods[r["reference_period"]] = (
                        r["reference_period"],int(r["period_key"]),int(r["year"]),r["period_grain"])
                    series[r["series_id"]] = (
                        r["series_id"],r["source_id"],r["category_label"],r["geography"],
                        r["unit"],r["scalar_factor"],r["vector_id"],r["coordinate"],
                        r["dimensions_json"])
                    observations.append((
                        r["row_hash"],r["source_id"],r["series_id"],int(r["period_key"]),
                        r["reference_period"],int(r["year"]),r["period_grain"],
                        r["category_label"],r["geography"],r["unit"],r["scalar_factor"],
                        r["vector_id"],r["coordinate"],
                        Decimal(r["measure_value"]) if r["measure_value"] else None,
                        r["status_code"],r["dimensions_json"]))
                cursor.executemany(PERIOD_SQL, list(periods.values()))
                cursor.executemany(SERIES_SQL, list(series.values()))
                cursor.executemany(STAGE_SQL, observations)
                conn.commit()
                count += len(batch)
    finally:
        cursor.close()
    return count

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", nargs="+",choices=TABLES.keys(),default=["32100054"])
    parser.add_argument("--processed-dir",type=Path,default=ROOT/"data/processed")
    parser.add_argument("--batch-size",type=int,default=1000)
    args = parser.parse_args()
    with connection() as conn:
        for pid in args.tables:
            count = upload_file(args.processed_dir/f"{pid}_staging.csv",conn,args.batch_size)
            print(json.dumps({"source_id":pid,"candidate_rows_staged":count,
                              "facts_approved_automatically":0}))
    print("Inspect dim_series candidate labels and approve selected series in SQL before CALL sp_materialize_approved_facts().")

if __name__ == "__main__":
    main()
