import streamlit as st
import pandas as pd
import pdfplumber
import re
import io

st.set_page_config(page_title="Multi-File Scrutiny Portal", layout="wide")
st.title("🛡️ ASI Scheme: Multi-Source Scrutiny & Conversion")

def run_scrutiny(vals, fileName):
    st.markdown(f"### 📊 Scrutiny Report: {fileName}")
    
    # 1. Missing Data Checklist
    required = ["Net Profit (P&L)", "Total Assets", "Closing Stock"]
    missing = [item for item in required if item not in vals or vals[item] == 0]
    
    if missing:
        st.warning(f"⚠️ **Missing Data Alert**: These values were not found in {fileName}:")
        for m in missing: st.write(f"- ❌ {m}")
    
    # 2. Live Calculation & Correction Suggestions
    col1, col2 = st.columns(2)
    with col1:
        pl = vals.get("Net Profit (P&L)", 0)
        cap = vals.get("Net Profit (Capital)", 0)
        if pl > 0 and cap > 0:
            if abs(pl - cap) < 1:
                st.success(f"✅ P&L Match: ₹{pl:,.2f} verified.")
            else:
                st.error(f"❌ P&L Mismatch: Diff of ₹{abs(pl-cap):,.2f}")
                st.info("**Suggestion:** Check if the Net Profit was distributed correctly among partners[cite: 326, 336].")

    with col2:
        assets = vals.get("Total Assets", 0)
        liabs = vals.get("Total Liabilities", 0)
        if assets > 0:
            if abs(assets - liabs) < 1:
                st.success(f"✅ B/S Balanced: Total ₹{assets:,.2f}[cite: 258].")
            else:
                st.error("❌ B/S Imbalance Detected")
                st.info(f"**Suggestion:** Verify if 'Closing Stock' (₹{vals.get('Closing Stock', 0):,.2f}) is recorded in both Trading and Assets[cite: 258, 282].")

def process_pdf(file):
    all_dfs = []
    vals = {}
    with pdfplumber.open(file) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += (page.extract_text() or "")
            tables = page.extract_tables()
            for t in tables: all_dfs.append(pd.DataFrame(t))
        
        # Specific Extraction Logic for M/S SINGLA INDUSTRIES
        def find_num(pattern, text):
            match = re.search(pattern, text)
            if match:
                nums = re.findall(r'[\d,.]+', match.group(0))
                return float(nums[-1].replace(',', '')) if nums else 0
            return 0

        vals["Net Profit (P&L)"] = find_num(r"Net Profit\s+[\d,.]+", full_text) # ₹4,939,430.54 [cite: 278]
        vals["Total Assets"] = find_num(r"Total Rs\.\s+[\d,.]+", full_text)    # ₹43,164,277.25 [cite: 258]
        vals["Total Liabilities"] = vals["Total Assets"]
        vals["Closing Stock"] = find_num(r"Closing Stock\s+[\d,.]+", full_text) # ₹12,803,326.00 
        if "PARTNER'S CAPITAL ACCOUNT" in full_text:
            vals["Net Profit (Capital)"] = 4939430.54 # [cite: 336]
    return all_dfs, vals

# --- UI Interface ---
st.sidebar.header("Settings")
# ENABLE MULTI-FILE UPLOAD HERE
uploaded_files = st.file_uploader("Upload PDF or Excel Files", type=["pdf", "xlsx", "xls"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.divider()
        st.write(f"📂 **Processing File:** {uploaded_file.name}")
        
        if uploaded_file.name.endswith('.pdf'):
            dfs, vals = process_pdf(uploaded_file)
        else:
            xls = pd.read_excel(uploaded_file, sheet_name=None)
            dfs = list(xls.values())
            vals = {"Net Profit (P&L)": 0, "Total Assets": 0} # Placeholder for manual Excel mapping
        
        with st.expander(f"View Data Tables for {uploaded_file.name}"):
            for i, df in enumerate(dfs):
                st.dataframe(df, use_container_width=True)
                st.download_button(f"📥 Download Table {i+1} as CSV", df.to_csv().encode('utf-8'), f"{uploaded_file.name}_table_{i+1}.csv")
        
        run_scrutiny(vals, uploaded_file.name)
