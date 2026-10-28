CREATE TABLE IF NOT EXISTS retail_sales (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_no TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    invoice_date TIMESTAMP NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    customer_id TEXT,
    country TEXT NOT NULL,
    revenue NUMERIC(14, 2) NOT NULL
);
