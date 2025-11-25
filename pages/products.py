from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st
from datetime import datetime as dt
import json
import pandas as pd
from style import load_css
load_css()

# Create credentials
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Initialize client
client = bigquery.Client(credentials=credentials, project=st.secrets["gcp_service_account"]["project_id"])

#target table:
dataset_id = "SEMA_NATURALS_DB"
table_id = "products_new"
table_ref = f"{client.project}.{dataset_id}.{table_id}"




with st.form("products_form"):
    col1,col2,col3 = st.columns(3)

    with col1:
        product_name = st.text_input(
            "Product Name",
            value="",
            key="product_name"
        )

        product_description = st.text_area(
            "Product Description",
            value="",
            key="product_description"
        )

    with col2:
        retail_price = st.number_input(
            "Retail Price (Ksh)",
            min_value=1,
            step=50,
            value=50,
            key="product_price"
        )

        wholesale_price = st.number_input(
            "WholeSale Price (Units)",
            min_value=1,
            step=50,
            value=20,
            key="wholesale_price"
        )

    with col3:
        product_id = st.text_input(
            "Product ID",
            value="",
            key="product_id"
        )

        date_added =st.date_input(
            "Date Added",
            key="date_added"
        )
    save_button = st.form_submit_button("✅ Add Product")
    
if save_button:
    input_dict = {
        "product_id": product_id,
        "product_name": product_name,
        "description": product_description,
        "retail_price_ksh_": retail_price,
        "wholesale_price_ksh_": wholesale_price,
        "updated_at": date_added
    }

    st.write("You have entered the following product details:")
    st.json(input_dict)

    # 🪣 Step 3: Load only new product rows
    new_df = pd.DataFrame([input_dict])
    new_df['updated_at'] = pd.to_datetime(new_df['updated_at'])
    new_df['Current_date'] = dt.now()

    if not new_df.empty:
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
        load_job = client.load_table_from_dataframe(new_df, table_ref, job_config=job_config)
        load_job.result()
        st.success("✅ New rows successfully updated")
    else:
        st.warning("⚠️ No new rows found — nothing to upload.")


    query = "select * from `dbt-demos-392016.SEMA_NATURALS_DB.products_new` where product_name is not null LIMIT 10"
    results = client.query(query).to_dataframe()

    product_config = (
    results[['product_name','retail_price_ksh_','wholesale_price_ksh_']].groupby('product_name')
        .apply(lambda x: x.drop('product_name', axis=1).values.tolist())
        .to_dict()
    )    
    with open('data/config_files/product_config.json', 'w') as f:
         json.dump(product_config, f, indent=4)

    st.write("### Existing Products")
    st.dataframe(results)
