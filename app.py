import streamlit as st
import pandas as pd

st.title("BeLYarn Quality System")

uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx","xls"]
)

if uploaded_file:

    xls = pd.ExcelFile(uploaded_file)

    st.write("Sheets Found:")

    for sheet in xls.sheet_names:
        st.write(sheet)
