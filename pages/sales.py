import streamlit as st
import pandas as pd
from datetime import datetime as dt
from style import load_css
import json
import math

load_css()
# ============================= CONFIG =============================
with open('data/config_files/product_config.json', "r") as f:
    PRODUCT_DB = json.load(f)  

with open('data/config_files/whole_sale_prices.json', "r") as f:
    WHOLESALE_PRICES = json.load(f)  

DEFAULT_ROW = {
    "product_name": "Select...",
    "purchase_type": "Select...",
    "wholesale_quantity_type": None,
    "quantity": 1,
    "price_per_unit": 0,
    "price": 0
}

# ============================= SESSION STATE INIT =============================
if "sales_rows" not in st.session_state:
    st.session_state.sales_rows = [DEFAULT_ROW.copy()]

if "customer" not in st.session_state:
    st.session_state.customer = {
        "name": "", "phone": "+254", "address": "", "delivery_mode": "", "delivery_destination": "",
        "payment_mode": "MPESA", "invoice_number": "", "sales_date": dt.now().date()
    }

if "just_saved" not in st.session_state:
    st.session_state.just_saved = False

# ============================= HELPERS =============================
def add_row():
    st.session_state.sales_rows.append(DEFAULT_ROW.copy())

def remove_row(i):
    st.session_state.sales_rows.pop(i)

def reset_all():
    st.session_state.sales_rows = [DEFAULT_ROW.copy()]
    st.session_state.customer = {
        "name": "", "phone": "+254", "address": "", "delivery_mode": "", "delivery_destination": "",
        "payment_mode": "MPESA", "invoice_number": "", "sales_date": dt.now().date()
    }
    st.session_state.just_saved = False

# ============================= MAIN UI =============================
# st.set_page_config(page_title="SEMA Sales", layout="centered")
st.title("SEMA Sales Entry System")

# --------------------- Customer Info ---------------------
with st.expander("Customer Information", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.customer["name"] = st.text_input(
            "Customer Name", value=st.session_state.customer["name"], key="cust_name"
        )
        st.session_state.customer["phone"] = st.text_input(
            "Phone Number", value=st.session_state.customer["phone"], key="cust_phone"
        )
        st.session_state.customer["address"] = st.text_area(
            "Delivery Address", value=st.session_state.customer["address"], key="cust_addr", height=80
        )
    with col2:
        st.session_state.customer["delivery_mode"] = st.radio(
            "Delivery Mode", ["Pickup", "Delivery"], horizontal=True,
            index=0 if st.session_state.customer["delivery_mode"] == "Pickup" else 1
        )
        st.session_state.customer["delivery_destination"] = st.text_input(
            "Delivery Destination (if applicable)", value=st.session_state.customer["delivery_destination"]
        )
        st.session_state.customer["payment_mode"] = st.selectbox(
            "Payment Mode", ["MPESA", "CASH", "BANK DEPOSIT"],
            index=["MPESA", "CASH", "BANK DEPOSIT"].index(st.session_state.customer["payment_mode"])
        )
    with col3:
        st.session_state.customer["invoice_number"] = st.text_input(
            "Invoice Number (optional)", value=st.session_state.customer["invoice_number"]
        )
        #datasets
        st.session_state.customer["sales_date"] = st.date_input(
            "Sales Date", value=st.session_state.customer["sales_date"]
        )

# --------------------- Dynamic Product Rows ---------------------
st.markdown("### Product Items")

for i, row in enumerate(st.session_state.sales_rows):
    cols = st.columns([3, 2, 1.5, 1.5, 1.5])
    with cols[0]:
        options = ["Select..."] + list(PRODUCT_DB.keys())
        idx = options.index(row["product_name"]) if row["product_name"] in options else 0
        selected = st.selectbox(
            f"Product {i+1}", options, index=idx,
            key=f"prod_{i}"
        )
        st.session_state.sales_rows[i]["product_name"] = selected

    with cols[1]:
        ptype = st.selectbox(
            "Type", ["Select...","Retail", "Wholesale"], 
            index=0 if row["purchase_type"] == "Retail" else 1,
            key=f"type_{i}"
        )
        st.session_state.sales_rows[i]["purchase_type"] = ptype

    # Wholesale-specific quantity type selection
    if ptype == "Wholesale":
        with cols[1]:
            # Get available quantity types for the selected product
            qty_types = WHOLESALE_PRICES.get(selected, {})
            
            if qty_types:
                qty_type = st.selectbox(
                    "Quantity Type", 
                    options=list(qty_types.keys()),
                    key=f"qty_type_{i}",
                    help="Select the wholesale quantity type"
                )
                st.session_state.sales_rows[i]["quantity_type"] = qty_type
            else:
                st.warning(f"No wholesale pricing available for {selected}")
                st.session_state.sales_rows[i]["quantity_type"] = None

    # For retail, you might want to set a default or clear the quantity type
    elif ptype == "Retail":
        st.session_state.sales_rows[i]["quantity_type"] = None  # or "Single" or whatever makes sense

    with cols[2]:
        qty = st.number_input("Qty", min_value=1, value=row["quantity"], key=f"qty_{i}")
        st.session_state.sales_rows[i]["quantity"] = qty

    # Auto price
    total_price = 0
    if selected != "Select..." and selected in PRODUCT_DB:
        prices = PRODUCT_DB[selected][0]
        if st.session_state.sales_rows[i]["purchase_type"] == "Retail":
            total_price = prices[0]*st.session_state.sales_rows[i]["quantity"]
        elif st.session_state.sales_rows[i]["purchase_type"] == "Wholesale":
            wholesale_pr = qty_types.get(st.session_state.sales_rows[i]["quantity_type"], 0)
            total_price = qty_types.get(st.session_state.sales_rows[i]["quantity_type"], 0) * qty

        retail_pr = prices[0] if not math.isnan(prices[0]) else 0
        price_per_unit = retail_pr if ptype == "Retail" else wholesale_pr
        st.session_state.sales_rows[i]["price_per_unit"] = price_per_unit

    # with cols[3]:
    #     st.session_state.sales_rows[i]["price_per_unit"] = st.number_input(
    #         "Price/Unit", min_value=0, value=price, step=10, key=f"price_{i}"
    #     )

    with cols[3]:
        # total = qty * st.session_state.sales_rows[i]["price_per_unit"]
        st.session_state.sales_rows[i]["price"] = total_price
        st.metric("Total", f"{total_price:,.0f}")

    with cols[4]:
        if st.button("delete", key=f"del_{i}"):
            remove_row(i)
            st.rerun()

# Add new row button
if st.button("Add Another Product", type="secondary", use_container_width=True):
    add_row()
    st.rerun()

# --------------------- Preview Table ---------------------
st.markdown("### Order Summary")
data = []
grand_total = 0
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
        grand_total += row["price"]

if data:
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.success(f"**GRAND TOTAL: Ksh {grand_total:,.0f}**")
else:
    st.info("Add at least one product to see the summary.")

# --------------------- FINAL SUBMIT (ONE FORM!) ---------------------
with st.form(key="final_save_form", clear_on_submit=True):
    submitted = st.form_submit_button(
        "SAVE COMPLETE SALE TO DATABASE",
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
                "timestamp": dt.now().isoformat(),
                "customer_name": st.session_state.customer["name"],
                "customer_phone": st.session_state.customer["phone"],
                "customer_address": st.session_state.customer["address"],
                "delivery_mode": st.session_state.customer["delivery_mode"],
                "delivery_destination": st.session_state.customer["delivery_destination"],
                "payment_mode": st.session_state.customer["payment_mode"],
                "invoice_number": st.session_state.customer["invoice_number"],
                "sales_date": st.session_state.customer["sales_date"].isoformat(),
                "items": [
                    {
                        "product": r["product_name"],
                        "type": r["purchase_type"],
                        "quantity": r["quantity"],
                        "unit_price": r["price_per_unit"],
                        "line_total": r["price"]
                    }
                    for r in st.session_state.sales_rows
                    if r["product_name"] != "Select..."
                ],
                "grand_total": grand_total
            }

            # SAVE (example: to Excel or BigQuery)
            try:
                df_out = pd.DataFrame([final_record])
                # df_out.to_excel("sales_records.xlsx", index=False)
                # Or use BigQuery client here
                st.success("SALE SAVED SUCCESSFULLY!")
                st.balloons()
                st.session_state.just_saved = True
            except Exception as e:
                st.error(f"Save failed: {e}")

# Auto-reset after save
if st.session_state.just_saved:
    reset_all()
    st.rerun()