# RetailPulse Analytics

An end-to-end portfolio project for e-commerce transaction analytics using Python, PostgreSQL, SQL, and Streamlit.

## Business questions
- How do sales and orders change over time?
- Which products and countries drive sales?
- Which identified customers are most valuable (RFM)?
- What does repeat-purchase retention look like?

## Dataset
UCI Online Retail: https://archive.ics.uci.edu/dataset/352/online+retail

Historical transactions from 2010–2011. This is a public learning dataset, not live business data.

## Setup (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
If PowerShell activation is blocked, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and use that Python executable for subsequent commands.

Download `Online Retail.xlsx` from UCI and put it in `data/raw/`.

```powershell
python src/audit.py
```

## Planned deliverables
- Data-quality report and documented cleaning rules
- PostgreSQL schema and business SQL queries
- RFM and cohort retention analysis
- Streamlit dashboard and reproducible deployment

## Metric definitions (to finalize after audit)
- Gross merchandise sales: sum of positive-quantity, positive-price sales line values (not profit).
- Cancellations/returns: tracked separately, not silently mixed into sales.
- Order count: distinct non-cancellation invoice numbers.
- AOV: sales value / distinct qualifying orders.
- Customer analyses: identified CustomerID rows only, with coverage reported.

## Limitations
No cost-of-goods or marketing spend columns; therefore profit, margin, CAC and ROAS cannot be calculated accurately from this dataset alone. Historical dates must not be presented as current sales.
