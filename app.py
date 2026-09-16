import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="BeLYarn Quality Intelligence Platform",
    page_icon="🏭",
    layout="wide"
)

# =========================
# STYLE
# =========================

st.markdown("""
<style>

.main {
    background-color:#0f172a;
}

div[data-testid="metric-container"]{
    background:#111827;
    border:1px solid #374151;
    padding:20px;
    border-radius:18px;
    text-align:center;
}

div[data-testid="metric-container"] label{
    font-size:20px !important;
    font-weight:bold;
}

div[data-testid="metric-container"] div{
    font-size:38px !important;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.title("🏭 BeLYarn Quality Intelligence Platform")

uploaded_file = st.file_uploader(
    "Upload Quality Report",
    type=["xlsx"]
)

if uploaded_file:

    xls = pd.ExcelFile(uploaded_file)

    stage = st.sidebar.selectbox(
        "Production Stage",
        xls.sheet_names
    )

    df = pd.read_excel(
        uploaded_file,
        sheet_name=stage
    )

    df.columns = [str(c).strip() for c in df.columns]

    # =========================
    # PRODUCT FILTER
    # =========================

    if "Product" in df.columns:

        product = st.sidebar.selectbox(
            "Product",
            sorted(
                df["Product"]
                .dropna()
                .astype(str)
                .unique()
            )
        )

        df = df[
            df["Product"].astype(str) == product
        ]

    # =========================
    # BLEND FILTER
    # =========================

    if "BLEND" in df.columns:

        blend = st.sidebar.selectbox(
            "Blend",
            sorted(
                df["BLEND"]
                .dropna()
                .astype(str)
                .unique()
            )
        )

        df = df[
            df["BLEND"].astype(str) == blend
        ]

    # =========================
    # KPI NAMES
    # =========================

    cv_col = "C.V m"
    ipi_col = "IPI"
    rkm_col = "RKM"
    elg_col = "ELG"
    bf_col = "Bforce"

    # =========================
    # TOP METRICS
    # =========================

    total_lots = len(df)

    avg_cv = round(df[cv_col].mean(), 2)
    avg_ipi = round(df[ipi_col].mean(), 2)
    avg_rkm = round(df[rkm_col].mean(), 2)
    avg_elg = round(df[elg_col].mean(), 2)
    avg_bf = round(df[bf_col].mean(), 2)

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Lots", total_lots)
    c2.metric("CV.M", avg_cv)
    c3.metric("IPI", avg_ipi)
    c4.metric("RKM", avg_rkm)
    c5.metric("ELG", avg_elg)
    c6.metric("BForce", avg_bf)

    st.markdown("---")

    # =========================
    # GAUGE CHARTS
    # =========================

    g1, g2, g3 = st.columns(3)

    with g1:

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_cv,
            title={"text":"CV.M"},
            gauge={
                "axis":{"range":[0,20]},
                "bar":{"color":"royalblue"}
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

    with g2:

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_ipi,
            title={"text":"IPI"},
            gauge={
                "axis":{"range":[0,300]},
                "bar":{"color":"orange"}
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

    with g3:

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_rkm,
            title={"text":"RKM"},
            gauge={
                "axis":{"range":[0,25]},
                "bar":{"color":"green"}
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =========================
    # BAR CHART
    # =========================

    metric_df = pd.DataFrame({

        "Metric":[
            "CV.M",
            "IPI",
            "RKM",
            "ELG",
            "BForce"
        ],

        "Value":[
            avg_cv,
            avg_ipi,
            avg_rkm,
            avg_elg,
            avg_bf
        ]

    })

    fig_bar = px.bar(
        metric_df,
        x="Metric",
        y="Value",
        color="Value",
        text="Value",
        title="Quality KPI Overview"
    )

    fig_bar.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # =========================
    # RADAR CHART
    # =========================

    fig_radar = go.Figure()

    fig_radar.add_trace(
        go.Scatterpolar(
            r=[
                avg_cv,
                avg_ipi,
                avg_rkm,
                avg_elg,
                avg_bf
            ],
            theta=[
                "CV.M",
                "IPI",
                "RKM",
                "ELG",
                "BForce"
            ],
            fill="toself"
        )
    )

    fig_radar.update_layout(
        title="Quality Profile",
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        )
    )

    st.plotly_chart(
        fig_radar,
        use_container_width=True
    )

    st.markdown("---")

    # =========================
    # CV TREND
    # =========================

    if "LOT" in df.columns:

        if cv_col in df.columns:

            fig_cv = px.line(
                df.sort_values("LOT"),
                x="LOT",
                y=cv_col,
                markers=True,
                title="CV.M Trend"
            )

            st.plotly_chart(
                fig_cv,
                use_container_width=True
            )

        if ipi_col in df.columns:

            fig_ipi = px.line(
                df.sort_values("LOT"),
                x="LOT",
                y=ipi_col,
                markers=True,
                title="IPI Trend"
            )

            st.plotly_chart(
                fig_ipi,
                use_container_width=True
            )

        if rkm_col in df.columns:

            fig_rkm = px.line(
                df.sort_values("LOT"),
                x="LOT",
                y=rkm_col,
                markers=True,
                title="RKM Trend"
            )

            st.plotly_chart(
                fig_rkm,
                use_container_width=True
            )

    st.markdown("---")

    # =========================
    # SCATTER QUALITY MAP
    # =========================

    if "LOT" in df.columns:

        fig_scatter = px.scatter(
            df,
            x="LOT",
            y="IPI",
            size="IPI",
            color="IPI",
            hover_data=[
                "RKM",
                "ELG",
                "Bforce"
            ],
            title="Quality Heat Map"
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True
        )

    st.markdown("---")

    # =========================
    # MIN AVG MAX
    # =========================

    st.subheader("📊 Statistics")

    stats = pd.DataFrame({

        "Metric":[
            "CV.M",
            "IPI",
            "RKM",
            "ELG",
            "BForce"
        ],

        "Min":[
            round(df[cv_col].min(),2),
            round(df[ipi_col].min(),2),
            round(df[rkm_col].min(),2),
            round(df[elg_col].min(),2),
            round(df[bf_col].min(),2)
        ],

        "Average":[
            round(df[cv_col].mean(),2),
            round(df[ipi_col].mean(),2),
            round(df[rkm_col].mean(),2),
            round(df[elg_col].mean(),2),
            round(df[bf_col].mean(),2)
        ],

        "Max":[
            round(df[cv_col].max(),2),
            round(df[ipi_col].max(),2),
            round(df[rkm_col].max(),2),
            round(df[elg_col].max(),2),
            round(df[bf_col].max(),2)
        ]

    })

    st.dataframe(
        stats,
        use_container_width=True
    )

    st.markdown("---")

    # =========================
    # DETAIL TABLE
    # =========================

    st.subheader("📄 Detailed Results")

    show_cols = []

    for c in [
        "LOT",
        "Act.Count",
        "C.V m",
        "IPI",
        "RKM",
        "ELG",
        "Bforce",
        "BLEND"
    ]:

        if c in df.columns:
            show_cols.append(c)

    st.dataframe(
        df[show_cols],
        use_container_width=True,
        height=500
    )

quality_score = round(
    (
        (100 - avg_cv * 4)
        +
        (100 - (avg_ipi / 3))
        +
        (avg_rkm * 4)
        +
        (avg_elg * 12)
        +
        (avg_bf / 4)
    ) / 5,
    1
)

st.markdown(
    f"""
    <div style='background:#16a34a;
                padding:20px;
                border-radius:15px;
                text-align:center'>
        <h1>⭐ Quality Index</h1>
        <h1>{quality_score}%</h1>
    </div>
    """,
    unsafe_allow_html=True
)

    st.info(
        "Upload Report Of Quality Control BeLYarn.xlsx"
    )
else:
