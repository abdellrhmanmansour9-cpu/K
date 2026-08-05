import streamlit as st
import pandas as pd
import plotly.express as px

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

    # =====================
    # FILTERS
    # =====================

    if "Product" in df.columns:

        product = st.sidebar.selectbox(
            "Product",
            ["All"] +
            sorted(df["Product"].dropna().unique())
        )

        if product != "All":

            df = df[
                df["Product"] == product
            ]

    if "M.C" in df.columns:

        machine = st.sidebar.selectbox(
            "Machine",
            ["All"] +
            sorted(
                df["M.C"]
                .astype(str)
                .unique()
            )
        )

        if machine != "All":

            df = df[
                df["M.C"]
                .astype(str)
                == machine
            ]

    st.header(stage)

    # =====================
    # CV CHART
    # =====================

    if (
        "M.C" in df.columns
        and
        "C.V" in df.columns
    ):

        machine_cv = (
            df.groupby("M.C")["C.V"]
            .mean()
            .reset_index()
            .sort_values(
                "C.V",
                ascending=False
            )
        )

        st.subheader(
            "📈 Average CV By Machine"
        )

        fig = px.bar(
            machine_cv,
            x="M.C",
            y="C.V",
            text_auto=".2f",
            color="C.V",
            color_continuous_scale="RdYlGn_r"
        )

        fig.update_layout(
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================
    # RAW DATA
    # =====================

    with st.expander(
        "Raw Data"
    ):

        st.dataframe(
            df,
            use_container_width=True
        )
