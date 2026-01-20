import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="ASI Scrutiny Portal", layout="wide")
st.title("🏭 ASI Scheme: Scrutiny & CSV Streamliner")

def seize_asi_data(file):
    with pdfplumber.open(file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    # Target ASI variables for the CSV Headers
    mapping = {
        "Total_Input": [r"Total Input", r"Total Operating Expenses"],
        "Total_Output": [r"Total Output", r"Gross Value of Output"],
        "GVA": [r"GVA", r"Gross Value Added"],
        "Net_Profit": [r"Net Profit", r"PAT"],
        "Total_Employees": [r"Total Persons Engaged", r"Number of Employees"]
    }

    found_row = {}
    lines = text.split('\n')
    for header, keywords in mapping.items():
        found_row[header] = 0.0
        for line in lines:
            if any(re.search(k, line, re.IGNORECASE) for k in keywords):
                nums = re.findall(r'\(?\d[\d,.]*\)?', line)
                if nums:
                    val = nums[0].replace(',', '')
                    if '(' in val: val = '-' + val.replace('(', '').replace(')', '')
                    found_row[header] = float(val)
                    break
    return pd.DataFrame([found_row])

# Web Interface
st.info("Upload your ASI Scheme PDF. The system will extract content into headers.")
file = st.file_uploader("Upload ASI Document", type="pdf")

if file:
    df = seize_asi_data(file)
    st.subheader("📊 Streamlined ASI Table")
    st.dataframe(df) # Content appears directly under headers
    
    # Scrutiny Check: GVA Calculation
    # GVA = Total Output - Total Input
    calculated_gva = df["Total_Output"][0] - df["Total_Input"][0]
    st.write(f"**Calculated GVA:** {calculated_gva:,.2f}")
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download ASI CSV", data=csv, file_name="asi_scrutiny.csv")
