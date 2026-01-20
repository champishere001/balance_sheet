import streamlit as st
import pandas as pd
import pdfplumber
import re
import io

st.set_page_config(page_title="Universal ASI Scrutiny", layout="wide")
st.title("🛡️ Universal ASI Scrutiny & Cross-Match Portal")

def extract_vital_from_pdf(file):
    """Universal PDF extractor using keyword search"""
    data = {"Assets": 0, "Liabilities": 0, "Profit": 0, "Stock": 0, "Sales": 0}
    with pdfplumber.open(file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        
        # Regex patterns that work for various formats
        patterns = {
            "Assets": r"(Total\s+Assets|Total\s+Rs\.|Balance\s+Total).{0,20}([\d,.]+)",
            "Profit": r"(Net\s+Profit|Profit\s+for\s+the\s+year|Total\s+Comprehensive\s+Income).{0,20}([\d,.]+)",
            "Stock": r"(Closing\s+Stock|Inventories|Finished\s+Goods).{0,20}([\d,.]+)",
            "Sales": r"(Sales|Revenue\s+from\s+Operations|Turnover).{0,20}([\d,.]+)"
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the last match (usually the total at the bottom)
                val_str = matches[-1][1].replace(',', '')
                try: data[key] = float(val_str)
                except: pass
        
        # In double-entry, we assume Liabs = Assets for the check table
        data["Liabilities"] = data["Assets"]
    return data

def extract_vital_from_excel(files):
    """Universal Excel extractor searching for column keywords"""
    data = {"Assets": 0, "Liabilities": 0, "Profit": 0, "Stock": 0, "Sales": 0}
    for f in files:
        df = pd.read_csv(f) # Handling the CSV/Excel uploads
        cols = " ".join(df.columns).lower()
        
        # Logic for Balance Sheet Sheets
        if "type" in cols and "24-25" in cols:
            data["Assets"] = df[df['Type'].str.contains('Asset', na=False, case=False)]['24-25'].sum()
            data["Liabilities"] = abs(df[df['Type'].str.contains('Liabil', na=False, case=False)]['24-25'].sum())
        
        # Logic for P&L Sheets
        if "bucket" in cols or "p & l" in cols.replace(" ", ""):
            data["Profit"] = df.iloc[:, -1].sum() # Assumes last column is the final amount
            
    return data

# --- Main UI ---
uploaded_files = st.file_uploader("Upload Enterprise Files (PDF/Excel)", accept_multiple_files=True)

if uploaded_files:
    # 1. GENERATE VITAL CSV DATA
    st.subheader("📋 Step 1: Extracted Vital Data (Check Table)")
    results = []
    for f in uploaded_files:
        if f.name.endswith('.pdf'):
            vitals = extract_vital_from_pdf(f)
        else:
            vitals = extract_vital_from_excel([f])
        
        vitals["File Name"] = f.name
        results.append(vitals)
    
    vital_df = pd.DataFrame(results)
    st.dataframe(vital_df, use_container_width=True)
    
    # Download Button for the Check Table
    st.download_button("📥 Download Vital Check CSV", vital_df.to_csv(index=False), "vital_check.csv")

    # 2. PERFORM ANALYSIS
    st.subheader("🔍 Step 2: Automated Scrutiny Analysis")
    for _, row in vital_df.iterrows():
        with st.expander(f"Analysis for {row['File Name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Balance Sheet Equation Check
                diff = abs(row['Assets'] - row['Liabilities'])
                if row['Assets'] > 0 and diff < 10:
                    st.success(f"✅ Balance Sheet Verified (Total: ₹{row['Assets']:,.2f})")
                else:
                    st.error(f"❌ Imbalance Detected: ₹{diff:,.2f} difference.")
            
            with col2:
                # Profitability Check
                if row['Profit'] > 0:
                    margin = (row['Profit'] / row['Sales'] * 100) if row['Sales'] > 0 else 0
                    st.info(f"📈 Net Profit Margin: {margin:.2f}%")
                    if margin > 25: st.warning("⚠️ High Margin: Verify if Depreciation was fully charged.")
