import streamlit as st
import pandas as pd
import re
from fuzzywuzzy import process

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="ASI Audit Pro",
    layout="wide"
)

st.title("🛡️ ASI Master Scrutiny & Analysis Engine")

# =================================================
# CONFIGURATION
# =================================================
VITAL_COLUMNS = [
    "description", "particular", "item", "details",
    "amount", "value", "total", "24-25", "2024-25"
]

AUDIT_TARGETS = {
    "Total Assets": [
        "total assets", "fixed assets",
        "closing balance", "balance sheet total"
    ],
    "Total Wages": [
        "wages", "wages & salaries", "salaries",
        "emoluments", "manpower cost", "labour charges"
    ],
    "Turnover": [
        "sales", "turnover", "total output",
        "value of output", "production and sale"
    ],
    "Raw Material": [
        "raw material", "material consumed",
        "consumption of raw material"
    ]
}

# =================================================
# SMART FILE LOADER (HEADER DETECTION)
# =================================================
def smart_load(file):
    if file.name.endswith(".csv"):
        raw = pd.read_csv(file, header=None)
    else:
        raw = pd.read_excel(file, header=None)

    header_idx = 0
    for i in range(min(len(raw), 25)):
        row = raw.iloc[i].astype(str).str.lower().tolist()
        matches = sum(
            1 for k in VITAL_COLUMNS if any(k in cell for cell in row)
        )
        if matches >= 3:
            header_idx = i
            break

    file.seek(0)
    if file.name.endswith(".csv"):
        df = pd.read_csv(file, skiprows=header_idx)
    else:
        df = pd.read_excel(file, skiprows=header_idx)

    return df, header_idx

# =================================================
# CORE EXTRACTION LOGIC (ROW + YEAR AWARE)
# =================================================
def extract_metric(df, target_key):
    df = df.copy()
    df.columns = [str(c).lower() for c in df.columns]

    # Identify description column
    desc_col = None
    for c in df.columns:
        if any(x in c for x in ["description", "particular", "item", "details"]):
            desc_col = c
            break

    if desc_col is None:
        return 0

    # Prefer 2024-25 column
    year_col = None
    for c in df.columns[::-1]:
        if any(y in c for y in ["24-25", "2024-25", "2024"]):
            year_col = c
            break

    numeric_cols = [year_col] if year_col else df.columns.difference([desc_col])

    total = 0.0

    for _, row in df.iterrows():
        text = str(row[desc_col]).lower()

        match = process.extractOne(text, AUDIT_TARGETS[target_key])
        if match and match[1] >= 75:
            for nc in numeric_cols:
                val = pd.to_numeric(
                    re.sub(r"[^\d.-]", "", str(row[nc])),
                    errors="coerce"
                )
                if pd.notna(val):
                    total += val

    return round(total, 2)

# =================================================
# SIDEBAR INPUT
# =================================================
st.sidebar.header("📁 Upload ASI Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload FTO-8 / Manpower / Consumption / Production files",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

# =================================================
# MAIN PROCESSING
# =================================================
if uploaded_files:
    results = []

    for f in uploaded_files:
        with st.status(f"Scanning {f.name} ..."):
            df, header_row = smart_load(f)

            record = {
                "File Name": f.name,
                "Detected Header Row": header_row + 1
            }

            for target in AUDIT_TARGETS:
                value = extract_metric(df, target)
                if value > 0:
                    record[target] = value

            results.append(record)

    master_df = pd.DataFrame(results).fillna(0)

    # =================================================
    # DASHBOARD
    # =================================================
    st.header("📊 Scrutiny Dashboard")
    st.dataframe(master_df, use_container_width=True)

    st.subheader("🔍 Intelligent Cross-Check")
    c1, c2, c3, c4 = st.columns(4)

    total_wages = master_df["Total Wages"].sum() if "Total Wages" in master_df.columns else 0
    total_sales = master_df["Turnover"].sum() if "Turnover" in master_df.columns else 0
    total_assets = master_df["Total Assets"].sum() if "Total Assets" in master_df.columns else 0
    total_rm = master_df["Raw Material"].sum() if "Raw Material" in master_df.columns else 0

    with c1:
        st.metric("Total Wages (24-25)", f"₹ {total_wages:,.2f}")
        if total_wages == 0:
            st.warning("Wages not detected")

    with c2:
        st.metric("Turnover (24-25)", f"₹ {total_sales:,.2f}")

    with c3:
        st.metric("Total Assets", f"₹ {total_assets:,.2f}")

    with c4:
        st.metric("Raw Material", f"₹ {total_rm:,.2f}")

    # =================================================
    # EXPORT
    # =================================================
    st.divider()
    csv_out = master_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Audit-Ready CSV",
        csv_out,
        "ASI_Consolidated_Audit_24_25.csv",
        "text/csv"
    )

else:
    st.info("⬅ Upload ASI schedules from the sidebar to start analysis")
