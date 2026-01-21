import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Autonomous ASI Auditor", layout="wide")
st.title("🛡️ Smart-Header ASI Scrutiny Portal")

# --- VITAL CONFIGURATION ---
VITAL_KEYWORDS = ["description", "account", "amount", "debit", "credit", "24-25", "total"]

def find_header_row(df):
    """Scans the top of a file to find where the actual table headers start."""
    for i in range(min(len(df), 20)):  # Check first 20 rows
        row_values = [str(val).lower() for val in df.iloc[i].values]
        # Count how many vital keywords are in this row
        matches = sum(1 for word in VITAL_KEYWORDS if any(word in cell for cell in row_values))
        if matches >= 2:  # If row contains 2 or more keywords, it's likely the header
            return i
    return 0

def process_file_smartly(file):
    """Reads file and auto-adjusts the header position."""
    if file.name.endswith('.csv'):
        # Read as raw initially to find header
        raw_df = pd.read_csv(file, header=None)
        header_idx = find_header_row(raw_df)
        file.seek(0) # Reset file pointer
        df = pd.read_csv(file, skiprows=header_idx)
    else:
        # Excel Multi-sheet logic
        xl = pd.ExcelFile(file)
        all_sheets = []
        for name in xl.sheet_names:
            raw_df = pd.read_excel(file, sheet_name=name, header=None)
            header_idx = find_header_row(raw_df)
            df = pd.read_excel(file, sheet_name=name, skiprows=header_idx)
            df['SheetSource'] = name
            all_sheets.append(df)
        return pd.concat(all_sheets, ignore_index=True) if all_sheets else pd.DataFrame()
    return df

# --- UI INTERFACE ---
uploaded_files = st.file_uploader("Upload ASI Files (Any format/alignment)", accept_multiple_files=True)

if uploaded_files:
    master_vitals = []
    
    for f in uploaded_files:
        with st.spinner(f"Smart-scanning {f.name}..."):
            df = process_file_smartly(f)
            
            # Now that we have a clean DF, find the data
            cols = [str(c).lower() for c in df.columns]
            
            res = {"File": f.name}
            # Example: Smart-finding Total Assets
            asset_matches = [c for c in df.columns if '24-25' in str(c) or 'amount' in str(c).lower()]
            if asset_matches:
                # Assuming the last row or a row containing 'Total' is the vital cell
                res["Total Value Found"] = pd.to_numeric(df[asset_matches[-1]], errors='coerce').sum()
            
            master_vitals.append(res)

    # Display Results
    st.subheader("📋 Smart-Extracted Check Table")
    summary_df = pd.DataFrame(master_vitals)
    st.dataframe(summary_df, use_container_width=True)
    
    # Download Button
    st.download_button("📥 Download Autonomous CSV", summary_df.to_csv(index=False), "Smart_Audit.csv")
