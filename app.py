import streamlit as st
import pdfplumber
import pandas as pd
import re

# Webpage Interface (HTML-style)
st.set_page_config(page_title="ASI Scrutiny Portal", layout="wide")
st.title("🏭 ASI Scheme: Active Scrutiny Portal")

def seize_asi_content(file):
    with pdfplumber.open(file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    # These become your CSV Headers
    mapping = {
        "Total_Input": [r"Total Input", r"Operating Expenses"],
        "Total_Output": [r"Total Output", r"Gross Value"],
        "GVA": [r"GVA", r"Gross Value Added"],
        "Wages_Salaries": [r"Wages and Salaries", r"Total Wages"]
    }

    found = {}
    for header, keys in mapping.items():
        found[header] = 0.0
        for line in text.split('\n'):
            if any(re.search(k, line, re.IGNORECASE) for k in keys):
                nums = re.findall(r'\(?\d[\d,.]*\)?', line)
                if nums:
                    val = nums[0].replace(',', '')
                    if '(' in val: val = '-' + val.replace('(', '').replace(')', '')
                    found[header] = float(val)
                    break
    return pd.DataFrame([found])

# Web Interface Interaction
file = st.file_uploader("Upload ASI Scheme PDF", type="pdf")

if file:
    df = seize_asi_content(file)
    st.write("### 🔍 Extracted Data Preview")
    st.table(df) # Streamlined: Content under Headers
    
    # Download Portable CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Streamlined CSV", data=csv, file_name="asi_scrutiny.csv")
