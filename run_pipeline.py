from src.data_cleaning import load_data, clean_data, save_clean
from src.features import add_features
from src.churn_model import train_model, score_customers
from src.clv import add_clv
from src.segmentation import add_segments

df = load_data()
df = clean_data(df)
df = add_features(df)
save_clean(df)
print("Cleaned data shape:", df.shape)

model = train_model(df)
scored = score_customers(model, df)
scored = add_clv(scored)
scored = add_segments(scored)
scored.to_csv("data/processed/scored_customers.csv", index=False)
print("\nSaved data/processed/scored_customers.csv")

print("\nSegment summary:")
summary = scored.groupby("segment").agg(
    customers=("customerID", "count"),
    avg_churn_prob=("churn_prob", "mean"),
    avg_monthly_charge=("MonthlyCharges", "mean"),
    total_clv=("clv", "sum"),
).round(2)
print(summary)

print("\nTop 5 'Save First' customers by CLV:")
save_first = scored[scored["segment"] == "Save First"]
print(
    save_first.sort_values("clv", ascending=False)
    .head(5)[["customerID", "Contract", "tenure", "MonthlyCharges", "churn_prob", "clv"]]
)