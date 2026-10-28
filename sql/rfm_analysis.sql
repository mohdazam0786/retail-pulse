-- Calculate recency, purchase frequency, and monetary value
-- for each identified customer.

WITH customer_metrics AS (
    SELECT
        customer_id,
        MAX(invoice_date) AS last_purchase_date,
        COUNT(DISTINCT invoice_no) AS frequency,
        ROUND(SUM(revenue), 2) AS monetary
    FROM retail_sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
analysis_date AS (
    SELECT MAX(invoice_date)::date + 1 AS reference_date
    FROM retail_sales
)
SELECT
    cm.customer_id,
    (ad.reference_date - cm.last_purchase_date::date)
        AS recency_days,
    cm.frequency,
    cm.monetary
FROM customer_metrics cm
CROSS JOIN analysis_date ad
ORDER BY cm.monetary DESC
LIMIT 20;
