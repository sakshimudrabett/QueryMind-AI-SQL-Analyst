import pandas as pd
import sqlite3

def load_csv_to_db(csv_path, db_name="sales.db"):
    df = pd.read_csv(csv_path)

    conn = sqlite3.connect(db_name)
    df.to_sql("sales", conn, if_exists="replace", index=False)

    conn.close()
    print("✅ Data loaded into SQLite database")

if __name__ == "__main__":
    load_csv_to_db("data/sales_data.csv")
