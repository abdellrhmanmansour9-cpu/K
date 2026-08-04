import streamlit as st
import pandas as pd

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="BeLYarn Quality System",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BeLYarn Quality System")
st.subheader("Quality Control Weekly Dashboard")

# ==================================
# FILE UPLOAD
# ==================================

uploaded_file = st.file_uploader(
    "Upload Weekly Quality Report",
    type=["xlsx", "xls"]
)

if uploaded_file:

    xls = pd.ExcelFile(uploaded_file)

    sheet = st.sidebar.selectbox(
        "Select Stage",
        xls.sheet_names
    )

    df = pd.read_excel(
        uploaded_file,
        sheet_name=sheet
    )

    df.columns = df.columns.str.strip()

    # ==================================
    # CLEANING
    # ==================================

    for col in df.columns:

        try:
            df[col] = pd.to_numeric(
                df[col],
                errors="ignore"
            )
        except:
            pass

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

    # ==================================
    # SIDEBAR FILTERS
    # ==================================

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

    # ==================================
    # KPI
    # ==================================

    st.header(f"📊 {sheet}")

    k1, k2, k3, k4 = st.columns(4)

    if "COUNT" in df.columns:

        k1.metric(
            "Average Count",
            f"{df['COUNT'].mean():.2f}"
        )

    elif "Act.Count" in df.columns:

        k1.metric(
            "Average Count",
            f"{df['Act.Count'].mean():.2f}"
        )

    if "C.V" in df.columns:

        k2.metric(
            "Average CV",
            f"{df['C.V'].mean():.2f}"
        )

    elif "C.V m" in df.columns:

        k2.metric(
            "Average CVm",
            f"{df['C.V m'].mean():.2f}"
        )

    if "NEPS" in df.columns:

        k3.metric(
            "Average Neps",
            f"{df['NEPS'].dropna().mean():.0f}"
        )

    if "NER%" in df.columns:

        k4.metric(
            "Average NER%",
            f"{df['NER%'].dropna().mean():.1f}%"
        )

    elif "RKM" in df.columns:

        k4.metric(
            "Average RKM",
            f"{df['RKM'].mean():.2f}"
        )

    # ==================================
    # MACHINE RANKING
    # ==================================

    if "M.C" in df.columns and "C.V" in df.columns:

        ranking = df.copy()

        if "NEPS" in ranking.columns:

            ranking = ranking[
                ranking["NEPS"].notna()
            ]

        if len(ranking) > 0:

            if "NER%" in ranking.columns:

                ranking["Quality Score"] = (

                    (100 - ranking["NEPS"])

                    +

                    (100 - ranking["C.V"] * 10)

                    +

                    ranking["NER%"]

                )

            elif "NEPS" in ranking.columns:

                ranking["Quality Score"] = (

                    (100 - ranking["NEPS"])

                    +

                    (100 - ranking["C.V"] * 10)

                )

            ranking = ranking.sort_values(
                "Quality Score",
                ascending=False
            )

            best = ranking.iloc[0]
            worst = ranking.iloc[-1]

            col1, col2 = st.columns(2)

            with col1:

                st.success(
                    f"""
🏆 Best Machine

Machine : {best['M.C']}

CV : {best['C.V']:.2f}

Neps : {best['NEPS']:.0f}
"""
                )

            with col2:

                st.error(
                    f"""
🔻 Worst Machine

Machine : {worst['M.C']}

CV : {worst['C.V']:.2f}

Neps : {worst['NEPS']:.0f}
"""
                )

            st.subheader("🏅 Ranking")

            st.dataframe(
                ranking,
                use_container_width=True
            )

    # ==================================
    # BLEND ANALYSIS
    # ==================================

    if "BLEND" in df.columns:

        st.subheader("🧶 Blend Analysis")

        blend_summary = (
            df.groupby("BLEND")
            .mean(numeric_only=True)
            .reset_index()
        )

        st.dataframe(
            blend_summary,
            use_container_width=True
        )

    # ==================================
    # LOT ANALYSIS
    # ==================================

    if "LOT" in df.columns:

        st.subheader("📦 LOT Analysis")

        selected_lot = st.selectbox(
            "Select LOT",
            sorted(df["LOT"].dropna().unique())
        )

        lot_data = df[
            df["LOT"] == selected_lot
        ]

        st.dataframe(
            lot_data,
            use_container_width=True
        )

    # ==================================
    # RAW DATA
    # ==================================

    st.subheader("📋 Raw Data")

    st.dataframe(
        df,
        use_container_width=True
    )
    # ==================================
# FILTERS
# ==================================

st.sidebar.header("🎯 Filters")

# LOT

if "LOT" in df.columns:

    lots = st.sidebar.multiselect(
        "LOT",
        sorted(df["LOT"].dropna().unique())
    )

    if lots:

        df = df[df["LOT"].isin(lots)]

# BLEND

if "BLEND" in df.columns:

    blends = st.sidebar.multiselect(
        "Blend",
        sorted(df["BLEND"].dropna().unique())
    )

    if blends:

        df = df[df["BLEND"].isin(blends)]

# MACHINE

if "M.C" in df.columns:

    machines = st.sidebar.multiselect(
        "Machine",
        sorted(df["M.C"].dropna().unique())
    )

    if machines:

        df = df[df["M.C"].isin(machines)]

# COUNT

if "COUNT" in df.columns:

    counts = st.sidebar.multiselect(
        "Count",
        sorted(df["COUNT"].dropna().unique())
    )

    if counts:

        df = df[df["COUNT"].isin(counts)]

# PRODUCT

if "Product" in df.columns:

    products = st.sidebar.multiselect(
        "Product",
        sorted(df["Product"].dropna().unique())
    )

    if products:

        df = df[df["Product"].isin(products)]

