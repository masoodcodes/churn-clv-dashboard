import pandas as pd


def load_data(path="data/raw/telco_churn.csv"):
    return pd.read_csv(path)


def clean_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    # TotalCharges is text in the raw file; blanks are new customers (tenure 0)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0)

    df = df.drop_duplicates(subset="customerID")

    # Churn as 1/0 for the model
    df["Churn_flag"] = (df["Churn"] == "Yes").astype(int)

    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
    return df


def save_clean(df, path="data/processed/clean_data.csv"):
    df.to_csv(path, index=False)