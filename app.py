import streamlit as st
import pandas as pd
import numpy as np
import math

# Try-except block to handle missing Plotly gracefully
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# --- PAGE CONFIG ---
st.set_page_config(page_title="ASI Forensic Audit Suite", layout="wide", page_icon="🕵️")

# --- FIXED CSS ---
st.markdown("""
    <style>
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #e0e0e0; 
    }
    </style>
    """, unsafe_allow_html=True) # Fixed the parameter name here

# ================= HELPER FUNCTIONS =================
def clean_df(df):
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if not df.empty:
        # Remove common "Total" rows that skew forensic results
        df = df[~df.iloc[:, 0].astype(str).str.contains("Total|Grand Total|Balance", case=False, na=False)]
    df.columns = [str(c).strip() for c in df.columns]
    return df

def get_first_digit(n):
    n = abs(n)
    if n < 1 or pd.isna(n): return None
    return int(str(n)[0])

def check_benford(series):
    digits = series.apply(get_first_digit).dropna()
    if len(digits) == 0: return None
    counts = digits.value_counts(normalize=True).sort_index()
    expected = pd.Series({i: math.log10(1 + 1/i) for i in range(1, 10)})
    return pd.DataFrame({"Actual": counts, "Expected": expected}).fillna(0)

# ================= APP UI =================
st.title("🛡️ ASI Intelligent Forensic Audit Suite")

if not PLOTLY_AVAILABLE:
    st.error("🚨 **Plotly is missing!** Please add `plotly` to your `requirements.txt` file and redeploy.")

uploaded_file = st.file_uploader("Upload Trial Balance / Ledger (Excel)", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df_raw = pd.read_excel(uploaded_file)
        df = clean_df(df_raw)
        
        # Identify numeric columns for the "Hard Look"
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not num_cols:
            st.error("No numeric columns found. Please check your Excel format.")
            st.stop()

        col_to_audit = st.sidebar.selectbox("Select Value Column", num_cols)
        
        # --- DASHBOARD METRICS ---
        total_val = df[col_to_audit].sum()
        m1, m2 = st.columns(2)
        m1.metric("Total Column Value", f"₹{total_val:,.2f}")
        m2.metric("Total Rows", len(df))

        tab1, tab2 = st.tabs(["🔍 Forensic Analysis", "🚩 Outlier Detection"])

        with tab1:
            st.subheader("Benford's Law (Fraud Detection)")
            ben_df = check_benford(df[col_to_audit])
            if ben_df is not None and PLOTLY_AVAILABLE:
                fig = px.bar(ben_df, barmode="group", title="Leading Digit Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            # Rule of 9 Check
            diff_input = st.number_input("Enter your Trial Balance difference (if any):", value=0.0)
            if diff_input != 0 and diff_input % 9 == 0:
                st.warning("🕵️ Possible Transposition Error: Your difference is divisible by 9.")

        with tab2:
            st.subheader("Statistical Outliers")
            z_scores = (df[col_to_audit] - df[col_to_audit].mean()) / df[col_to_audit].std()
            outliers = df[abs(z_scores) > 2]
            
            if not outliers.empty:
                st.write(f"Found {len(outliers)} entries with unusual values:")
                st.dataframe(outliers)
            else:
                st.success("No statistical outliers detected.")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Please upload an Excel file to begin.")
