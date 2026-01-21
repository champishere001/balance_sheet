import streamlit as st
import pandas as pd
import numpy as np

# ================= CONFIG & STYLING =================
st.set_page_config(page_title="ASI Intelligent Audit Engine", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ ASI Intelligent Audit & Cross-Check Engine")
st.info("Upload one or multiple Trial Balance files (Excel) to perform automated classification and variance analysis.")

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
    debit, credit = [], []
    desc = None
    for c in df.columns:
        cl = c.lower()
        if "debit" in cl or cl.endswith("dr"):
            debit.append(c)
        elif "credit" in cl or cl.endswith("cr"):
            credit.append(c)
        elif any(k in cl for k in ["desc", "particulars", "account"]):
            desc = c
    return debit, credit, desc or df.columns[0]

def classify(desc):
    d = str(desc).lower()
    if any(k in d for k in ["capital", "reserve", "loan", "creditor", "payable", "provision"]):
        return "Liability"
    if any(k in d for k in ["asset", "plant", "machinery", "building", "cash", "bank", "receivable"]):
        return "Asset"
    if any(k in d for k in ["salary", "wage", "expense", "consumption", "purchase", "rent"]):
        return "Expense"
    if any(k in d for k in ["sales", "turnover", "income", "revenue", "gain"]):
        return "Income"
    return "Other"

# ================= FILE UPLOADER =================
uploaded_files = st.file_uploader(
    "Upload Trial Balance / Balance Sheet (Excel)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    key="audit_uploader"
)

# ================= PROCESSING LOGIC =================
if uploaded_files:
    all_summaries = {}
    
    for uploaded_file in uploaded_files:
        try:
            # Load and Process
            df = pd.read_excel(uploaded_file, header=0)
            df = clean_df(df)
            debit_cols, credit_cols, desc_col = detect_columns(df)

            # Calculation
            df["Debit"] = df[debit_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1) if debit_cols else 0
            df["Credit"] = df[credit_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1) if credit_cols else 0
            df["Category"] = df[desc_col].apply(classify)
            df["Net Amount"] = df["Debit"] - df["Credit"]

            # Store results
            all_summaries[uploaded_file.name] = df

            with st.expander(f"📁 Analysis: {uploaded_file.name}", expanded=len(uploaded_files) == 1):
                col1, col2, col3 = st.columns(3)
                total_dr = df["Debit"].sum()
                total_cr = df["Credit"].sum()
                diff = abs(total_dr - total_cr)

                col1.metric("Total Debit", f"₹{total_dr:,.2f}")
                col2.metric("Total Credit", f"₹{total_cr:,.2f}")
                col3.metric("Balance Status", "MATCHED ✅" if diff < 1 else f"DIFF: ₹{diff:,.2f}", delta=-diff if diff > 1 else None)

                # Anomaly Detection
                st.subheader("🚩 Audit Flags")
                anomalies = df[
                    ((df["Category"] == "Asset") & (df["Credit"] > df["Debit"])) |
                    ((df["Category"] == "Expense") & (df["Credit"] > df["Debit"]))
                ]
                if not anomalies.empty:
                    st.warning(f"Directional Anomaly: {len(anomalies)} Asset/Expense accounts have Credit balances.")
                    st.dataframe(anomalies[[desc_col, "Debit", "Credit", "Category"]], use_container_width=True)
                else:
                    st.success("No directional anomalies detected.")

                st.subheader("Category Breakdown")
                cat_summary = df.groupby("Category")[["Debit", "Credit"]].sum()
                st.bar_chart(cat_summary)
                st.dataframe(cat_summary, use_container_width=True)

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    # ================= CROSS-CHECK / VARIANCE ANALYSIS =================
    if len(all_summaries) >= 2:
        st.divider()
        st.header("⚖️ Comparative Variance Analysis")
        
        file_names = list(all_summaries.keys())
        col_a, col_b = st.columns(2)
        base_file = col_a.selectbox("Select Base Period (PY)", file_names, index=0)
        comp_file = col_b.selectbox("Select Comparison Period (CY)", file_names, index=1)

        df_py = all_summaries[base_file].groupby("Category")["Net Amount"].sum()
        df_cy = all_summaries[comp_file].groupby("Category")["Net Amount"].sum()

        variance_df = pd.DataFrame({"Prior Year": df_py, "Current Year": df_cy})
        variance_df["Abs Variance"] = variance_df["Current Year"] - variance_df["Prior Year"]
        variance_df["% Change"] = (variance_df["Abs Variance"] / variance_df["Prior Year"].replace(0, np.nan)) * 100

        st.dataframe(variance_df.style.format("{:,.2f}").highlight_max(axis=0, color='#ffebcc'), use_container_width=True)
        
        st.subheader("Visual Variance")
        st.line_chart(variance_df[["Prior Year", "Current Year"]])

    # ================= GLOBAL DOWNLOAD =================
    if all_summaries:
        st.sidebar.header("Export Data")
        for name, data in all_summaries.items():
            st.sidebar.download_button(
                label=f"📥 Download {name} (Processed)",
                data=data.to_csv(index=False).encode("utf-8"),
                file_name=f"Processed_{name}.csv",
                mime="text/csv"
            )
else:
    st.write("Please upload one or more Excel files to begin the audit process.")
