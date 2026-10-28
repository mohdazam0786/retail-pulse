import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

required_vars = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
]

missing = [
    key for key in required_vars
    if not os.getenv(key)
]

if missing:
    raise RuntimeError(
        f"Missing environment variables: {missing}"
    )

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(database_url)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT
                    current_database(),
                    current_user,
                    version()
            """)
        )

        database, user, version = result.fetchone()

        print("Connection successful!")
        print("Database:", database)
        print("User:", user)
        print("Version:", version.split(",")[0])

finally:
    engine.dispose()
