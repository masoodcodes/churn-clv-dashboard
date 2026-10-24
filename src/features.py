import pandas as pd

SERVICE_COLS = [
    "PhoneService", "MultipleLines", "OnlineSecurity", "OnlineBackup",
    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
]


def add_features(df):
    df = df.copy()

    df["tenure_group"] = pd.cut(
        df["tenure"],
        bins=[-1, 12, 24, 48, 72],
        labels=["0-12 months", "13-24 months", "25-48 months", "49-72 months"],
    )

    df["num_services"] = (df[SERVICE_COLS] == "Yes").sum(axis=1)
    df["avg_monthly_spend"] = df["TotalCharges"] / df["tenure"].replace(0, 1)
    df["is_month_to_month"] = (df["Contract"] == "Month-to-month").astype(int)
    df["has_tech_support"] = (df["TechSupport"] == "Yes").astype(int)
    df["auto_pay"] = df["PaymentMethod"].str.contains("automatic").astype(int)
    return df