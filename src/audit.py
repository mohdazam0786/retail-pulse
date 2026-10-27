from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'raw' / 'Online Retail.xlsx'
EXPECTED = {'InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country'}


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f'Download the UCI dataset and place it at {INPUT}')
    df = pd.read_excel(INPUT, engine='openpyxl', dtype={'InvoiceNo': 'string', 'StockCode': 'string', 'CustomerID': 'string'})
    missing = EXPECTED - set(df.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    print('Shape:', df.shape)
    print('\nDtypes:\n', df.dtypes.to_string())
    print('\nMissing values:\n', df.isna().sum().to_string())
    print('\nExact duplicate rows:', df.duplicated().sum())
    print('Cancellation invoice rows:', df['InvoiceNo'].str.startswith('C', na=False).sum())
    print('Nonpositive quantity rows:', (df['Quantity'] <= 0).sum())
    print('Nonpositive unit price rows:', (df['UnitPrice'] <= 0).sum())
    print('Date range:', df['InvoiceDate'].min(), 'to', df['InvoiceDate'].max())
    print('Unique invoices:', df['InvoiceNo'].nunique())
    print('Unique identified customers:', df['CustomerID'].nunique())
    print('Countries:', df['Country'].nunique())
    print('\nSample:\n', df.head().to_string(index=False))


if __name__ == '__main__':
    main()
