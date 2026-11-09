import unittest
from etl.load_cimt_csv import validate

def valid_row():
    return {
        "reference_period":"2025-01","hs_code":"2202",
        "commodity_name":"Beverages","trade_flow":"Import",
        "partner_country":"Country A","clearance_geography":"Canada",
        "value_cad":"100.50","quantity":"","quantity_unit":"",
        "source_note":"User-verified source document","classification_version":"HS2022"
    }

class CimtTests(unittest.TestCase):
    def test_valid_row(self):
        r=validate(valid_row())
        self.assertEqual(str(r["value"]),"100.50")
    def test_negative_rejected(self):
        r=valid_row();r["value_cad"]="-3"
        with self.assertRaises(ValueError):validate(r)
    def test_unrelated_product_rejected(self):
        r=valid_row();r["hs_code"]="8703"
        with self.assertRaises(ValueError):validate(r)
    def test_unverified_period_rejected(self):
        r=valid_row();r["reference_period"]="2026-01"
        with self.assertRaises(ValueError):validate(r)
    def test_wrong_qty_unit_rejected(self):
        r=valid_row();r["quantity"]="10"
        with self.assertRaises(ValueError):validate(r)
    def test_duplicate_grain_hash(self):
        self.assertEqual(validate(valid_row())["id"],validate(valid_row())["id"])

if __name__=="__main__":
    unittest.main()
