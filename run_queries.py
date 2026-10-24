import sqlite3
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

conn = sqlite3.connect("data/churn.db")

with open("sql/queries.sql", encoding="utf-8") as f:
    text = f.read()

for i, query in enumerate(text.split(";"), start=1):
    if not query.strip():
        continue
    print(f"\n----- Query {i} -----")
    print(pd.read_sql_query(query, conn).to_string(index=False))

conn.close()