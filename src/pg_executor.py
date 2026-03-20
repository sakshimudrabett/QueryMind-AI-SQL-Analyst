"""
pg_executor.py
Connects to PostgreSQL, runs SELECT queries, and introspects schema.
Uses psycopg2 with connection pooling via a simple cached connector.
"""

import re
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import lru_cache


# ──────────────────────────────────────────────
# Connection helpers
# ──────────────────────────────────────────────

def _connect(database_url: str):
    """Create a fresh psycopg2 connection from a URL string."""
    return psycopg2.connect(database_url, connect_timeout=10)


def test_connection(database_url: str) -> tuple[bool, str]:
    """
    Test if a PostgreSQL connection URL is valid and reachable.

    Returns:
        (True, success_message) or (False, error_message)
    """
    try:
        conn = _connect(database_url)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0].split(",")[0]
        conn.close()
        return True, f"✓ Connected — {version}"
    except Exception as e:
        return False, f"Connection failed: {e}"


# ──────────────────────────────────────────────
# Query runner
# ──────────────────────────────────────────────

_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE|EXEC|EXECUTE)\b",
    re.IGNORECASE,
)


def run_query(sql: str, database_url: str) -> pd.DataFrame:
    """
    Execute a SQL SELECT query and return results as a DataFrame.

    Args:
        sql          : SQL query string (SELECT only).
        database_url : PostgreSQL connection URL.

    Returns:
        pandas DataFrame with query results.

    Raises:
        ValueError  : If query contains forbidden DML/DDL keywords.
        psycopg2.Error : On query execution failure.
    """
    sql_clean = sql.strip()

    if _FORBIDDEN.search(sql_clean):
        raise ValueError(
            "Only SELECT queries are permitted. "
            "Detected a forbidden SQL keyword."
        )

    conn = _connect(database_url)
    try:
        df = pd.read_sql_query(sql_clean, conn)
        return df
    finally:
        conn.close()


# ──────────────────────────────────────────────
# Schema introspection
# ──────────────────────────────────────────────

def upload_dataframe(df: pd.DataFrame, table_name: str, database_url: str) -> None:
    """
    Upload a pandas DataFrame to PostgreSQL as a new table.
    Replaces the table if it already exists.
    Column names are auto-cleaned to be SQL-safe.

    Args:
        df           : DataFrame to upload.
        table_name   : Target table name (will be cleaned automatically).
        database_url : PostgreSQL connection URL.
    """
    import re

    # Clean column names: lowercase, replace spaces/special chars with underscore
    df = df.copy()
    df.columns = [
        re.sub(r"[^a-z0-9_]", "_", re.sub(r"\s+", "_", str(c).lower())).strip("_")
        for c in df.columns
    ]

    # Use SQLAlchemy engine for to_sql compatibility
    from sqlalchemy import create_engine
    engine = create_engine(database_url)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    engine.dispose()


def get_schema(database_url: str, schema_name: str = "public") -> dict[str, list[tuple[str, str]]]:
    """
    Introspect all tables and columns in the given PostgreSQL schema.

    Args:
        database_url : PostgreSQL connection URL.
        schema_name  : Postgres schema to inspect (default: 'public').

    Returns:
        Dict mapping table_name → list of (column_name, data_type) tuples.
    """
    query = """
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position;
    """

    conn = _connect(database_url)
    try:
        cur = conn.cursor()
        cur.execute(query, (schema_name,))
        rows = cur.fetchall()
    finally:
        conn.close()

    schema: dict[str, list[tuple[str, str]]] = {}
    for table_name, column_name, data_type in rows:
        schema.setdefault(table_name, []).append((column_name, data_type))

    return schema