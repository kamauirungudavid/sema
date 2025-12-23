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


{
  "Superfood": 500,
  "Slippery elm": 600,
  "Castor oil": 800,
  "Cranberry": 1200,
  "Hair growth oil": 800,
  "Shea soap": 700,
  "Vitamin C": 1050,
  "Hair oil": 900,
  "Antifungal oil": 1200,
  "Menthol": 1500,
  "Anti foaming cleanser": 3000,
  "Red maca": 500,
  "Black seed oil": 1200,
  "Cayenne pepper": 1200,
  "Sunscreen": 500,
  "Night cream": 1200,
  "Hyluronic acid serum": 1000,
  "African prunus": 1500,
  "Tumeric oil": 1600,
  "Shillajit": 800,
  "Moisturising body butter": 1500,
  "Brightening cream": 1400,
  "Tumeric cleanser": null,
  "Coconut oil": null,
  "Jars": null
}




####products

f'''CREATE TABLE IF NOT EXISTS `your_project.your_dataset.products` (
  -- Product Information
  product_id STRING NOT NULL,
  product_name STRING NOT NULL,
  description STRING,
  category STRING,
  retail_price_ksh NUMERIC,
  
  -- Wholesale options as a nested/repeated field
  wholesale_options ARRAY<STRUCT<
    unit STRING,
    price NUMERIC
  >>,
  
  -- Timestamps
  date_added DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  
  -- Optional metadata
  is_active BOOL DEFAULT TRUE,
  version INT64 DEFAULT 1,
  
  -- Partitioning and clustering for optimization
  PARTITION BY DATE(date_added),
  CLUSTER BY category, product_id
);'''