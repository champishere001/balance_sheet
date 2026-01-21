import streamlit as st
import pandas as pd
import numpy as np
import re

# ================= CONFIG =================
st.set_page_config(page_title="ASI Intelligent Audit Engine", layout="wide")

# ================= CORE UTILITIES =================
def robust_numeric_cleaner(series):
    def clean_value(val):
        if pd.isna(val) or val == "": return 0.0
        s = str(val).strip().lower()
        is_negative = False
        if "(" in s and ")" in s: is_negative = True
        s = re.sub(r'[^-0-9.]', '', s)
        try:
            num = float(s) if s else 0.0
            return -num if is_negative else num
        except: return 0.0
    return series.apply(clean_value)

def clean_df(df):
    df = df.dropna(how="all")
    # Ensuring we don't skip data rows while removing grand totals
    if not df.empty:
        df.columns = [str(c).strip() for c in df.columns]
    return df

# ================= MAIN APP =================
st.title("🛡️ ASI Intelligent Audit & Cross-Check Engine")

uploaded_files = st.file_uploader("Upload Excel Files", type=["xlsx", "xls"], accept_multiple_files=True)

if uploaded_files:
    all_summaries = {}
    
    for file in uploaded_files:
        df = pd.read_excel(file)
        df = clean_df(df)
        
        # 1. Map Columns
        cols = df.columns.tolist()
        dr_col = next((c for c in cols if "debit" in c.lower() or c.lower().endswith("dr")), None)
        cr_col = next((c for c in cols if "credit" in c.lower() or c.lower().endswith("cr")), None)
        desc_col = next((c for c in cols if any(k in c.lower() for k in ["desc", "particulars", "account"])), cols[0])
        
        # 2. Clean Numeric Data
        if dr_col: df[dr_col] = robust_numeric_cleaner(df[dr_col])
        if cr_col: df[cr_col] = robust_numeric_cleaner(df[cr_col])
        
        # 3. Spatial Consistency Check (Your Custom Requirement)
        # If coordinates exist, ensure height/elevation is present
        lat_col = next((c for c in cols if "lat" in c.lower()), None)
        lon_col = next((c for c in cols if "lon" in c.lower()), None)
        height_col = next((c for c in cols if any(k in c.lower() for k in ["height", "elev", "floor"])), None)

        if lat_col and lon_col and not height_col:
            st.warning(f"🚩 **Audit Alert ({file.name}):** Latitude/Longitude detected without a corresponding Height/Floor column. Adjusting coordinates requires height verification.")

        # 4. Totals for Reconciliation
        total_dr = df[dr_col].sum() if dr_col else 0
        total_cr = df[cr_col].sum() if cr_col else 0
        
        all_summaries[file.name] = {"df": df, "dr": total_dr, "cr": total_cr}

        with st.expander(f"Analysis: {file.name}"):
            st.write(f"**Total Debits:** ₹{total_dr:,.2f} | **Total Credits:** ₹{total_cr:,.2f}")
            if abs(total_dr - total_cr) < 0.01:
                st.success("Reconciled: All entries account for the final result.")
            else:
                st.error(f"Mismatch: ₹{abs(total_dr - total_cr):,.2f}")
            st.dataframe(df)

    # 5. Financial Summary (The Fix for the Error)
    if all_summaries:
        st.divider()
        st.header("📊 Financial Performance")
        target = st.selectbox("Select file for P&L View", list(all_summaries.keys()))
        data = all_summaries[target]
        
        # Using a simple Bar Chart instead of Pie Chart to avoid library version errors
        pl_summary = pd.DataFrame({
            "Metric": ["Total Debits", "Total Credits"],
            "Amount": [data["dr"], data["cr"]]
        })
        st.bar_chart(pl_summary.set_index("Metric"))
