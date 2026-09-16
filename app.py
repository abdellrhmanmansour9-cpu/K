import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="BeLYarn Quality Intelligence Platform",
    page_icon="🏭",
    layout="wide"
)

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

    # ---------------------------
    # Product Filter
    # ---------------------------

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

        df = df[df["Product"].astype(str) == product]

    # ---------------------------
    # Blend Filter
    # ---------------------------

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

        df = df[df["BLEND"].astype(str) == blend]
# ==========================================
# CARD DASHBOARD
# ==========================================

if "Card" in stage:

    st.header("🧶 Card Quality Dashboard")

    avg_cv = round(df["C.V"].mean(), 2)
    avg_neps = round(df["NEPS"].mean(), 2)
    avg_ner = round(df["NER%"].mean(), 2)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Lots", len(df))
    c2.metric("Avg CV", avg_cv)
    c3.metric("Avg NEPS", avg_neps)
    c4.metric("Avg NER%", avg_ner)

    card_score = round(
        (
            (100 - avg_cv * 10) * 0.45
            +
            (100 - avg_neps / 2) * 0.35
            +
            avg_ner * 0.20
        ),
        1
    )

    st.success(
        f"⭐ Card Quality Index : {card_score}%"
    )

    metric_df = pd.DataFrame({
        "Metric": ["CV", "NEPS", "NER%"],
        "Value": [avg_cv, avg_neps, avg_ner]
    })

    fig_bar = px.bar(
        metric_df,
        x="Metric",
        y="Value",
        color="Value",
        text="Value",
        title="Card Quality Overview"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    fig_cv = px.line(
        df,
        x="LOT",
        y="C.V",
        markers=True,
        title="CV Trend"
    )

    st.plotly_chart(
        fig_cv,
        use_container_width=True
    )

    fig_neps = px.line(
        df,
        x="LOT",
        y="NEPS",
        markers=True,
        title="NEPS Trend"
    )

    st.plotly_chart(
        fig_neps,
        use_container_width=True
    )

    fig_ner = px.line(
        df,
        x="LOT",
        y="NER%",
        markers=True,
        title="NER% Trend"
    )

    st.plotly_chart(
        fig_ner,
        use_container_width=True
    )

    st.subheader("🏆 Best Card Lots")

    best_df = df.sort_values(
        ["NER%", "C.V"],
        ascending=[False, True]
    ).head(5)

    st.dataframe(
        best_df,
        use_container_width=True
    )

    st.subheader("⚠️ Worst Card Lots")

    worst_df = df.sort_values(
        ["NEPS", "C.V"],
        ascending=False
    ).head(5)

    st.dataframe(
        worst_df,
        use_container_width=True
    )

    st.subheader("🚨 Card Outliers")

    outliers = df[
        (
            df["NEPS"]
            >
            (
                df["NEPS"].mean()
                +
                df["NEPS"].std()
            )
        )
        |
        (
            df["C.V"]
            >
            (
                df["C.V"].mean()
                +
                df["C.V"].std()
            )
        )
    ]

    st.dataframe(
        outliers,
        use_container_width=True
    )

    st.subheader("📄 Card Details")

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )

    st.stop()
    cv_col = "C.V m"
    ipi_col = "IPI"
    rkm_col = "RKM"
    elg_col = "ELG"
    bf_col = "Bforce"

    avg_cv = round(df[cv_col].mean(), 2)
    avg_ipi = round(df[ipi_col].mean(), 2)
    avg_rkm = round(df[rkm_col].mean(), 2)
    avg_elg = round(df[elg_col].mean(), 2)
    avg_bf = round(df[bf_col].mean(), 2)

    total_lots = len(df)

    # ---------------------------
    # TOP KPIs
    # ---------------------------

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Lots", total_lots)
    c2.metric("CV.M", avg_cv)
    c3.metric("IPI", avg_ipi)
    c4.metric("RKM", avg_rkm)
    c5.metric("ELG", avg_elg)
    c6.metric("BForce", avg_bf)

    # ---------------------------
    # Quality Index
    # ---------------------------

    quality_score = round(
        (
            (100 - avg_cv * 4)
            +
            (100 - avg_ipi / 3)
            +
            (avg_rkm * 4)
            +
            (avg_elg * 12)
            +
            (avg_bf / 4)
        ) / 5,
        1
    )

    st.success(f"⭐ Quality Index : {quality_score}%")

    # ---------------------------
    # Gauges
    # ---------------------------

    g1, g2, g3 = st.columns(3)

    with g1:

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=avg_cv,
                title={"text": "CV.M"},
                gauge={"axis": {"range": [0, 20]}}
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    with g2:

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=avg_ipi,
                title={"text": "IPI"},
                gauge={"axis": {"range": [0, 300]}}
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    with g3:

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=avg_rkm,
                title={"text": "RKM"},
                gauge={"axis": {"range": [0, 25]}}
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------
    # KPI BAR CHART
    # ---------------------------

    metric_df = pd.DataFrame({
        "Metric": ["CV.M", "IPI", "RKM", "ELG", "BForce"],
        "Value": [avg_cv, avg_ipi, avg_rkm, avg_elg, avg_bf]
    })

    fig_bar = px.bar(
        metric_df,
        x="Metric",
        y="Value",
        color="Value",
        text="Value"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # ---------------------------
    # Best Lots
    # ---------------------------

    st.subheader("🏆 Best Lots")

    best_df = df.sort_values(
        ["RKM", "Bforce"],
        ascending=False
    ).head(5)

    st.dataframe(
        best_df,
        use_container_width=True
    )

    # ---------------------------
    # Worst Lots
    # ---------------------------

    st.subheader("⚠️ Worst Lots")

    worst_df = df.sort_values(
        "IPI",
        ascending=False
    ).head(5)

    st.dataframe(
        worst_df,
        use_container_width=True
    )

    # ---------------------------
    # Radar
    # ---------------------------

    radar = go.Figure()

    radar.add_trace(
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

    st.plotly_chart(
        radar,
        use_container_width=True
    )

    # ---------------------------
    # Trends
    # ---------------------------

    if "LOT" in df.columns:

        fig_cv = px.line(
            df,
            x="LOT",
            y="C.V m",
            title="CV.M Trend",
            markers=True
        )

        st.plotly_chart(
            fig_cv,
            use_container_width=True
        )

        fig_ipi = px.line(
            df,
            x="LOT",
            y="IPI",
            title="IPI Trend",
            markers=True
        )

        st.plotly_chart(
            fig_ipi,
            use_container_width=True
        )

    # ---------------------------
    # Quality Map
    # ---------------------------

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
            ]
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True
        )

    # ---------------------------
    # PASS FAIL
    # ---------------------------

    status = []

    for _, row in df.iterrows():

        score = 0

        if row["IPI"] < df["IPI"].mean():
            score += 1

        if row["RKM"] > df["RKM"].mean():
            score += 1

        if row["ELG"] > df["ELG"].mean():
            score += 1

        if row["Bforce"] > df["Bforce"].mean():
            score += 1

        if row["C.V m"] < df["C.V m"].mean():
            score += 1

        status.append(
            "PASS" if score >= 3 else "FAIL"
        )

    df["Status"] = status

    fig_pie = px.pie(
        df,
        names="Status",
        color="Status",
        color_discrete_map={
            "PASS": "green",
            "FAIL": "red"
        }
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

    # ---------------------------
    # Outliers
    # ---------------------------

    st.subheader("🚨 Outliers")

    outliers = df[
        (df["IPI"] > df["IPI"].mean() + df["IPI"].std())
        |
        (df["RKM"] < df["RKM"].mean() - df["RKM"].std())
    ]

    st.dataframe(
        outliers,
        use_container_width=True
    )

    # ---------------------------
    # Statistics
    # ---------------------------

    st.subheader("📊 Statistics")

    stats = pd.DataFrame({

        "Metric": [
            "CV.M",
            "IPI",
            "RKM",
            "ELG",
            "BForce"
        ],

        "Min": [
            df["C.V m"].min(),
            df["IPI"].min(),
            df["RKM"].min(),
            df["ELG"].min(),
            df["Bforce"].min()
        ],

        "Average": [
            df["C.V m"].mean(),
            df["IPI"].mean(),
            df["RKM"].mean(),
            df["ELG"].mean(),
            df["Bforce"].mean()
        ],

        "Max": [
            df["C.V m"].max(),
            df["IPI"].max(),
            df["RKM"].max(),
            df["ELG"].max(),
            df["Bforce"].max()
        ]

    })

    st.dataframe(
        stats.round(2),
        use_container_width=True
    )

    # ---------------------------
    # Detailed Results
    # ---------------------------

    st.subheader("📄 Detailed Results")

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )

else:

    st.info(
        "Upload Report Of Quality Control BeLYarn.xlsx"
    )
