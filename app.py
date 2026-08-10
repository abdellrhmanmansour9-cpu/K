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
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "Upload Quality Report",
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

    # ==========================================
    # FILTERS
    # ==========================================

    st.sidebar.header("🎯 Filters")

    for col in ["Product", "LOT", "BLEND", "M.C"]:

        if col in df.columns:

            selected = st.sidebar.selectbox(
                col,
                ["All"] +
                sorted(
                    df[col]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
            )

            if selected != "All":

                df = df[
                    df[col]
                    .astype(str)
                    == selected
                ]

    # ==========================================
    # NUMERIC CONVERSION
    # ==========================================

    for col in df.columns:

        try:
            df[col] = pd.to_numeric(
                df[col],
                errors="ignore"
            )
        except:
            pass

    # ==========================================
    # HEADER
    # ==========================================

    st.header(f"📊 {stage}")

    # ==========================================
    # KPI
    # ==========================================

    kpi_cols = st.columns(6)

    kpi_cols[0].metric(
        "Records",
        len(df)
    )

    if "Product" in df.columns:
        kpi_cols[1].metric(
            "Products",
            df["Product"].nunique()
        )

    if "LOT" in df.columns:
        kpi_cols[2].metric(
            "Lots",
            df["LOT"].nunique()
        )

    if "BLEND" in df.columns:
        kpi_cols[3].metric(
            "Blends",
            df["BLEND"].nunique()
        )

    if "RKM" in df.columns:
        kpi_cols[4].metric(
            "RKM Avg",
            round(df["RKM"].mean(), 2)
        )

    if "C.V m" in df.columns:
        kpi_cols[5].metric(
            "CVm Avg",
            round(df["C.V m"].mean(), 2)
        )
    elif "C.V" in df.columns:
        kpi_cols[5].metric(
            "CV Avg",
            round(df["C.V"].mean(), 2)
        )

    # ==========================================
    # QUALITY SCORE
    # ==========================================

    if "RKM" in df.columns:

        score = max(
            0,
            min(
                100,
                df["RKM"].mean() * 5
            )
        )

        st.subheader("🎯 Quality Score")

        st.progress(score / 100)

        st.metric(
            "Overall Quality Score",
            f"{score:.1f}%"
        )

    # ==========================================
    # PRODUCT ANALYSIS
    # ==========================================

    if (
        "Product" in df.columns
        and
        "RKM" in df.columns
    ):

        st.subheader("🏆 RKM By Product")

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

    if (
        "Product" in df.columns
        and
        "NEPS" in df.columns
    ):

        st.subheader("📈 NEPS By Product")

        chart = (
            df.groupby(
                "Product",
                as_index=False
            )["NEPS"]
            .mean()
        )

        fig = px.bar(
            chart,
            x="Product",
            y="NEPS",
            color="NEPS",
            text_auto=".0f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # MACHINE ANALYSIS
    # ==========================================

    if (
        "M.C" in df.columns
        and
        "C.V" in df.columns
    ):

        st.subheader("📊 CV By Machine")

        chart = (
            df.groupby(
                "M.C",
                as_index=False
            )["C.V"]
            .mean()
        )

        fig = px.bar(
            chart,
            x="M.C",
            y="C.V",
            color="C.V",
            text_auto=".2f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if (
        "M.C" in df.columns
        and
        "NEPS" in df.columns
    ):

        st.subheader("🟠 NEPS By Machine")

        chart = (
            df.groupby(
                "M.C",
                as_index=False
            )["NEPS"]
            .mean()
        )

        fig = px.bar(
            chart,
            x="M.C",
            y="NEPS",
            color="NEPS",
            text_auto=".0f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if (
        "M.C" in df.columns
        and
        "NER%" in df.columns
    ):

        st.subheader("✅ Efficiency By Machine")

        chart = (
            df.groupby(
                "M.C",
                as_index=False
            )["NER%"]
            .mean()
        )

        fig = px.bar(
            chart,
            x="M.C",
            y="NER%",
            color="NER%",
            text_auto=".1f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # BLEND ANALYSIS
    # ==========================================

    if (
        "BLEND" in df.columns
        and
        "NEPS" in df.columns
    ):

        st.subheader("🧵 NEPS By Blend")

        chart = (
            df.groupby(
                "BLEND",
                as_index=False
            )["NEPS"]
            .mean()
        )

        fig = px.bar(
            chart,
            x="BLEND",
            y="NEPS",
            color="NEPS"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # SCATTER CHARTS
    # ==========================================

    if (
        "RKM" in df.columns
        and
        "C.V m" in df.columns
    ):

        st.subheader("📉 RKM vs CVm")

        fig = px.scatter(
            df,
            x="C.V m",
            y="RKM",
            color="Product"
            if "Product" in df.columns
            else None
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================================
    # RAW DATA
    # ==========================================

    with st.expander("📋 Raw Data"):

        st.dataframe(
            df,
            use_container_width=True
        )
