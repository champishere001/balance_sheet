import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import cv2
import numpy as np
import re
import io
from fuzzywuzzy import process

st.set_page_config(page_title="ASI Autonomous Audit Pro", layout="wide")
st.title("🛡️ ASI Scrutiny: The Autonomous Super-Portal")

# --- 1. CONFIGURATION & INTELLIGENT MAPPING ---
VITAL_ALIASES = {
    "Total Assets": ["total assets", "grand total", "total rs.", "total assets and liabilities", "balance sheet total"],
    "Net Profit": ["net profit", "profit for the year", "profit/(loss) for the period", "surplus after tax"],
    "Turnover": ["sales", "revenue from operations", "income from sales", "total turnover"],
    "Wages": ["wages", "salaries and wages", "employee benefit expenses", "manpower cost"]
}

# --- 2. CORE ENGINES ---
def clean_numeric(val):
    if pd.isna(val): return 0.0
    s = str(val).replace(',', '').replace('Rs.', '').replace('₹', '').strip()
    # Handle accounting brackets: (100) -> -100
    if '(' in s and ')' in s:
        s = '-' + s.replace('(', '').replace(')', '')
    try: return float(re.findall(r"[-+]?\d*\.\d+|\d+", s)[0])
    except: return 0.0

def extract_from_excel(file):
    """Processes all sheets and identifies vital rows by fuzzy matching headers"""
    results = {"Source": file.name}
    dfs = pd.read_excel(file, sheet_name=None)
    for sheet_name, df in dfs.items():
        # Flatten all text in the sheet to search for vital metrics
        text_blob = df.to_string().lower()
        for metric, aliases in VITAL_ALIASES.items():
            if any(alias in text_blob for alias in aliases):
                # If we find a keyword, we try to find the number in the nearest numeric column
                # This is a 'Smart Guess' for autonomous detection
                best_match = process.extractOne(metric, df.iloc[:, 0].astype(str))
                if best_match and best_match[1] > 80:
                    row_idx = best_match[2]
                    results[metric] = clean_numeric(df.iloc[row_idx, -1])
    return results

def extract_from_pdf(file, use_ocr=False):
    """Uses pdfplumber for digital text or OCR for scans"""
    results = {"Source": file.name}
    full_text = ""
    
    if use_ocr:
        images = convert_from_bytes(file.read())
        for img in images:
            full_text += pytesseract.image_to_string(img)
    else:
        with pdfplumber.open(file) as pdf:
            full_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])

    # Autonomous Regex: Look for Alias + closest Number
    for metric, aliases in VITAL_ALIASES.items():
        for alias in aliases:
            pattern = rf"{alias}.*?([\d,.]+)"
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                results[metric] = clean_numeric(match.group(1))
                break
    return results

# --- 3. UI INTERFACE ---
st.sidebar.header("⚙️ Audit Settings")
ocr_mode = st.sidebar.checkbox("Enable OCR (For Scanned/Image PDFs)", value=False)
st.sidebar.info("The system automatically identifies headers like 'Total Assets' vs 'Grand Total'.")

uploaded_files = st.file_uploader("Upload All Enterprise Files (PDF/Excel)", accept_multiple_files=True)

if uploaded_files:
    summary_data = []
    
    with st.status("🚀 Autonomously analyzing documents...") as status:
        for f in uploaded_files:
            if f.name.endswith(('.xlsx', '.xls')):
                data = extract_from_excel(f)
            else:
                data = extract_from_pdf(f, use_ocr=ocr_mode)
            summary_data.append(data)
        status.update(label="Analysis Complete!", state="complete")

    # --- 4. THE VITAL CHECK TABLE & CSV GENERATION ---
    vital_df = pd.DataFrame(summary_data).fillna(0)
    
    st.subheader("📋 Step 1: Autonomous Vital Check Table")
    st.write("Below are the values identified from your documents. If a value is 0, the header was not recognized.")
    st.dataframe(vital_df, use_container_width=True)
    
    # EXPORT BUTTON
    csv_bytes = vital_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Audit Summary (CSV)",
        data=csv_bytes,
        file_name="ASI_Consolidated_Audit.csv",
        mime="text/csv"
    )

    # --- 5. CROSS-ANALYSIS & ERROR DETECTION ---
    st.subheader("🔍 Step 2: Intelligent Scrutiny Analysis")
    for _, row in vital_df.iterrows():
        with st.expander(f"Scrutiny Report: {row['Source']}"):
            c1, c2, c3 = st.columns(3)
            with c1:
                if row.get('Total Assets', 0) > 0:
                    st.success(f"Assets Identified: ₹{row['Total Assets']:,.2f}")
                else:
                    st.error("❌ Total Assets not found. Check if the scan is clear.")
            with c2:
                if row.get('Net Profit', 0) != 0:
                    st.info(f"Net Profit: ₹{row['Net Profit']:,.2f}")
            with c3:
                # Automatic Trend Analysis
                if row.get('Turnover', 0) > 0:
                    margin = (row['Net Profit'] / row['Turnover']) * 100
                    st.metric("Net Margin", f"{margin:.2f}%")
