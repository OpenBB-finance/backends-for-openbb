import os
from functools import lru_cache
from typing import Generator

import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector import SnowflakeConnection

load_dotenv()

@lru_cache
def get_snowflake_settings() -> dict:
    """Get Snowflake connection settings from environment variables."""
    return {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
    }

def get_snowflake_connection() -> Generator[SnowflakeConnection, None, None]:
    """Create and yield a Snowflake connection, ensuring proper cleanup."""
    conn = snowflake.connector.connect(**get_snowflake_settings())
    try:
        yield conn
    finally:
        conn.close()
