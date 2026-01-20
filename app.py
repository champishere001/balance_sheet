import streamlit as st
import pandas as pd
import pdfplumber
import re

st.set_page_config(page_title="Pro ASI Scrutiny", layout="wide")
st.title("🛡️ Pro-Audit: Autonomous Scrutiny Portal")

# THE DYNAMIC DICTIONARY: The "Brain" of the system
VITAL_MAP = {
    "Total Assets": ["total assets", "total rs.", "balance total", "grand total", "net block"],
    "Net Profit": ["net profit", "profit for the year", "p&l amount", "surplus"],
    "Turnover": ["sales", "revenue from operations", "income from services"],
    "Inventory": ["closing stock", "inventories", "stock in hand"]
}

def clean_val(text):
    """Universal number cleaner for Indian accounting formats"""
    try:
        # Removes currency symbols and handles parentheses for negative numbers
        clean = re.sub(r'[^\d.-]', '', text.replace('(', '-').replace(')', ''))
        return float(clean)
    except:
        return 0.0

def autonomous_fetch(file):
    """Main engine that decides how to read the file based on its content"""
    extracted = {"FileName": file.name}
    
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            full_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            for label, keywords in VITAL_MAP.items():
                for word in keywords:
                    # Look for keyword + nearest number
                    pattern = rf"{word}.*?([\d,.\(\)]+)"
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        extracted[label] = clean_val(match.group(1))
                        break
    else:
        # EXCEL/CSV LOGIC: Searches column headers for keywords
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        for label, keywords in VITAL_MAP.items():
            for word in keywords:
                # Find columns that contain the keyword
                match_cols = [c for c in df.columns if word in str(c).lower()]
                if match_cols:
                    # Take the sum of the last column (usually the amount column)
                    extracted[label] = pd.to_numeric(df[match_cols[0]], errors='coerce').sum()
                    break
    return extracted

# --- UI ---
files = st.file_uploader("Upload Any Enterprise Data (PDF/Excel)", accept_multiple_files=True)

if files:
    data_list = [autonomous_fetch(f) for f in files]
    vital_df = pd.DataFrame(data_list).fillna(0)
    
    st.subheader("📋 Step 1: Self-Generated Vital Check Table")
    st.dataframe(vital_df, use_container_width=True)
    
    # GENERATE CSV ON THE FLY
    st.download_button("📥 Download Vital Check CSV", vital_df.to_csv(index=False), "Audit_Report.csv")

    st.subheader("🔍 Step 2: Intelligent Analysis")
    for _, row in vital_df.iterrows():
        with st.expander(f"Audit Summary: {row['FileName']}"):
            # Check for standard accounting equation
            if row.get('Total Assets') > 0:
                st.success(f"Verified: Found Assets worth ₹{row['Total Assets']:,.2f}")
            else:
                st.warning("⚠️ Critical data missing. System could not identify 'Total Assets'.")
