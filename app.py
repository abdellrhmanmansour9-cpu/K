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
    "Upload Quality Report",
    type=["xlsx"]
)

if uploaded_file:

    xls = pd.ExcelFile(uploaded_file)

    page = st.sidebar.selectbox(
        "Select Stage",
        xls.sheet_names
    )

    df = pd.read_excel(
        uploaded_file,
        sheet_name=page
    )

    df.columns = df.columns.str.strip()

    st.header(page)

    # FILTERS

    if "Product" in df.columns:

        product = st.sidebar.selectbox(
            "Product",
            ["All"] +
            sorted(
                df["Product"]
                .astype(str)
                .unique()
                .tolist()
            )
        )

        if product != "All":
            df = df[df["Product"].astype(str) == product]

    if "BLEND" in df.columns:

        blend = st.sidebar.selectbox(
            "Blend",
            ["All"] +
            sorted(
                df["BLEND"]
                .astype(str)
                .unique()
                .tolist()
            )
        )

        if blend != "All":
            df = df[df["BLEND"].astype(str) == blend]

    # KPI

    cols = st.columns(5)

    cols[0].metric(
        "Records",
        len(df)
    )

    if "RKM" in df.columns:
        cols[1].metric(
            "RKM Avg",
            round(df["RKM"].mean(),2)
        )

    if "C.V m" in df.columns:
        cols[2].metric(
            "CVm Avg",
            round(df["C.V m"].mean(),2)
        )

    if "IPI" in df.columns:
        cols[3].metric(
            "IPI Avg",
            round(df["IPI"].mean(),0)
        )

    if "H" in df.columns:
        cols[4].metric(
            "Hairiness",
            round(df["H"].mean(),2)
        )

    # RKM

    if "RKM" in df.columns:

        st.subheader("RKM By Product")

        rkm = (
            df.groupby(
                "Product",
                as_index=False
            )["RKM"]
            .mean()
        )

        fig = px.bar(
            rkm,
            x="Product",
            y="RKM",
            color="RKM",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # CVm

    if "C.V m" in df.columns:

        st.subheader("CVm By Product")

        cvm = (
            df.groupby(
                "Product",
                as_index=False
            )["C.V m"]
            .mean()
        )

        fig = px.bar(
            cvm,
            x="Product",
            y="C.V m",
            color="C.V m",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # NEPS

    if "NEPS" in df.columns:

        st.subheader("NEPS By Product")

        neps = (
            df.groupby(
                "Product",
                as_index=False
            )["NEPS"]
            .mean()
        )

        fig = px.bar(
            neps,
            x="Product",
            y="NEPS",
            color="NEPS",
            text_auto=".0f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # RKM vs CVm

    if (
        "RKM" in df.columns
        and
        "C.V m" in df.columns
    ):

        st.subheader(
            "RKM vs CVm"
        )

        fig = px.scatter(
            df,
            x="C.V m",
            y="RKM",
            color="Product"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.dataframe(
        df,
        use_container_width=True
    )
