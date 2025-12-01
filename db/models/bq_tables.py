# Run this in BigQuery console or through your preferred method
#CREATE SALES RECORDS TABLE
f'''
CREATE TABLE IF NOT EXISTS `dbt-demos-392016.SEMA_NATURALS_DB.sales_records2` (
  customer_name        STRING,
  customer_phone       STRING,
  customer_address     STRING,
  delivery_mode        STRING,
  delivery_destination STRING,
  payment_mode         STRING,
  invoice_number       STRING,
  sales_date           STRING,   -- store dates as ISO strings
  overall_discount     FLOAT64,
  grand_total          FLOAT64,
  undiscounted_total   FLOAT64,
  delivery_fee        FLOAT64,
  items                STRING,   -- store JSON as string
  created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
'''