-- 1. Calculate overall business KPIs, including transaction lines,
-- unique invoices, identified customers, total revenue, and revenue per invoice.
SELECT
    COUNT(*) AS transaction_lines,
    COUNT(DISTINCT invoice_no) AS invoice_count,
    COUNT(DISTINCT customer_id) AS identified_customers,
    ROUND(SUM(revenue), 2) AS total_line_revenue,
    ROUND(
        SUM(revenue) /
        NULLIF(COUNT(DISTINCT invoice_no), 0),
        2
    ) AS revenue_per_invoice
FROM retail_sales;


-- 2. Identify the top 10 countries by revenue and compare their
-- revenue, number of invoices, and identified customers.
SELECT
    country,
    ROUND(SUM(revenue), 2) AS revenue,
    COUNT(DISTINCT invoice_no) AS invoice_count,
    COUNT(DISTINCT customer_id) AS identified_customers
FROM retail_sales
GROUP BY country
ORDER BY revenue DESC
LIMIT 10;


-- 3. Analyze monthly sales performance by calculating total revenue
-- and the number of unique invoices for each month.
SELECT
    DATE_TRUNC('month', invoice_date)::date AS month,
    ROUND(SUM(revenue), 2) AS revenue,
    COUNT(DISTINCT invoice_no) AS invoices
FROM retail_sales
GROUP BY 1
ORDER BY 1;


-- 4. Find the top 10 products by revenue and evaluate their
-- sales volume using total units sold and product revenue.
SELECT
    stock_code,
    MAX(description) AS product_name,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue), 2) AS revenue
FROM retail_sales
GROUP BY stock_code
ORDER BY revenue DESC
LIMIT 10;
