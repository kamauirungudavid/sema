import streamlit as st
import pandas as pd
from datetime import datetime as dt,date
from style import load_css
import json
import math
from google.oauth2 import service_account
from google.cloud import bigquery
from pandas_gbq import to_gbq


load_css()
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Initialize client
client = bigquery.Client(credentials=credentials, project=st.secrets["gcp_service_account"]["project_id"])

#target table:
dataset_id = "SEMA_NATURALS_DB"
table_id = "sales"
table_ref = f"{client.project}.{dataset_id}.{table_id}"


# ============================= CONFIG =============================
with open('data/config_files/retail_config_file.json', "r") as f:
    PRODUCT_DB = json.load(f)

with open('data/config_files/wholesale_options_config_file.json', "r") as f:
    WHOLESALE_PRICES = json.load(f)

DEFAULT_ROW = {
    "product_name": "Select...",
    "purchase_type": "Select...",
    "wholesale_quantity_type": None,
    "quantity": 1,
    "price_per_unit": 0,
    "price": 0
}

DEFAULT_CUSTOMER = {
    "name": "", 
    "phone": "+254", 
    "address": "", 
    "delivery_mode": "Pickup", 
    "delivery_destination": "",
    "payment_mode": "MPESA", 
    "email": "", 
    "sales_date": dt.now().date()
}

# ============================= SESSION STATE INIT =============================
def initialize_session_state():
    """Initialize or reset all session state variables"""
    if "sales_rows" not in st.session_state:
        st.session_state.sales_rows = [DEFAULT_ROW.copy()]
    
    if "customer" not in st.session_state:
        st.session_state.customer = DEFAULT_CUSTOMER.copy()
    
    if "just_saved" not in st.session_state:
        st.session_state.just_saved = False
    
    if "form_key" not in st.session_state:
        st.session_state.form_key = 0

initialize_session_state()

# ============================= HELPERS =============================
def add_row():
    st.session_state.sales_rows.append(DEFAULT_ROW.copy())

def remove_row(i):
    st.session_state.sales_rows.pop(i)

def reset_all():
    """Completely reset everything to default values"""
    st.session_state.sales_rows = [DEFAULT_ROW.copy()]
    st.session_state.customer = DEFAULT_CUSTOMER.copy()
    st.session_state.just_saved = False
    st.session_state.form_key += 1  # This forces the form to reset

# ============================= MAIN UI =============================
st.write("### SEMA Sales Entry System")

# Use form key to force reset
form_key = st.session_state.form_key

# --------------------- Customer Info ---------------------
with st.expander("Customer Information", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.customer["name"] = st.text_input(
            "Customer Name", 
            value=st.session_state.customer["name"], 
            key=f"cust_name_{form_key}"
        )
        st.session_state.customer["phone"] = st.text_input(
            "Phone Number", 
            value=st.session_state.customer["phone"], 
            key=f"cust_phone_{form_key}"
        )
        st.session_state.customer["address"] = st.text_area(
            "Delivery Address", 
            value=st.session_state.customer["address"], 
            key=f"cust_addr_{form_key}", 
            height=80
        )
    with col2:
        st.session_state.customer["delivery_mode"] = st.radio(
            "Delivery Mode", 
            ["Pickup", "Delivery"], 
            horizontal=True,
            index=0 if st.session_state.customer["delivery_mode"] == "Pickup" else 1,
            key=f"delivery_mode_{form_key}"
        )
        st.session_state.customer["delivery_destination"] = st.text_input(
            "Delivery Means (if applicable)", 
            value=st.session_state.customer["delivery_destination"],
            key=f"delivery_dest_{form_key}"
        )
        st.session_state.customer["delivery_fee"] = st.number_input(
            "Delivery Fee", 
           value=st.session_state.customer["delivery_fee"] if "delivery_fee" in st.session_state.customer else 0,
            key=f"delivery_fee_{form_key}"
        )
        
    with col3:
        st.session_state.customer["email"] = st.text_input(
            "Customer Email (optional)", 
            value=st.session_state.customer["email"],
            key=f"cust_email_{form_key}"
        )
        st.session_state.customer["payment_mode"] = st.selectbox(
            "Payment Mode", 
            ["MPESA", "CASH", "BANK DEPOSIT"],
            index=["MPESA", "CASH", "BANK DEPOSIT"].index(st.session_state.customer["payment_mode"]),
            key=f"payment_mode_{form_key}"
        )
        st.session_state.customer["sales_date"] = st.date_input(
            "Sales Date", 
            value=st.session_state.customer["sales_date"],
            key=f"sales_date_{form_key}"
        )

# --------------------- Dynamic Product Rows ---------------------
st.markdown("### Product Items")

for i, row in enumerate(st.session_state.sales_rows):
    cols = st.columns([3, 2, 1.5, 1.5, 1.5])
    with cols[0]:
        options = ["Select..."] + list(PRODUCT_DB.keys())
        idx = options.index(row["product_name"]) if row["product_name"] in options else 0
        selected = st.selectbox(
            f"Product {i+1}", 
            options, 
            index=idx,
            key=f"prod_{i}_{form_key}"
        )
        st.session_state.sales_rows[i]["product_name"] = selected

    with cols[1]:
        ptype = st.selectbox(
            "Type", 
            ["Select...", "Retail", "Wholesale"], 
            index=["Select...", "Retail", "Wholesale"].index(row["purchase_type"]) if row["purchase_type"] in ["Select...", "Retail", "Wholesale"] else 0,
            key=f"type_{i}_{form_key}"
        )
        st.session_state.sales_rows[i]["purchase_type"] = ptype

    # Wholesale-specific quantity type selection
    if ptype == "Wholesale":
        with cols[1]:
            # Get available quantity types for the selected product
            qty_types = WHOLESALE_PRICES.get(selected, {})
            
            if qty_types:
                current_qty_type = st.session_state.sales_rows[i].get("quantity_type")
                available_qty_types = list(qty_types.keys())
                qty_type_idx = available_qty_types.index(current_qty_type) if current_qty_type in available_qty_types else 0
                
                qty_type = st.selectbox(
                    "Quantity Type", 
                    options=available_qty_types,
                    index=qty_type_idx,
                    key=f"qty_type_{i}_{form_key}",
                    help="Select the wholesale quantity type"
                )
                st.session_state.sales_rows[i]["quantity_type"] = qty_type
            else:
                st.warning(f"No wholesale pricing available for {selected}")
                st.session_state.sales_rows[i]["quantity_type"] = None
    else:
        st.session_state.sales_rows[i]["quantity_type"] = None

    with cols[2]:
        qty = st.number_input(
            "Qty", 
            min_value=1, 
            value=row["quantity"], 
            key=f"qty_{i}_{form_key}"
        )
        st.session_state.sales_rows[i]["quantity"] = qty

    # Auto price calculation
    total_price = 0
    wholesale_pr = 0
    if selected != "Select..." and selected in PRODUCT_DB:
        prices = PRODUCT_DB[selected]
        if st.session_state.sales_rows[i]["purchase_type"] == "Retail":
            total_price = prices * st.session_state.sales_rows[i]["quantity"]
        elif st.session_state.sales_rows[i]["purchase_type"] == "Wholesale":
            qty_types = WHOLESALE_PRICES.get(selected, {})
            wholesale_pr = qty_types.get(st.session_state.sales_rows[i]["quantity_type"], 0)
            total_price = wholesale_pr * qty

        retail_pr = prices if not math.isnan(prices) else 0
        price_per_unit = retail_pr if ptype == "Retail" else wholesale_pr
        st.session_state.sales_rows[i]["price_per_unit"] = price_per_unit

    with cols[3]:
        st.session_state.sales_rows[i]["price"] = total_price
        st.metric("Total", f"{total_price:,.0f}")

    with cols[4]:
        if st.button("Delete", key=f"del_{i}_{form_key}"):
            remove_row(i)
            st.rerun()

# Add new row button
if st.button("Add Another Product", type="secondary", use_container_width=True):
    add_row()
    st.rerun()

# --------------------- Preview Table ---------------------
st.markdown("### Order Summary")
data = []
undiscounted_price = 0
for row in st.session_state.sales_rows:
    if row["product_name"] != "Select...":
        data.append({
            "Product": row["product_name"],
            "Type": row["purchase_type"],
            "wholesale Qty Type": row.get("quantity_type", ""),
            "Qty": row["quantity"],
            "Price/Unit": f"Ksh {row['price_per_unit']:,.0f}",
            "Line Total": f"Ksh {row['price']:,.0f}"
        })
        undiscounted_price += row["price"]

col1, col2 = st.columns(2)
with col1:
    discount_applied = st.selectbox(
        "Discount Awarded?", 
        ["No", "Yes"],
        key=f"discount_applied_{form_key}"
    )
with col2:
    discount = st.number_input(
        "Discount Amount (Ksh)", 
        value=0, 
        key=f"discount_{form_key}"
    )
    grand_total = undiscounted_price - discount

if data:
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.success(f"**GRAND TOTAL: Ksh {grand_total:,.0f}**")
else:
    st.info("Add at least one product to see the summary.")

# --------------------- FINAL SUBMIT ---------------------
with st.form(key=f"final_save_form_{form_key}"):
    submitted = st.form_submit_button(
        "SAVE COMPLETE SALE RECORD",
        type="primary",
        use_container_width=True
    )

    if submitted:
        # Validation
        if not st.session_state.customer["name"]:
            st.error("Customer name is required.")
        elif not data:
            st.error("Add at least one product.")
        else:
            # Build final record
            final_record = {
                "customer_name": st.session_state.customer["name"],
                "customer_phone": st.session_state.customer["phone"],
                "customer_address": st.session_state.customer["address"],
                "delivery_mode": st.session_state.customer["delivery_mode"],
                "delivery_destination": st.session_state.customer["delivery_destination"],
                "payment_mode": st.session_state.customer["payment_mode"],
                "invoice_number": st.session_state.customer["email"],
                "sales_date": st.session_state.customer["sales_date"],
                "overall_discount": discount,
                "items": [
                    {
                        "product": r["product_name"],
                        "type": r["purchase_type"],
                        "quantity": r["quantity"],
                        "wholesale_quantity_type": r.get("quantity_type"),
                        "unit_price": r["price_per_unit"],
                        "line_total": r["price"]
                    }
                    for r in st.session_state.sales_rows
                    if r["product_name"] != "Select..."
                ],
                "grand_total": grand_total,
                "undiscounted_total": undiscounted_price,
                "delivery_fee": st.session_state.customer.get("delivery_fee", 0)

            }

            # SAVE (example: to Excel or BigQuery)
            try:
                final_record["sales_date"] = final_record["sales_date"].isoformat() if isinstance(final_record["sales_date"], (dt, date)) else final_record["sales_date"]

                df = pd.DataFrame([final_record])
                df['items'] = df['items'].apply(lambda x: json.dumps(x))

                # ---- Load job (instead of streaming insert) ----
                table_id = f"{client.project}.SEMA_NATURALS_DB.sales"

                job_config = bigquery.LoadJobConfig(
                    write_disposition="WRITE_APPEND",  # append to table
                    autodetect=True,                   # detect schema from DataFrame
                )
                

                load_job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
                load_job.result() 
                # Or use BigQuery client here
                st.success("SALE SAVED SUCCESSFULLY!")
                st.balloons()
                # Reset everything immediately
                reset_all()
                st.rerun()  # Force immediate refresh
            except Exception as e:
                st.error(f"Save failed: {e}")