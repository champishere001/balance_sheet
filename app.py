import streamlit as st
import pandas as pd
import pdfplumber
import io
import re

st.set_page_config(page_title="ASI Scrutiny Portal", layout="wide")
st.title("🛡️ ASI Scheme: Live Scrutiny & Conversion Portal")

def run_scrutiny(extracted_values):
    """Active Cross-Matching Logic"""
    st.subheader("🔍 Scrutiny: Cross-Matching Report")
    
    # 1. Net Profit Handshake
    pl_profit = extracted_values.get("Net Profit (P&L)", 0)
    cap_profit = extracted_values.get("Net Profit (Capital)", 0)
    
    if pl_profit > 0 and cap_profit > 0:
        if abs(pl_profit - cap_profit) < 1:
            st.success(f"✅ P&L Match: Net Profit of ₹{pl_profit:,.2f} matches across accounts.")
        else:
            st.error(f"❌ Mismatch: P&L Profit ({pl_profit:,.2f}) != Capital Account Profit ({cap_profit:,.2f})")
            st.warning("💡 Suggestion: Check if the profit distribution ratio between partners is calculated correctly.")

    # 2. Balance Sheet Equality
    assets = extracted_values.get("Total Assets", 0)
    liabilities = extracted_values.get("Total Liabilities", 0)
    if assets > 0 and abs(assets - liabilities) < 1:
        st.success(f"✅ B/S Balanced: Assets and Liabilities match at ₹{assets:,.2f}")
    elif assets > 0:
        st.error("❌ B/S Imbalance: Total Assets do not match Total Liabilities.")

def process_pdf(file):
    all_dfs = []
    found_values = {}
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            text = page.extract_text() or ""
            
            # Seize Major Values for Scrutiny (based on Singla Industries sample)
            if "Net Profit" in text:
                nums = re.findall(r'[\d,.]+', text)
                if nums: found_values["Net Profit (P&L)"] = float(nums[-1].replace(',', ''))
            if "Total Rs." in text:
                nums = re.findall(r'[\d,.]+', text)
                if nums: found_values["Total Assets"] = float(nums[-1].replace(',', ''))
                found_values["Total Liabilities"] = float(nums[-1].replace(',', ''))

            for table in tables:
                all_dfs.append(pd.DataFrame(table))
    return all_dfs, found_values

# --- Main Interface ---
upload_type = st.sidebar.selectbox("Upload Format", ["PDF Document", "Multi-Sheet Excel"])
uploaded_file = st.file_uploader(f"Upload {upload_type}", type=["pdf", "xlsx", "xls"])

if uploaded_file:
    extracted_dfs = []
    vals = {}

    if upload_type == "PDF Document":
        extracted_dfs, vals = process_pdf(uploaded_file)
    else:
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        for name, df in excel_data.items():
            extracted_dfs.append(df)
            st.write(f"📂 Sheet: {name}")
            st.dataframe(df)

    # Display Tables and Scrutiny
    if extracted_dfs:
        st.subheader("📝 Extracted Data Tables")
        for i, df in enumerate(extracted_dfs):
            with st.expander(f"Table/Sheet {i+1}"):
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, f"table_{i+1}.csv", "text/csv")
        
        # Run the Live Scrutiny
        run_scrutiny(vals)
