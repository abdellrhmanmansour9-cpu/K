import streamlit as st
import pandas as pd

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

    # Ignore NEPS = 0

    if "NEPS" in df.columns:

        df["NEPS"] = pd.to_numeric(
            df["NEPS"],
            errors="coerce"
        )

        df["NEPS"] = df["NEPS"].replace(
            0,
            pd.NA
        )

    st.header(f"📊 {stage}")

    # KPI

    c1, c2, c3, c4 = st.columns(4)

    if "COUNT" in df.columns:

        c1.metric(
            "Average Count",
            round(df["COUNT"].mean(), 2)
        )

    elif "Act.Count" in df.columns:

        c1.metric(
            "Average Count",
            round(df["Act.Count"].mean(), 2)
        )

    if "C.V" in df.columns:

        c2.metric(
            "Average CV",
            round(df["C.V"].mean(), 2)
        )

    elif "C.V m" in df.columns:

        c2.metric(
            "Average CVm",
            round(df["C.V m"].mean(), 2)
        )

    if "NEPS" in df.columns:

        c3.metric(
            "Average Neps",
            round(df["NEPS"].dropna().mean(), 0)
        )

    if "RKM" in df.columns:

        c4.metric(
            "Average RKM",
            round(df["RKM"].mean(), 2)
        )

    # Best & Worst

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

            if "M.C" in temp.columns:

                with col1:

                    st.success(
                        f"""
🏆 Best Machine

{best['M.C']}

Neps = {best['NEPS']}
"""
                    )

                with col2:

                    st.error(
                        f"""
🔻 Worst Machine

{worst['M.C']}

Neps = {worst['NEPS']}
"""
                    )

            elif "Product" in temp.columns:

                with col1:

                    st.success(
                        f"""
🏆 Best Product

{best['Product']}

Neps = {best['NEPS']}
"""
                    )

                with col2:

                    st.error(
                        f"""
🔻 Worst Product

{worst['Product']}

Neps = {worst['NEPS']}
"""
                    )

    st.subheader("📋 Data Preview")

    st.dataframe(
        df,
        use_container_width=True
    )
