from google.cloud import bigquery
import streamlit as st
from datetime import datetime as dt
import json
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
from pandas_gbq import to_gbq

from style import load_css

load_css()
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Initialize client
client = bigquery.Client(credentials=credentials, project=st.secrets["gcp_service_account"]["project_id"])


def get_sales(start_date, end_date):
    query = f"""
        
WITH unnest_sales AS (
  SELECT 
    customer_name,
    invoice_number as email,
    customer_phone,
    delivery_destination,
    delivery_mode,
    payment_mode,
    grand_total,
    undiscounted_total,
    delivery_fee,
    overall_discount,
    JSON_VALUE(item, '$.product') AS product,
    JSON_VALUE(item, '$.type') AS type,
    CAST(JSON_VALUE(item, '$.quantity') AS INT64) AS quantity,
    CAST(JSON_VALUE(item, '$.unit_price') AS FLOAT64) AS unit_price,
    CAST(JSON_VALUE(item, '$.line_total') AS FLOAT64) AS line_total
  FROM `dbt-demos-392016.SEMA_NATURALS_DB.sales`,
  UNNEST(JSON_QUERY_ARRAY(items)) AS item
  WHERE date(sales_date) between date('{start_date}') and date('{end_date}')
    )
    SELECT customer_name,
    delivery_destination,
    email,
    customer_phone,
    AVG(grand_total) as discounted_total,
    AVG(undiscounted_total) AS undiscounted_total,
    AVG(delivery_fee) AS delivery_fee,
    AVG(overall_discount) AS overall_discount,
    product,
    type,
    quantity,
    line_total
    FROM unnest_sales
    GROUP BY 
    customer_name,
    delivery_destination,
    email,
    customer_phone,
    product,
    type,
    quantity,
    line_total
    ;
    """                     
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    return df   




#### STREAMLIT APP ####

with st.spinner("Loading Sales Dashboard..."):
    st.write("#### Sales Dashboard")
    col1, col2, col3= st.columns(3)
    with col1:
        start_date = st.date_input("Start date", dt(2025, 1, 1))
    with col2:
        end_date = st.date_input("End date", dt.now())
    with col3:
        if st.button("Refresh Data"):
            st.experimental_rerun()
    
    col1,col2,col3,col4,col5 = st.columns(5)
    with st.spinner("Fetching Sales Data..."):
        sales_df = get_sales(start_date, end_date)
        total_undisc_sale = sales_df['undiscounted_total'].sum()
        total_disc_sale = sales_df['discounted_total'].sum()
        total_disc_offered = sales_df['overall_discount'].sum()
        delivery_charges = sales_df['delivery_fee'].sum()

    with col1:
        st.metric("Total Undiscounted Sales", f"Kes: {total_undisc_sale:,.0f}") 
    with col2:
        st.metric("Total Discounted Sales", f"Kes: {total_disc_sale:,.0f}")
    with col3:
        st.metric("Total Discounts Offered", f"Kes: {total_disc_offered:,.0f}")
    with col4:
        st.metric("Delivery Charges Collected", f"Kes: {delivery_charges:,.0f}")
    with col5:
        profit = total_disc_sale - (total_undisc_sale - total_disc_offered)
        st.metric("Estimated Profit", f"Kes: {profit:,.0f}")

    st.write("#### Overview")
    tab1, tab2 = st.tabs(["Performance", "Items Sold"])
    with tab1:

        col1, col2 = st.columns(2)
        with col1:
            product_sales_summary = sales_df.groupby('product').agg(
            total_sales_amount = ('line_total', 'sum'),
            total_quantity_sold = ('quantity', 'sum' )).reset_index()
            #top revenue generating products
            top_revenue_products = product_sales_summary.sort_values(by='total_sales_amount', ascending=False).head(5)
            st.write("**Top 5 Revenue Generating Products**")   
            st.dataframe(top_revenue_products.style.format({
                'total_sales_amount': 'KES {:,.2f}',
                'total_quantity_sold': '{:,.0f}'
            }))

        with col2:
            ##top selling products
            top_products = sales_df.groupby('product').agg(
                total_quantity_sold = ('quantity', 'sum' )
            ).reset_index().sort_values(by='total_quantity_sold', ascending=False).head(5)
            st.write("**Top 5 Best Selling Products**")
            st.dataframe(top_products.style.format({
                'total_quantity_sold': '{:,.0f}'
            }))
 
           

    with tab2:
        st.write("Items Sold Data")
        st.dataframe(sales_df)
        