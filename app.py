import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="BeLYarn Quality Control",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BeLYarn Quality Control Dashboard")

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
    # CLEAN DATA
    # =====================

    if "NEPS" in df.columns:
        df["NEPS"] = pd.to_numeric(
            df["NEPS"],
            errors="coerce"
        )
        df["NEPS"] = df["NEPS"].replace(
            0,
            pd.NA
        )

    if "NER%" in df.columns:
        df["NER%"] = pd.to_numeric(
            df["NER%"],
            errors="coerce"
        )
        df["NER%"] = df["NER%"].replace(
            0,
            pd.NA
        )

        valid = df["NER%"].dropna()

        if len(valid) > 0 and valid.max() <= 1:
            df["NER%"] = df["NER%"] * 100

    # =====================
    # FILTERS
    # =====================

    st.sidebar.header("🎯 Filters")

    if "Product" in df.columns:

        product = st.sidebar.selectbox(
            "Product",
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

    if "M.C" in df.columns:

        machine = st.sidebar.selectbox(
            "Machine",
            ["All"] +
            sorted(
                df["M.C"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        if machine != "All":
            df = df[
                df["M.C"] == machine
            ]

    if "LOT" in df.columns:

        lot = st.sidebar.selectbox(
            "LOT",
            ["All"] +
            sorted(
                df["LOT"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        if lot != "All":
            df = df[
                df["LOT"] == lot
            ]

    if "BLEND" in df.columns:

        blend = st.sidebar.selectbox(
            "Blend",
            ["All"] +
            sorted(
                df["BLEND"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        if blend != "All":
            df = df[
                df["BLEND"] == blend
            ]

    st.header(f"📊 {stage}")

    # =====================
    # KPI
    # =====================

    c1, c2, c3, c4 = st.columns(4)

    if "COUNT" in df.columns:
        c1.metric(
            "Average Count",
            f"{df['COUNT'].mean():.2f}"
        )

    elif "Act.Count" in df.columns:
        c1.metric(
            "Average Count",
            f"{df['Act.Count'].mean():.2f}"
        )

    if "C.V" in df.columns:
        c2.metric(
            "Average CV",
            f"{df['C.V'].mean():.2f}"
        )

    elif "C.V m" in df.columns:
        c2.metric(
            "Average CVm",
            f"{df['C.V m'].mean():.2f}"
        )

    if "NEPS" in df.columns:
        c3.metric(
            "Average Neps",
            f"{df['NEPS'].dropna().mean():.0f}"
        )

    if "NER%" in df.columns:

        c4.metric(
            "Average NER%",
            f"{df['NER%'].dropna().mean():.1f}%"
        )

    elif "RKM" in df.columns:

        c4.metric(
            "Average RKM",
            f"{df['RKM'].mean():.2f}"
        )

    # =====================
    # QUALITY GAUGE
    # =====================

    if "NEPS" in df.columns:

        score = max(
            0,
            min(
                100,
                100 - df["NEPS"]
                .dropna()
                .mean()
            )
        )

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=score,
                title={
                    "text":
                    "Quality Score"
                },
                gauge={
                    "axis": {
                        "range":[0,100]
                    },
                    "steps":[
                        {
                            "range":[0,50],
                            "color":"red"
                        },
                        {
                            "range":[50,75],
                            "color":"orange"
                        },
                        {
                            "range":[75,100],
                            "color":"green"
                        }
                    ]
                }
            )
        )

        st.plotly_chart(
            fig_gauge,
            use_container_width=True
        )

    # =====================
    # BEST & WORST
    # =====================

    if "NEPS" in df.columns:

        temp = df.dropna(
            subset=["NEPS"]
        )

        if len(temp) > 0:

            best = temp.loc[
                temp["NEPS"].idxmin()
            ]

            worst = temp.loc[
                temp["NEPS"].idxmax()
            ]

            col1, col2 = st.columns(2)

            label = (
                "Product"
                if "Product"
                in temp.columns
                else "M.C"
            )

            with col1:

                st.success(
                    f"""
🏆 Best

{best[label]}

NEPS = {best['NEPS']:.0f}
"""
                )

            with col2:

                st.error(
                    f"""
🔻 Worst

{worst[label]}

NEPS = {worst['NEPS']:.0f}
"""
                )

    # =====================
    # CHARTS
    # =====================

    if "M.C" in df.columns and "C.V" in df.columns:

        st.subheader("📈 CV By Machine")

        fig_cv = px.bar(
            df,
            x="M.C",
            y="C.V",
            color="C.V"
        )

        st.plotly_chart(
            fig_cv,
            use_container_width=True
        )

    if "M.C" in df.columns and "NEPS" in df.columns:

        st.subheader("📈 Neps By Machine")

        fig_neps = px.bar(
            df,
            x="M.C",
            y="NEPS",
            color="NEPS"
        )

        st.plotly_chart(
            fig_neps,
            use_container_width=True
        )

    if "Product" in df.columns and "C.V m" in df.columns:

        st.subheader("📈 CVm By Product")

        fig_cvm = px.bar(
            df,
            x="Product",
            y="C.V m",
            color="C.V m"
        )

        st.plotly_chart(
            fig_cvm,
            use_container_width=True
        )

    if "Product" in df.columns and "IPI" in df.columns:

        st.subheader("📈 IPI By Product")

        fig_ipi = px.bar(
            df,
            x="Product",
            y="IPI",
            color="IPI"
        )

        st.plotly_chart(
            fig_ipi,
            use_container_width=True
        )

    # =====================
    # PIVOT TABLE
    # =====================

    if "BLEND" in df.columns:

        st.subheader(
            "📊 Blend Analysis"
        )

        pivot = pd.pivot_table(
            df,
            values=[
                c for c in df.columns
                if c not in [
                    "LOT",
                    "BLEND",
                    "M.C",
                    "Product"
                ]
            ],
            index="BLEND",
            aggfunc="mean"
        )

        st.dataframe(
            pivot,
            use_container_width=True
        )

    # =====================
    # RAW DATA
    # =====================

    with st.expander(
        "📋 View Raw Data"
    ):

        st.dataframe(
            df,
            use_container_width=True
        )
