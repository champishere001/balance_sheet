import streamlit as st
import pandas as pd
import pdfplumber
import re
import io

st.set_page_config(page_title="ASI Vital Check Portal", layout="wide")
st.title("🛡️ ASI Universal Scrutiny & CSV Generator")

def universal_extractor(file):
    """Detects file type and fetches vital ASI data using fuzzy keywords"""
    vitals = {"Entity": "Unknown", "Total Assets": 0, "Net Profit": 0, "Sales": 0, "Wages": 0}
    
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            vitals["Entity"] = text.split('\n')[0][:50] # Captures top line as name
            # Keyword regex for various formats
            vitals["Total Assets"] = find_val(r"(Total\s+Assets|Total\s+Rs\.)", text)
            vitals["Net Profit"] = find_val(r"(Net\s+Profit|Profit\s+for\s+the\s+year)", text)
            vitals["Sales"] = find_val(r"(Sales|Revenue|Turnover)", text)
            vitals["Wages"] = find_val(r"(Wages|Manpower|Salaries)", text)
            
    else: # Excel/CSV Logic
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        vitals["Entity"] = file.name
        # Search columns for keywords
        col_str = " ".join(df.columns).lower()
        if '24-25' in col_str or 'final' in col_str:
            vitals["Total Assets"] = df.iloc[:, -1].sum() if "asset" in col_str else 0
            vitals["Net Profit"] = df.iloc[:, -1].sum() if "p&l" in col_str.lower() else 0

    return vitals

def find_val(term, text):
    match = re.search(term + r".{0,25}([\d,.]+)", text, re.IGNORECASE)
    if match:
        try: return float(match.group(2).replace(',', ''))
        except: return 0
    return 0

# --- UI Interface ---
files = st.file_uploader("Upload All Enterprise Files", accept_multiple_files=True)

if files:
    all_vitals = []
    for f in files:
        data = universal_extractor(f)
        all_vitals.append(data)
    
    # Create the Vital DataFrame
    vital_df = pd.DataFrame(all_vitals)
    
    # DISPLAY TABLE
    st.subheader("📊 Fetched Vital Data Table")
    st.dataframe(vital_df, use_container_width=True)
    
    # THE DOWNLOAD BUTTON (This solves your 'not generating' issue)
    csv_data = vital_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Vital Data CSV",
        data=csv_data,
        file_name="ASI_Vital_Check_Report.csv",
        mime="text/csv"
    )

    # ANALYSIS SECTION
    st.subheader("🔍 Automated Analysis")
    for index, row in vital_df.iterrows():
        if row['Total Assets'] > 0:
            st.success(f"✅ {row['Entity']}: Data fetched successfully. Assets: ₹{row['Total Assets']:,.2f}")
        else:
            st.warning(f"⚠️ {row['Entity']}: Vital cells not found. Check if headers are standard.")
