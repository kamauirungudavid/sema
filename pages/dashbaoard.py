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