import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- Google Auth Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

# --- Open your Google Sheet ---
spreadsheet = client.open("Access Control Sheet")  # or use .open_by_key(sheet_id)
worksheet = spreadsheet.sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

st.dataframe(df)
