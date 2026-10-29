
from datetime import date, timedelta
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from db import fetch_data


st.set_page_config(
    page_title="RetailPulse | Sales Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 RetailPulse")
st.caption("E-commerce Sales Analytics & Customer Intelligence")

# Get available date range and countries from PostgreSQL
@st.cache_data(ttl=300)
def get_filter_options():
    dates = fetch_data("""
        SELECT MIN(invoice_date)::date AS min_date,
               MAX(invoice_date)::date AS max_date
        FROM retail_sales
    """)

    countries = fetch_data("""
        SELECT DISTINCT country
        FROM retail_sales
        ORDER BY country
    """)

    return dates.iloc[0], countries["country"].tolist()


@st.cache_data(ttl=300)
def get_sales_kpis(start_date, end_date, selected_countries):
    query = """
        SELECT
            COUNT(*) AS transaction_lines,
            COUNT(DISTINCT invoice_no) AS invoice_count,
            COUNT(DISTINCT customer_id) AS customer_count,
            COALESCE(SUM(revenue), 0) AS total_revenue,
            COALESCE(
                SUM(revenue) /
                NULLIF(COUNT(DISTINCT invoice_no), 0),
                0
            ) AS revenue_per_invoice
        FROM retail_sales
        WHERE invoice_date >= :start_date
          AND invoice_date < (:end_date + INTERVAL '1 day')
          AND country = ANY(:countries)
    """

    return fetch_data(query, {
        "start_date": start_date,
        "end_date": end_date,
        "countries": selected_countries,
    }).iloc[0]


@st.cache_data(ttl=300)
def get_monthly_revenue(start_date, end_date, selected_countries):
    return fetch_data("""
        SELECT
            DATE_TRUNC('month', invoice_date)::date AS month,
            SUM(revenue) AS revenue
        FROM retail_sales
        WHERE invoice_date >= :start_date
          AND invoice_date < (:end_date + INTERVAL '1 day')
          AND country = ANY(:countries)
        GROUP BY 1
        ORDER BY 1
    """, {
        "start_date": start_date,
        "end_date": end_date,
        "countries": selected_countries,
    })


@st.cache_data(ttl=300)
def get_country_revenue(start_date, end_date, selected_countries):
    return fetch_data("""
        SELECT country, SUM(revenue) AS revenue
        FROM retail_sales
        WHERE invoice_date >= :start_date
          AND invoice_date < (:end_date + INTERVAL '1 day')
          AND country = ANY(:countries)
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 10
    """, {
        "start_date": start_date,
        "end_date": end_date,
        "countries": selected_countries,
    })


@st.cache_data(ttl=300)
def get_rfm_segments():
    # RFM uses the complete dataset, independent of sales filters.
    return fetch_data("""
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
                r.reference_date - cm.last_purchase_date
                    AS recency_days,
                cm.frequency,
                cm.monetary
            FROM customer_metrics cm
            CROSS JOIN reference r
        ),
        scored AS (
            SELECT *,
                NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
                NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
                NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
            FROM rfm
        ),
        segmented AS (
            SELECT *,
                CASE
                    WHEN r_score >= 4 AND f_score >= 4
                         AND m_score >= 4 THEN 'Champions'
                    WHEN f_score >= 4 AND m_score >= 3
                        THEN 'Loyal Customers'
                    WHEN r_score >= 4 AND f_score <= 2
                        THEN 'Recent Customers'
                    WHEN r_score <= 2 AND f_score >= 3
                         AND m_score >= 3 THEN 'At Risk'
                    WHEN r_score <= 2 AND f_score <= 2
                        THEN 'Hibernating'
                    WHEN r_score >= 3 AND f_score >= 2
                        THEN 'Potential Loyalists'
                    ELSE 'Needs Attention'
                END AS customer_segment
            FROM scored
        )
        SELECT customer_segment, COUNT(*) AS customer_count
        FROM segmented
        GROUP BY customer_segment
        ORDER BY customer_count DESC
    """)


try:
    date_info, all_countries = get_filter_options()

    if pd.isna(date_info["min_date"]) or pd.isna(date_info["max_date"]):
        st.error("retail_sales table mein sales dates nahi mili.")
        st.stop()

    min_date = date_info["min_date"]
    max_date = date_info["max_date"]

    st.sidebar.header("Dashboard Filters")

    date_range = st.sidebar.date_input(
        "Invoice date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    selected_countries = st.sidebar.multiselect(
        "Countries",
        options=all_countries,
        default=all_countries,
    )

    if len(date_range) != 2:
        st.info("Please select both a start date and an end date.")
        st.stop()

    start_date, end_date = date_range

    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()

    if not selected_countries:
        st.warning("Select at least one country to view sales.")
        st.stop()

    kpis = get_sales_kpis(
        start_date, end_date, selected_countries
    )

    st.subheader("Sales Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recorded Revenue", f"{kpis['total_revenue']:,.2f}")
    c2.metric("Invoices", f"{kpis['invoice_count']:,}")
    c3.metric("Identified Customers", f"{kpis['customer_count']:,}")
    c4.metric("Revenue per Invoice", f"{kpis['revenue_per_invoice']:,.2f}")

    st.caption(
        f"Showing {start_date:%d %b %Y} – {end_date:%d %b %Y}. "
        "Revenue represents recorded sales, not profit."
    )

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Monthly Revenue Trend")
        monthly = get_monthly_revenue(
            start_date, end_date, selected_countries
        )

        if monthly.empty:
            st.info("No sales found for these filters.")
        else:
            monthly["month"] = pd.to_datetime(monthly["month"])
            st.line_chart(
                monthly.set_index("month")["revenue"],
                y_label="Recorded revenue",
            )

    with right:
        st.subheader("Top Countries")
        country_data = get_country_revenue(
            start_date, end_date, selected_countries
        )

        if country_data.empty:
            st.info("No country data found.")
        else:
            country_data = country_data.sort_values(
                "revenue", ascending=True
            )
            st.bar_chart(
                country_data.set_index("country")["revenue"],
                x_label="Country",
                y_label="Recorded revenue",
                horizontal=True,
            )

    st.divider()
    st.subheader("Customer Segmentation — RFM")

    segments = get_rfm_segments()
    total_segmented = int(segments["customer_count"].sum())

    if not segments.empty:
        s1, s2 = st.columns([2, 1])

        with s1:
            st.bar_chart(
                segments.set_index("customer_segment")["customer_count"],
                x_label="Customer segment",
                y_label="Number of customers",
                horizontal=True,
            )

        with s2:
            st.metric("Segmented Customers", f"{total_segmented:,}")
            st.dataframe(segments, hide_index=True, use_container_width=True)

    with st.expander("About this dashboard"):
        st.write(
            "Sales charts follow the selected date range and countries. "
            "RFM segmentation uses the full cleaned dataset and excludes "
            "transactions without a customer ID from customer-level analysis."
        )
        st.write(
            "The dataset ends on 9 December 2011, so December 2011 is "
            "a partial month. RFM segments use heuristic scoring rules."
        )

except Exception as exc:
    st.error("Dashboard could not load data from PostgreSQL.")
    st.exception(exc)
    st.info(
        "Check your .env database settings, PostgreSQL service, "
        "table name, and SQL query."
    )
