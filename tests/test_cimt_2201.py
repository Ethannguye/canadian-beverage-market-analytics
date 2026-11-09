"""Check 2201 and combined HS6 trade against original, unedited user exports."""
import csv
import tempfile
import unittest
from pathlib import Path
from etl.prepare_cimt_2201 import run as run2201, read_total_exports, read_file, HS2201_IMPORT, HS2201_EXPORT
from etl.prepare_cimt_all import run as run_all

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/source_exports/cimt"

class HS2201Tests(unittest.TestCase):
    def test_2201_originals_are_complete(self):
        expected={"2201.10":(4330,1253),"2201.90":(4816,1164)}
        for code, (imports, exports) in expected.items():
            i=read_file(SOURCE/HS2201_IMPORT[code], code)
            e=read_total_exports(SOURCE/HS2201_EXPORT[code], code)
            self.assertEqual((len(i),len(e)),(imports,exports))
            self.assertEqual(len({r["reference_period"] for r in i}),72)
            self.assertEqual(len({r["reference_period"] for r in e}),72)
            self.assertTrue(all(r["hs_code"]==code.replace(".","") for r in e))
            self.assertTrue(all(".00 -" in r["commodity_name"] for r in e))

    def test_full_hs2201_balances(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);profile=run2201(SOURCE,p)
            self.assertEqual(profile["all_rows"],11457)
            self.assertEqual(profile["monthly_rows"],144)
            self.assertEqual(profile["annual_rows"],12)
            with (p/"cimt_2201_trade_annual_balances_2020_2025.csv").open(newline="",encoding="utf-8") as f:
                rows={(r["year"],r["hs_code"]):r for r in csv.DictReader(f)}
            self.assertEqual(int(rows[("2025","220110")]["imports_cad"]),98740904)
            self.assertEqual(int(rows[("2025","220190")]["imports_cad"]),49177038)

    def test_all_five_codes_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);profile=run_all(SOURCE,p)
            self.assertEqual(profile["total_rows"],36091)
            self.assertEqual(profile["hs2201_rows"],11457)
            self.assertEqual(profile["hs2202_rows"],24634)
            self.assertEqual(profile["month_hs_rows"],360)
            self.assertEqual(profile["annual_hs_rows"],30)
            with (p/"cimt_all_trade_annual_balances_2020_2025.csv").open(newline="",encoding="utf-8") as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),30)
            for row in rows:
                self.assertEqual(int(row["trade_balance_cad"]),
                  int(row["exports_cad"])-int(row["imports_cad"]))

if __name__=="__main__":
    unittest.main()
