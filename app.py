import streamlit as st
import pandas as pd
import numpy as np
import re

# ================= CONFIG & STYLING =================
st.set_page_config(page_title="ASI Intelligent Audit Engine", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ ASI Intelligent Audit & Cross-Check Engine")

# ================= CORE UTILITIES =================
def robust_numeric_cleaner(series):
    """Converts messy accounting strings to precise floats."""
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
    """Strips empty rows/cols and prepares headers."""
    df = df.dropna(how="all")
    if not df.empty:
        df.columns = [str(c).strip() for c in df.columns]
    return df

def detect_columns(df):
    """Maps financial and spatial columns while avoiding truth-value ambiguity."""
    debit, credit, desc = [], [], None
    lat, lon, height = None, None, None
    
    for c in df.columns:
        cl = str(c).lower()
        if "debit" in cl or cl.endswith("dr"): debit.append(c)
        elif "credit" in cl or cl.endswith("cr"): credit.append(c)
        elif any(k in cl for k in ["desc", "particulars", "account", "ledger"]): desc = c
        
        # Spatial detection (Instruction: Height check for Lat/Lon)
        if "lat" in cl: lat = c
        elif "lon" in cl: lon = c
        elif any(k in cl for k in ["height", "elev", "floor"]): height = c
        
    return debit, credit, desc or df.columns[0], lat, lon, height

def classify(desc):
    """Categorizes accounts for automated P&L matching."""
    d = str(desc).lower()
    if any(k in d for k in ["capital", "reserve", "loan", "creditor", "payable"]): return "Liability"
    if any(k in d for k in ["asset", "plant", "machinery", "building", "cash", "bank", "debtor"]): return "Asset"
    if any(k in d for k in ["salary", "wage", "expense", "purchase", "rent", "consumption"]): return "Expense"
    if any(k in d for k in ["sales", "turnover", "income", "revenue"]): return "Income"
    return "Other"

# ================= MAIN ENGINE =================
uploaded_files = st.file_uploader(
    "Upload Trial Balance / Audit Sheets (Excel)", 
    type=["xlsx", "xls"], 
    accept_multiple_files=True
)

if uploaded_files:
    all_data = {}
    
    for file in uploaded_files:
        try:
            df_raw = pd.read_excel(file)
            df = clean_df(df_raw)
            dr_cols, cr_cols, desc_col, lat_c, lon_c, h_c = detect_columns(df)

            # 1. Clean All Data in Sheets
            for col in dr_cols + cr_cols:
                df[col] = robust_numeric_cleaner(df[col])

            df["Debit"] = df[dr_cols].sum(axis=1) if dr_cols else 0
            df["Credit"] = df[cr_cols].sum(axis=1) if cr_cols else 0
            df["Category"] = df[desc_col].apply(classify)
            df["Net_Amount"] = df["Debit"] - df["Credit"]

            all_data[file.name] = {
                "df": df, 
                "total_dr": df["Debit"].sum(), 
                "total_cr": df["Credit"].sum(),
                "desc_col": desc_col,
                "spatial": (lat_c, lon_c, h_c)
            }

            # 2. P&L Matching Logic
            income = abs(df[df["Category"] == "Income"]["Net_Amount"].sum())
            expense = df[df["Category"] == "Expense"]["Net_Amount"].sum()
            net_profit = income - expense

            # 3. UI Display with Matching Status
            with st.expander(f"📁 Audit & P&L Reconciliation: {file.name}"):
                tb_diff = round(all_data[file.name]["total_dr"] - all_data[file.name]["total_cr"], 2)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Net Profit / (Loss)", f"₹{net_profit:,.2f}")
                
                # Trial Balance Status
                if abs(tb_diff) < 1:
                    c2.success("TB MATCHED ✅")
                else:
                    c2.error(f"TB MISMATCH: ₹{tb_diff:,.2f}")

                # Spatial Audit Check
                if lat_c and lon_c:
                    if h_c:
                        st.info(f"📍 Height ({h_c}) verified for spatial adjustment.")
                    else:
                        st.warning("⚠️ Spatial Warning: Height missing for coordinate adjustment.")

                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Processing error in {file.name}: {e}")

    # ================= CONSOLIDATED FINANCIAL MATCHING =================
    if all_data:
        st.divider()
        st.header("📊 Final Profit & Loss vs. Balance Sheet Match")
        
        target = st.selectbox("Select File to Match", list(all_data.keys()))
        t_df = all_data[target]["df"]
        
        # Breakdown calculation
        p_l_summary = t_df.groupby("Category")["Net_Amount"].sum().reset_index()
        
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("Category-wise Net Movement")
            st.table(p_l_summary)
        
        with col_r:
            st.subheader("P&L Performance")
            # Using Bar Chart for maximum compatibility
            st.bar_chart(p_l_summary.set_index("Category"))

else:
    st.info("👋 System Ready. Upload files to verify TB and P&L matching.")
