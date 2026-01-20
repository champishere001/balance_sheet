import streamlit as st
import pandas as pd
import pdfplumber
import re
import io

st.set_page_config(page_title="Autonomous ASI Scrutiny", layout="wide")
st.title("🛡️ Autonomous Scrutiny: Self-Identifying Data Portal")

# 1. UNIVERSAL HEADER DICTIONARY
# The system will search for ANY of these variations in your files
MAPPING = {
    "Assets": ["total assets", "total rs.", "balance total", "grand total", "fixed assets", "current assets"],
    "Liabilities": ["total liabilities", "liabilities and equity", "total capital and liabilities"],
    "Profit": ["net profit", "profit for the year", "profit after tax", "p&l", "surplus"],
    "Stock": ["closing stock", "inventories", "stock in hand", "inventory at end"],
    "Sales": ["sales", "revenue from operations", "turnover", "income from sales"],
    "Wages": ["wages", "manpower expenses", "employee benefit expenses", "salaries and wages"]
}

def auto_find_value(text, keywords):
    """Searches text for keyword variations and extracts the following number"""
    for word in keywords:
        # Regex looks for the word followed by some spaces/chars and a currency figure
        pattern = r"(" + word + r").{0,30}([\d,.]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val = match.group(2).replace(',', '')
                return float(val)
            except:
                continue
    return 0

def process_unknown_file(file):
    """Detects file type and runs self-identifying logic"""
    results = {"Entity": file.name, "Assets": 0, "Liabilities": 0, "Profit": 0, "Stock": 0, "Sales": 0, "Wages": 0}
    
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            full_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            for key, keywords in MAPPING.items():
                results[key] = auto_find_value(full_text, keywords)
    
    else: # Excel/CSV Logic
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        # Flatten all column names to search for matches
        cols = [str(c).lower() for c in df.columns]
        
        for key, keywords in MAPPING.items():
            for word in keywords:
                # If a column name matches one of our vital keywords
                match_col = [c for c in df.columns if word in str(c).lower()]
                if match_col:
                    # Take the sum of the column or the last value (usually the total)
                    results[key] = pd.to_numeric(df[match_col[0]], errors='coerce').sum()
                    break
    return results

# --- UI ---
st.sidebar.header("Auto-Header Engine Active")
uploaded_files = st.file_uploader("Upload any Enterprise File", accept_multiple_files=True)

if uploaded_files:
    summary_list = []
    for f in uploaded_files:
        with st.spinner(f"Searching headers in {f.name}..."):
            data = process_unknown_file(f)
            summary_list.append(data)
    
    # GENERATE VITAL CSV
    vital_df = pd.DataFrame(summary_list)
    
    st.subheader("📋 Step 1: Self-Generated Vital Check Table")
    st.write("The system identified these values by scanning for keywords in your files.")
    st.dataframe(vital_df, use_container_width=True)
    
    # DOWNLOAD CSV
    csv_bytes = vital_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Vital Data CSV", csv_bytes, "Autonomous_Vital_Report.csv", "text/csv")

    # DYNAMIC ANALYSIS
    st.subheader("🔍 Step 2: Analysis Based on Identified Data")
    for _, row in vital_df.iterrows():
        with st.expander(f"Scrutiny for {row['Entity']}"):
            if row['Assets'] == row['Liabilities'] and row['Assets'] > 0:
                st.success("✅ Balance Sheet Logic Verified.")
            elif row['Assets'] > 0:
                st.error(f"❌ Imbalance: Assets ({row['Assets']:,.2f}) vs Liabs ({row['Liabilities']:,.2f})")
            
            if row['Profit'] > 0 and row['Sales'] > 0:
                margin = (row['Profit'] / row['Sales']) * 100
                st.info(f"📊 Profitability Detected: {margin:.2f}% Net Margin.")
