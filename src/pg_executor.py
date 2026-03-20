"""
pg_executor.py
Connects to PostgreSQL, runs SELECT queries, and introspects schema.
Automatically casts date and numeric columns on CSV upload.
"""

import re
import pandas as pd
import psycopg2
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
        ValueError     : If query contains forbidden DML/DDL keywords.
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
# CSV Upload with smart type detection
# ──────────────────────────────────────────────

def upload_dataframe(df: pd.DataFrame, table_name: str, database_url: str) -> None:
    """
    Upload a pandas DataFrame to PostgreSQL as a new table.
    - Cleans column names to be SQL-safe
    - Auto-detects and converts date columns to proper datetime type
    - Auto-detects and converts numeric columns to proper numeric type
    - Replaces the table if it already exists

    Args:
        df           : DataFrame to upload.
        table_name   : Target table name.
        database_url : PostgreSQL connection URL.
    """
    from sqlalchemy import create_engine

    df = df.copy()

    # ── Clean column names ──────────────────────
    df.columns = [
        re.sub(r"[^a-z0-9_]", "_", re.sub(r"\s+", "_", str(c).lower())).strip("_")
        for c in df.columns
    ]

    # ── Auto-detect date columns ────────────────
    date_hints = ["date", "time", "created", "updated", "day", "month", "year", "period", "week", "quarter"]
    for col in df.columns:
        if any(hint in col.lower() for hint in date_hints):
            try:
                converted = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
                # Only apply if most values parsed successfully
                if converted.notna().sum() > len(df) * 0.7:
                    df[col] = converted
            except Exception:
                pass

    # ── Auto-detect numeric columns ─────────────
    for col in df.columns:
        if df[col].dtype == object:
            try:
                converted = pd.to_numeric(df[col], errors="coerce")
                # Only apply if most values parsed successfully
                if converted.notna().sum() > len(df) * 0.8:
                    df[col] = converted
            except Exception:
                pass

    # ── Upload to PostgreSQL ────────────────────
    engine = create_engine(database_url)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    engine.dispose()


# ──────────────────────────────────────────────
# Schema introspection
# ──────────────────────────────────────────────

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