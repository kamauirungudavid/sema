import pandas as pd
import streamlit as st
from google.cloud import bigquery
import pandas as pd

# Load credentials
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)
# import plotly.express as px
# from data.get_data import get_data
# from modules.login import login



st.set_page_config(page_title="Access Control Demo", layout="wide")


####### APP STYLE #########
# Load CSS function
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="🚗 VEHICLE PARTICULARS FORM", page_icon="🌟", layout="wide")
local_css("style.css")

col_logo, col_title = st.columns([1,4])
# with col_logo:
#     st.image("logo/logo.png", width=80)  # your logo file

# Define your pages. Use the path to your page files.
pages = [
    st.Page("pages/sales.py", title="SALES", icon="📋"),
    st.Page("pages/manufacturing.py", title="MANUFACTURING", icon="📌"),
    st.Page("pages/dashbaoard.py", title="DASHBOARD", icon="🙋‍♂️"),
    
   
    # st.Page("pages/treasury.py", title="Treasury", icon="💰"),
    # st.Page("pages/reinsurance.py", title="REO", icon="⚖"),
    # st.Page("pages/business_partnering.py", title="Finance Business Partnering", icon="🤝"),
]

# Create the navigation menu
selected_page = st.navigation(pages)

# Run the selected page
selected_page.run()