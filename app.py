import streamlit as st
import pandas as pd

# =================================
# PAGE CONFIG
# =================================

st.set_page_config(
    page_title="BeLYarn Quality System",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BeLYarn Quality System")
st.subheader("Quality Control Dashboard")

# =================================
# UPLOAD
# =================================

uploaded_file = st.file_uploader(
    "Upload Weekly Report",
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

    st.header(f"📊 {sheet}")

    # ==========================
    # KPI CARD
    # ==========================

    cols = st.columns(4)

    if "COUNT" in df.columns:

        cols[0].metric(
            "Avg Count",
            f"{df['COUNT'].mean():.2f}"
        )

    elif "Act.Count" in df.columns:

        cols[0].metric(
            "Avg Count",
            f"{df['Act.Count'].mean():.2f}"
        )

    if "C.V" in df.columns:

        cols[1].metric(
            "Avg CV",
            f"{df['C.V'].mean():.2f}"
        )

    elif "C.V m" in df.columns:

        cols[1].metric(
            "Avg CVm",
            f"{df['C.V m'].mean():.2f}"
        )

    if "NEPS" in df.columns:

        cols[2].metric(
            "Avg Neps",
            f"{df['NEPS'].mean():.0f}"
        )

    if "NER%" in df.columns:

        cols[3].metric(
            "Avg NER%",
            f"{df['NER%'].mean():.1f}%"
        )

    elif "RKM" in df.columns:

        cols[3].metric(
            "Avg RKM",
            f"{df['RKM'].mean():.2f}"
        )

    # ==========================
    # BEST / WORST
    # ==========================

    if all(col in df.columns for col in ["C.V", "NEPS"]):

        ranking = df.copy()

        if "NER%" in df.columns:

            ranking["Quality Score"] = (
                (100 - ranking["NEPS"])
                +
                (100 - ranking["C.V"] * 10)
                +
                ranking["NER%"]
            )

        else:

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

        c1, c2 = st.columns(2)

        with c1:

            st.success(
                f"""
🏆 Best Machine

Machine : {best['M.C']}

CV : {best['C.V']:.2f}

Neps : {best['NEPS']:.0f}
"""
            )

        with c2:

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

    # ==========================
    # WINDING ANALYSIS
    # ==========================

    if "IPI" in df.columns:

        st.subheader("🧵 Winding Analysis")

        ranking = df.copy()

        ranking["Quality Score"] = (

            (100 - ranking["C.V m"])

            +

            (100 - (ranking["IPI"] / 10))

            +

            ranking["RKM"]

            +

            ranking["Bforce"]

        )

        ranking = ranking.sort_values(
            "Quality Score",
            ascending=False
        )

        best = ranking.iloc[0]
        worst = ranking.iloc[-1]

        c1, c2 = st.columns(2)

        with c1:

            st.success(
                f"""
🏆 Best Product

Product : {best.get('Product','N/A')}

CVm : {best['C.V m']:.2f}

IPI : {best['IPI']}

RKM : {best['RKM']:.2f}
"""
            )

        with c2:

            st.error(
                f"""
🔻 Worst Product

Product : {worst.get('Product','N/A')}

CVm : {worst['C.V m']:.2f}

IPI : {worst['IPI']}

RKM : {worst['RKM']:.2f}
"""
            )

    # ==========================
    # BLEND ANALYSIS
    # ==========================

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

    # ==========================
    # LOT ANALYSIS
    # ==========================

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

    # ==========================
    # RAW DATA
    # ==========================

    st.subheader("📋 Raw Data")

    st.dataframe(
        df,
        use_container_width=True
    )
