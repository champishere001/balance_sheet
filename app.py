import streamlit as st
import pandas as pd
import numpy as np
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import cv2
import io
import re

st.set_page_config(page_title="Intelligent Cross-Check", layout="wide")
st.title("🔍 Intelligent Cross-Check (Excel + Scanned PDF)")

uploaded_file = st.file_uploader(
    "Upload Excel or Scanned PDF",
    type=["xlsx", "xls", "pdf"]
)

def clean_dataframe(df):
    df = df.dropna(axis=1, how="all")  # drop empty columns
    df = df.dropna(axis=0, how="all")  # drop empty rows
    df.columns = [str(c).strip() for c in df.columns]
    return df

def ocr_pdf_to_text(pdf_bytes):
    images = convert_from_bytes(pdf_bytes, dpi=300)
    full_text = ""

    for img in images:
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
        text = pytesseract.image_to_string(gray, config="--psm 6")
        full_text += "\n" + text

    return full_text

def text_to_table(text):
    rows = []
    for line in text.split("\n"):
        line = re.sub(r"\s{2,}", "|", line.strip())
        if "|" in line:
            rows.append(line.split("|"))

    if not rows:
        return None

    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    df = pd.DataFrame(rows)
    return clean_dataframe(df)

if uploaded_file:
    try:
        if uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
            df = clean_dataframe(df)

            st.success("Excel file processed successfully")
            st.dataframe(df, use_container_width=True)

        elif uploaded_file.name.endswith(".pdf"):
            st.info("Scanned PDF detected – running OCR")

            text = ocr_pdf_to_text(uploaded_file.read())
            df = text_to_table(text)

            if df is not None:
                st.success("Scanned PDF converted to table")
                st.dataframe(df, use_container_width=True)
            else:
                st.error("Could not detect tabular structure")

    except Exception as e:
        st.error(f"Error: {e}")
import streamlit as st
import pandas as pd
import numpy as np
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import cv2
import io
import re

st.set_page_config(page_title="Intelligent Cross-Check", layout="wide")
st.title("🔍 Intelligent Cross-Check (Excel + Scanned PDF)")

uploaded_file = st.file_uploader(
    "Upload Excel or Scanned PDF",
    type=["xlsx", "xls", "pdf"]
)

def clean_dataframe(df):
    df = df.dropna(axis=1, how="all")  # drop empty columns
    df = df.dropna(axis=0, how="all")  # drop empty rows
    df.columns = [str(c).strip() for c in df.columns]
    return df

def ocr_pdf_to_text(pdf_bytes):
    images = convert_from_bytes(pdf_bytes, dpi=300)
    full_text = ""

    for img in images:
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
        text = pytesseract.image_to_string(gray, config="--psm 6")
        full_text += "\n" + text

    return full_text

def text_to_table(text):
    rows = []
    for line in text.split("\n"):
        line = re.sub(r"\s{2,}", "|", line.strip())
        if "|" in line:
            rows.append(line.split("|"))

    if not rows:
        return None

    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    df = pd.DataFrame(rows)
    return clean_dataframe(df)

if uploaded_file:
    try:
        if uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
            df = clean_dataframe(df)

            st.success("Excel file processed successfully")
            st.dataframe(df, use_container_width=True)

        elif uploaded_file.name.endswith(".pdf"):
            st.info("Scanned PDF detected – running OCR")

            text = ocr_pdf_to_text(uploaded_file.read())
            df = text_to_table(text)

            if df is not None:
                st.success("Scanned PDF converted to table")
                st.dataframe(df, use_container_width=True)
            else:
                st.error("Could not detect tabular structure")

    except Exception as e:
        st.error(f"Error: {e}")
