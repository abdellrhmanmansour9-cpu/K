import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="BelYarn Quality Intelligence Platform",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BelYarn Quality Intelligence Platform")

# ==========================================
# FILE UPLOAD
# ==========================================
uploaded_file = st.file_uploader(
    "Upload Weekly Report",
    type=["xlsx"]
)

if uploaded_file:

    # ==========================================
    # READ EXCEL
    # ==========================================
    xls = pd.ExcelFile(uploaded_file)

    stage = st.sidebar.selectbox(
        "Select Stage",
        xls.sheet_names
    )

    df = pd.read_excel(
        uploaded_file,
        sheet_name=stage
    )

    # ==========================================
    # CLEAN COLUMNS
    # ==========================================
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ==========================================
    # NUMERIC CONVERSIONS
    # ==========================================
    numeric_cols = [
        "C.V",
        "CV",
        "NEPS",
        "NER%",
        "RKM"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    if "NEPS" in df.columns:
        df["NEPS"] = df["NEPS"].replace(
            0,
            pd.NA
        )

    # ==========================================
    # FILTERS
    # ==========================================
    st.sidebar.header("🎯 Filters")

    if "M.C" in df.columns:

        machine = st.sidebar.selectbox(
            "Machine",
            ["All"]
            +
            sorted(
                df["M.C"]
                .astype(str)
                .dropna()
                .unique()
                .tolist()
            )
        )

        if machine != "All":
            df = df[
                df["M.C"].astype(str)
                == machine
            ]

    if "LOT" in df.columns:

        lot = st.sidebar.selectbox(
            "LOT",
            ["All"]
            +
            sorted(
                df["LOT"]
                .astype(str)
                .dropna()
                .unique()
                .tolist()
            )
        )

        if lot != "All":
            df = df[
                df["LOT"].astype(str)
                == lot
            ]

    if "BLEND" in df.columns:

        blend = st.sidebar.selectbox(
            "Blend",
            ["All"]
            +
            sorted(
                df["BLEND"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

        if blend != "All":
            df = df[
                df["BLEND"].astype(str)
                == blend
            ]

    # ==========================================
    # HEADER
    # ==========================================
    st.header(f"📊 {stage}")

    # ==========================================
    # KPI
    # ==========================================
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
    elif "CV" in df.columns:
        c2.metric(
            "CV Avg",
            round(df["CV"].mean(), 2)
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

    if "RKM" in df.columns:
        c4.metric(
            "RKM Avg",
            round(
                df["RKM"].mean(),
                2
            )
        )

    # ==========================================
    # MACHINE RANKING
    # ==========================================
    cv_col = None

    if "C.V" in df.columns:
        cv_col = "C.V"
    elif "CV" in df.columns:
        cv_col = "CV"

    if (
        "M.C" in df.columns
        and
        cv_col is not None
    ):

        agg_dict = {
            cv_col: "mean"
        }

        if "NEPS" in df.columns:
            agg_dict["NEPS"] = "mean"

        if "NER%" in df.columns:
            agg_dict["NER%"] = "mean"

        ranking = (
            df.groupby(
                "M.C",
                as_index=False
            )
            .agg(agg_dict)
        )

        top5 = ranking.nsmallest(
            5,
            cv_col
        )

        worst5 = ranking.nlargest(
            5,
            cv_col
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "🏆 Top 5 Machines"
            )

            st.dataframe(
                top5,
                use_container_width=True
            )

        with col2:

            st.subheader(
                "🔻 Worst 5 Machines"
            )

            st.dataframe(
                worst5,
                use_container_width=True
            )

        # ==========================================
        # CV CHART
        # ==========================================
        st.subheader(
            "📈 Average CV By Machine"
        )

        fig_cv = px.bar(
            ranking.sort_values(cv_col),
            x="M.C",
            y=cv_col,
            text_auto=".2f",
            color=cv_col,
            color_continuous_scale="RdYlGn_r"
        )

        st.plotly_chart(
            fig_cv,
            use_container_width=True
        )

        # ==========================================
        # NEPS CHART
        # ==========================================
        if "NEPS" in ranking.columns:

            st.subheader(
                "🟠 Average Neps By Machine"
            )

            fig_neps = px.bar(
                ranking.sort_values(
                    "NEPS",
                    ascending=False
                ),
                x="M.C",
                y="NEPS",
                text_auto=".0f",
                color="NEPS",
                color_continuous_scale="Reds"
            )

            st.plotly_chart(
                fig_neps,
                use_container_width=True
            )

        # ==========================================
        # EFFICIENCY CHART
        # ==========================================
        if "NER%" in ranking.columns:

            st.subheader(
                "✅ Efficiency % By Machine"
            )

            fig_eff = px.bar(
                ranking.sort_values(
                    "NER%",
                    ascending=False
                ),
                x="M.C",
                y="NER%",
                text_auto=".1f",
                color="NER%",
                color_continuous_scale="Greens"
            )

            st.plotly_chart(
                fig_eff,
                use_container_width=True
            )

    # ==========================================
    # BLEND DISTRIBUTION
    # ==========================================
    if "BLEND" in df.columns:

        st.subheader(
            "🧵 Blend Distribution"
        )

        blend_chart = (
            df["BLEND"]
            .astype(str)
            .value_counts()
            .reset_index()
        )

        blend_chart.columns = [
            "Blend",
            "Count"
        ]

        fig_blend = px.pie(
            blend_chart,
            names="Blend",
            values="Count",
            hole=0.4
        )

        st.plotly_chart(
            fig_blend,
            use_container_width=True
        )

    # ==========================================
    # EFFICIENCY BY BLEND
    # ==========================================
    if (
        "BLEND" in df.columns
        and
        "NER%" in df.columns
    ):

        st.subheader(
            "📊 Efficiency By Blend"
        )

        blend_eff = (
            df.groupby(
                "BLEND",
                as_index=False
            )["NER%"]
            .mean()
        )

        fig_blend_eff = px.bar(
            blend_eff,
            x="BLEND",
            y="NER%",
            text_auto=".1f",
            color="NER%",
            color_continuous_scale="Viridis"
        )

        st.plotly_chart(
            fig_blend_eff,
            use_container_width=True
        )

    # ==========================================
    # RAW DATA
    # ==========================================
    with st.expander(
        "📋 Raw Data"
    ):
        st.dataframe(
            df,
            use_container_width=True
        )
