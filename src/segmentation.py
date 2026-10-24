def add_segments(df, risk_threshold=0.5):
    df = df.copy()
    value_cutoff = df["clv"].median()

    high_risk = df["churn_prob"] >= risk_threshold
    high_value = df["clv"] >= value_cutoff

    df["segment"] = "Maintain"
    df.loc[high_risk & high_value, "segment"] = "Save First"
    df.loc[high_risk & ~high_value, "segment"] = "Low-Cost Retention"
    df.loc[~high_risk & high_value, "segment"] = "Protect (Loyal)"
    return df