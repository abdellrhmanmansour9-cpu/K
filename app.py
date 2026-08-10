import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="BelYarn Quality Intelligence Platform",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BelYarn Quality Intelligence Platform")

# =====================================================
# UPLOAD FILE
# =====================================================

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

    df = pd.read_excel(uploaded_file, sheet_name=page)

    # =====================================================
    # CLEAN COLUMN NAMES
    # =====================================================

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # =====================================================
    # NUMERIC COLUMNS
    # =====================================================

    numeric_cols = [
        "Act.Count",
        "Count",
        "C.V",
        "CV",
        "CVm",
        "C.V m",
        "THIN",
        "THICK",
        "NEPS",
        "IPI",
        "H",
        "RKM",
        "ELG",
        "Bforce",
        "Twist"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # =====================================================
    # FILTERS
    # =====================================================

    st.sidebar.header("Filters")

    if "Product" in df.columns:

        product = st.sidebar.selectbox(
            "Product",
            ["All"] +
            sorted(
                df["Product"]
                .dropna()
                .astype(str)
                .unique()
            )
        )

        if product != "All":
            df = df[df["Product"].astype(str) == product]

    if "LOT" in df.columns:

        lot = st.sidebar.selectbox(
            "LOT",
            ["All"] +
            sorted(
                df["LOT"]
                .dropna()
                .astype(str)
                .unique()
            )
        )

        if lot != "All":
            df = df[df["LOT"].astype(str) == lot]

    if "BLEND" in df.columns:

        blend = st.sidebar.selectbox(
            "Blend",
            ["All"] +
            sorted(
                df["BLEND"]
                .dropna()
                .astype(str)
                .unique()
            )
        )

        if blend != "All":
            df = df[df["BLEND"].astype(str) == blend]

    st.header(page)

    # =====================================================
    # KPI SECTION
    # =====================================================

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Records", len(df))

    if "Product" in df.columns:
        c2.metric(
            "Products",
            df["Product"].nunique()
        )

    if "LOT" in df.columns:
        c3.metric(
            "Lots",
            df["LOT"].nunique()
        )

    if "C.V m" in df.columns:
        c4.metric(
            "Avg CVm",
            round(df["C.V m"].mean(), 2)
        )

    if "IPI" in df.columns:
        c5.metric(
            "Avg IPI",
            round(df["IPI"].mean(), 1)
        )

    if "RKM" in df.columns:
        c6.metric(
            "Avg RKM",
            round(df["RKM"].mean(), 1)
        )

    # =====================================================
    # PRODUCT ANALYSIS
    # =====================================================

    if "Product" in df.columns:

        st.subheader("Product Distribution")

        fig = px.histogram(
            df,
            x="Product",
            color="Product"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # CVM
    # =====================================================

    if (
        "Product" in df.columns and
        "C.V m" in df.columns
    ):

        st.subheader("CVm By Product")

        chart = (
            df.groupby(
                "Product",
                as_index=False
            )["C.V m"]
            .mean()
        )

        fig = px.bar(
            chart,
            x="Product",
            y="C.V m",
            color="C.V m",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # RKM
    # =====================================================

    if (
        "Product" in df.columns and
        "RKM" in df.columns
    ):

        st.subheader("RKM By Product")

        chart = (
            df.groupby(
                "Product",
                as_index=False
            )["RKM"]
            .mean()
        )

        fig = px.bar(
            chart,
            x="Product",
            y="RKM",
            color="RKM",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ======
