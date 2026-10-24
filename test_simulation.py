import pandas as pd
from src.simulation import run_simulation

df = pd.read_csv("data/processed/scored_customers.csv")

print("Scenario 1: target 'Save First', cut risk 20%, $20 per customer")
print(run_simulation(df, ["Save First"], churn_reduction=0.20, cost_per_customer=20))

print("\nScenario 2: same, plus a 10% discount")
print(run_simulation(df, ["Save First"], churn_reduction=0.20, cost_per_customer=20, discount=0.10))

print("\nScenario 3: target Save First + Low-Cost Retention, $5 per customer")
print(run_simulation(df, ["Save First", "Low-Cost Retention"], churn_reduction=0.10, cost_per_customer=5))