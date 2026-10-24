def add_clv(df, margin=0.30, max_months=60):
    """
    CLV = monthly charge x expected lifetime (months) x profit margin

    Assumptions (put these in your README):
    - churn_prob is treated as the yearly chance the customer leaves
    - expected lifetime in years = 1 / churn_prob
    - lifetime is capped at max_months (5 years) so low-risk customers
      don't get unrealistic values
    - margin = share of revenue that is profit
    """
    df = df.copy()
    prob = df["churn_prob"].clip(lower=0.02)
    df["expected_months"] = (12 / prob).clip(upper=max_months)
    df["clv"] = df["MonthlyCharges"] * df["expected_months"] * margin
    return df