import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BelYarn Quality Intelligence Platform",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BelYarn Quality Intelligence Platform")

uploaded_file = st.file_uploader(
    "Upload Quality Report",
    type=["xlsx"]
)

if uploaded_file:

    excel_file = pd.ExcelFile(uploaded_file)

    page = st.sidebar.selectbox(
        "Select Stage",
        excel_file.sheet_names
    )

    df = pd.read_excel(
        uploaded_file,
        sheet_name=page
    )

    st.header(page)

    st.write("Columns Found:")
    st.write(df.columns.tolist())

    st.dataframe(
        df.head(),
        use_container_width=True
    )
