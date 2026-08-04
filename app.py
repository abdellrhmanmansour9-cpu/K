import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BeLYarn Quality Control",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BeLYarn Quality Control")

uploaded_file = st.file_uploader(
    "Upload Weekly Report",
    type=["xlsx"]
)

if uploaded_file:

    xls = pd.ExcelFile(uploaded_file)

    stage = st.sidebar.selectbox(
        "Select Stage",
        xls.sheet_names
    )

    df = pd.read_excel(
        uploaded_file,
        sheet_name=stage
    )

    st.header(stage)

    st.dataframe(
        df,
        use_container_width=True
    )
