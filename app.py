import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="ASI Smart Extractor", layout="wide")
st.title("📊 Smart Data Extraction Portal")

# Keywords jo headers pehchanne mein madad karenge
ANCHOR_KEYWORDS = ["description", "account", "material", "nsso", "amount", "sl. no.", "category"]

def find_actual_header(df):
    """Scan top 20 rows to find the row that looks like a header"""
    for i in range(min(len(df), 20)):
        row_values = [str(val).lower() for val in df.iloc[i].values]
        matches = sum(1 for key in ANCHOR_KEYWORDS if any(key in cell for cell in row_values))
        if matches >= 2: # Agar 2 ya zyada keywords mil gaye toh ye header hai
            return i
    return 0

def extract_vitals(df, filename):
    """Data clean karke vital points nikalna"""
    vitals = {"File Name": filename, "Total Value": 0, "Rows Found": len(df)}
    
    # Sabhi columns ko lowercase kar rahe hain search ke liye
    cols = [str(c).lower() for c in df.columns]
    
    # Smart logic for values (FTO 8 '24-25' or 'final Amt' etc.)
    target_cols = [c for c in df.columns if any(x in str(c).lower() for x in ['24-25', 'amount', 'value', 'sum of'])]
    
    if target_cols:
        # Numeric values convert karke sum nikalna
        vitals["Total Value"] = pd.to_numeric(df[target_cols[-1]], errors='coerce').sum()
        
    return vitals

# --- UI ---
uploaded_files = st.file_uploader("Upload All Files (FTO 8, Manpower, etc.)", accept_multiple_files=True)

if uploaded_files:
    extraction_results = []
    
    for f in uploaded_files:
        # File type ke hisaab se reading
        if f.name.endswith('.csv'):
            # Pehle raw read karo header dhundhne ke liye
            raw_df = pd.read_csv(f, header=None)
            header_row = find_actual_header(raw_df)
            f.seek(0)
            df = pd.read_csv(f, skiprows=header_row)
        else:
            # Excel Multi-sheet support
            xl = pd.ExcelFile(f)
            for sheet in xl.sheet_names:
                raw_df = pd.read_excel(f, sheet_name=sheet, header=None)
                header_row = find_actual_header(raw_df)
                df = pd.read_excel(f, sheet_name=sheet, skiprows=header_row)
                
                res = extract_vitals(df, f"{f.name} ({sheet})")
                extraction_results.append(res)
            continue # Excel sheets are handled inside the loop

        res = extract_vitals(df, f.name)
        extraction_results.append(res)

    # Output Table
    st.subheader("📋 Extraction Summary (Check Table)")
    summary_df = pd.DataFrame(extraction_results)
    st.dataframe(summary_df, use_container_width=True)

    # Download
    csv_data = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Extracted Data CSV", csv_data, "Extracted_ASI_Data.csv")
