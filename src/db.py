import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL .env file is not there.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def fetch_data(query: str, params: dict | None = None) -> pd.DataFrame:
    """Execute a parameterized SQL query and return a DataFrame."""
    with engine.connect() as connection:
        return pd.read_sql_query(
            text(query),
            connection,
            params=params or {},
        )