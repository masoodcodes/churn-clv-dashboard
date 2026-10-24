import sqlite3
import pandas as pd

df = pd.read_csv("data/processed/scored_customers.csv")
df["tenure_group"] = df["tenure_group"].astype(str)

conn = sqlite3.connect("data/churn.db")
df.to_sql("customers", conn, if_exists="replace", index=False)

# A small second table, so we can practise JOINs
actions = pd.DataFrame({
    "segment": ["Save First", "Low-Cost Retention", "Protect (Loyal)", "Maintain"],
    "recommended_action": [
        "Personal call + tailored offer",
        "Automated email or SMS",
        "Loyalty rewards",
        "No action",
    ],
})
actions.to_sql("segment_actions", conn, if_exists="replace", index=False)

print("Tables created:")
print(pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table'", conn
))
print("Rows in customers:", pd.read_sql_query(
    "SELECT COUNT(*) AS n FROM customers", conn
)["n"][0])
conn.close()