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
    .status-box { padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ ASI Intelligent Audit & Cross-Check Engine")

# ================= CORE UTILITIES =================
def robust_numeric_cleaner(series):
    """Bulletproof conversion of accounting strings to floats."""
    def clean_value(val):
        if pd.isna(val) or val == "": return 0.0
        s = str(val).strip().lower()
        is_negative = False
        # Handle (1,234.56) accounting format
        if "(" in s and ")" in s: is_negative = True
        # Remove ₹, $, commas, and spaces
        s = re.sub(r'[^-0-9.]', '', s)
        try:
            num = float(s) if s else 0.0
            return -num if is_negative else num
        except: return 0.0
    return series.apply(clean_value)

def fix_duplicate_columns(df):
    cols, counter = [], {}
    for c in df.columns:
        if c in counter:
            counter[c] += 1
            cols.append(f"{c}_{counter[c]}")
        else:
            counter[c] = 0
            cols.append(c)
    df.columns = cols
    return df

def clean_df(df):
    """Initial structural cleanup."""
    # Remove rows that are completely empty
    df = df.dropna(how="all")
    # Identify and remove 'Total' rows to prevent double counting
    if not df.empty:
        first_col = df.columns[0]
        df = df[~df[first_col].astype(str).str.contains("total|sum|balance c/f", case=False, na=False)]
    df.columns = [str(c).strip() for c in df.columns]
    return fix_duplicate_columns(df)

def detect_columns(df):
    debit, credit, desc = [], [], None
    for c in df.columns:
        cl = c.lower()
        if "debit" in cl or cl.endswith("dr"): debit.append(c)
        elif "credit" in cl or cl.endswith("cr"): credit.append(c)
        elif any(k in cl for k in ["desc", "particulars", "account", "ledger"]): desc = c
    return debit, credit, desc or df.columns[0]

def classify(desc):
    d = str(desc).lower()
    if any(k in d for k in ["capital", "reserve", "loan", "creditor", "payable", "provision"]): return "Liability"
    if any(k in d for k in ["asset", "plant", "machinery", "building", "cash", "bank", "receivable", "debtor"]): return "Asset"
    if any(k in d for k in ["salary", "wage", "expense", "purchase", "rent", "tax"]): return "Expense"
    if any(k in d for k in ["sales", "turnover", "income", "revenue", "gain"]): return "Income"
    return "Other"

# ================= FILE UPLOADER =================
uploaded_files = st.file_uploader(
    "Upload Trial Balance Excel Files (Multi-file enabled)",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    all_summaries = {}
    
    for file in uploaded_files:
        try:
            # 1. Load and Structure
            df_raw = pd.read_excel(file)
            df = clean_df(df_raw)
            dr_cols, cr_cols, desc_col = detect_columns(df)

            # 2. Robust Numeric Conversion (Ensures cross-check accuracy)
            for col in dr_cols + cr_cols:
                df[col] = robust_numeric_cleaner(df[col])

            # 3. Calculation Logic
            df["Debit"] = df[dr_cols].sum(axis=1) if dr_cols else 0
            df["Credit"] = df[cr_cols].sum(axis=1) if cr_cols else 0
            df["Category"] = df[desc_col].apply(classify)
            df["Net Amount"] = df["Debit"] - df["Credit"]

            all_summaries[file.name] = df

            # 4. Individual File Reconciliation Check
            with st.expander(f"📄 Audit Log: {file.name}"):
                total_dr = df["Debit"].sum()
                total_cr = df["Credit"].sum()
                recon_diff = round(total_dr - total_cr, 2)

                c1, c2, c3 = st.columns(3)
                c1.metric("Sum of Debits", f"₹{total_dr:,.2f}")
                c2.metric("Sum of Credits", f"₹{total_cr:,.2f}")
                
                if abs(recon_diff) < 0.01:
                    c3.success("RECONCILED ✅")
                else:
                    c3.error(f"MISMATCH: ₹{recon_diff:,.2f}")
                    st.warning("Possible causes: Merged cells, hidden 'Total' rows, or non-numeric characters in source.")

                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Failed to process {file.name}: {e}")

    # ================= CONSOLIDATED FINANCIAL INTELLIGENCE =================
    if all_summaries:
        st.divider()
        st.header("📈 Financial Analysis & Working Capital")
        
        target = st.selectbox("Select file for Key Ratios", list(all_summaries.keys()))
        adf = all_summaries[target]
        
        # Working Capital Logic
        ca = adf[(adf["Category"] == "Asset") & (adf[desc_col].str.contains("Cash|Bank|Receivable|Stock|Inventory|Debtor", case=False, na=False))]["Net Amount"].sum()
        cl = abs(adf[(adf["Category"] == "Liability") & (adf[desc_col].str.contains("Payable|Creditor|Provision|Loan", case=False, na=False))]["Net Amount"].sum())
        wc = ca - cl
        
        # P&L Logic
        inc = abs(adf[adf["Category"] == "Income"]["Net Amount"].sum())
        exp = adf[adf["Category"] == "Expense"]["Net Amount"].sum()
        net_profit = inc - exp

        

        m1, m2, m3 = st.columns(3)
        m1.metric("Working Capital", f"₹{wc:,.2f}", delta="Liquidity Position")
        m2.metric("Net Profit / Loss", f"₹{net_profit:,.2f}", delta_color="normal")
        m3.metric("Current Ratio", f"{ca/cl:.2f}" if cl != 0 else "N/A")

        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Asset vs Liability Distribution")
            st.bar_chart(adf.groupby("Category")["Net Amount"].sum())
        with col_right:
            st.subheader("Income vs Expense")
            pl_chart = pd.DataFrame({"Amount": [inc, exp]}, index=["Income", "Expense"])
            st.pie_chart(pl_chart)

    # ================= COMPARATIVE VARIANCE =================
    if len(all_summaries) >= 2:
        st.divider()
        st.header("⚖️ Year-on-Year Variance")
        f_list = list(all_summaries.keys())
        col_a, col_b = st.columns(2)
        py = col_a.selectbox("Prior Period (PY)", f_list, index=0)
        cy = col_b.selectbox("Current Period (CY)", f_list, index=1)

        v_py = all_summaries[py].groupby("Category")["Net Amount"].sum()
        v_cy = all_summaries[cy].groupby("Category")["Net Amount"].sum()
        
        v_df = pd.DataFrame({"PY": v_py, "CY": v_cy}).fillna(0)
        v_df["Variance"] = v_df["CY"] - v_df["PY"]
        v_df["% Change"] = (v_df["Variance"] / v_df["PY"].replace(0, np.nan)) * 100
        
        st.write("Movement by Category:")
        st.table(v_df.style.format("{:,.2f}"))

        

else:
    st.info("Please upload your Trial Balance Excel sheets to begin the automated audit.")
