# Run this in BigQuery console or through your preferred method
#CREATE SALES RECORDS TABLE
f'''
CREATE TABLE IF NOT EXISTS `your-project-id.sema_sales.sales_records` (
  timestamp TIMESTAMP,
  customer_name STRING,
  customer_phone STRING,
  customer_address STRING,
  delivery_mode STRING,
  delivery_destination STRING,
  payment_mode STRING,
  invoice_number STRING,
  sales_date DATE,
  overall_discount FLOAT64,
  grand_total FLOAT64,
  items ARRAY<STRUCT<
    product STRING,
    type STRING,
    quantity INT64,
    unit_price FLOAT64,
    line_total FLOAT64
  >>,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
'''