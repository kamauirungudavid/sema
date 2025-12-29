from unicodedata import name
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

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Manufacturing Expense Capture", layout="wide")
# st.write("🏭 Expense Capture System")

# Initialize session state for different expense types
if 'raw_materials' not in st.session_state:
    st.session_state.raw_materials = []
if 'labor' not in st.session_state:
    st.session_state.labor = []
if 'overhead' not in st.session_state:
    st.session_state.overhead = []
if 'maintenance' not in st.session_state:
    st.session_state.maintenance = []

# Define different expense type schemas
RAW_MATERIALS_CATEGORIES = [
    "Baobab", "Sunflower", "Shea Nuts", 
    "Coconut", "Castor Beans", "Herbs",
]

LABOR_CATEGORIES = [
    "Packaging Labor", "Machine Operation", "Quality Inspection",
    "General Operations", "Engineering",  "Training"
]

OVERHEAD_CATEGORIES = [
    "Factory Rent", "Utilities", "Insurance", 
    "Property Tax", "Depreciation", "Security"
]

MAINTENANCE_CATEGORIES = [
    "Preventive Maintenance", "Repairs", "Spare Parts",
    "Calibration", "Tool Replacement", "Equipment Servicing"
]

# Main layout with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Raw Materials", "👷 Labor", "🏢 Overhead", 
    "🔧 Maintenance", "📊 Summary"
])

# --------------------------
# TAB 1: RAW MATERIALS
# --------------------------
with tab1:
    st.header("Raw Materials Purchase")
    
    with st.expander("➕ Add New Raw Material Purchase", expanded=True):
        with st.form("raw_materials_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Purchase Date", datetime.now(), key="rm_date")
                material_type = st.selectbox("Material Type", RAW_MATERIALS_CATEGORIES, key="rm_type")
                quantity = st.number_input("Quantity", min_value=0.0, step=0.01, key="rm_qty")
                unit = st.selectbox("Unit", ["kg", "lbs", "pieces", "liters", "meters", "rolls"], key="rm_unit")
            
            with col2:
                unit_price = st.number_input("Unit Price ($)", min_value=0.0, step=0.01, key="rm_price")
                vendor = st.text_input("Supplier/Vendor", key="rm_vendor")
                po_number = st.text_input("PO Number", key="rm_po")
                warehouse_location = st.selectbox("Storage Location", 
                                                 ["Main Warehouse", "Production Floor", "Tool Crib", "Chemical Storage"], 
                                                 key="rm_location")
            
            batch_number = st.text_input("Batch/Lot Number (Optional)", key="rm_batch")
            notes = st.text_area("Notes (Quality, Specifications, etc.)", key="rm_notes")
            
            submitted = st.form_submit_button("💾 Save Raw Material Purchase")
            
            if submitted and quantity > 0 and unit_price > 0:
                total_cost = quantity * unit_price
                
                raw_material = {
                    "id": f"RM-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "date": date.strftime("%Y-%m-%d"),
                    "material_type": material_type,
                    "quantity": quantity,
                    "unit": unit,
                    "unit_price": unit_price,
                    "total_cost": total_cost,
                    "vendor": vendor,
                    "po_number": po_number,
                    "warehouse_location": warehouse_location,
                    "batch_number": batch_number,
                    "notes": notes,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.raw_materials.append(raw_material)
                st.success(f"✅ Saved: {quantity} {unit} of {material_type} for ${total_cost:,.2f}")
    
    # Display raw materials table
    if st.session_state.raw_materials:
        st.subheader("Raw Materials Inventory")
        rm_df = pd.DataFrame(st.session_state.raw_materials)
        
        # Calculate totals
        total_qty = rm_df['quantity'].sum()
        total_value = rm_df['total_cost'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items", len(rm_df))
        col2.metric("Total Quantity", f"{total_qty:,.2f}")
        col3.metric("Total Value", f"${total_value:,.2f}")
        
        st.dataframe(
            rm_df[['date', 'material_type', 'quantity', 'unit', 'unit_price', 'total_cost', 'vendor']],
            use_container_width=True
        )

# --------------------------
# TAB 2: LABOR
# --------------------------
with tab2:
    st.header("Labor Costs")
    
    with st.expander("➕ Add Labor Entry", expanded=True):
        with st.form("labor_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Work Date", datetime.now(), key="lab_date")
                employee_id = st.text_input("Employee ID", key="lab_emp_id")
                employee_name = st.text_input("Employee Name", key="lab_name")
                labor_type = st.selectbox("Labor Type", LABOR_CATEGORIES, key="lab_type")
            
            with col2:
                hours_worked = st.number_input("Hours Worked", min_value=0.0, step=0.1, key="lab_hours")
                hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, step=0.01, key="lab_rate")
                department = st.selectbox("Department", 
                                         ["Production", "Assembly", "Quality", "Maintenance", 
                                          "Engineering", "R&D", "Administration"], 
                                         key="lab_dept")
                shift = st.selectbox("Shift", ["Day", "Night", "Weekend"], key="lab_shift")
            
            project_code = st.text_input("Project/Job Code (Optional)", key="lab_project")
            task_description = st.text_area("Task Description", key="lab_task")
            
            submitted = st.form_submit_button("💾 Save Labor Entry")
            
            if submitted and hours_worked > 0 and hourly_rate > 0:
                total_cost = hours_worked * hourly_rate
                
                labor_entry = {
                    "id": f"LAB-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "date": date.strftime("%Y-%m-%d"),
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "labor_type": labor_type,
                    "hours_worked": hours_worked,
                    "hourly_rate": hourly_rate,
                    "total_cost": total_cost,
                    "department": department,
                    "shift": shift,
                    "project_code": project_code,
                    "task_description": task_description,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.labor.append(labor_entry)
                st.success(f"✅ Saved: {hours_worked} hours for {employee_name} - ${total_cost:,.2f}")
    
    # Display labor table
    if st.session_state.labor:
        st.subheader("Labor Records")
        lab_df = pd.DataFrame(st.session_state.labor)
        
        # Calculate totals
        total_hours = lab_df['hours_worked'].sum()
        total_labor_cost = lab_df['total_cost'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Entries", len(lab_df))
        col2.metric("Total Hours", f"{total_hours:,.1f}")
        col3.metric("Total Labor Cost", f"${total_labor_cost:,.2f}")
        
        st.dataframe(
            lab_df[['date', 'employee_name', 'labor_type', 'hours_worked', 'hourly_rate', 'total_cost', 'department']],
            use_container_width=True
        )

# --------------------------
# TAB 3: OVERHEAD
# --------------------------
with tab3:
    st.header("Factory Overhead")
    
    with st.expander("➕ Add Overhead Expense", expanded=True):
        with st.form("overhead_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Expense Date", datetime.now(), key="oh_date")
                expense_type = st.selectbox("Expense Type", OVERHEAD_CATEGORIES, key="oh_type")
                amount = st.number_input("Amount ($)", min_value=0.0, step=0.01, key="oh_amount")
                payment_method = st.selectbox("Payment Method", 
                                            ["Credit Card", "Bank Transfer", "Check", "Cash"], 
                                            key="oh_payment")
            
            with col2:
                vendor = st.text_input("Vendor", key="oh_vendor")
                invoice_number = st.text_input("Invoice Number", key="oh_invoice")
                period = st.selectbox("Coverage Period", 
                                     ["Monthly", "Quarterly", "Annual", "One-time"], 
                                     key="oh_period")
                cost_center = st.selectbox("Cost Center", 
                                          ["Factory A", "Factory B", "Warehouse", "Admin Building"], 
                                          key="oh_center")
            
            description = st.text_area("Description", key="oh_desc")
            
            submitted = st.form_submit_button("💾 Save Overhead Expense")
            
            if submitted and amount > 0:
                overhead_entry = {
                    "id": f"OH-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "date": date.strftime("%Y-%m-%d"),
                    "expense_type": expense_type,
                    "amount": amount,
                    "payment_method": payment_method,
                    "vendor": vendor,
                    "invoice_number": invoice_number,
                    "period": period,
                    "cost_center": cost_center,
                    "description": description,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.overhead.append(overhead_entry)
                st.success(f"✅ Saved overhead expense: ${amount:,.2f} for {expense_type}")
    
    # Display overhead table
    if st.session_state.overhead:
        st.subheader("Overhead Expenses")
        oh_df = pd.DataFrame(st.session_state.overhead)
        total_overhead = oh_df['amount'].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Expenses", len(oh_df))
        col2.metric("Total Overhead", f"${total_overhead:,.2f}")
        
        st.dataframe(
            oh_df[['date', 'expense_type', 'amount', 'vendor', 'invoice_number', 'cost_center']],
            use_container_width=True
        )

# --------------------------
# TAB 4: MAINTENANCE
# --------------------------
with tab4:
    st.header("Maintenance & Repairs")
    
    with st.expander("➕ Add Maintenance Record", expanded=True):
        with st.form("maintenance_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Service Date", datetime.now(), key="maint_date")
                maintenance_type = st.selectbox("Type", MAINTENANCE_CATEGORIES, key="maint_type")
                equipment_id = st.text_input("Equipment ID", key="maint_equip")
                equipment_name = st.text_input("Equipment Name", key="maint_name")
            
            with col2:
                cost = st.number_input("Cost ($)", min_value=0.0, step=0.01, key="maint_cost")
                service_provider = st.selectbox("Service By", 
                                               ["Internal Team", "External Vendor", "Contractor"], 
                                               key="maint_provider")
                downtime_hours = st.number_input("Downtime (hours)", min_value=0.0, step=0.1, key="maint_downtime")
                priority = st.selectbox("Priority", ["Routine", "Urgent", "Emergency"], key="maint_priority")
            
            vendor_name = st.text_input("Vendor Name (if external)", key="maint_vendor")
            description = st.text_area("Work Description", key="maint_desc")
            parts_used = st.text_area("Parts/Spares Used", key="maint_parts")
            
            submitted = st.form_submit_button("💾 Save Maintenance Record")
            
            if submitted and cost >= 0:
                maintenance_entry = {
                    "id": f"MAINT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "date": date.strftime("%Y-%m-%d"),
                    "maintenance_type": maintenance_type,
                    "equipment_id": equipment_id,
                    "equipment_name": equipment_name,
                    "cost": cost,
                    "service_provider": service_provider,
                    "vendor_name": vendor_name,
                    "downtime_hours": downtime_hours,
                    "priority": priority,
                    "description": description,
                    "parts_used": parts_used,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.maintenance.append(maintenance_entry)
                st.success(f"✅ Saved maintenance record for {equipment_name} - ${cost:,.2f}")
    
    # Display maintenance table
    if st.session_state.maintenance:
        st.subheader("Maintenance Records")
        maint_df = pd.DataFrame(st.session_state.maintenance)
        total_maintenance = maint_df['cost'].sum()
        total_downtime = maint_df['downtime_hours'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(maint_df))
        col2.metric("Total Maintenance Cost", f"${total_maintenance:,.2f}")
        col3.metric("Total Downtime", f"{total_downtime:,.1f} hours")
        
        st.dataframe(
            maint_df[['date', 'equipment_name', 'maintenance_type', 'cost', 'service_provider', 'priority', 'downtime_hours']],
            use_container_width=True
        )

# --------------------------
# TAB 5: SUMMARY & EXPORT
# --------------------------
with tab5:
    st.header("📊 Expense Summary")
    
    # Calculate totals
    total_raw_materials = sum(item['total_cost'] for item in st.session_state.raw_materials)
    total_labor = sum(item['total_cost'] for item in st.session_state.labor)
    total_overhead = sum(item['amount'] for item in st.session_state.overhead)
    total_maintenance = sum(item['cost'] for item in st.session_state.maintenance)
    
    grand_total = total_raw_materials + total_labor + total_overhead + total_maintenance
    
    # Display summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Raw Materials", f"${total_raw_materials:,.2f}", 
                 f"{len(st.session_state.raw_materials)} items")
    
    with col2:
        st.metric("Labor", f"${total_labor:,.2f}", 
                 f"{len(st.session_state.labor)} entries")
    
    with col3:
        st.metric("Overhead", f"${total_overhead:,.2f}", 
                 f"{len(st.session_state.overhead)} expenses")
    
    with col4:
        st.metric("Maintenance", f"${total_maintenance:,.2f}", 
                 f"{len(st.session_state.maintenance)} records")
    
    with col5:
        st.metric("Grand Total", f"${grand_total:,.2f}")
    
    st.markdown("---")
    
    # Export Section
    st.subheader("📤 Export Data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.raw_materials:
            rm_df = pd.DataFrame(st.session_state.raw_materials)
            csv_rm = rm_df.to_csv(index=False)
            st.download_button(
                label="📥 Raw Materials CSV",
                data=csv_rm,
                file_name=f"raw_materials_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.session_state.labor:
            lab_df = pd.DataFrame(st.session_state.labor)
            csv_lab = lab_df.to_csv(index=False)
            st.download_button(
                label="📥 Labor CSV",
                data=csv_lab,
                file_name=f"labor_costs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.session_state.overhead:
            oh_df = pd.DataFrame(st.session_state.overhead)
            csv_oh = oh_df.to_csv(index=False)
            st.download_button(
                label="📥 Overhead CSV",
                data=csv_oh,
                file_name=f"overhead_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col4:
        if st.session_state.maintenance:
            maint_df = pd.DataFrame(st.session_state.maintenance)
            csv_maint = maint_df.to_csv(index=False)
            st.download_button(
                label="📥 Maintenance CSV",
                data=csv_maint,
                file_name=f"maintenance_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Combined export
    st.markdown("---")
    if st.button("📊 Export All Data to Excel (Multiple Sheets)"):
        from io import BytesIO
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if st.session_state.raw_materials:
                pd.DataFrame(st.session_state.raw_materials).to_excel(writer, sheet_name='Raw Materials', index=False)
            if st.session_state.labor:
                pd.DataFrame(st.session_state.labor).to_excel(writer, sheet_name='Labor', index=False)
            if st.session_state.overhead:
                pd.DataFrame(st.session_state.overhead).to_excel(writer, sheet_name='Overhead', index=False)
            if st.session_state.maintenance:
                pd.DataFrame(st.session_state.maintenance).to_excel(writer, sheet_name='Maintenance', index=False)
        
        st.download_button(
            label="📥 Download Excel File",
            data=output.getvalue(),
            file_name=f"manufacturing_expenses_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Clear all data
    st.markdown("---")
    st.subheader("🔄 Data Management")
    
    if st.button("🗑️ Clear All Data"):
        if st.checkbox("Confirm: This will delete ALL expense records"):
            st.session_state.raw_materials = []
            st.session_state.labor = []
            st.session_state.overhead = []
            st.session_state.maintenance = []
            st.success("All data cleared!")
            st.rerun()

# Sidebar instructions
with st.sidebar:
    st.markdown("### 📋 How to Use")
    st.markdown("""
    **Separate Expense Tracking:**
    1. **Raw Materials**: Track material purchases
    2. **Labor**: Record employee hours & costs  
    3. **Overhead**: Factory operating expenses
    4. **Maintenance**: Equipment servicing & repairs
    
    **Each tab:**
    - Has its own unique form
    - Stores data separately
    - Can be exported independently
    - Maintains different data structure
    """)
    
    # Quick stats in sidebar
    st.markdown("### 📈 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("RM Items", len(st.session_state.raw_materials))
        st.metric("Labor Entries", len(st.session_state.labor))
    with col2:
        st.metric("OH Expenses", len(st.session_state.overhead))
        st.metric("Maint Records", len(st.session_state.maintenance))