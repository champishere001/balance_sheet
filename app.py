import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import numpy as np
import cv2
import io

st.title("🛡️ ASI Scrutiny: Scanned PDF to CSV Converter")

def process_scanned_pdf(file_bytes):
    # 1. Convert PDF pages to Images
    images = convert_from_bytes(file_bytes)
    all_data = []

    for i, image in enumerate(images):
        st.info(f"Processing Page {i+1} via OCR...")
        
        # 2. Image Pre-processing (Enhance contrast for better reading)
        open_cv_image = np.array(image)
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # 3. Perform OCR to find the table data
        # 'data' output gives us the positional coordinates of every word
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DATAFRAME)
        
        # Clean up empty OCR blocks
        df = data[data.conf > 30] # Only keep results with >30% confidence
        
        # Group text by line (top coordinate) to rebuild the table rows
        lines = df.groupby('block_num')
        page_content = []
        for _, line in lines:
            row_text = " ".join(line['text'].astype(str))
            page_content.append(row_text)
            
        all_data.append(pd.DataFrame(page_content, columns=[f"Page_{i+1}_Data"]))

    return all_data

# --- UI ---
uploaded_file = st.file_uploader("Upload Scanned Balance Sheet (PDF)", type="pdf")

if uploaded_file:
    file_bytes = uploaded_file.read()
    tables = process_scanned_pdf(file_bytes)
    
    for i, table in enumerate(tables):
        st.subheader(f"Extracted Table - Page {i+1}")
        st.dataframe(table, use_container_width=True)
        
        # Generate CSV
        csv = table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download Page {i+1} as CSV",
            data=csv,
            file_name=f"scanned_page_{i+1}.csv",
            mime="text/csv"
        )
