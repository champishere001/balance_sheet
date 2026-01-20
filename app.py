import streamlit as st
import pandas as pd
import pdfplumber
import io
import re

st.set_page_config(page_title="ASI Live Scrutiny Portal", layout="wide")
st.title("🛡️ ASI Scheme: Live Scrutiny & Data Conversion")

def run_scrutiny(extracted_values):
    """Performs live calculations based on uploaded data"""
    st.subheader("🔍 Scrutiny: Live Calculation Report")
    
    pl_profit = extracted_values.get("Net Profit (P&L)", 0)
    cap_profit = extracted_values.get("Net Profit (Capital)", 0)
    assets = extracted_values.get("Total Assets", 0)
    liabilities = extracted_values.get("Total Liabilities", 0)

    col1, col2 = st.columns(2)

    with col1:
        # P&L Calculation Match
        if pl_profit > 0 or cap_profit > 0:
            if abs(pl_profit - cap_profit) < 1:
                st.success(f"✅ P&L Match: Net Profit of ₹{pl_profit:,.2f} verified.")
            else:
                st.error(f"❌ Mismatch: P&L ({pl_profit:,.2f}) vs Capital ({cap_profit:,.2f})")
                st.info("💡 Tip: Verify if the 'Interest on Capital' was deducted before Net Profit.")

    with col2:
        # Balance Sheet Accounting Equation
        if assets > 0 or liabilities > 0:
            if abs(assets - liabilities) < 1:
                st.success(f"✅ B/S Balanced: Total at ₹{assets:,.2f}")
            else:
                st.error(f"❌ B/S Imbalance: Assets ({assets:,.2f}) != Liabilities ({liabilities:,.2f})")

def process_excel(file):
    """Converts Multi-Sheet Excel into searchable data for scrutiny"""
    all_dfs = pd.read_excel(file, sheet_name=None)
    vals = {}
    for sheet_name, df in all_dfs.items():
        # Search for specific values within the cells
        for col in df.columns:
            if "Net Profit" in str(col):
                vals["Net Profit (P&L)"] = df[col].iloc[-1]
            if "Total" in str(col):
                vals["Total Assets"] = df[col].iloc[-1]
    return all_dfs, vals

def process_pdf(file):
    """Existing PDF extraction logic"""
    all_dfs = []
    found_values = {}
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            # Regex to find values from M/S SINGLA INDUSTRIES format
            if "Net Profit" in text:
                nums = re.findall(r'[\d,.]+', text)
                if nums: found_values["Net Profit (P&L)"] = float(nums[-1].replace(',', ''))
            if "Total Rs." in text:
                nums = re.findall(r'[\d,.]+', text)
                if nums: 
                    found_values["Total Assets"] = float(nums[-1].replace(',', ''))
                    found_values["Total Liabilities"] = float(nums[-1].replace(',', ''))
            
            tables = page.extract_tables()
            for table in tables:
                all_dfs.append(pd.DataFrame(table))
    return all_dfs, found_values

# --- UI Interface ---
upload_type = st.sidebar.selectbox("Select Upload Format", ["PDF Document", "Multi-Sheet Excel"])
uploaded_file = st.file_uploader(f"Upload {upload_type}", type=["pdf", "xlsx", "xls"])

if uploaded_file:
    data_to_show = {}
    vals = {}

    if upload_type == "PDF Document":
        dfs, vals = process_pdf(uploaded_file)
        for i, df in enumerate(dfs): data_to_show[f"Table {i+1}"] = df
    else:
        data_to_show, vals = process_excel(uploaded_file)

    # Output Display
    st.subheader("📝 Extracted Data Tables")
    for name, df in data_to_show.items():
        with st.expander(name):
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download {name} CSV", csv, f"{name}.csv")
    
    # Trigger Live Calculations
    run_scrutiny(vals)
