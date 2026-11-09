import unittest
from etl.common import TABLES, BEVERAGE_PATTERN, ALCOHOL_EXCLUSION, digest, period_info, series_columns
from etl.prepare_statcan import clean_num, pick_category

class PeriodTests(unittest.TestCase):
    def test_month(self):
        self.assertEqual(period_info("2025-12"), (202512,"2025-12","monthly",2025))
    def test_annual(self):
        self.assertEqual(period_info("2020"), (202000,"2020","annual",2020))
    def test_quarter(self):
        self.assertEqual(period_info("2024-Q2"), (202406,"2024-Q2","quarterly",2024))
    def test_bad_date(self):
        self.assertIsNone(period_info("2025-13"))
    def test_stable_hash(self):
        self.assertEqual(digest(["a", 1]), digest(["a", 1]))
        self.assertNotEqual(digest(["a", 1]), digest(["a", 2]))
    def test_dimension_selection(self):
        self.assertEqual(series_columns(["REF_DATE","GEO","VECTOR","Products","UOM"]),["Products"])
    def test_numeric(self):
        self.assertEqual(clean_num("1,200.5"),"1200.5")
        self.assertEqual(clean_num(".."),"")
    def test_label(self):
        self.assertEqual(pick_category({"Products and product groups":"Soft drinks"}),"Soft drinks")
    def test_exclude_alcohol_candidates(self):
        self.assertIsNotNone(ALCOHOL_EXCLUSION.search("Ciders, coolers and other refreshment beverages"))
        self.assertIsNone(ALCOHOL_EXCLUSION.search("Non-alcoholic soft drinks"))
        self.assertIsNotNone(ALCOHOL_EXCLUSION.search("Alcoholic beverages, at retail"))
        self.assertIsNotNone(ALCOHOL_EXCLUSION.search("Cannabis-infused beverages"))
        self.assertIsNotNone(ALCOHOL_EXCLUSION.search("Retail commissions based on beverages"))
    def test_beverage_candidate(self):
        self.assertIsNotNone(BEVERAGE_PATTERN.search("Carbonated soft drinks"))
        self.assertIsNone(BEVERAGE_PATTERN.search("Automotive components"))

if __name__ == "__main__":
    unittest.main()
