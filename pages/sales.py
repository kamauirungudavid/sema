import streamlit as st
import pandas as pd
from datetime import datetime as dt
import json
import math
from google.cloud import bigquery

# --- Defaults for cleared state ---
DEFAULTS = {
    "customer_name": "",
    "customer_phone": "+254",
    "purchase_type": "Select...",
    "delivery_mode": "",
    "product_name": "Select...",
    "quantity": "",
    "pickup_status": "PENDING",
    "payment_mode": "Select...",
    "invoice_number": "",
    "delivery_destination": "",
    "sales_date": dt.now().date(),
}

with open('data/config_files/product_config.json',  "r") as f:
    product_list = json.load(f)

# Ensure session state keys exist (so UI can read them)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Form block ---
with st.form("sales_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        cust_name = st.text_input(
            "Customer Name",
            value=st.session_state["customer_name"],
            key="customer_name"
        )

        cust_phone = st.text_input(
            "Customer Phone Number",
            value=st.session_state["customer_phone"],
            placeholder="+254712345678",
            key="customer_phone"
        )

        purchase_type_options = ["Select...", "Retail", "Wholesale"]
        purchase_type = st.selectbox(
            "Purchase Type",
            purchase_type_options,
            index=purchase_type_options.index(st.session_state["purchase_type"])
            if st.session_state["purchase_type"] in purchase_type_options else 0,
            key="purchase_type"
        )

        delivery_mode = st.text_input(
            "Delivery Mode",
            value=st.session_state["delivery_mode"],
            placeholder="e.g. PICKUP",
            key="delivery_mode"
        )

    with col2:
        product_name_options = ["Select...."] + list(product_list.keys())
        # Set default index
        default_index = 0  # "Select...." is the first option
        if "product_name" in st.session_state and st.session_state["product_name"] in product_name_options:
            default_index = product_name_options.index(st.session_state["product_name"])

        product_name = st.selectbox(
            "Product Name",
            product_name_options,
            index=default_index,
            key="product_name"
        )


        quantity = st.text_input(
            "Purchase Quantity (Units)",
            value=st.session_state["quantity"],
            placeholder="e.g. 5",
            key="quantity"
        )


        retail_price = 1
        wholesale_price = 1

        # Only lookup if a real product is selected
        if product_name in product_list:
            prices = product_list[product_name][0]
            retail_price = prices[0] if not math.isnan(prices[0]) else 1
            wholesale_price = prices[1] if not math.isnan(prices[1]) else 1

        if "price_amount" not in st.session_state:
            st.session_state["price_amount"] = int(retail_price)
        elif product_name != "Select....":
            # Auto-update number_input whenever a new product is selected
            st.session_state["price_amount"] = int(retail_price)

        # Number input (auto-filled)
        price_amount = st.number_input(
            "Price Amount (Ksh)",
            min_value=1,
            step=10,
            key="price_amount"
        )
        pickup_status = st.selectbox(
            "Pickup Status",
            ["PENDING", "PICKED UP", "DELIVERED"],
            index=["PENDING", "PICKED UP", "DELIVERED"].index(st.session_state.get("pickup_status", "PENDING")),
            key="pickup_status"
        )

    with col3:
        payment_mode_options = ["Select...", "MPESA", "BANK DEPOSIT", "CASH"]
        payment_mode = st.selectbox(
            "Payment Mode",
            payment_mode_options,
            index=payment_mode_options.index(st.session_state["payment_mode"])
            if st.session_state["payment_mode"] in payment_mode_options else 0,
            key="payment_mode"
        )

        invoice = st.text_input(
            "Invoice Number",
            value=st.session_state["invoice_number"],
            placeholder="e.g. INV-001",
            key="invoice_number"
        )

        destination = st.text_input(
            "Delivery Destination",
            value=st.session_state["delivery_destination"],
            placeholder="e.g. Nairobi",
            key="delivery_destination"
        )

        sales_date = st.date_input(
            "Sales Date",
            value=st.session_state["sales_date"],
            key="sales_date"
        )

    preview_records = st.form_submit_button("✅ Preview Sales Record")

# --- Post-submit logic ---
col1, col2 = st.columns(2)

with col1:
    if preview_records:
        if purchase_type == "Select..." or product_name == "Select..." or payment_mode == "Select...":
            st.warning("⚠️ Please select valid options for all dropdown fields.")
        else:
            st.success("✅ Sales Record preview generated!")
            sales_record = {
                "Customer Name": cust_name,
                "Customer Phone": cust_phone,
                "Purchase Type": purchase_type,
                "Product Name": product_name,
                "Quantity": quantity,
                "Price Amount": price_amount,
                "Payment Mode": payment_mode,
                "Invoice Number": invoice,
                "Delivery Destination": destination,
                "Sales Date": sales_date.strftime("%Y-%m-%d"),
            }
            st.json(sales_record)

with col2:
    if preview_records:
        sales_record_df = pd.DataFrame([{
            "Customer Name": cust_name,
            "Customer Phone": cust_phone,
            "Purchase Type": purchase_type,
            "Product Name": product_name,
            "Quantity": quantity,
            "Price Amount": price_amount,
            "Payment Mode": payment_mode,
            "Invoice Number": invoice,
            "Delivery Destination": destination,
            "Sales Date": sales_date.strftime("%Y-%m-%d"),
        }])
        st.dataframe(sales_record_df)

        save_sales = st.button("💾 Save Sales Record")
        if save_sales:
            # Save to Excel (or perform DB write, etc.)
            sales_record_df.to_excel("sales_record.xlsx", index=False)
            st.success("✅ Sales record saved successfully!")

            # --- Clear UI by assigning cleared/default values to session_state ---
            for k, v in DEFAULTS.items():
                st.session_state[k] = v

            # Force a rerun so inputs update to the cleared values
            st.experimental_rerun()
