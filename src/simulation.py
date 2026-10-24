def run_simulation(
    df,
    segments,
    churn_reduction=0.20,
    cost_per_customer=20.0,
    discount=0.0,
    margin=0.30,
    months=12,
):
    """
    What-if: target some segments with a retention campaign.

    segments          list of segment names to target
    churn_reduction   relative cut in churn risk (0.20 = risk falls by 20%)
    cost_per_customer cost of the campaign per targeted customer
    discount          price discount given to targeted customers (0.10 = 10%)
    margin            share of revenue that is profit
    months            time window for the benefit (12 = one year)
    """
    t = df[df["segment"].isin(segments)]
    n = len(t)

    if n == 0:
        return {
            "customers_targeted": 0, "expected_churners_before": 0.0,
            "expected_churners_after": 0.0, "customers_saved": 0.0,
            "profit_saved": 0.0, "discount_cost": 0.0, "campaign_cost": 0.0,
            "net_benefit": 0.0, "roi_pct": 0.0,
        }

    old_prob = t["churn_prob"]
    new_prob = old_prob * (1 - churn_reduction)
    charge = t["MonthlyCharges"]

    customers_saved = (old_prob - new_prob).sum()
    profit_saved = ((old_prob - new_prob) * charge * months * margin).sum()
    discount_cost = ((1 - new_prob) * charge * discount * months).sum()
    campaign_cost = n * cost_per_customer

    total_cost = campaign_cost + discount_cost
    net_benefit = profit_saved - total_cost
    roi_pct = (net_benefit / total_cost * 100) if total_cost > 0 else 0.0

    return {
        "customers_targeted": n,
        "expected_churners_before": round(old_prob.sum(), 1),
        "expected_churners_after": round(new_prob.sum(), 1),
        "customers_saved": round(customers_saved, 1),
        "profit_saved": round(profit_saved, 2),
        "discount_cost": round(discount_cost, 2),
        "campaign_cost": round(campaign_cost, 2),
        "net_benefit": round(net_benefit, 2),
        "roi_pct": round(roi_pct, 1),
    }