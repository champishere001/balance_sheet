import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="ASI Financial Engine", layout="wide")

# --- CSS FOR METRICS ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007BFF; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ================= CORE FUNCTIONS =================
def classify_extended(desc):
    d = str(desc).lower()
    if any(k in d for k in ["sales", "revenue", "income", "turnover"]): return "Income"
    if any(k in d for k in ["purchase", "wage", "salary", "rent", "electricity", "expense", "admin"]): return "Expense"
    if any(k in d for k in ["cash", "bank", "debtor", "stock", "inventory", "receivable"]): return "Current Asset"
    if any(k in d for k in ["creditor", "payable", "short term loan", "od", "overdraft"]): return "Current Liability"
    if any(k in d for k in ["fixed asset", "machinery", "building", "land"]): return "Fixed Asset"
    return "Equity/Long-Term Liab"

# ================= APP UI =================
st.title("🛡️ ASI Financial & Audit Engine")

uploaded_file = st.file_uploader("Upload Trial Balance (Excel)", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        
        # 1. Cleaning and Detection
        df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
        df.columns = [str(c).strip() for c in df.columns]
        
        # Auto-detect Amount Columns
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        desc_col = df.columns[0]
        
        st.sidebar.header("Setup")
        val_col = st.sidebar.selectbox("Select Balance/Amount Column", num_cols)
        
        # 2. Financial Classification
        df["Category"] = df[desc_col].apply(classify_extended)
        
        # 3. Aggregation
        totals = df.groupby("Category")[val_col].sum()
        
        income = totals.get("Income", 0)
        expense = totals.get("Expense", 0)
        current_assets = totals.get("Current Asset", 0)
        current_liabilities = totals.get("Current Liability", 0)
        
        # 4. Calculations
        net_profit = income - expense
        working_capital = current_assets - current_liabilities
        current_ratio = current_assets / current_liabilities if current_liabilities != 0 else 0

        # --- DISPLAY RESULTS ---
        st.subheader("💰 Profit & Loss Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Income", f"₹{income:,.2f}")
        c2.metric("Total Expenses", f"₹{expense:,.2f}")
        c3.metric("Net Profit/Loss", f"₹{net_profit:,.2f}", delta=f"{net_profit:,.2f}")

        st.divider()

        st.subheader("🏥 Working Capital & Liquidity")
        w1, w2, w3 = st.columns(3)
        w1.metric("Current Assets", f"₹{current_assets:,.2f}")
        w2.metric("Current Liabilities", f"₹{current_liabilities:,.2f}")
        w3.metric("Working Capital", f"₹{working_capital:,.2f}", delta="Healthy" if working_capital > 0 else "Risk")

        # --- DATA VIEW ---
        with st.expander("View Categorized Data"):
            st.dataframe(df[[desc_col, val_col, "Category"]], use_container_width=True)

    except Exception as e:
        st.error(f"Error processing data: {e}")
else:
    st.info("Please upload an Excel file to see P&L and Working Capital.")
