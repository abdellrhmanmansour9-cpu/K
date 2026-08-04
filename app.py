import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BeLYarn Quality Control",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BeLYarn Quality Control")

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

    st.header(f"📊 {stage}")

    # =========================
    # KPI
    # =========================

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

        temp_neps = df["NEPS"].replace(0, pd.NA)

        c3.metric(
            "Average Neps",
            f"{temp_neps.dropna().mean():.0f}"
        )

    if "NER%" in df.columns:

        temp_ner = df["NER%"].replace(0, pd.NA)

        if len(temp_ner.dropna()) > 0:

            if temp_ner.dropna().max() <= 1:

                temp_ner = temp_ner * 100

        c4.metric(
            "Average NER%",
            f"{temp_ner.dropna().mean():.1f}%"
        )

    elif "RKM" in df.columns:

        c4.metric(
            "Average RKM",
            f"{df['RKM'].mean():.2f}"
        )

    # =========================
    # DATA PREVIEW
    # =========================

    st.subheader("📋 Data Preview")

    st.dataframe(
        df,
        use_container_width=True
    )
