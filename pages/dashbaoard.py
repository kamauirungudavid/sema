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
            date(sales_date) as sales_date,
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
            sales_date,
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
            sales_date,
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
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("Start date", "2025-11-01")
    with col2:
        end_date = st.date_input("End date", dt.now())
    with col3:
        specific_customer = st.text_input("Customer Name (optional)", value="")
    
    col1,col2,col3,col4,col5 = st.columns(5)
    with st.spinner("Fetching Sales Data..."):
        sales_df = get_sales(start_date, end_date)
        
        dup_cols = [
            "customer_name",
            "delivery_destination",
            "customer_phone",
            "sales_date",
            "product",
            "line_total",
                ]
        if specific_customer:
            specific_customer = specific_customer.lower()
            sales_df = sales_df[sales_df['customer_name']
                .str.lower().str.contains(specific_customer, na=False)]
        sales_df.drop_duplicates(subset=dup_cols,inplace=True)

        total_undisc_sale = sales_df['line_total'].sum()
        total_disc_sale = sales_df['line_total'].sum() - sales_df['overall_discount'].mean()
        total_disc_offered = sales_df['overall_discount'].mean()
        delivery_charges = sales_df.groupby(['customer_name','sales_date'])['delivery_fee'].mean()

    with col1:
        st.metric("Total Undiscounted Sales", f"Kes: {total_undisc_sale:,.0f}") 
    with col2:
        st.metric("Total Discounted Sales", f"Kes: {total_disc_sale:,.0f}")
    with col3:
        st.metric("Total Discounts Offered", f"Kes: {total_disc_offered:,.0f}")
    with col4:
        st.metric("Delivery Charges Collected", f"Kes: {delivery_charges:,.0f}")
    with col5:
        profit = total_undisc_sale - total_disc_offered
        st.metric("Estimated Profit", f"Kes: {profit:,.0f}")

    st.write("#### Overview")
    tab1, tab2, tab3 = st.tabs(["Performance", "Items Sold", "Edit Sales"])
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
        st.dataframe(sales_df.drop(columns=['overall_discount','delivery_fee','discounted_total','undiscounted_total']).style.format({
            'line_total': 'KES {:,.2f}',
            'quantity': '{:,.0f}'
        }))



    with tab3:
        st.write("Edit Sales Record")
        
        # Form 1: Load record
        with st.form(key="load_record_form"):
            col1, col2 = st.columns(2)
            with col1:
                editor = st.text_input("Editor", type="password", key="editor_input")
            with col2:
                record_id = st.text_input("Record ID", key="record_id_input")
            
            load_button = st.form_submit_button(label="Load Record")
        def get_sales_to_edit(record_id):
                    query = f"""
                        SELECT 
                            *
                        FROM `dbt-demos-392016.SEMA_NATURALS_DB.sales_prod`
                        WHERE customer_name = '{record_id}'
                        order by DATE(created_at) DESC
                            ;
                    """                     
                    query_job = client.query(query)
                    results = query_job.result()
                    df = results.to_dataframe()
                    return df  
        
        # Store loaded data in session state
        if load_button and editor == "joyceditor1":
            df_existing = get_sales_to_edit(record_id)
            st.session_state['record_to_edit'] = df_existing
            st.session_state['record_id'] = record_id
            st.rerun()
        
        # Form 2: Edit record (only shows after loading)
        if 'record_to_edit' in st.session_state and st.session_state.record_to_edit is not None:
            st.write(f"Editing record for: {st.session_state.get('record_id', 'Unknown')}")
            
            # Edit the record
            edited_df = st.data_editor(
                st.session_state.record_to_edit,
                num_rows="fixed",  # Use "fixed" for editing existing rows only
                key="record_editor"
            )
            edited_df['items'] = edited_df['items'].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)


            st.write(edited_df)
            
            # Save button (outside any form)
            if st.button("💾 Save Changes", key="save_changes_btn"):
                try:
                    # Convert items to JSON string
                    edited_df['items'] = edited_df['items'].apply(lambda x: json.dumps(x))
                    
                    # ---- Update in BigQuery ----
                    # IMPORTANT: You should use UPDATE or DELETE+INSERT, not WRITE_APPEND
                    
                    # Method 1: Delete old records and insert new ones
                    delete_query = f"""
                        DELETE FROM `EMA_NATURALS_DB.sales`
                        WHERE customer_name = '{st.session_state.record_id}'
                    """
                    client.query(delete_query)
                    
                    # Insert the updated records
                    table_id = f"{client.project}.SEMA_NATURALS_DB.sales"
                    job_config = bigquery.LoadJobConfig(
                        write_disposition="WRITE_APPEND",
                        autodetect=True,
                    )
                    
                    load_job = client.load_table_from_dataframe(edited_df, table_id, job_config=job_config)
                    load_job.result()
                    
                    st.success("Record updated successfully!")
                    # Clear session state
                    del st.session_state['record_to_edit']
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error updating record: {e}")
            
            # Cancel button
            if st.button("❌ Cancel", key="cancel_edit"):
                del st.session_state['record_to_edit']
                st.rerun()

        