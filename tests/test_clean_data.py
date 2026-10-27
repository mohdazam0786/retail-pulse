import unittest
import pandas as pd

from src.clean_data import clean_data

class TestCleanData(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "InvoiceNo": [
                "1001", "1001", "C1002", "1003", "1004", "1005"
            ],
            "StockCode": [
                "A", "A", "B", "C", "D", "E"
            ],
            "Description": [
                "Product A", "Product A", "Product B",
                "Product C", "Product D", None
            ],
            "Quantity": [2, 2, -1, -2, 1, 1],
            "InvoiceDate": pd.to_datetime([
                "2011-01-01", "2011-01-01", "2011-01-02",
                "2011-01-03", "2011-01-04", "2011-01-05"
            ]),
            "UnitPrice": [10.0, 10.0, 5.0, 5.0, 0.0, 5.0],
            "CustomerID": ["123", "123", "124", "125", "126", None],
            "Country": ["UK", "UK", "UK", "UK", "UK", "UK"],
        })

    def test_duplicates_are_removed(self):
        cleaned, report = clean_data(self.df)

        self.assertEqual(report["exact_duplicates_removed"], 1)

    def test_cancellations_are_excluded(self):
        cleaned, report = clean_data(self.df)

        self.assertFalse(
            cleaned["InvoiceNo"].str.startswith("C").any()
        )

    def test_only_positive_sales_remain(self):
        cleaned, report = clean_data(self.df)

        self.assertTrue((cleaned["Quantity"] > 0).all())
        self.assertTrue((cleaned["UnitPrice"] > 0).all())

    def test_revenue_is_calculated_correctly(self):
        cleaned, report = clean_data(self.df)

        self.assertAlmostEqual(
            cleaned["Revenue"].sum(), 25.0
        )

    def test_missing_customer_is_preserved(self):
        cleaned, report = clean_data(self.df)

        self.assertEqual(
            cleaned["CustomerID"].isna().sum(), 1
        )

    def test_missing_description_is_preserved(self):
        cleaned, report = clean_data(self.df)

        self.assertEqual(
            cleaned["Description"].isna().sum(), 1
        )


if __name__ == "__main__":
    unittest.main()
