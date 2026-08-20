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

    if "NEPS" in df.columns:

        df["NEPS"] = pd.to_numeric(
            df["NEPS"],
            errors="coerce"
        )

        df["NEPS"] = df["NEPS"].replace(
            0,
            pd.NA
        )

    # =====================
    # FILTERS
    # =====================

    st.sidebar.header("Filters")

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

    # =====================
    # KPI
    # =====================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Records",
        len(df)
    )

    if "C.V" in df.columns:

        c2.metric(
            "CV Avg",
            round(df["C.V"].mean(), 2)
        )

    if "NEPS" in df.columns:

        c3.metric(
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

        c4.metric(
            "NER Avg %",
            round(
                ner.mean(),
                1
            )
        )

    # =====================
    # MACHINE RANKING
    # =====================

    if (
        "M.C" in df.columns
        and
        "C.V" in df.columns
    ):

        ranking = (
            df.groupby("M.C")
            .agg({
                "C.V": "mean",
                "NEPS": "mean"
            })
            .reset_index()
        )

        ranking["Score"] = (
            ranking["C.V"] * 40
            +
            ranking["NEPS"] * 60
        )

        best = ranking
