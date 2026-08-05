import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BelYarn Quality Intelligence Platform",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BelYarn Quality Intelligence Platform")

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

    df.columns = df.columns.str.strip()

    # تجاهل النبس = 0

    if "NEPS" in df.columns:

        df["NEPS"] = pd.to_numeric(
            df["NEPS"],
            errors="coerce"
        )

        df["NEPS"] = df["NEPS"].replace(
            0,
            pd.NA
        )

    # فلتر منتج

    if "Product" in df.columns:

        product = st.sidebar.selectbox(
            "Select Product",
            ["All"] +
            sorted(
                df["Product"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        if product != "All":

            df = df[
                df["Product"] == product
            ]

    # فلتر ماكينة

    if "M.C" in df.columns:

        machine = st.sidebar.selectbox(
            "Select Machine",
            ["All"] +
            sorted(
                df["M.C"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        if machine != "All":

            df = df[
                df["M.C"].astype(str) == machine
            ]

    st.header(stage)

    st.dataframe(
        df,
        use_container_width=True
    )
