
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "Online Retail.xlsx"
OUTPUT_DIR = ROOT / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "online_retail_clean.csv"
REPORT_FILE = OUTPUT_DIR / "cleaning_report.txt"


def load_data(path: Path) -> pd.DataFrame:
    """Load the original retail dataset."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Place Online Retail.xlsx inside data/raw/."
        )

    df = pd.read_excel(
        path,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "CustomerID": "string",
        },
    )

    df.columns = df.columns.str.strip()
    return df


def clean_data(df: pd.DataFrame):
    """Clean transaction records and report excluded rows."""

    original_rows = len(df)
    report = {}

    # 1. Remove exact duplicate records
    df = df.drop_duplicates().copy()
    report["exact_duplicates_removed"] = (
        original_rows - len(df)
    )

    # 2. Identify cancellation invoices
    invoice = df["InvoiceNo"].fillna("").str.strip()
    is_cancellation = invoice.str.upper().str.startswith("C")

    report["cancellation_rows"] = int(is_cancellation.sum())

    # 3. Exclude cancellation invoices from the sales dataset
    sales = df.loc[~is_cancellation].copy()
    report["rows_after_cancellation_filter"] = len(sales)

    # 4. Exclude invalid sales quantities and prices
    valid_quantity = sales["Quantity"].gt(0)
    valid_price = sales["UnitPrice"].gt(0)

    report["nonpositive_quantity_rows"] = int(
        (~valid_quantity).sum()
    )
    report["nonpositive_price_rows"] = int(
        (~valid_price).sum()
    )

    sales = sales.loc[valid_quantity & valid_price].copy()

    # 5. Preserve rows with missing customer IDs.
    # Customer-level analysis will handle them separately.
    sales["CustomerID"] = (
        sales["CustomerID"]
        .str.strip()
        .replace("", pd.NA)
    )

    # 6. Standardize product descriptions
    sales["Description"] = (
        sales["Description"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    # 7. Calculate line-level sales revenue
    sales["Revenue"] = (
        sales["Quantity"] * sales["UnitPrice"]
    ).round(2)

    # 8. Validate final data
    if sales.empty:
        raise ValueError("No valid sales records remain.")

    if sales["Revenue"].isna().any():
        raise ValueError("Revenue contains missing values.")

    if not sales["Quantity"].gt(0).all():
        raise ValueError("Invalid quantity remains.")

    if not sales["UnitPrice"].gt(0).all():
        raise ValueError("Invalid unit price remains.")

    report["final_rows"] = len(sales)
    report["rows_removed_total"] = (
        original_rows - len(sales)
    )
    report["missing_customer_ids_retained"] = int(
        sales["CustomerID"].isna().sum()
    )
    report["missing_descriptions_retained"] = int(
        sales["Description"].isna().sum()
    )
    report["total_line_revenue"] = round(
        sales["Revenue"].sum(), 2
    )

    return sales, report


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_data(RAW_FILE)
    cleaned_df, report = clean_data(raw_df)

    cleaned_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        file.write("RETAILPULSE DATA CLEANING REPORT\n")
        file.write("=" * 40 + "\n")

        for key, value in report.items():
            file.write(f"{key}: {value}\n")

    print("Cleaning completed successfully.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Report file: {REPORT_FILE}")
    print("\nCleaning summary:")

    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
