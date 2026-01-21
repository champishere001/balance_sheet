import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="ASI Intelligent Audit Engine", layout="wide")
st.title("🛡️ ASI Intelligent Audit & Cross-Check Engine")

# ================= FILE UPLOADER =================
uploaded_file = st.file_uploader(
    "Upload Trial Balance / Balance Sheet (Excel only on cloud)",
    type=["xlsx", "xls", "pdf"],
    key="audit_uploader"
)

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
        elif "desc" in cl:
            desc = c

    return debit, credit, desc or df.columns[0]

def classify(desc):
    d = str(desc).lower()
    if any(k in d for k in ["capital", "reserve", "loan", "creditor"]):
        return "Liability"
    if any(k in d for k in ["asset", "plant", "machinery", "building"]):
        return "Asset"
    if any(k in d for k in ["salary", "wage", "expense", "consumption"]):
        return "Expense"
    if any(k in d for k in ["sales", "turnover", "income"]):
        return "Income"
    return "Other"

# ================= MAIN =================
if uploaded_file:

    # ---------- PDF HANDLING ----------
    if uploaded_file.name.endswith(".pdf"):
        st.error(
            "⚠️ Scanned PDF OCR is NOT supported on Streamlit Cloud.\n\n"
            "✔ Please upload Excel here.\n"
            "✔ For PDF OCR, run the same app on your local system."
        )
        st.stop()

    # ---------- EXCEL ----------
    try:
        df = pd.read_excel(uploaded_file, header=0)
        df = clean_df(df)

        st.subheader("📄 Cleaned Data")
        st.dataframe(df, use_container_width=True)

        debit_cols, credit_cols, desc_col = detect_columns(df)

        df["Debit"] = (
            df[debit_cols]
            .apply(pd.to_numeric, errors="coerce")
            .sum(axis=1)
            if debit_cols else 0
        )

        df["Credit"] = (
            df[credit_cols]
            .apply(pd.to_numeric, errors="coerce")
            .sum(axis=1)
            if credit_cols else 0
        )

        df["Category"] = df[desc_col].apply(classify)

        # ---------- DASHBOARD ----------
        st.subheader("📊 Audit Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Debit", f"₹{df['Debit'].sum():,.2f}")
        col2.metric("Total Credit", f"₹{df['Credit'].sum():,.2f}")
        col3.metric(
            "Status",
            "MATCHED ✅" if abs(df["Debit"].sum() - df["Credit"].sum()) < 1 else "MISMATCH ⚠️"
        )

        st.subheader("📌 Category-wise Summary")
        st.dataframe(
            df.groupby("Category")[["Debit", "Credit"]].sum(),
            use_container_width=True
        )

        st.download_button(
            "📥 Download Audit-Ready CSV",
            df.to_csv(index=False).encode("utf-8"),
            "ASI_Audit_Output.csv",
            "text/csv"
        )

    except Exception as e:
        st.error(f"Processing failed: {e}")
