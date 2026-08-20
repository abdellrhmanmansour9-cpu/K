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
        "Stage",
        xls.sheet_names
    )

    df = pd.read_excel(
        uploaded_file,
        sheet_name=stage
    )

    df.columns = df.columns.str.strip()

    # تنظيف البيانات

    if "NEPS" in df.columns:

        df["NEPS"] = pd.to_numeric(
            df["NEPS"],
            errors="coerce"
        )

        df["NEPS"] = df["NEPS"].replace(
            0,
            pd.NA
        )

    # =========================
    # FILTERS
    # =========================

    st.sidebar.header("🎯 Filters")

    if "M.C" in df.columns:

        machine = st.sidebar.selectbox(
            "Machine",
            ["All"] +
            sorted(df["M.C"].astype(str).unique())
        )

        if machine != "All":

            df = df[
                df["M.C"].astype(str)
                == machine
            ]

    if "LOT" in df.columns:

        lot = st.sidebar.selectbox(
            "LOT",
            ["All"] +
            sorted(df["LOT"].astype(str).unique())
        )

        if lot != "All":

            df = df[
                df["LOT"].astype(str)
                == lot
            ]

    if "BLEND" in df.columns:

        blend = st.sidebar.selectbox(
            "Blend",
            ["All"] +
            sorted(df["BLEND"].dropna().unique())
        )

        if blend != "All":

            df = df[
                df["BLEND"] == blend
            ]

    st.header(f"📊 {stage}")

    # =========================
    # KPI
    # =========================

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Records",
        len(df)
    )

    if "C.V" in df.columns:

        k2.metric(
            "CV Avg",
            round(df["C.V"].mean(), 2)
        )

    if "NEPS" in df.columns:

        k3.metric(
            "Neps Avg",
            round(
                df["NEPS"]
                .dropna()
                .mean(),
                0
            )
        )

    if "NER%" in df.columns:

        ner = pd.to_numeric(
            df["NER%"],
            errors="coerce"
        )

        if ner.max() <= 1:

            ner = ner * 100

        k4.metric(
            "NER%",
            round(
                ner.mean(),
                1
            )
        )

    # =========================
    # CARD DASHBOARD
    # =========================

    if (
        "M.C" in df.columns
        and "C.V" in df.columns
        and "NEPS" in df.columns
    ):

        ranking = (
            df.groupby("M.C")
            .agg({
                "C.V": "mean",
                "NEPS": "mean"
            })
            .reset_index()
        )

        # Quality Status

        def status(row):

            if (
                row["C.V"] <= 3.2
                and row["NEPS"] <= 80
            ):
                return "🟢 Excellent"

            elif (
                row["C.V"] <= 3.5
                and row["NEPS"] <= 100
            ):
                return "🟡 Warning"

            else:
                return "🔴 Out Of Spec"

        ranking["Status"] = ranking.apply(
            status,
            axis=1
        )

        # Best & Worst

        ranking["Score"] = (
            ranking["C.V"] * 40
            +
            ranking["NEPS"] * 60
        )

        best = ranking.nsmallest(
            1,
            "Score"
        )

        worst = ranking.nlargest(
            1,
            "Score"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.success(
                f"""
🏆 BEST MACHINE

Machine : {best.iloc[0]['M.C']}

CV : {best.iloc[0]['C.V']:.2f}

Neps : {best.iloc[0]['NEPS']:.0f}

Status : {best.iloc[0]['Status']}
"""
            )

        with c2:

            st.error(
                f"""
🔻 WORST MACHINE

Machine : {worst.iloc[0]['M.C']}

CV : {worst.iloc[0]['C.V']:.2f}

Neps : {worst.iloc[0]['NEPS']:.0f}

Status : {worst.iloc[0]['Status']}
"""
            )

        st.subheader(
            "🎯 Machine Status"
        )

        st.dataframe(
            ranking.sort_values(
                "Score"
            ),
            use_container_width=True
        )

        # CV Chart

        st.subheader(
            "📈 CV Ranking"
        )

        fig_cv = px.bar(
            ranking.sort_values("C.V"),
            x="M.C",
            y="C.V",
            color="C.V",
            text_auto=".2f",
            color_continuous_scale="RdYlGn_r"
        )

        st.plotly_chart(
            fig_cv,
            use_container_width=True
        )

        # Neps Chart

        st.subheader(
            "🔥 Neps Ranking"
        )

        fig_neps = px.bar(
            ranking.sort_values("NEPS"),
            x="M.C",
            y="NEPS",
            color="NEPS",
            text_auto=".0f",
            color_continuous_scale="RdYlGn_r"
        )

        st.plotly_chart(
            fig_neps,
            use_container_width=True
        )

    with st.expander(
        "📋 Raw Data"
    ):

        st.dataframe(
            df,
            use_container_width=True
        )
