import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="ASI Intelligent Audit Engine", layout="wide")

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
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    # Filter out common "Total" rows that cause double-counting
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

def classify(desc):
    d = str(desc).lower()
    if any(k in d for k in ["capital", "reserve", "loan", "creditor", "payable", "tax"]): return "Liability"
    if any(k in d for k in ["asset", "plant", "machinery", "building", "cash", "bank", "receivable"]): return "Asset"
    if any(k in d for k in ["salary", "wage", "expense", "consumption", "rent", "purchase"]): return "Expense"
    if any(k in d for k in ["sales", "turnover", "income", "revenue"]): return "Income"
    return "Other"

# ================= UI SETUP =================
st.title("🛡️ ASI Intelligent Audit & Cross-Check Engine")

uploaded_file = st.file_uploader("Upload Trial Balance (Excel)", type=["xlsx", "xls"])

if uploaded_file:
    try:
        # Load and Preprocess
        df_raw = pd.read_excel(uploaded_file)
        df = clean_df(df_raw)
        
        # Initial Detection
        d_cols, c_cols, desc_col = detect_columns(df)
        
        # Sidebar for Manual Overrides
        st.sidebar.header("⚙️ Column Mapping")
        final_desc = st.sidebar.selectbox("Description Column", df.columns, index=list(df.columns).index(desc_col))
        final_debit = st.sidebar.multiselect("Debit Columns", df.columns, default=d_cols)
        final_credit = st.sidebar.multiselect("Credit Columns", df.columns, default=c_cols)

        # Calculations
        df["Debit"] = df[final_debit].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
        df["Credit"] = df[final_credit].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
        df["Category"] = df[final_desc].apply(classify)

        # --- Dashboard Metrics ---
        total_dr = df["Debit"].sum()
        total_cr = df["Credit"].sum()
        diff = abs(total_dr - total_cr)

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Debit", f"₹{total_dr:,.2f}")
        m2.metric("Total Credit", f"₹{total_cr:,.2f}")
        m3.metric("Difference", f"₹{diff:,.2f}", delta=None, delta_color="inverse" if diff > 1 else "normal")

        if diff < 1:
            st.success("✅ Trial Balance Matched!")
        else:
            st.error(f"⚠️ Mismatch Detected: ₹{diff:,.2f}")

        # --- Visualizations ---
        st.divider()
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("📊 Financial Composition")
            summary = df.groupby("Category")[["Debit", "Credit"]].sum().reset_index()
            fig = px.bar(summary, x="Category", y=["Debit", "Credit"], barmode="group", color_discrete_sequence=["#1f77b4", "#ff7f0e"])
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("🚩 Audit Anomalies")
            # Logic: Flag round numbers > 10k or negative entries
            anomalies = df[(df["Debit"] > 0) & (df["Debit"] % 1000 == 0) & (df["Debit"] >= 10000)]
            if not anomalies.empty:
                st.warning(f"Found {len(anomalies)} large round-sum transactions (Potential Manual Entries).")
                st.dataframe(anomalies[[final_desc, "Debit", "Credit"]].head(5))
            else:
                st.info("No suspicious round-sum entries found.")

        # --- Data Table ---
        st.subheader("📝 Processed Audit Data")
        st.dataframe(df[[final_desc, "Debit", "Credit", "Category"]], use_container_width=True)

        # --- Download ---
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Audit Report", data=csv, file_name="Audit_Analysis.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload an Excel file to begin the audit analysis.")
