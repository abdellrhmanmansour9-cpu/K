import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BeLYarn Quality System",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BeLYarn Quality Control System")

uploaded_file = st.file_uploader(
    "Upload Weekly Quality Report",
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

    # تجاهل النبس = صفر
    if "NEPS" in df.columns:
        df["NEPS"] = pd.to_numeric(
            df["NEPS"],
            errors="coerce"
        )
        df["NEPS"] = df["NEPS"].replace(
            0,
            pd.NA
        )

    # تجاهل الكفاءة = صفر
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

    # Filters

    st.sidebar.header("🎯 Filters")

    if "LOT" in df.columns:

        lots = st.sidebar.multiselect(
            "LOT",
            sorted(df["LOT"].dropna().unique())
        )

        if lots:
            df = df[df["LOT"].isin(lots)]

    if "BLEND" in df.columns:

        blends = st.sidebar.multiselect(
            "Blend",
            sorted(df["BLEND"].dropna().unique())
        )

        if blends:
            df = df[df["BLEND"].isin(blends)]

    if "M.C" in df.columns:

        machines = st.sidebar.multiselect(
            "Machine",
            sorted(df["M.C"].dropna().unique())
        )

        if machines:
            df = df[df["M.C"].isin(machines)]

    st.header(f"📊 {stage}")

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

    st.subheader("📋 Data Preview")

    st.dataframe(
        df,
        use_container_width=True
    )
