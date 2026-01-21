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
    """Ensures accounting formats (₹, commas, parentheses) are converted to floats."""
    def clean_value(val):
        if pd.isna(val) or val == "": return 0.0
        s = str(val).strip().lower()
        is_negative = False
        # Handle (1,234.56) accounting format as negative
        if "(" in s and ")" in s: is_negative = True
        # Strip all but numbers, decimals, and minus signs
        s = re.sub(r'[^-0-9.]', '', s)
        try:
            num = float(s) if s else 0.0
            return -num if is_negative else num
        except: return 0.0
    return series.apply(clean_value)

def clean_df(df):
    """Removes empty rows and handles basic structural cleanup."""
    df = df.dropna(how="all")
    if not df.empty:
        df.columns = [str(c).strip() for c in df.columns]
    return df

def detect_columns(df):
    """Automatically maps financial and spatial columns."""
    debit, credit, desc = [], [], None
    lat, lon, height = None, None, None
    
    for c in df.columns:
        cl = c.lower()
        # Financial detection
        if "debit" in cl or cl.endswith("dr"): debit.append(c)
        elif "credit" in cl or cl.endswith("cr"): credit.append(c)
        elif any(k in cl for k in ["desc", "particulars", "account", "ledger"]): desc = c
        
        # Spatial detection (User Requirement)
        if "lat" in cl: lat = c
        elif "lon" in cl: lon = c
        elif any(k in cl for k in ["height", "elev", "floor"]): height = c
        
    return debit, credit, desc or df.columns[0], lat, lon, height

def classify(desc):
    """Categorizes accounts based on common accounting terminology."""
    d = str(desc).lower()
    if any(k in d for k in ["capital", "reserve", "loan", "creditor", "payable", "provision"]): return "Liability"
    if any(k in d for k in ["asset", "plant", "machinery", "building", "cash", "bank", "receivable", "debtor"]): return "Asset"
    if any(k in d for k in ["salary", "wage", "expense", "purchase", "rent", "tax"]): return "Expense"
    if any(k in d for k in ["sales", "turnover", "income", "revenue", "gain"]): return "Income"
    return "Other"

# ================= FILE UPLOADER =================
uploaded_files = st.file_uploader(
    "Upload Trial Balance / Spatial Audit Sheets (Excel)", 
    type=["xlsx", "xls"], 
    accept_multiple_files=True
)

if uploaded_files:
    all_data = {}
    
    for file in uploaded_files:
        try:
            # 1. Load Data
            df = pd.read_excel(file)
            df = clean_df(df)
            dr_cols, cr_cols, desc_col, lat_c, lon_c, h_c = detect_columns(df)

            # 2. Financial Cleaning & Calculation
            for col in dr_cols + cr_cols:
                df[col] = robust_numeric_cleaner(df[col])

            df["Debit"] = df[dr_cols].sum(axis=1) if dr_cols else 0
            df["Credit"] = df[cr_cols].sum(axis=1) if cr_cols else 0
            df["Category"] = df[desc_col].apply(classify)
            df["Net Amount"] = df["Debit"] - df["Credit"]

            all_data[file.name] = {
                "df": df, 
                "total_dr": df["Debit"].sum(), 
                "total_cr": df["Credit"].sum(),
                "spatial": (lat_c, lon_c, h_c)
            }

            # 3. Individual Reconciliation & Spatial Audit
            with st.expander(f"📁 Audit Details: {file.name}"):
                # Financial Check
                diff = round(all_data[file.name]["total_dr"] - all_data[file.name]["total_cr"], 2)
                c1, c2, c3 = st.columns(3)
                c1.metric("Debits", f"₹{all_data[file.name]['total_dr']:,.2f}")
                c2.metric("Credits", f"₹{all_data[file.name]['total_cr']:,.2f}")
                
                if abs(diff) < 0.01:
                    c3.success("RECONCILED ✅")
                else:
                    c3.error(f"MISMATCH: ₹{diff:,.2f}")

                # Spatial Check (Requirement: Height must adjust with Lat/Lon)
                if lat_c and lon_c:
                    if h_c:
                        st.info(f"📍 Spatial data detected. Height ({h_c}) is included for coordinate adjustment.")
                    else:
                        st.warning("⚠️ Spatial Alert: Lat/Lon detected without Height. Coordinates cannot be fully adjusted.")

                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")

    # ================= CONSOLIDATED INTELLIGENCE =================
    if all_data:
        st.divider()
        st.header("📊 Financial Performance & Working Capital")
        
        target = st.selectbox("Select entity for deep-dive", list(all_data.keys()))
        target_df = all_data[target]["df"]
        
        # P&L and Working Capital Logic
        inc = abs(target_df[target_df["Category"] == "Income"]["Net Amount"].sum())
        exp = target_df[target_df["Category"] == "Expense"]["Net Amount"].sum()
        ca = target_df[(target_df["Category"] == "Asset") & (target_df[desc_col].str.contains("Cash|Bank|Receivable|Stock", case=False, na=False))]["Net Amount"].sum()
        cl = abs(target_df[(target_df["Category"] == "Liability") & (target_df[desc_col].str.contains("Payable|Creditor|Loan", case=False, na=False))]["Net Amount"].sum())
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Net Profit/Loss", f"₹{inc - exp:,.2f}")
        col_m2.metric("Working Capital", f"₹{ca - cl:,.2f}")
        col_m3.metric("Current Ratio", f"{ca/cl:.2f}" if cl != 0 else "N/A")

        # Stable Visualizations (Avoiding st.pie_chart for compatibility)
        st.subheader("Account Category Distribution")
        cat_data = target_df.groupby("Category")[["Debit", "Credit"]].sum()
        st.bar_chart(cat_data)

else:
    st.info("👋 Ready for audit. Please upload your Excel sheets to proceed.")
