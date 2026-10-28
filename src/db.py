import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL .env is not there."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def fetch_data(query: str):
    """Run a SQL query and return its results as a DataFrame."""
    import pandas as pd

    with engine.connect() as connection:
        return pd.read_sql_query(text(query), connection)
