import streamlit as st
import pandas as pd
import io
import re
from fuzzywuzzy import process

st.set_page_config(page_title="ASI Audit Pro", layout="wide")
st.title("🛡️ ASI Master Scrutiny & Analysis Engine")

# --- 1. INTELLIGENT CONFIGURATION ---
# The tool uses these to find data no matter which row it starts on
VITAL_COLUMNS = ["description", "nsso", "amount", "value", "24-25", "total", "category"]
AUDIT_TARGETS = {
    "Total Assets": ["fixed assets", "total assets", "closing dr", "balance sheet total"],
    "Total Wages": ["wages", "salaries", "employee benefits", "manpower cost"],
    "Turnover": ["sales", "revenue", "turnover", "dispatched value"],
    "Raw Material": ["consumption", "rm consumed", "material cost"]
}

# --- 2. THE "SMART" EXTRACTION CORE ---
def smart_load(file):
    """Detects headers and converts any file to a clean Audit-Ready CSV"""
    if file.name.endswith('.csv'):
        raw = pd.read_csv(file, header=None)
    else:
        raw = pd.read_excel(file, header=None)
    
    # Header Hunting Logic
    header_idx = 0
    for i in range(min(len(raw), 25)):
        row = [str(x).lower() for x in raw.iloc[i].values]
        matches = sum(1 for k in VITAL_COLUMNS if any(k in cell for cell in row))
        if matches >= 2:
            header_idx = i
            break
            
    file.seek(0)
    df = pd.read_csv(file, skiprows=header_idx) if file.name.endswith('.csv') else pd.read_excel(file, skiprows=header_idx)
    return df, header_idx

def extract_metric(df, target_key):
    """Fuzzy searches for a metric and extracts its value"""
    full_text = " ".join(df.columns.astype(str)).lower()
    # Find column name that matches our keywords
    potential_cols = []
    for kw in AUDIT_TARGETS[target_key]:
        matches = [c for c in df.columns if kw in str(c).lower()]
        potential_cols.extend(matches)
    
    if potential_cols:
        target_col = potential_cols[0]
        # Summing numeric values (cleaning strings like 'Rs.' or ',' first)
        clean_values = pd.to_numeric(df[target_col].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
        return clean_values.sum()
    return 0

# --- 3. UI & UPLOAD HUB ---
st.sidebar.header("📁 Data Input")
uploaded_files = st.file_uploader("Upload all ASI Schedules (FTO 8, Manpower, Consumption)", 
                                  accept_multiple_files=True)

if uploaded_files:
    all_summary = []
    
    for f in uploaded_files:
        with st.status(f"Scanning {f.name}...") as status:
            df, row_found = smart_load(f)
            
            # Identify what kind of file this is
            file_vitals = {"File": f.name, "Header_Row": row_found + 1}
            for target in AUDIT_TARGETS:
                val = extract_metric(df, target)
                if val > 0:
                    file_vitals[target] = val
            
            all_summary.append(file_vitals)
            status.update(label=f"Verified {f.name}", state="complete")

    # --- 4. THE ANALYTICS DASHBOARD ---
    st.header("📊 Scrutiny Dashboard")
    master_df = pd.DataFrame(all_summary).fillna(0)
    st.dataframe(master_df, use_container_width=True)

    # Cross-Verification Logic
    st.subheader("🔍 Intelligent Cross-Check")
    col1, col2 = st.columns(2)
    
    with col1:
        # Comparison: Wages in Trial Balance vs Manpower Report
        total_wages = master_df["Total Wages"].sum()
        st.metric("Consolidated Wages", f"₹{total_wages:,.2f}")
        if total_wages == 0:
            st.error("⚠️ Wages not detected in any file. Check 'Manpower' headers.")

    with col2:
        total_sales = master_df["Turnover"].sum()
        st.metric("Total Turnover", f"₹{total_sales:,.2f}")

    # --- 5. DATA EXPORT ---
    st.divider()
    csv_out = master_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Audit-Ready CSV", csv_out, "ASI_Consolidated_Audit.csv", "text/csv")
