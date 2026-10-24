import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.simulation import run_simulation

st.set_page_config(page_title="Churn & CLV Dashboard", layout="wide")

TENURE_ORDER = ["0-12 months", "13-24 months", "25-48 months", "49-72 months"]


@st.cache_data
def load_data():
    return pd.read_csv(ROOT / "data" / "processed" / "scored_customers.csv")


full_df = load_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
contracts = st.sidebar.multiselect(
    "Contract type",
    options=sorted(full_df["Contract"].unique()),
    default=sorted(full_df["Contract"].unique()),
)
df = full_df[full_df["Contract"].isin(contracts)]

if df.empty:
    st.warning("No customers match the filters. Pick at least one contract type.")
    st.stop()

st.title("Customer Churn + CLV Dashboard")
st.caption("Churn risk, customer lifetime value, and what-if retention scenarios")

# ---------- KPIs ----------
high_risk = df[df["churn_prob"] >= 0.5]
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers", f"{len(df):,}")
k2.metric("Actual churn rate", f"{df['Churn_flag'].mean() * 100:.1f}%")
k3.metric("High-risk customers", f"{len(high_risk):,}")
k4.metric("Monthly revenue at risk", f"${high_risk['MonthlyCharges'].sum():,.0f}")
k5.metric("Total CLV", f"${df['clv'].sum() / 1e6:.2f}M")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "At-risk customers", "CLV segments", "What-if simulator"]
)

# ---------- Tab 1: Overview ----------
with tab1:
    c1, c2 = st.columns(2)

    by_contract = (
        df.groupby("Contract")["Churn_flag"].mean().mul(100).round(1).reset_index()
    )
    fig1 = px.bar(
        by_contract, x="Contract", y="Churn_flag",
        title="Churn rate by contract (%)", labels={"Churn_flag": "Churn rate (%)"},
    )
    c1.plotly_chart(fig1, use_container_width=True)

    by_tenure = (
        df.groupby("tenure_group")["Churn_flag"].mean().mul(100).round(1).reset_index()
    )
    fig2 = px.bar(
        by_tenure, x="tenure_group", y="Churn_flag",
        title="Churn rate by tenure (%)",
        labels={"Churn_flag": "Churn rate (%)", "tenure_group": "Tenure"},
        category_orders={"tenure_group": TENURE_ORDER},
    )
    c2.plotly_chart(fig2, use_container_width=True)

    by_pay = (
        df.groupby("PaymentMethod")["Churn_flag"].mean().mul(100).round(1).reset_index()
    )
    fig3 = px.bar(
        by_pay, x="PaymentMethod", y="Churn_flag",
        title="Churn rate by payment method (%)",
        labels={"Churn_flag": "Churn rate (%)"},
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------- Tab 2: At-risk customers ----------
with tab2:
    st.subheader("Top 20 customers by churn risk")
    top = df.sort_values("churn_prob", ascending=False).head(20)
    show = top[
        ["customerID", "Contract", "tenure", "MonthlyCharges",
         "churn_prob", "clv", "segment"]
    ].copy()
    show["churn_prob"] = show["churn_prob"].round(3)
    show["clv"] = show["clv"].round(0)
    st.dataframe(show, use_container_width=True)

    st.download_button(
        "Download all high-risk customers (CSV)",
        high_risk.to_csv(index=False),
        file_name="high_risk_customers.csv",
        mime="text/csv",
    )

# ---------- Tab 3: CLV segments ----------
with tab3:
    summary = df.groupby("segment").agg(
        customers=("customerID", "count"),
        avg_churn_risk=("churn_prob", "mean"),
        avg_monthly_charge=("MonthlyCharges", "mean"),
        total_clv=("clv", "sum"),
    ).round(2).reset_index()
    st.dataframe(summary, use_container_width=True)

    fig4 = px.scatter(
        df.sample(min(2000, len(df)), random_state=1),
        x="churn_prob", y="clv", color="segment",
        title="Churn risk vs customer lifetime value",
        labels={"churn_prob": "Churn risk", "clv": "CLV ($)"},
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.info(
        "Save First = high value + high risk (priority). "
        "Low-Cost Retention = high risk, lower value (cheap actions only). "
        "Protect (Loyal) = high value, low risk. Maintain = everyone else."
    )

# ---------- Tab 4: What-if simulator ----------
with tab4:
    st.subheader("What if we run a retention campaign?")
    left, right = st.columns([1, 2])

    with left:
        targets = st.multiselect(
            "Target segments",
            options=sorted(df["segment"].unique()),
            default=[s for s in ["Save First"] if s in df["segment"].unique()],
        )
        reduction = st.slider("Churn risk reduction (%)", 0, 50, 20) / 100
        cost = st.slider("Campaign cost per customer ($)", 0, 100, 20)
        discount = st.slider("Discount offered (%)", 0, 30, 0) / 100
        margin = st.slider("Profit margin (%)", 10, 60, 30) / 100
        months = st.slider("Time window (months)", 3, 24, 12)

    result = run_simulation(
        df, targets,
        churn_reduction=reduction, cost_per_customer=cost,
        discount=discount, margin=margin, months=months,
    )

    with right:
        m1, m2, m3 = st.columns(3)
        m1.metric("Customers targeted", f"{result['customers_targeted']:,}")
        m2.metric("Customers saved", f"{result['customers_saved']:,.0f}")
        m3.metric("ROI", f"{result['roi_pct']:.0f}%")

        m4, m5, m6 = st.columns(3)
        m4.metric("Profit saved", f"${result['profit_saved']:,.0f}")
        m5.metric(
            "Total cost",
            f"${result['campaign_cost'] + result['discount_cost']:,.0f}",
        )
        m6.metric("Net benefit", f"${result['net_benefit']:,.0f}")

        chart_df = pd.DataFrame({
            "Item": ["Profit saved", "Campaign cost", "Discount cost", "Net benefit"],
            "Amount": [
                result["profit_saved"], -result["campaign_cost"],
                -result["discount_cost"], result["net_benefit"],
            ],
        })
        fig5 = px.bar(chart_df, x="Item", y="Amount", title="Campaign economics ($)")
        st.plotly_chart(fig5, use_container_width=True)

        if result["net_benefit"] < 0:
            st.error("This campaign loses money. Try a cheaper action or a smaller discount.")
        else:
            st.success("This campaign is profitable under these assumptions.")

    st.caption(
        "Assumptions: churn risk is treated as the 12-month chance of leaving; "
        "a saved customer is worth monthly charge x months x margin; "
        "discounts are paid to every targeted customer who stays."
    )