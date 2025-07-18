import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- PAGE CONFIG ---
st.set_page_config(page_title="Access Request Viewer", layout="wide")
st.title("🔐 SG / US Access Viewer")

# --- GOOGLE SHEETS AUTH ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

# --- LOAD DATA ---
sheet = client.open("SG / US Access (Tickets)").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- RENAME COLUMNS FOR CLARITY ---
df.rename(columns={
    "\u7533\u8bf7\u4eba": "Requester",
    "Ticket Number": "Ticket Number",
    "Access First Date": "Access Start",
    "Access Last Date": "Access End",
    "Access Purpose": "Access Purpose",
    "Location": "Location",
    "Vendor Company Full Name": "Company",
    "Remarks / Loading bay details (exact day , timeframe)": "Remarks"
}, inplace=True)

# --- FILTER PANEL ---
st.sidebar.header("🔍 Filter Options")
requesters = sorted(df["Requester"].dropna().unique())
selected_requester = st.sidebar.selectbox("Select Requester (申请人)", requesters)

filtered_df = df[df["Requester"] == selected_requester]

# Optional: Filter by Company
companies = sorted(filtered_df["Company"].dropna().unique())
selected_company = st.sidebar.selectbox("Filter by Company (Vendor Company Full Name)", ["All"] + companies)
if selected_company != "All":
    filtered_df = filtered_df[filtered_df["Company"] == selected_company]

# Optional: Filter by Date Range
start_date = st.sidebar.date_input("Access Start Date From", value=None)
end_date = st.sidebar.date_input("Access End Date To", value=None)

if start_date:
    filtered_df = filtered_df[pd.to_datetime(filtered_df["Access Start"], errors='coerce') >= pd.to_datetime(start_date)]
if end_date:
    filtered_df = filtered_df[pd.to_datetime(filtered_df["Access End"], errors='coerce') <= pd.to_datetime(end_date)]

# --- DISPLAY DATA ---
st.success(f"Showing {len(filtered_df)} records for **{selected_requester}**")
st.dataframe(filtered_df[["Ticket Number", "Access Start", "Access End", "Access Purpose", "Location", "Company", "Remarks"]], use_container_width=True)

# --- DOWNLOAD OPTION ---
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name=f"access_requests_{selected_requester.replace(' ', '_')}.csv",
    mime="text/csv"
)
