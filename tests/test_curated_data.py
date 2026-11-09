"""Guardrails for verified published extracts checked into source control.

Tests are run without downloading any data or using the public network.
"""
import csv
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]/"data"/"curated"

def records(name):
    with (ROOT/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

class CuratedDataTests(unittest.TestCase):
    def test_retail_coverage_and_unique_grain(self):
        r=records("retail_beverage_2020_2025.csv")
        self.assertEqual(len(r),144)
        self.assertEqual(len({(x["source_vector"],x["reference_period"]) for x in r}),144)
        self.assertEqual(set(x["classification_vintage"] for x in r),{"NAPCS 2017","NAPCS 2022"})
        self.assertEqual({x["product_group"] for x in r},
            {"Soft drinks excluding bottled water",
             "Other non-alcoholic beverages excluding soft drinks milk hot and frozen drinks"})
        for x in r:
            self.assertTrue(2020 <= int(x["year"]) <= 2025)
            self.assertEqual(len(x["reference_period"]),7)
            self.assertGreater(int(x["value_cad_thousands"]),0)
        soft2025=sum(int(x["value_cad_thousands"]) for x in r if
            x["year"]=="2025" and x["product_group"]=="Soft drinks excluding bottled water")
        self.assertEqual(soft2025,4883636)

    def test_cpi_coverage(self):
        r=records("cpi_beverages_2020_2025.csv")
        self.assertEqual(len(r),360)
        self.assertEqual(len({(x["source_vector"],x["reference_period"]) for x in r}),360)
        self.assertTrue(all(x["base_year"]=="2002=100" for x in r))
        self.assertTrue(all(float(x["cpi_index"])>0 for x in r))

    def test_manufacturing_coverage(self):
        r=records("manufacturing_soft_drinks_2020_2025.csv")
        self.assertEqual(len(r),144)
        self.assertEqual({x["province"] for x in r},{"Ontario","Quebec"})
        self.assertEqual(len({(x["source_vector"],x["reference_period"]) for x in r}),144)
        self.assertTrue(all(x["naics_code"]=="31211" and
                            x["adjustment"]=="Unadjusted" for x in r))

    def test_food_availability_missingness_and_scope(self):
        r=records("food_availability_2020_2025.csv")
        self.assertEqual(len(r),24)
        self.assertEqual(len({(x["source_vector"],x["year"]) for x in r}),24)
        self.assertEqual({x["product"] for x in r},
            {"Soft drinks","Bottled water","Coffee","Tea"})
        self.assertEqual(sum(x["value_status"]=="missing_in_source" for x in r),9)
        self.assertEqual(sum(x["value_status"]=="observed" for x in r),15)
        self.assertTrue(all(x["value"]=="" for x in r
                            if x["value_status"]=="missing_in_source"))

if __name__=="__main__":
    unittest.main()
