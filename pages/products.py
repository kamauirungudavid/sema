from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st
from datetime import datetime as dt, date
import json
import pandas as pd
from style import load_css
load_css()
import pandas as pd
from datetime import datetime, date
import json


# Create credentials
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Initialize client
client = bigquery.Client(credentials=credentials, project=st.secrets["gcp_service_account"]["project_id"])

add_product, edit_product = st.tabs(["➕ Add Product", "✏️ Edit Product"])

with add_product:
    # ============================= CONSTANTS =============================
    DEFAULT_ROW = {"unit": "", "price": 0}
    DEFAULT_PRODUCT = {
        "product_id": "",
        "prod_name": "",
        "description": "",
        "category": "",
        "retail_price_ksh": 0,
        "date_added": date.today().strftime("%Y-%m-%d"),
        "wholesale_options": [DEFAULT_ROW.copy()]
    }
    # ============================= INIT SESSION STATE =============================
    if "wholesale_rows" not in st.session_state:
        st.session_state.wholesale_rows = [DEFAULT_ROW.copy()]
        st.session_state.product = DEFAULT_PRODUCT.copy()

    if "form_key" not in st.session_state:
        st.session_state.form_key = 0

    # ============================= HELPERS =============================
    def add_row():
        """Add a new wholesale option row"""
        st.session_state.wholesale_rows.append(DEFAULT_ROW.copy())

    def remove_row(i):
        """Remove a wholesale option row"""
        if len(st.session_state.wholesale_rows) > 1:
            st.session_state.wholesale_rows.pop(i)

    def reset_all():
        """Completely reset everything to default values"""
        
        # Reset product fields
        st.session_state.product = DEFAULT_PRODUCT.copy()

        # Reset wholesale rows
        st.session_state.wholesale_rows = [DEFAULT_ROW.copy()]

        # Clear removal flags
        st.session_state.rows_to_remove = []

        # Force Streamlit to recreate widgets
        st.session_state.form_key += 1

    # ============================= MAIN FORM =============================
    # Use form_key to force form reset when needed
    with st.form(key=f"products_form_{st.session_state.form_key}"):
        st.markdown("### Product Information")
        
        # Basic Information in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.session_state.product["prod_name"] = st.text_input(
                "Product Name *", 
                value=st.session_state.product["prod_name"], 
                placeholder="Superfood"
            )
            
            st.session_state.product["product_description"] = st.text_input(
                "Product Description *", 
                value=st.session_state.product["description"], 
                help="Enter the description of the product",
            )


        with col2:

            st.session_state.product["retail_price_ksh"] = st.number_input(
                "Retail Price (Ksh) *", 
                value=st.session_state.product["retail_price_ksh"], 
                help="Price for single unit retail",
            )


            st.session_state.product["product_id"] = st.text_input(
                "Product ID *", 
                value=st.session_state.product["product_id"],
                placeholder="e.g., PROD-001",
                help="Unique identifier for the product",
            )


        with col3:
            st.session_state.product["date_added"] = st.date_input(
                "Date Added *", 
                value=st.session_state.product["date_added"],
                help="Date when product was added",
            )

            
            # Category selection
            category_options = ["Edible", "Non-Edible", "Skincare", "Wellness"]
            current_category = st.session_state.product["category"]
            try:
                default_index = category_options.index(current_category)
            except ValueError:
                default_index = 0  # or handle appropriately for your use case

            st.session_state.product["category"] = st.selectbox(
                "Category", 
                category_options,
                index=default_index,
                help="Product category"
            )
            
        ############## Wholesale Options Section ##############
        st.markdown("---")
        st.markdown("### 🏷️ Wholesale Options")
        
        # Use a different approach for row removal - collect indices to remove
        rows_to_remove = st.session_state.get("rows_to_remove", [])
        
        # Display all rows
        for i, row in enumerate(st.session_state.wholesale_rows):
            cols = st.columns([3, 2, 2, 1])
            
            with cols[0]:
                unit = st.text_input(
                    "Unit",
                    value=row["unit"],
                    placeholder="e.g., 10kg, 1 carton",
                    key=f"unit_{i}_{st.session_state.form_key}",
                    label_visibility="collapsed"
                )
                st.session_state.wholesale_rows[i]["unit"] = unit
            
            with cols[1]:
                price = st.number_input(
                    "Price (Ksh)",
                    min_value=0,
                    step=50,
                    value=row["price"],
                    key=f"price_{i}_{st.session_state.form_key}",
                    label_visibility="collapsed"
                )
                st.session_state.wholesale_rows[i]["price"] = price
            
            with cols[2]:
                # Add a checkbox for removal instead of a button
                remove_this = st.checkbox(
                    "Remove",
                    key=f"remove_check_{i}_{st.session_state.form_key}",
                    label_visibility="collapsed"
                )
                if remove_this:
                    rows_to_remove.append(i)
            
            with cols[3]:
                # Spacer
                st.write("")
        
        # Store rows to remove in session state
        st.session_state.rows_to_remove = rows_to_remove
        
        # Add and Save buttons - using form_submit_button is correct here
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            add_clicked = st.form_submit_button("➕ Add Row", type="secondary")
        with col3:
            save_button = st.form_submit_button("💾 Save Product", type="primary")

    # Handle row removals and additions OUTSIDE the form
    if st.session_state.get("rows_to_remove"):
        # Remove rows in reverse order
        for i in sorted(st.session_state.rows_to_remove, reverse=True):
            remove_row(i)
        st.session_state.rows_to_remove = []  # Clear the list
        st.rerun()

    if add_clicked:
        add_row()
        st.rerun()

    # Handle the form submission outside the form
    if save_button:
        # Filter out empty rows
        valid_rows = []
        for row in st.session_state.wholesale_rows:
            if row["unit"] and row["price"] > 0:
                valid_rows.append(row.copy())

        st.write(valid_rows)
        # Validate required fields

        if not st.session_state.product["prod_name"]:
            st.error("❌ Product Name is required.")
        else:
            # Create product data
            product_data = {
                "product_id": st.session_state.product["product_id"],
                "product_name": st.session_state.product["prod_name"],
                "category": st.session_state.product["category"],
                "retail_price_ksh": st.session_state.product["retail_price_ksh"],
                "wholesale_options": [
                            {
                                "unit": row["unit"],
                                "price": row["price"]
                            }
                            for row in valid_rows
                        ],
                "date_added": str(st.session_state.product["date_added"]),
                "updated_at": dt.now()
            }
            
            # st.success(f"✅ Product '{product_name}' saved successfully!")
            
            
            # SAVE to BigQuery
            try:
                product_data["wholesale_options"] = json.dumps(product_data["wholesale_options"])
                df = pd.DataFrame([product_data])

                st.write(df)

                
                table_id = f"{client.project}.SEMA_NATURALS_DB.products"
                
                job_config = bigquery.LoadJobConfig(
                    write_disposition="WRITE_APPEND",
                    autodetect=True,
                )
                # def fetch_product_names():
                #     """Fetch distinct product names for dropdown"""
                #     query = f"""
                #     SELECT *
                #     FROM `dbt-demos-392016.SEMA_NATURALS_DB.products4`
                #     """
                #     df = client.query(query).to_dataframe()
                #     return df
                # ex_df = fetch_product_names()
                # ex_df['date_added'] = ex_df['date_added'].astype(str)
                # st.write(ex_df)
                load_job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
                load_job.result()
                
                st.success("PRODUCT SAVED SUCCESSFULLY!")
                st.balloons()
                
                # Reset everything immediately
                reset_all()
                st.rerun()  
            except Exception as e:
                st.error(f"Save failed: {e}")



with edit_product:
    # ============================= CONSTANTS =============================
    DEFAULT_ROW = {"unit": "", "price": 0}
    CATEGORIES = ["Edible", "Non-Edible", "Skincare", "Wellness"]
    PRODUCTS_TABLE = "dbt-demos-392016.SEMA_NATURALS_DB.products"

    st.session_state.loaded_product = st.session_state.get("loaded_product", {
        "product_id": "",   
        "product_name": "",
        "description": "",
        "category": CATEGORIES[0],
        "retail_price_ksh": 0,
        "date_added": date.today().strftime("%Y-%m-%d"),
        "wholesale_options": [DEFAULT_ROW.copy()],
        "updated_at": None
    })
 
    # ============================= HELPERS =============================
    @st.cache_data(ttl=300)
    def fetch_product_names():
        """Fetch distinct product names for dropdown"""
        query = f"""
        SELECT DISTINCT product_name
        FROM `{PRODUCTS_TABLE}`
        ORDER BY product_name
        """
        return client.query(query).to_dataframe()

    def fetch_latest_product(product_name):
        """Fetch the latest version of a product"""
        query = f"""
        SELECT * 
        FROM `{PRODUCTS_TABLE}`
        WHERE product_name = @product_name
        ORDER BY updated_at DESC
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("product_name", "STRING", product_name)
            ]
        )
        
        df = client.query(query, job_config=job_config).to_dataframe()
        if df.empty:
            df = pd.DataFrame([{
                "product_id": "",   
                "product_name": "",
                "description": "",
                "category": CATEGORIES[0],
                "retail_price_ksh": 0,
                "date_added": date.today().strftime("%Y-%m-%d"),
                "wholesale_options": json.dumps([DEFAULT_ROW.copy()]),
                "updated_at": None
            }])
        return  df.iloc[0].to_dict()
    
    
    # ============================= PRODUCT SELECTION =============================
    st.markdown("### Select Product to Edit")
    
    # Fetch products for dropdown
    products_df = fetch_product_names()
    product_options = products_df["product_name"].tolist()

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        product_search = st.selectbox(
            "Select Product",
            options=product_options,
            index=0,
            placeholder="Select...",
            help="Type part of the product name to filter the dropdown"
        )
    with col2:
        load_button = st.button("Load Product", type="primary")
        if load_button:
            st.session_state.loaded_product = fetch_latest_product(product_search)
            # st.session_state.edit_wholesale_rows = json.loads(st.session_state.loaded_product["wholesale_options"])
            with col3:
                st.write(st.session_state.loaded_product)

     # Basic Information in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        product_name = st.text_input(
            "Product Name *", 
            value= st.session_state.loaded_product.get("product_name", ""),
            placeholder="Superfood"
        )
        
        product_description = st.text_input(
            "Product Description *", 
            value=st.session_state.loaded_product.get("description", ""),
            help="Enter the description of the product",
        )


    with col2:

        retail_price_ksh = st.number_input(
            "Retail Price (Ksh) *", 
            value=st.session_state.loaded_product.get("retail_price_ksh", 0),
            help="Price for single unit retail",
        )
 

        product_id = st.text_input(
            "Product ID *", 
            value=st.session_state.loaded_product.get("product_id", ""),
            help="Unique identifier for the product",
        )


    with col3:
        date_added = st.text_input(
            "Date Added *", 
            value=st.session_state.loaded_product.get("date_added", date.today().strftime("%Y-%m-%d")),
            help="Date when product was added",
        )

        
        # Category selection
        category_options = ["Edible", "Non-Edible", "Skincare", "Wellness"]
        current_category = st.session_state.product["category"] 
        try:
            default_index = category_options.index(current_category)
        except ValueError:
            default_index = 0  # or handle appropriately for your use case

        category = st.selectbox(
            "Category", 
            placeholder=st.session_state.loaded_product.get("category", category_options[0]),
            options=category_options,
            index=default_index
        )
        
    ############## Wholesale Options Section ##############
    st.markdown("---")
    st.markdown("### 🏷️ Wholesale Options")
    
    # Use a different approach for row removal - collect indices to remove
    rows_to_remove = st.session_state.get("rows_to_remove", [])
    
    # Display all rows
    raw = st.session_state.loaded_product.get("wholesale_options")

    if isinstance(raw, str):
        wholesale_options = json.loads(raw)
    elif isinstance(raw, list):
        wholesale_options = raw
    else:
        wholesale_options = []

    if not wholesale_options:
        wholesale_options = [DEFAULT_ROW.copy()]
    st.write(wholesale_options)
    st.session_state.loaded_product["wholesale_options"] = wholesale_options


    for i, row in enumerate(st.session_state.wholesale_rows):
        cols = st.columns([3, 2, 1])

        with cols[0]:
            st.session_state.wholesale_rows[i]["unit"] = st.text_input(
                "Unit",
                value=row.get("unit", ""),
                key=f"unit_{i}",
                label_visibility="collapsed"
            )

        with cols[1]:
            st.session_state.wholesale_rows[i]["price"] = st.number_input(
                "Price (Ksh)",
                value=row.get("price", 0),
                min_value=0,
                step=50,
                key=f"price_{i}",
                label_visibility="collapsed"
            )

        with cols[2]:
            if st.checkbox("❌", key=f"remove_{i}"):
                rows_to_remove.append(i)
    
    # Store rows to remove in session state
    st.session_state.rows_to_remove = rows_to_remove
    
    # Add and Save buttons - using form_submit_button is correct here
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        add_clicked = st.button("➕ Add Row_", type="secondary")
    with col3:
        save_button = st.button("💾 Save Product", type="primary")

# Handle row removals and additions OUTSIDE the form
if st.session_state.get("rows_to_remove"):
    # Remove rows in reverse order
    for i in sorted(st.session_state.rows_to_remove, reverse=True):
        remove_row(i)
    st.session_state.rows_to_remove = []  # Clear the list
    st.rerun()

if add_clicked:
    add_row()
    st.rerun()

# Handle the form submission outside the form
if save_button:
    # Filter out empty rows
    valid_rows = []
    for row in st.session_state.wholesale_rows:
        if row["unit"] and row["price"] > 0:
            valid_rows.append(row.copy())

    st.write(valid_rows)
    # Validate required fields

    if not st.session_state.product["prod_name"]:
        # Create product data
        product_data_ = {
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "retail_price_ksh": retail_price_ksh,
            "wholesale_options": [
                        {
                            "unit": row["unit"],
                            "price": row["price"]
                        }
                        for row in valid_rows
                    ],
            "date_added": date_added,
            "updated_at": dt.now()
        }
            
            # st.success(f"✅ Product '{product_name}' saved successfully!")
            
            
            # SAVE to BigQuery
        try:
            product_data_["wholesale_options"] = json.dumps(product_data_["wholesale_options"])
            df_ = pd.DataFrame([product_data_])

            st.write(df_)

            
            table_id = f"{client.project}.SEMA_NATURALS_DB.products"
            
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
                autodetect=True,
            )
            # def fetch_product_names():
            #     """Fetch distinct product names for dropdown"""
            #     query = f"""
            #     SELECT *
            #     FROM `dbt-demos-392016.SEMA_NATURALS_DB.products4`
            #     """
            #     df = client.query(query).to_dataframe()
            #     return df
            # ex_df = fetch_product_names()
            # ex_df['date_added'] = ex_df['date_added'].astype(str)
            # st.write(ex_df)
            load_job = client.load_table_from_dataframe(df_, table_id, job_config=job_config)
            load_job.result()
            
            st.success("PRODUCT SAVED SUCCESSFULLY!")
            st.balloons()
            
            # Reset everything immediately
            reset_all()
            st.rerun()  
        except Exception as e:
            st.error(f"Save failed: {e}")

