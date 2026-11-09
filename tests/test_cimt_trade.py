"""Smoke/integrity tests against exact official raw files uploaded by user."""
import csv
import tempfile
import unittest
from pathlib import Path
from etl.prepare_cimt_trade import EXPORT_INPUTS, read_total_exports, run

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"data/source_exports/cimt"

class CimtFullTradeTests(unittest.TestCase):
    def test_export_file_coverage(self):
        expected={"2202.10":3695,"2202.91":976,"2202.99":4293}
        for code,filename in EXPORT_INPUTS.items():
            data=read_total_exports(RAW/filename,code)
            self.assertEqual(len(data),expected[code])
            self.assertEqual({r["trade_flow"] for r in data},{"Export"})
            self.assertEqual(len({r["reference_period"] for r in data}),72)

    def test_curated_trade_summaries_match_rebuilt_official_sources(self):
        curated = ROOT / "data" / "curated"
        files = [
            ("cimt_trade_monthly_balances_2020_2025.csv",("reference_period","hs_code")),
            ("cimt_trade_annual_balances_2020_2025.csv",("year","hs_code")),
            ("cimt_trade_annual_partner_2020_2025.csv",("year","hs_code","partner_country")),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            produced = Path(tmp)
            run(RAW,produced)
            for filename, key_names in files:
                def keyed(path):
                    with path.open(encoding="utf-8",newline="") as f:
                        values = list(csv.DictReader(f))
                    return {tuple(row[n] for n in key_names):row for row in values}
                from_originals = keyed(produced/filename)
                committed = keyed(curated/filename)
                self.assertEqual(committed,from_originals,filename)

    def test_trade_balance_reproducibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            profile=run(RAW,out)
            self.assertEqual(profile["import_rows"],15670)
            self.assertEqual(profile["total_export_rows"],8964)
            self.assertEqual(profile["all_observations"],24634)
            self.assertEqual(profile["monthly_hs_rows"],216)
            self.assertEqual(profile["annual_hs_rows"],18)
            with (out/"cimt_trade_annual_balances_2020_2025.csv").open(newline="",encoding="utf-8") as f:
                rows=list(csv.DictReader(f))
            r={(x["year"],x["hs_code"]):x for x in rows}
            self.assertEqual(int(r[("2025","220210")]["exports_cad"]),345659136)
            self.assertEqual(int(r[("2025","220291")]["exports_cad"]),10275799)
            self.assertEqual(int(r[("2025","220299")]["exports_cad"]),426863410)
            self.assertEqual(int(r[("2025","220299")]["trade_balance_cad"]),-490474959)
            self.assertEqual(int(r[("2025","220210")]["trade_balance_cad"]),-396808824)
            self.assertEqual(int(r[("2025","220291")]["trade_balance_cad"]),-26472746)
            self.assertEqual(sum(int(x["trade_balance_cad"]) for x in rows
                                 if x["year"]=="2025"),-913756529)

if __name__=="__main__":
    unittest.main()
