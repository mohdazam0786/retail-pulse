import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data" / "processed" / "online_retail_clean.csv"

load_dotenv(ROOT / ".env")

database_url = URL.create(
    "postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.environ["DB_NAME"],
)

engine = create_engine(database_url)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS retail_sales (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_no TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    invoice_date TIMESTAMP NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    customer_id TEXT,
    country TEXT NOT NULL,
    revenue NUMERIC(14, 2) NOT NULL
);
"""

def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_FILE}")

    df = pd.read_csv(
        CSV_FILE,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "Description": "string",
            "CustomerID": "string",
            "Country": "string",
        },
        parse_dates=["InvoiceDate"],
    )

    df = df.rename(columns={
        "InvoiceNo": "invoice_no",
        "StockCode": "stock_code",
        "Description": "description",
        "Quantity": "quantity",
        "InvoiceDate": "invoice_date",
        "UnitPrice": "unit_price",
        "CustomerID": "customer_id",
        "Country": "country",
        "Revenue": "revenue",
    })

    expected_columns = [
        "invoice_no", "stock_code", "description",
        "quantity", "invoice_date", "unit_price",
        "customer_id", "country", "revenue",
    ]

    if list(df.columns) != expected_columns:
        raise ValueError(f"Unexpected CSV columns: {list(df.columns)}")

    if df.empty:
        raise ValueError("CSV contains no rows.")

    if df[expected_columns].isna().any().any():
        # Missing customer IDs and descriptions are allowed.
        required = [
            "invoice_no", "stock_code", "quantity",
            "invoice_date", "unit_price", "country", "revenue",
        ]
        if df[required].isna().any().any():
            raise ValueError("Required columns contain missing values.")

    if not df["quantity"].gt(0).all():
        raise ValueError("Nonpositive quantities found.")

    if not df["unit_price"].gt(0).all():
        raise ValueError("Nonpositive prices found.")

    df["revenue"] = df["quantity"] * df["unit_price"]

    with engine.begin() as connection:
        connection.execute(text(CREATE_TABLE))

        # Replace the existing imported dataset transactionally.
        connection.execute(text("TRUNCATE TABLE retail_sales RESTART IDENTITY"))

        df.to_sql(
            "retail_sales",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=2000,
            method="multi",
        )

        imported_rows = connection.execute(
            text("SELECT COUNT(*) FROM retail_sales")
        ).scalar_one()

        total_revenue = connection.execute(
            text("SELECT SUM(revenue) FROM retail_sales")
        ).scalar_one()

        if imported_rows != len(df):
            raise RuntimeError(
                f"Expected {len(df)} rows, imported {imported_rows}"
            )

    print("Import successful!")
    print(f"Rows imported: {imported_rows:,}")
    print(f"Total line revenue: {total_revenue:,.2f}")

    engine.dispose()


if __name__ == "__main__":
    main()
