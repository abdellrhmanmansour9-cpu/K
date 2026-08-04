import streamlit as st
import pandas as pd

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="BeLYarn Quality Control",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BeLYarn Quality Control")

# =====================================
# FILE UPLOAD
# =====================================

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

    # =====================================
    # CLEAN DATA
    # =====================================

    if "NEPS" in df.columns:

        df["NEPS"] = pd.to_numeric(
            df["NEPS"],
            errors="coerce"
        )

        # صفر = لم يتم التحليل

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

        if len(valid) > 0:

            if valid.max() <= 1:

                df["NER%"] = df["NER%"] * 100

    # =====================================
    # FILTERS
    # =====================================

    st.sidebar.header("🎯 Filters")

    if "Product" in df.columns:

        product = st.sidebar.selectbox(
            "Product",
            ["All"] + sorted(
                df["Product"].dropna().unique().tolist()
            )
        )

        if product != "All":

            df = df[df["Product"] == product]

    if "M.C" in df.columns:

        machine = st.sidebar.selectbox(
            "Machine",
            ["All"] + sorted(
                df["M.C"].dropna().unique().tolist()
            )
        )

        if machine != "All":

            df = df[df["M.C"] == machine]

    if "LOT" in df.columns:

        lot = st.sidebar.selectbox(
            "LOT",
            ["All"] + sorted(
                df["LOT"].dropna().unique().tolist()
            )
        )

        if lot != "All":

            df = df[df["LOT"] == lot]

    if "BLEND" in df.columns:

        blend = st.sidebar.selectbox(
            "Blend",
            ["All"] + sorted(
                df["BLEND"].dropna().unique().tolist()
            )
        )

        if blend != "All":

            df = df[df["BLEND"] == blend]

    # =====================================
    # TITLE
    # =====================================

    st.header(f"📊 {stage}")

    # =====================================
    # KPI
    # =====================================

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

    # =====================================
    # QUALITY SCORE
    # =====================================

    if "NEPS" in df.columns:

        quality_score = 100 - df["NEPS"].dropna().mean()

        quality_score = max(
            0,
            min(
                100,
                quality_score
            )
        )

        st.metric(
            "🏭 Quality Score",
            f"{quality_score:.1f}"
        )

    # =====================================
    # BEST / WORST
    # =====================================

    if "NEPS" in df.columns:

        temp = df.dropna(
            subset=["NEPS"]
        )

        if len(temp) > 0:

            if "Product" in temp.columns:

                best = temp.loc[
                    temp["NEPS"].idxmin()
                ]

                worst = temp.loc[
                    temp["NEPS"].idxmax()
                ]

                col1, col2 = st.columns(2)

                with col1:

                    st.success(
                        f"""
🏆 Best Product

{best['Product']}

NEPS = {best['NEPS']:.0f}
"""
                    )

                with col2:

                    st.error(
                        f"""
🔻 Worst Product

{worst['Product']}

NEPS = {worst['NEPS']:.0f}
"""
                    )

            elif "M.C" in temp.columns:

                best = temp.loc[
                    temp["NEPS"].idxmin()
                ]

                worst = temp.loc[
                    temp["NEPS"].idxmax()
                ]

                col1, col2 = st.columns(2)

                with col1:

                    st.success(
                        f"""
🏆 Best Machine

{best['M.C']}

NEPS = {best['NEPS']:.0f}
"""
                    )

                with col2:

                    st.error(
                        f"""
🔻 Worst Machine

{worst['M.C']}

NEPS = {worst['NEPS']:.0f}
"""
                    )

    # =====================================
    # DATA TABLE
    # =====================================

    st.subheader("📋 Data Preview")

    st.dataframe(
        df,
        use_container_width=True
    )
