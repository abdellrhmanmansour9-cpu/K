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

    df.columns = df.columns.astype(str).str.strip()

    # -----------------------------
    # Filters
    # -----------------------------

    st.sidebar.header("🎯 Filters")

    filter_columns = [
        "Product",
        "LOT",
        "BLEND",
        "M.C"
    ]

    for col in filter_columns:

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

    # -----------------------------
    # Numeric Conversion
    # -----------------------------

    numeric_cols = [
        "COUNT",
        "Act.Count",
        "Twist",
        "C.V",
        "C.V m",
        "NEPS",
        "NER%",
        "NOILS",
        "THIN",
        "THICK",
        "IPI",
        "H",
        "RKM",
        "ELG",
        "Bforce"
    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    st.header(f"📊 {page}")

    # -----------------------------
    # KPI
    # -----------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Records",
        len(df)
    )

    if "LOT" in df.columns:
        c2.metric(
            "Lots",
            df["LOT"].nunique()
        )

    if "BLEND" in df.columns:
        c3.metric(
            "Blends",
            df["BLEND"].nunique()
        )

    if "Product" in df.columns:
        c4.metric(
            "Products",
            df["Product"].nunique()
        )

    if "M.C" in df.columns:
        c5.metric(
            "Machines",
            df["M.C"].nunique()
        )

    # -----------------------------
    # Card / Breaker / Finisher
    # -----------------------------

    if "C.V" in df.columns:

        st.subheader("📈 CV Analysis")

        metric1, metric2 = st.columns(2)

        metric1.metric(
            "Average CV",
            round(df["C.V"].mean(), 2)
        )

        if "NEPS" in df.columns:
            metric2.metric(
                "Average NEPS",
                round(df["NEPS"].mean(), 0)
            )

        if "M.C" in df.columns:

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
                text_auto=".2f",
                title="CV By Machine"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # -----------------------------
    # NEPS
    # -----------------------------

    if (
        "M.C" in df.columns
        and
        "NEPS" in df.columns
    ):

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
            text_auto=".0f",
            title="NEPS By Machine"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------
    # Efficiency
    # -----------------------------

    if (
        "M.C" in df.columns
        and
        "NER%" in df.columns
    ):

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
            text_auto=".1f",
            title="Efficiency By Machine"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------
    # Blend Analysis
    # -----------------------------

    if (
        "BLEND" in df.columns
        and
        "NEPS" in df.columns
    ):

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
            color="NEPS",
            title="NEPS By Blend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------
    # Comber
    # -----------------------------

    if "NOILS" in df.columns:

        st.subheader("🧶 Comber Analysis")

        st.metric(
            "Average NOILS",
            round(
                df["NOILS"].mean(),
                2
            )
        )

        if "M.C" in df.columns:

            chart = (
                df.groupby(
                    "M.C",
                    as_index=False
                )["NOILS"]
                .mean()
            )

            fig = px.bar(
                chart,
                x="M.C",
                y="NOILS",
                color="NOILS",
                text_auto=".2f",
                title="NOILS By Machine"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # -----------------------------
    # Winding
    # -----------------------------

    if "RKM" in df.columns:

        st.subheader("🧵 Winding Quality")

        k1, k2, k3, k4 = st.columns(4)

        k1.metric(
            "RKM Avg",
            round(df["RKM"].mean(), 2)
        )

        if "C.V m" in df.columns:
            k2.metric(
                "CVm Avg",
                round(df["C.V m"].mean(), 2)
            )

        if "IPI" in df.columns:
            k3.metric(
                "IPI Avg",
                round(df["IPI"].mean(), 1)
            )

        if "H" in df.columns:
            k4.metric(
                "Hairiness",
                round(df["H"].mean(), 2)
            )

        # RKM By Product

        if "Product" in df.columns:

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
                text_auto=".2f",
                title="RKM By Product"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # CVm By Product

        if (
            "Product" in df.columns
            and
            "C.V m" in df.columns
        ):

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
                text_auto=".2f",
                title="CVm By Product"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # RKM vs CVm

        if "C.V m" in df.columns:

            fig = px.scatter(
                df,
                x="C.V m",
                y="RKM",
                color="Product"
                if "Product" in df.columns
                else None,
                title="RKM vs CVm"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # -----------------------------
    # Machine Ranking
    # -----------------------------

    if (
        "M.C" in df.columns
        and
        "C.V" in df.columns
    ):

        ranking = (
            df.groupby(
                "M.C",
                as_index=False
            )["C.V"]
            .mean()
        )

        c1, c2 = st.columns(2)

        with c1:

            st.subheader(
                "🏆 Top Machines"
            )

            st.dataframe(
                ranking.nsmallest(
                    5,
                    "C.V"
                ),
                use_container_width=True
            )

        with c2:

            st.subheader(
                "🔻 Worst Machines"
            )

            st.dataframe(
                ranking.nlargest(
                    5,
                    "C.V"
                ),
                use_container_width=True
            )

    # -----------------------------
    # Raw Data
    # -----------------------------

    with st.expander("📋 Raw Data"):

        st.dataframe(
            df,
            use_container_width=True
        )
