"""Tests based on user-exported, official CIMT CSV files in the repository."""
import tempfile
import unittest
from pathlib import Path
from etl.prepare_cimt_exports import INPUTS, read_file, run

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/source_exports/cimt"

class CimtSourceTests(unittest.TestCase):
    def test_original_files_full_period(self):
        expected={"2202.10":7577, "2202.91":1533, "2202.99":6560}
        for code, filename in INPUTS.items():
            self.assertEqual(len(read_file(SOURCE/filename, code)), expected[code])
    def test_full_transform_and_2025_amounts(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=run(SOURCE, Path(tmp))
            self.assertEqual(profile["observations"],15670)
            self.assertEqual(profile["monthly_totals_rows"],216)
            self.assertEqual(profile["annual_rows"],18)
            csvfile=Path(tmp)/"cimt_imports_annual_totals_2020_2025.csv"
            import csv
            with csvfile.open(encoding="utf-8",newline="") as f:
                rows=list(csv.DictReader(f))
            amounts={(r["year"],r["hs_code"]):int(r["value_cad"]) for r in rows}
            self.assertEqual(amounts[("2025","220210")],742467960)
            self.assertEqual(amounts[("2025","220291")],36748545)
            self.assertEqual(amounts[("2025","220299")],917338369)
if __name__=="__main__":
    unittest.main()
