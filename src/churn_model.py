import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DROP_COLS = ["customerID", "Churn", "Churn_flag"]


def get_xy(df):
    X = df.drop(columns=DROP_COLS).copy()
    X["tenure_group"] = X["tenure_group"].astype(str)
    y = df["Churn_flag"]
    return X, y


def build_pipeline(model, X):
    cat_cols = X.select_dtypes(exclude="number").columns.tolist()
    num_cols = [c for c in X.columns if c not in cat_cols]
    pre = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ])
    return Pipeline([("pre", pre), ("model", model)])


def train_model(df, model_path="models/churn_model.pkl"):
    X, y = get_xy(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, max_depth=8, class_weight="balanced", random_state=42
        ),
    }

    best_name, best_auc, best_pipe = None, 0, None
    print("\nModel comparison (test set):")
    for name, model in models.items():
        pipe = build_pipeline(model, X)
        pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        auc = roc_auc_score(y_test, proba)
        print(
            f"{name}: accuracy={accuracy_score(y_test, pred):.3f}, "
            f"precision={precision_score(y_test, pred):.3f}, "
            f"recall={recall_score(y_test, pred):.3f}, ROC-AUC={auc:.3f}"
        )
        if auc > best_auc:
            best_name, best_auc, best_pipe = name, auc, pipe

    print(f"\nBest model: {best_name} (ROC-AUC {best_auc:.3f})")
    joblib.dump(best_pipe, model_path)
    print("Saved model to", model_path)
    return best_pipe


def score_customers(model, df):
    X, _ = get_xy(df)
    df = df.copy()
    df["churn_prob"] = model.predict_proba(X)[:, 1]
    return df