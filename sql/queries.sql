-- 1. Churn rate by contract type
SELECT Contract,
       COUNT(*) AS customers,
       ROUND(AVG(Churn_flag) * 100, 1) AS churn_pct
FROM customers
GROUP BY Contract
ORDER BY churn_pct DESC;

-- 2. Churn rate by payment method
SELECT PaymentMethod,
       COUNT(*) AS customers,
       ROUND(AVG(Churn_flag) * 100, 1) AS churn_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_pct DESC;

-- 3. Revenue at risk by segment
SELECT segment,
       COUNT(*) AS customers,
       ROUND(SUM(MonthlyCharges), 0) AS monthly_revenue,
       ROUND(AVG(churn_prob), 2) AS avg_risk
FROM customers
GROUP BY segment
ORDER BY monthly_revenue DESC;

-- 4. Top 10 high-value customers to save (with recommended action, using JOIN)
SELECT c.customerID, c.Contract, c.tenure, c.MonthlyCharges,
       ROUND(c.churn_prob, 2) AS risk, ROUND(c.clv, 0) AS clv,
       a.recommended_action
FROM customers c
JOIN segment_actions a ON c.segment = a.segment
WHERE c.segment = 'Save First'
ORDER BY c.clv DESC
LIMIT 10;

-- 5. Customer risk bands (CASE WHEN)
SELECT CASE
         WHEN churn_prob >= 0.7 THEN 'High'
         WHEN churn_prob >= 0.4 THEN 'Medium'
         ELSE 'Low'
       END AS risk_band,
       COUNT(*) AS customers,
       ROUND(AVG(Churn_flag) * 100, 1) AS actual_churn_pct
FROM customers
GROUP BY risk_band
ORDER BY actual_churn_pct DESC;

-- 6. Rank customers by CLV within each contract type (window function)
SELECT *
FROM (
  SELECT customerID, Contract, ROUND(clv, 0) AS clv,
         RANK() OVER (PARTITION BY Contract ORDER BY clv DESC) AS clv_rank
  FROM customers
)
WHERE clv_rank <= 3
ORDER BY Contract, clv_rank;

-- 7. Share of churners by tenure group (subquery)
SELECT tenure_group,
       COUNT(*) AS churned,
       ROUND(COUNT(*) * 100.0 /
             (SELECT COUNT(*) FROM customers WHERE Churn_flag = 1), 1) AS pct_of_all_churners
FROM customers
WHERE Churn_flag = 1
GROUP BY tenure_group
ORDER BY pct_of_all_churners DESC;

-- 8. Segments with above-average risk (HAVING)
SELECT segment,
       ROUND(AVG(churn_prob), 2) AS avg_risk,
       ROUND(SUM(clv), 0) AS total_clv
FROM customers
GROUP BY segment
HAVING AVG(churn_prob) > (SELECT AVG(churn_prob) FROM customers);