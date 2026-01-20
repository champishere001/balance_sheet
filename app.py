import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="ASI Major Value Scrutiny", layout="wide")
st.title("🏭 ASI Scheme: Major Value Extraction & P&L Matching")

def extract_all_asi_values(file):
    with pdfplumber.open(file) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    
    # Comprehensive Mapping for All Major ASI Values
    mapping = {
        "Fixed_Capital": [r"Fixed Capital"],
        "Physical_Working_Capital": [r"Physical Working Capital", r"Stock of"],
        "Total_Inputs": [r"Total Input", r"Operating Expenses"],
        "Total_Outputs": [r"Total Output", r"Gross Value of Output"],
        "Depreciation": [r"Depreciation"],
        "GVA_Reported": [r"GVA", r"Gross Value Added"],
        "Wages_Salaries": [r"Wages and Salaries", r"Total Wages"],
        "Total_Persons": [r"Total Persons Engaged"]
    }

    found = {}
    lines = text.split('\n')
    for header, keywords in mapping.items():
        found[header] = 0.0
        for line in lines:
            if any(re.search(k, line, re.IGNORECASE) for k in keywords):
                nums = re.findall(r'\(?\d[\d,.]*\)?', line)
                if nums:
                    val = nums[0].replace(',', '')
                    if '(' in val: val = '-' + val.replace('(', '').replace(')', '')
                    found[header] = float(val)
                    break
    return found

file = st.file_uploader("Upload ASI Scheme Document", type="pdf")

if file:
    data = extract_all_asi_values(file)
    df = pd.DataFrame([data])
    
    # 📊 Display Major Values Table
    st.subheader("📋 Major Extraction Values")
    st.dataframe(df, use_container_width=True)

    # ⚖️ P&L Matching Logic
    calc_gva = data["Total_Outputs"] - data["Total_Inputs"]
    calc_nva = calc_gva - data["Depreciation"]
    diff = abs(calc_gva - data["GVA_Reported"])

    st.divider()
    st.subheader("🔍 P&L Scrutiny Analysis")

    if diff < 5: # Allowing small rounding margin
        st.success(f"✅ P&L Match: Calculated GVA ({calc_gva:,.2f}) matches Reported GVA.")
    else:
        st.error(f"❌ P&L Mismatch: There is a discrepancy of {diff:,.2f}")
        
        # 💡 Suggestion Engine
        st.markdown("### 🛠️ Suggestions to Resolve Mismatch")
        col1, col2 = st.columns(2)
        
        with col1:
            if data["Total_Outputs"] < data["Total_Inputs"]:
                st.warning("**Output Check**: Total Output is less than Input. Check if 'Closing Stock of Finished Goods' or 'Work-in-progress' was excluded.")
            st.info("**Depreciation**: Ensure Depreciation is NOT subtracted twice. It should be subtracted from GVA to get NVA, not from Output to get GVA.")
        
        with col2:
            st.info("**Input Validation**: Verify if 'Distributive Expenses' (Sales Tax, Freight) are properly handled as per ASI Block-H guidelines.")
            st.info("**Interest/Rent**: Check if Interest or Rent was mistakenly added to 'Total Inputs'. In ASI, these are part of 'Factor Payments', not Inputs.")

    # 📥 Download Streamlined CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Major Values CSV", data=csv, file_name="asi_major_values.csv")
