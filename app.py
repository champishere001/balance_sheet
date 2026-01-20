import streamlit as st
import pdfplumber
import pandas as pd
import io

st.set_page_config(page_title="PDF to Multi-CSV Converter", layout="wide")
st.title("📂 PDF Table Segmenter & CSV Converter")

def convert_pdf_to_multi_csv(uploaded_file):
    all_tables = []
    
    with pdfplumber.open(uploaded_file) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                # Convert raw table to Clean DataFrame
                df = pd.DataFrame(table)
                
                # Basic Cleaning: Use first row as header if it looks like text
                if not df.empty:
                    df.columns = df.iloc[0]
                    df = df[1:]
                    
                    # Identify the table type by scanning content
                    table_text = df.to_string().lower()
                    name = f"Table_{i+1}_{j+1}"
                    if "opening stock" in table_text or "sales" in table_text:
                        name = "Trading_Account"
                    elif "depreciation" in table_text or "block" in table_text:
                        name = "Fixed_Assets_Schedule"
                    elif "capital" in table_text or "liabilities" in table_text:
                        name = "Balance_Sheet"
                    
                    all_tables.append({"name": name, "df": df})
    return all_tables

# --- UI Interface ---
file = st.file_uploader("Upload ASI PDF Document", type="pdf")

if file:
    with st.spinner("Extracting segments..."):
        segments = convert_pdf_to_multi_csv(file)
    
    if segments:
        st.success(f"Found {len(segments)} distinct tables/sections!")
        
        # Display and provide download for each
        for item in segments:
            with st.expander(f"📥 {item['name']}"):
                st.dataframe(item['df'], use_container_width=True)
                
                # Individual CSV Conversion
                csv_buffer = io.StringIO()
                item['df'].to_csv(csv_buffer, index=False)
                
                st.download_button(
                    label=f"Download {item['name']}.csv",
                    data=csv_buffer.getvalue(),
                    file_name=f"{item['name']}.csv",
                    mime="text/csv"
                )
    else:
        st.error("No tables detected. The PDF might be an image/scan. Try OCR-enabled PDF.")
