
-- Summarize the number of customers and recorded spend
-- for each RFM segment.

WITH customer_metrics AS (
    SELECT
        customer_id,
        MAX(invoice_date)::date AS last_purchase_date,
        COUNT(DISTINCT invoice_no) AS frequency,
        SUM(revenue) AS monetary
    FROM retail_sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
reference AS (
    SELECT MAX(invoice_date)::date + 1 AS reference_date
    FROM retail_sales
),
rfm AS (
    SELECT
        customer_id,
        reference_date - last_purchase_date AS recency_days,
        frequency,
        monetary
    FROM customer_metrics
    CROSS JOIN reference
),
scored AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm
),
segmented AS (
    SELECT *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4
                THEN 'Champions'
            WHEN f_score >= 4 AND m_score >= 3
                THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2
                THEN 'Recent Customers'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3
                THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2
                THEN 'Hibernating'
            WHEN r_score >= 3 AND f_score >= 2
                THEN 'Potential Loyalists'
            ELSE 'Needs Attention'
        END AS customer_segment
    FROM scored
)
SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(SUM(monetary), 2) AS recorded_spend,
    ROUND(AVG(frequency), 2) AS avg_invoice_frequency
FROM segmented
GROUP BY customer_segment
ORDER BY customer_count DESC;
