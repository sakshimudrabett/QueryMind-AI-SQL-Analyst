import sqlite3
import pandas as pd

def run_query(query, db_name="sales.db"):
    conn = sqlite3.connect(db_name)

    try:
        result = pd.read_sql_query(query, conn)
        return result
    except Exception as e:
        return str(e)
    finally:
        conn.close()
