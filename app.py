import streamlit as st
import pandas as pd
import re

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="ASI Audit Pro", layout="wide")
st.title("🛡️ ASI Master Scrutiny & Analysis Engine")

# =====================================================
# UTILITY FUNCTIONS
# =====================================================
def clean_number(x):
    return pd.to_numeric(
        re.sub(r"[^\d.-]", "", str(x)),
        errors="coerce"
    )

def drop_nill_and_unnamed_columns(df):
    cols_to_keep = []
    for c in df.columns:
        # Drop unnamed columns
        if str(c).lower().startswith("unnamed"):
            continue
        # Drop fully empty columns
        if df[c].isna().all():
            continue
        cols_to_keep.append(c)
    return df[cols_to_keep]

def get_valid_numeric_columns(df, ignore_cols):
    valid = []
    for c in df.columns:
        if c in ignore_cols:
            continue
        nums = df[c].apply(clean_number)
        if nums.notna().any() and nums.abs().sum() > 0:
            valid.append(c)
    return valid

def get_valid_text_columns(df):
    return [
        c for c in df.columns
        if df[c].astype(str).str.strip().replace("nan", "").ne("").any()
    ]

# =====================================================
# SIDEBAR UPLOAD
# =====================================================
st.sidebar.header("📁 Upload Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload Balance Sheet / Trial Balance / ASI Schedules",
    type=["csv", "xls", "xlsx"],
    accept_multiple_files=True
)

# =====================================================
# MAIN LOGIC
# =====================================================
if uploaded_files:
    consolidated = []

    for f in uploaded_files:
        st.divider()
        st.subheader(f"📄 {f.name}")

        # Load file
        if f.name.endswith(".csv"):
            df = pd.read_csv(f)
        else:
            df = pd.read_excel(f)

        # Clean dataframe
        df = drop_nill_and_unnamed_columns(df)

        if df.empty or df.shape[1] < 2:
            st.warning("File has no usable data after cleaning")
            continue

        st.dataframe(df.head(10), use_container_width=True)

        # -----------------------------
        # COLUMN SELECTION
        # -----------------------------
        st.markdown("### 🔧 Column Mapping")

        text_cols = get_valid_text_columns(df)
        desc_col = st.selectbox(
            "Select Description / Particulars column",
            text_cols,
            key=f"{f.name}_desc"
        )

        numeric_cols = get_valid_numeric_columns(df, [desc_col])

        if not numeric_cols:
            st.warning("⚠️ No amount columns found (listing-only Trial Balance)")
            continue

        amt_cols = st.multiselect(
            "Select Amount / Dr / Cr column(s)",
            numeric_cols,
            key=f"{f.name}_amt"
        )

        if not amt_cols:
            st.info("Select at least one numeric column to calculate totals")
            continue

        # -----------------------------
        # METRIC EXTRACTION
        # -----------------------------
        metrics = {
            "Assets": ["asset"],
            "Liabilities": ["liability", "capital"],
            "Wages": ["wages", "salary", "emoluments"],
            "Turnover": ["sales", "turnover", "output"],
            "Raw Material": ["raw material", "consumption"]
        }

        for metric, keywords in metrics.items():
            total = 0.0
            for _, row in df.iterrows():
                text = str(row[desc_col]).lower()
                if any(k in text for k in keywords):
                    for c in amt_cols:
                        val = clean_number(row[c])
                        if pd.notna(val):
                            total += val

            if total != 0:
                consolidated.append({
                    "File": f.name,
                    "Metric": metric,
                    "Amount": round(total, 2)
                })

    # =====================================================
    # FINAL OUTPUT
    # =====================================================
    st.divider()
    st.header("📊 Consolidated Audit Summary")

    if consolidated:
        result_df = pd.DataFrame(consolidated)
        st.dataframe(result_df, use_container_width=True)

        st.subheader("🔍 Totals")
        for m in result_df["Metric"].unique():
            amt = result_df[result_df["Metric"] == m]["Amount"].sum()
            st.metric(m, f"₹ {amt:,.2f}")

        st.download_button(
            "📥 Download Audit CSV",
            result_df.to_csv(index=False).encode("utf-8"),
            "ASI_Audit_Final.csv",
            "text/csv"
        )
    else:
        st.warning("No calculable data found across uploaded files")

else:
    st.info("⬅ Upload balance sheet / trial balance / ASI schedules to start")
