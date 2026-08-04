import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================
# PAGE CONFIG
# ==================================

st.set_page_config(
    page_title="BELYARN Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BELYARN")
st.subheader("Quality Control Weekly Report")

# ==================================
# FILE UPLOAD
# ==================================

uploaded_file = st.file_uploader(
    "Upload Weekly Card Report",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is not None:

    # ==========================
    # READ FILE
    # ==========================

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()

    st.success("✅ File Uploaded Successfully")

    # ==========================
    # KPI
    # ==========================

    st.header("📊 KPI")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average Count",
        f"{df['COUNT'].mean():.2f}"
    )

    c2.metric(
        "Average CV",
        f"{df['CV'].mean():.2f}"
    )

    c3.metric(
        "Average Neps",
        f"{df['NEPS'].mean():.0f}"
    )

    c4.metric(
        "Average NRE%",
        f"{df['NRE%'].mean():.1f}%"
    )

    # ==========================
    # QUALITY SCORE
    # ==========================

    ranking = df.copy()

    ranking["Quality Score"] = (
        (100 - ranking["NEPS"])
        +
        (100 - (ranking["CV"] * 10))
        +
        ranking["NRE%"]
    )

    ranking = ranking.sort_values(
        "Quality Score",
        ascending=False
    )

    # ==========================
    # BEST & WORST MACHINE
    # ==========================

    best_machine = ranking.iloc[0]
    worst_machine = ranking.iloc[-1]

    st.header("🏆 Machine Performance")

    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"""
أفضل ماكينة

Machine : {best_machine['M/C']}

Count : {best_machine['COUNT']:.2f}

CV : {best_machine['CV']:.2f}

Neps : {best_machine['NEPS']:.0f}

NRE% : {best_machine['NRE%']:.2f}
"""
        )

    with col2:
        st.error(
            f"""
أسوأ ماكينة

Machine : {worst_machine['M/C']}

Count : {worst_machine['COUNT']:.2f}

CV : {worst_machine['CV']:.2f}

Neps : {worst_machine['NEPS']:.0f}

NRE% : {worst_machine['NRE%']:.2f}
"""
        )

    # ==========================
    # RANKING TABLE
    # ==========================

    st.header("🏅 Machine Ranking")

    st.dataframe(
        ranking,
        use_container_width=True
    )

    # ==========================
    # CV CHART
    # ==========================

    st.header("📈 CV By Machine")

    fig_cv = px.bar(
        ranking,
        x="M/C",
        y="CV",
        color="CV",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig_cv,
        use_container_width=True
    )

    # ==========================
    # NEPS CHART
    # ==========================

    st.header("📈 Neps By Machine")

    fig_neps = px.bar(
        ranking,
        x="M/C",
        y="NEPS",
        color="NEPS",
        text_auto=".0f"
    )

    st.plotly_chart(
        fig_neps,
        use_container_width=True
    )

    # ==========================
    # NRE CHART
    # ==========================

    st.header("📈 NRE% By Machine")

    fig_nre = px.bar(
        ranking,
        x="M/C",
        y="NRE%",
        color="NRE%",
        text_auto=".1f"
    )

    st.plotly_chart(
        fig_nre,
        use_container_width=True
    )

    # ==========================
    # DATA TABLE
    # ==========================

    st.header("📋 Raw Data")

    st.dataframe(
        df,
        use_container_width=True
    )
