
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from db import fetch_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def save_chart(filename):
    """Save the current chart to reports/figures."""
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {FIGURES_DIR / filename}")


def monthly_revenue_chart():
    query = """
        SELECT
            DATE_TRUNC('month', invoice_date)::date AS month,
            SUM(revenue) AS revenue
        FROM retail_sales
        GROUP BY 1
        ORDER BY 1;
    """
    df = fetch_data(query)

    plt.figure(figsize=(11, 5))
    sns.lineplot(data=df, x="month", y="revenue", marker="o")
    plt.title("Monthly Sales Revenue")
    plt.xlabel("Month")
    plt.ylabel("Recorded Revenue")
    plt.xticks(rotation=45)
    save_chart("monthly_revenue.png")


def country_revenue_chart():
    query = """
        SELECT
            country,
            SUM(revenue) AS revenue
        FROM retail_sales
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 10;
    """
    df = fetch_data(query)

    df = df.sort_values("revenue", ascending=True)

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="revenue", y="country")
    plt.title("Top 10 Countries by Recorded Revenue")
    plt.xlabel("Recorded Revenue")
    plt.ylabel("Country")
    save_chart("country_revenue.png")


def customer_segment_chart():
    query = """
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
                cm.customer_id,
                (r.reference_date - cm.last_purchase_date)
                    AS recency_days,
                cm.frequency,
                cm.monetary
            FROM customer_metrics cm
            CROSS JOIN reference r
        ),
        scored AS (
            SELECT *,
                NTILE(5) OVER (
                    ORDER BY recency_days DESC
                ) AS r_score,
                NTILE(5) OVER (
                    ORDER BY frequency ASC
                ) AS f_score,
                NTILE(5) OVER (
                    ORDER BY monetary ASC
                ) AS m_score
            FROM rfm
        ),
        segmented AS (
            SELECT *,
                CASE
                    WHEN r_score >= 4 AND f_score >= 4
                         AND m_score >= 4
                        THEN 'Champions'
                    WHEN f_score >= 4 AND m_score >= 3
                        THEN 'Loyal Customers'
                    WHEN r_score >= 4 AND f_score <= 2
                        THEN 'Recent Customers'
                    WHEN r_score <= 2 AND f_score >= 3
                         AND m_score >= 3
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
            COUNT(*) AS customer_count
        FROM segmented
        GROUP BY customer_segment
        ORDER BY customer_count DESC;
    """
    df = fetch_data(query)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df,
        x="customer_count",
        y="customer_segment"
    )
    plt.title("Customer Distribution by RFM Segment")
    plt.xlabel("Number of Customers")
    plt.ylabel("Customer Segment")
    save_chart("rfm_segments.png")


if __name__ == "__main__":
    monthly_revenue_chart()
    country_revenue_chart()
    customer_segment_chart()
    print("All visualizations generated successfully!")
