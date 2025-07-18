import streamlit as st
import pandas as pd

# --- SETTINGS ---
st.set_page_config(page_title="Access Request Viewer", layout="wide")
st.title("🔐 Access Request Viewer")

# --- DATA LOAD ---
@st.cache_data

def load_data():
    # Replace with your Google Sheet URL or upload CSV
    # For Google Sheets: use the export link format
    # Example: 'https://docs.google.com/spreadsheets/d/<sheet_id>/export?format=csv'
    url = st.secrets.get("sheet_csv_url", "")
    if not url:
        st.warning("Please configure your Google Sheet CSV URL in Streamlit secrets.")
        return pd.DataFrame()
    return pd.read_csv(url)

# Alternatively, allow file upload
uploaded_file = st.file_uploader("Upload CSV file of access requests", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = load_data()

if df.empty:
    st.stop()

# --- MAIN FILTERING ---
# Rename columns for readability if necessary
rename_cols = {
    "申请人": "Requester Name",
    "Ticket Number": "Ticket Number",
    "Access Purpose": "Access Purpose",
    "Location": "Location",
    "Access First Date": "Access Start",
    "Access Last Date": "Access End"
    # Add more as needed
}
df.rename(columns=rename_cols, inplace=True)

# Get unique requesters
requesters = sorted(df["Requester Name"].dropna().unique())
selected_requester = st.selectbox("Select Requester", requesters)

filtered_df = df[df["Requester Name"] == selected_requester]

st.success(f"Showing {len(filtered_df)} records for **{selected_requester}**")
st.dataframe(filtered_df, use_container_width=True)

# --- OPTIONAL EXPORT ---
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name=f"access_requests_{selected_requester.replace(' ', '_')}.csv",
    mime="text/csv"
)

# --- OPTIONAL SEARCH ---
with st.expander("🔎 Search & Filter Options"):
    search_term = st.text_input("Search in Ticket Number or Purpose")
    if search_term:
        result = filtered_df[
            filtered_df["Ticket Number"].astype(str).str.contains(search_term, case=False) |
            filtered_df["Access Purpose"].astype(str).str.contains(search_term, case=False)
        ]
        st.write(f"Found {len(result)} matching records:")
        st.dataframe(result, use_container_width=True)
