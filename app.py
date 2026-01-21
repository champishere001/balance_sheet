import streamlit as st
import pandas as pd
import re
from fuzzywuzzy import process

st.set_page_config(page_title="ASI Audit Pro", layout="wide")
st.title("🛡️ ASI Master Scrutiny & Analysis Engine")

# ==================================================
# CONFIG
# ==================================================
AUDIT_TARGETS = {
    "Total Assets": ["asset"],
    "Total Liabilities": ["liability", "capital"],
    "Total Wages": ["wages", "salary", "emoluments"],
    "Turnover": ["sales", "turnover", "output"],
    "Raw Material": ["raw material", "consumption"]
}

# ==================================================
# LOAD FILE
# ==================================================
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

# ==================================================
# CLEAN NUMBERS
# ==================================================
def clean_num(x):
    return pd.to_numeric(
        re.sub(r"[^\d.-]", "", str(x)),
        errors="coerce"
    )

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.header("📁 Upload Files")
files = st.sidebar.file_uploader(
    "Upload Balance Sheet / TB / ASI Schedules",
    accept_multiple_files=True,
    type=["csv", "xls", "xlsx"]
)

# ==================================================
# MAIN
# ==================================================
if files:
    final_summary = []

    for f in files:
        st.subheader(f"📄 {f.name}")
        df = load_file(f)
        df.columns = [str(c) for c in df.columns]

        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("### 🔧 Column Mapping (One-Time)")
        desc_col = st.selectbox(
            "Select Description / Particulars column",
            df.columns,
            key=f"{f.name}_desc"
        )

        num_cols = st.multiselect(
            "Select Amount / Dr / Cr column(s)",
            df.columns,
            key=f"{f.name}_num"
        )

        for target, keywords in AUDIT_TARGETS.items():
            total = 0.0
            for _, row in df.iterrows():
                text = str(row[desc_col]).lower()
                if any(k in text for k in keywords):
                    for nc in num_cols:
                        val = clean_num(row[nc])
                        if pd.notna(val):
                            total += val

            if total > 0:
                final_summary.append({
                    "File": f.name,
                    "Metric": target,
                    "Amount": round(total, 2)
                })

    # ==================================================
    # RESULT
    # ==================================================
    st.header("📊 Consolidated Audit Summary")
    result_df = pd.DataFrame(final_summary)

    if not result_df.empty:
        st.dataframe(result_df, use_container_width=True)

        st.subheader("🔍 Totals")
        for m in result_df["Metric"].unique():
            amt = result_df[result_df["Metric"] == m]["Amount"].sum()
            st.metric(m, f"₹ {amt:,.2f}")

        st.download_button(
            "📥 Download Audit CSV",
            result_df.to_csv(index=False).encode(),
            "ASI_Audit_Final.csv",
            "text/csv"
        )
    else:
        st.warning("No metrics detected. Please adjust column mapping.")

else:
    st.info("⬅ Upload balance sheet or ASI schedules to start")
