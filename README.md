# RetailPulse — E-commerce Sales Analytics

RetailPulse is an end-to-end sales analytics project built using Python, PostgreSQL, SQL, and Streamlit. It transforms raw retail transaction data into actionable sales insights and customer segments.

## Features

- **Data Cleaning:** Removes duplicate transactions, cancellation invoices, and invalid sales records.
- **PostgreSQL Integration:** Stores and queries cleaned transaction data.
- **Sales KPIs:** Tracks recorded revenue, invoice count, identified customers, and revenue per invoice.
- **Sales Trend Analysis:** Analyzes monthly revenue patterns.
- **Country Analysis:** Compares recorded sales across countries.
- **RFM Segmentation:** Classifies identified customers into seven segments.
- **Interactive Filters:** Filter sales data by invoice date and country.
- **Transaction Explorer:** Search and inspect filtered sales transactions.
- **CSV Export:** Download filtered transaction data.

## Tech Stack

- Python
- PostgreSQL
- SQL
- Pandas
- Matplotlib
- Seaborn
- SQLAlchemy
- Streamlit

## Project Structure

```text
retailpulse-starter/
├── app.py
├── src/
│   ├── db.py
│   ├── clean_data.py
│   ├── load_to_postgres.py
│   └── visualize.py
├── sql/
│   ├── schema.sql
│   ├── analytics.sql
│   ├── rfm_analysis.sql
│   ├── rfm_segments.sql
│   └── rfm_summary.sql
├── tests/
├── reports/
│   └── figures/
├── requirements.txt
├── .gitignore
└── README.md
```

*Update the file tree if your actual filenames differ.*

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/mohdazam0786/retail-pulse.git
cd retail-pulse
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database named `retailpulse` and configure the connection in a local `.env` file:

```text
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/retailpulse
```

Replace `YOUR_PASSWORD` with your local PostgreSQL password. Never commit `.env` or expose database credentials.

### 5. Prepare the dataset

Obtain the Online Retail dataset and place the Excel file in the location expected by `src/clean_data.py`.

Run the cleaning and database-loading scripts according to their configured paths and workflow.

### 6. Run the dashboard

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## Customer Segmentation

RetailPulse uses Recency, Frequency, and Monetary (RFM) metrics to segment identified customers into:

- Champions
- Loyal Customers
- Potential Loyalists
- Recent Customers
- At Risk
- Hibernating
- Needs Attention

The segment labels are based on heuristic SQL rules and should be validated against business objectives.

## Data Quality and Limitations

- The original dataset contains 541,909 rows.
- The current cleaned dataset contains 524,878 rows.
- The dataset covers December 2010 through December 9, 2011.
- December 2011 represents a partial month.
- Customers without an identified customer ID are excluded from RFM segmentation.
- Recorded sales revenue is not profit or customer lifetime value.
- The RFM results depend on the scoring and segmentation rules implemented in SQL.

## Future Improvements

- Deploy the dashboard online.
- Add product-level analysis and more advanced date comparisons.
- Improve dashboard visual design and reporting.
- Add automated data-quality checks and scheduled refreshes.

## Author

Mohd Azam Siddique

GitHub: [mohdazam0786](https://github.com/mohdazam0786)
