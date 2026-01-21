import streamlit as st
import pandas as pd
import numpy as np
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import cv2
import re

st.set_page_config(page_title="ASI Intelligent Audit Engine", layout="wide")
st.title("🛡️ ASI Intelligent Audit & Cross-Check Engine")

# ================= FILE UPLOADER =================
uploaded_file = st.file_uploader(
    "Upload Trial Balance / Balance Sheet (Excel or Scanned PDF)",
    type=["xlsx", "xls", "pdf"],
    key="audit_uploader"
)

# ================= FUNCTIONS =================
def clean_df(df):
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    return df

def detect_amount_columns(df):
    debit_col, credit_col, amount_col = None, None, None

    for c in df.columns:
        cl = c.lower()
        if "debit" in cl or cl.endswith("dr"):
            debit_col = c
        elif "credit" in cl or cl.endswith("cr"):
            credit_col = c
        elif "amount" in cl or "value" in cl:
            amount_col = c

    return debit_col, credit_col, amount_col

def classify_account(desc):
    d = desc.lower()
    if any(k in d for k in ["capital", "reserve", "loan", "creditor", "payable"]):
        return "Liability"
    if any(k in d for k in ["asset", "plant", "machinery", "building", "land"]):
        return "Asset"
    if any(k in d for k in ["wage", "salary", "expense", "consumption"]):
        return "Expense"
    if any(k in d for k in ["sales", "turnover", "income", "revenue"]):
        return "Income"
    return "Unclassified"

def ocr_pdf_to_df(pdf_bytes):
    images = convert_from_bytes(pdf_bytes, dpi=300)
    text = ""
    for img in images:
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
        text += "\n" + pytesseract.image_to_string(gray, config="--psm 6")

    rows = []
    for line in text.split("\n"):
        line = re.sub(r"\s{2,}", "|", line.strip())
        if "|" in line:
            rows.append(line.split("|"))

    if not rows:
        return None

    max_len = max(len(r) for r in rows)
    rows = [r + [""] * (max_len - len(r)) for r in rows]
    return clean_df(pd.DataFrame(rows))

# ================= MAIN =================
if uploaded_file:
    try:
        # ---------- LOAD ----------
        if uploaded_file.name.endswith((".xlsx", ".xls")):
            df = clean_df(pd.read_excel(uploaded_file))
        else:
            st.info("Running OCR on scanned PDF…")
            df = ocr_pdf_to_df(uploaded_file.read())
            if df is None:
                st.error("No readable table found in PDF")
                st.stop()

        st.subheader("📄 Cleaned Data")
        st.dataframe(df, use_container_width=True)

        # ---------- DETECTION ----------
        debit_col, credit_col, amount_col = detect_amount_columns(df)
        desc_col = next((c for c in df.columns if "desc" in c.lower()), df.columns[0])

        df["Debit"] = pd.to_numeric(df[debit_col], errors="coerce") if debit_col else 0
        df["Credit"] = pd.to_numeric(df[credit_col], errors="coerce") if credit_col else 0

        if amount_col and not debit_col and not credit_col:
            df["Debit"] = pd.to_numeric(df[amount_col], errors="coerce")

        df["Category"] = df[desc_col].astype(str).apply(classify_account)

        # ---------- DASHBOARD ----------
        st.subheader("📊 Audit Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Debit", f"₹{df['Debit'].sum():,.2f}")
        col2.metric("Total Credit", f"₹{df['Credit'].sum():,.2f}")
        col3.metric(
            "Balance Status",
            "MATCHED ✅" if abs(df["Debit"].sum() - df["Credit"].sum()) < 1 else "MISMATCH ⚠️"
        )

        st.subheader("📌 Category Totals")
        summary = df.groupby("Category")[["Debit", "Credit"]].sum()
        st.dataframe(summary, use_container_width=True)

        # ---------- EXPORT ----------
        st.download_button(
            "📥 Download Audit-Ready CSV",
            df.to_csv(index=False).encode("utf-8"),
            "ASI_Audit_Output.csv",
            "text/csv"
        )

    except Exception as e:
        st.error(f"Error: {e}")
