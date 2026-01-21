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

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="ASI Scrutiny Portal", layout="wide", page_icon="🛡️")
st.title("🛡️ ASI Scrutiny: Autonomous Multi-File Audit Portal")

# --- GLOBAL INTELLIGENCE: KEYWORD MAPPING ---
# This allows the system to find "Total Assets" even if it's called "Grand Total" or "24-25"
VITAL_MAP = {
    "Total Assets": ["total assets", "total rs.", "balance sheet total", "grand total", "24-25", "closing dr"],
    "Net Profit": ["net profit", "profit for the year", "final amt of p& l", "pl amount", "surplus"],
    "Sales/Turnover": ["sales", "revenue from operations", "turnover", "income from sales"],
    "Wages/Manpower": ["wages", "salaries", "employee benefits", "man-days"]
}

# --- HELPER FUNCTIONS ---
def clean_num(val):
    """Cleans currency strings, brackets, and commas into floats."""
    if pd.isna(val): return 0.0
    s = str(val).replace(',', '').replace('Rs.', '').replace('₹', '').strip()
    if '(' in s and ')' in s: s = '-' + s.replace('(', '').replace(')', '')
    try:
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", s)
        return float(nums[0]) if nums else 0.0
    except: return 0.0

def autonomous_excel_scan(file):
    """Scans all sheets in an Excel file and finds vital data."""
    results = []
    excel_file = pd.ExcelFile(file)
    for sheet in excel_file.sheet_names:
        df = pd.read_excel(file, sheet_name=sheet)
        if df.empty: continue
        
        sheet_info = {"FileName": file.name, "SheetName": sheet}
        col_text = " ".join([str(c) for c in df.columns]).lower()
        
        # Look for headers in columns
        for metric, keywords in VITAL_MAP.items():
            best_col = None
            for kw in keywords:
                matches = [c for c in df.columns if kw in str(c).lower()]
                if matches:
                    best_col = matches[0]
                    break
            
            if best_col:
                # If it's a balance sheet/PL, we usually want the total (last row) or sum
                sheet_info[metric] = df[best_col].apply(clean_num).sum()
            else:
                sheet_info[metric] = 0.0
        
        results.append(sheet_info)
    return results

def autonomous_pdf_scan(file, use_ocr=False):
    """Extracts text from PDF (Digital or Scanned) and finds values."""
    text = ""
    if use_ocr:
        images = convert_from_bytes(file.read())
        for img in images:
            text += pytesseract.image_to_string(img)
    else:
        with pdfplumber.open(file) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    
    extracted = {"FileName": file.name, "SheetName": "PDF Content"}
    for metric, keywords in VITAL_MAP.items():
        found = False
        for kw in keywords:
            pattern = rf"{kw}.*?([\d,.]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[metric] = clean_num(match.group(1))
                found = True
                break
        if not found: extracted[metric] = 0.0
    return [extracted]

# --- USER INTERFACE ---
st.sidebar.header("📁 Upload Hub")
uploaded_files = st.file_uploader("Upload ASI Files (Excel, CSV, PDF)", 
                                  accept_multiple_files=True, 
                                  type=["xlsx", "xls", "csv", "pdf"])

ocr_enabled = st.sidebar.checkbox("Enable OCR for Scanned PDFs", value=False)

if uploaded_files:
    master_data = []
    
    with st.status("🔍 Analyzing documents autonomously...") as status:
        for f in uploaded_files:
            if f.name.endswith(('.xlsx', '.xls')):
                master_data.extend(autonomous_excel_scan(f))
            elif f.name.endswith('.pdf'):
                master_data.extend(autonomous_pdf_scan(f, use_ocr=ocr_enabled))
            elif f.name.endswith('.csv'):
                df = pd.read_csv(f)
                master_data.append(analyze_sheet_generic(df, f.name, "CSV Root"))
        status.update(label="Analysis Complete!", state="complete")

    # --- THE VITAL CHECK TABLE ---
    st.subheader("📋 Step 1: Consolidated Check Table")
    final_df = pd.DataFrame(master_data).fillna(0)
    
    # Reorder columns for readability
    cols = ["FileName", "SheetName", "Total Assets", "Net Profit", "Sales/Turnover", "Wages/Manpower"]
    final_df = final_df[cols]
    
    st.dataframe(final_df, use_container_width=True)

    # 📥 MASTER DOWNLOAD BUTTON
    csv_bytes = final_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Master Scrutiny CSV", csv_bytes, "ASI_Final_Report.csv", "text/csv")

    # --- INDIVIDUAL CONVERSION OPTIONS ---
    st.divider()
    st.subheader("📂 Individual Sheet Conversion")
    st.info("Download individual sheets as CSVs for separate records.")
    
    for f in uploaded_files:
        if f.name.endswith(('.xlsx', '.xls')):
            xl = pd.ExcelFile(f)
            for s in xl.sheet_names:
                df_temp = pd.read_excel(f, sheet_name=s)
                st.download_button(f"Download {f.name} [{s}] as CSV", 
                                   df_temp.to_csv(index=False), 
                                   f"{f.name}_{s}.csv", "text/csv")

    # --- INTELLIGENT ANALYSIS ---
    st.divider()
    st.subheader("🔍 Step 2: Automated Analysis & Errors")
    for index, row in final_df.iterrows():
        if row['Total Assets'] > 0:
            with st.expander(f"Analysis for {row['FileName']} ({row['SheetName']})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"Assets Identified: ₹{row['Total Assets']:,.2f}")
                    if row['Net Profit'] > 0:
                        margin = (row['Net Profit'] / row['Sales/Turnover']) * 100 if row['Sales/Turnover'] > 0 else 0
                        st.metric("Net Profit Margin", f"{margin:.2f}%")
                with c2:
                    if row['Sales/Turnover'] == 0:
                        st.warning("⚠️ Turnover not found. Check if the sheet uses 'Revenue' or 'Income'.")

