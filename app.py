import streamlit as st
import pandas as pd
import numpy as np

# ================= CONFIG & STYLING =================
st.set_page_config(page_title="ASI Intelligent Audit Engine", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ ASI Intelligent Audit & Cross-Check Engine")

# ================= HELPERS =================
def fix_duplicate_columns(df):
    cols = []
    counter = {}
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
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    df = fix_duplicate_columns(df)
    return df

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
    if any(k in d for k in ["capital", "reserve", "loan", "creditor", "payable", "provision", "borrowing"]):
        return "Liability"
    if any(k in d for k in ["asset", "plant", "machinery", "building", "cash", "bank", "receivable", "debtor", "stock", "inventory"]):
        return "Asset"
    if any(k in d for k in ["salary", "wage", "expense", "consumption", "purchase", "rent", "tax", "interest paid"]):
        return "Expense"
    if any(k in d for k in ["sales", "turnover", "income", "revenue", "gain", "interest received"]):
        return "Income"
    return "Other"

# ================= FILE UPLOADER =================
uploaded_files = st.file_uploader(
    "Upload Trial Balance / Balance Sheet (Excel)",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    all_summaries = {}
    
    for file in uploaded_files:
        try:
            # 1. Processing
            df = pd.read_excel(file, header=0)
            df = clean_df(df)
            debit_cols, credit_cols, desc_col = detect_columns(df)

            # 2. Calculations
            df["Debit"] = df[debit_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1) if debit_cols else 0
            df["Credit"] = df[credit_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1) if credit_cols else 0
            df["Category"] = df[desc_col].apply(classify)
            df["Net Amount"] = df["Debit"] - df["Credit"]

            all_summaries[file.name] = df

            with st.expander(f"📁 Raw Data & Classification: {file.name}"):
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")

    # ================= FINANCIAL ANALYSIS SECTION =================
    st.divider()
    st.header("📈 Financial Performance & Working Capital")
    
    # Selection for focus analysis
    selected_name = st.selectbox("Select entity/period for Financial Analysis", list(all_summaries.keys()))
    adf = all_summaries[selected_name]
    desc_c = detect_columns(adf)[2]

    # --- P&L Calculation ---
    total_income = abs(adf[adf["Category"] == "Income"]["Net Amount"].sum())
    total_expense = adf[adf["Category"] == "Expense"]["Net Amount"].sum()
    net_pl = total_income - total_expense

    # --- Working Capital Calculation ---
    # Heuristic-based current items
    curr_assets = adf[
        (adf["Category"] == "Asset") & 
        (adf[desc_c].str.contains("Cash|Bank|Receivable|Stock|Inventory|Debtor", case=False, na=False))
    ]["Net Amount"].sum()

    curr_liabilities = abs(adf[
        (adf["Category"] == "Liability") & 
        (adf[desc_c].str.contains("Payable|Creditor|Short-term|Provision|Loan", case=False, na=False))
    ]["Net Amount"].sum())

    working_cap = curr_assets - curr_liabilities

    # --- Display Metrics ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Net Profit / (Loss)", f"₹{net_pl:,.2f}", delta=f"{'Profit' if net_pl > 0 else 'Loss'}")
    c2.metric("Working Capital", f"₹{working_cap:,.2f}")
    c3.metric("Current Ratio", f"{curr_assets/curr_liabilities:.2f}" if curr_liabilities != 0 else "N/A")

    # --- Visuals ---
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.subheader("Profit & Loss Mix")
        pl_data = pd.DataFrame({"Value": [total_income, total_expense]}, index=["Income", "Expense"])
        st.bar_chart(pl_data)

    with col_v2:
        st.subheader("Liquidity Mix")
        wc_data = pd.DataFrame({"Value": [curr_assets, curr_liabilities]}, index=["Current Assets", "Current Liabilities"])
        st.bar_chart(wc_data)

    # ================= VARIANCE ANALYSIS (If 2+ Files) =================
    if len(all_summaries) >= 2:
        st.divider()
        st.header("⚖️ Comparative Variance (PY vs CY)")
        f_names = list(all_summaries.keys())
        
        col_py, col_cy = st.columns(2)
        py_file = col_py.selectbox("Prior Year (PY)", f_names, index=0)
        cy_file = col_cy.selectbox("Current Year (CY)", f_names, index=1)

        # Merge for comparison
        py_group = all_summaries[py_file].groupby("Category")["Net Amount"].sum()
        cy_group = all_summaries[cy_file].groupby("Category")["Net Amount"].sum()
        
        variance = pd.DataFrame({"PY": py_group, "CY": cy_group}).fillna(0)
        variance["Abs Variance"] = variance["CY"] - variance["PY"]
        variance["% Change"] = (variance["Abs Variance"] / variance["PY"].replace(0, np.nan)) * 100
        
        st.dataframe(variance.style.format("{:,.2f}"), use_container_width=True)

else:
    st.info("👋 Welcome! Please upload your Trial Balance Excel files in the sidebar to begin.")
