import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="ASI Forensic Audit Suite", layout="wide", page_icon="🕵️")

# --- CUSTOM CSS FOR AUDITORS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_index=True)

# ================= HELPER FUNCTIONS =================
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
    # Remove empty columns/rows
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    # Remove Total/Subtotal rows to prevent double-counting
    if not df.empty:
        df = df[~df.iloc[:, 0].astype(str).str.contains("Total|Grand Total|Balance", case=False, na=False)]
    df.columns = [str(c).strip() for c in df.columns]
    df = fix_duplicate_columns(df)
    return df

def detect_columns(df):
    debit, credit = [], []
    desc = df.columns[0]
    for c in df.columns:
        cl = str(c).lower()
        if "debit" in cl or cl.endswith("dr"): debit.append(c)
        elif "credit" in cl or cl.endswith("cr"): credit.append(c)
        elif "desc" in cl or "particulars" in cl: desc = c
    return debit, credit, desc

def get_first_digit(n):
    n = abs(n)
    if n < 1 or pd.isna(n): return None
    return int(str(n)[0])

def check_benford(series):
    digits = series.apply(get_first_digit).dropna()
    if len(digits) == 0: return None
    counts = digits.value_counts(normalize=True).sort_index()
    expected = pd.Series({i: math.log10(1 + 1/i) for i in range(1, 10)})
    return pd.DataFrame({"Actual": counts, "Expected": expected}).fillna(0)

# ================= APP UI =================
st.title("🛡️ ASI Intelligent Forensic Audit Suite")
st.markdown("### Deep Analysis of Financial Statements & Ledger Integrity")

uploaded_file = st.file_uploader("Upload Trial Balance / Ledger (Excel)", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # 1. DATA LOADING
        df_raw = pd.read_excel(uploaded_file)
        df = clean_df(df_raw)
        
        d_cols, c_cols, desc_col = detect_columns(df)
        
        # 2. SIDEBAR CONFIG
        st.sidebar.header("⚙️ Column Mapping")
        final_desc = st.sidebar.selectbox("Description Column", df.columns, index=list(df.columns).index(desc_col))
        final_debit = st.sidebar.multiselect("Debit Columns", df.columns, default=d_cols)
        final_credit = st.sidebar.multiselect("Credit Columns", df.columns, default=c_cols)

        # 3. CORE CALCULATIONS
        df["Debit_Val"] = df[final_debit].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
        df["Credit_Val"] = df[final_credit].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
        df["Absolute_Val"] = df["Debit_Val"] + df["Credit_Val"]

        # --- DASHBOARD METRICS ---
        total_dr = df["Debit_Val"].sum()
        total_cr = df["Credit_Val"].sum()
        diff = total_dr - total_cr

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Debit", f"₹{total_dr:,.2f}")
        m2.metric("Total Credit", f"₹{total_cr:,.2f}")
        m3.metric("Net Difference", f"₹{abs(diff):,.2f}", 
                  delta="Out of Balance" if abs(diff) > 1 else "Balanced", 
                  delta_color="inverse" if abs(diff) > 1 else "normal")
        m4.metric("Total Rows Analyzed", f"{len(df)}")

        # --- TABBED ANALYSIS ---
        tab1, tab2, tab3 = st.tabs(["📊 Trial Balance Check", "🔍 Forensic Tests", "🚩 Outlier Detection"])

        with tab1:
            st.subheader("General Ledger Overview")
            if abs(diff) > 0.01:
                st.error(f"⚠️ Trial Balance Mismatch: {diff:,.2f}")
                if abs(diff) % 9 == 0:
                    st.warning("🕵️ Forensic Insight: Difference is divisible by 9. Check for transposed digits (e.g., 54 instead of 45).")
            else:
                st.success("✅ Trial Balance is mathematically sound.")
            
            st.dataframe(df[[final_desc, "Debit_Val", "Credit_Val"]], use_container_width=True)

        with tab2:
            st.subheader("Benford's Law Analysis")
            st.info("Benford's Law predicts the frequency of leading digits. Significant deviations can indicate manual data manipulation.")
            ben_df = check_benford(df["Absolute_Val"])
            if ben_df is not None:
                fig = px.line(ben_df, title="Digit Frequency vs. Natural Law", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Duplicate Check")
            dupes = df[df.duplicated(subset=["Absolute_Val"], keep=False) & (df["Absolute_Val"] > 0)]
            if not dupes.empty:
                st.warning(f"Found {len(dupes)} entries with identical amounts. Check for double-billing.")
                st.dataframe(dupes[[final_desc, "Absolute_Val"]].sort_values(by="Absolute_Val", ascending=False))

        with tab3:
            st.subheader("Statistical Outliers (Z-Score)")
            mean = df["Absolute_Val"].mean()
            std = df["Absolute_Val"].std()
            df['Z_Score'] = (df["Absolute_Val"] - mean) / std
            
            # Show top 5% of outliers
            outliers = df[df['Z_Score'] > 2].sort_values(by='Absolute_Val', ascending=False)
            if not outliers.empty:
                st.warning("High-Value Transactions for Manual Verification:")
                st.dataframe(outliers[[final_desc, "Absolute_Val", "Z_Score"]])
                
                fig_out = px.scatter(df, x=final_desc, y="Absolute_Val", color="Z_Score", 
                                     title="Transaction Distribution (Color by Z-Score)")
                st.plotly_chart(fig_out, use_container_width=True)

        # --- EXPORT ---
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Audit Report", data=csv, file_name="ASI_Forensic_Audit.csv", mime="text/csv")

    except Exception as e:
        st.error(f"System Error: {e}")
else:
    st.info("👋 Welcome! Please upload your Trial Balance Excel file to begin a 'Hard Look' audit.")
