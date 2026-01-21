import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Smart ASI Converter", layout="wide")
st.title("🛡️ Smart Header Discovery & CSV Converter")

# Keywords used to identify the header row
ANCHOR_KEYWORDS = ["description", "account", "material", "nsso", "qty", "amount", "sl. no.", "category"]

def smart_convert_to_df(file):
    """Converts Excel/PDF to CSV logic and finds the header row automatically"""
    if file.name.endswith('.csv'):
        raw_df = pd.read_csv(file, header=None)
    else:
        # Load Excel (first sheet by default for discovery)
        raw_df = pd.read_excel(file, header=None)

    # --- STEP 1: FIND THE HEADER ---
    header_row_index = 0
    max_matches = 0
    
    for i in range(min(len(raw_df), 20)):  # Scan top 20 rows
        row_values = [str(val).lower() for val in raw_df.iloc[i].values]
        # Count keyword matches in this specific row
        matches = sum(1 for key in ANCHOR_KEYWORDS if any(key in cell for cell in row_values))
        
        if matches > max_matches:
            max_matches = matches
            header_row_index = i
            
    # --- STEP 2: RE-LOAD WITH CORRECT HEADER ---
    file.seek(0)
    if file.name.endswith('.csv'):
        clean_df = pd.read_csv(file, skiprows=header_row_index)
    else:
        clean_df = pd.read_excel(file, skiprows=header_row_index)
        
    return clean_df, header_row_index

# --- UI INTERFACE ---
st.info("Upload any file. The system will skip empty rows and find the headers by itself.")
uploaded_files = st.file_uploader("Upload ASI Files", accept_multiple_files=True)

if uploaded_files:
    for f in uploaded_files:
        with st.expander(f"Processing: {f.name}", expanded=True):
            # Extract
            df, found_at = smart_convert_to_df(f)
            
            st.success(f"Header found at Row {found_at + 1}")
            
            # Show the cleaned table
            st.dataframe(df.head(10), use_container_width=True)
            
            # Convert to CSV for Download
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label=f"📥 Download Clean {f.name} as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"{f.name.split('.')[0]}_Cleaned.csv",
                mime="text/csv"
            )

    st.divider()
    st.subheader("🛠️ Why this is better?")
    st.write("1. **Automatic Alignment:** It doesn't matter if data starts at Row 1 or Row 10.")
    st.write("2. **Format Neutral:** Converts Excel to CSV instantly in the background.")
    st.write("3. **Multi-File:** Process your FTO 8, Manpower, and Consumption files in one go.")
