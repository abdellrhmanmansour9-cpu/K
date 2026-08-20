import streamlit as st
import pandas as pd
import plotly.express as px

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
        "Stage",
        xls.sheet_names
    )

    df = pd.read_excel(
        uploaded_file,
        sheet_name=stage
    )

    df.columns = df.columns.str.strip()

    if "NEPS" in df.columns:

        df["NEPS"] = pd.to_numeric(
            df["NEPS"],
            errors="coerce"
        )

        df["NEPS"] = df["NEPS"].replace(
            0,
            pd.NA
        )

    # =====================
    # FILTERS
    # =====================

    st.sidebar.header("Filters")

    if "M.C" in df.columns:

        machine = st.sidebar.selectbox(
            "Machine",
            ["All"] +
            sorted(
                df["M.C"]
                .astype(str)
                .unique()
                .tolist()
            )
        )

        if machine != "All":

            df = df[
                df["M.C"]
                .astype(str)
                == machine
            ]

    if "LOT" in df.columns:

        lot = st.sidebar.selectbox(
            "LOT",
            ["All"] +
            sorted(
                df["LOT"]
                .astype(str)
                .unique()
                .tolist()
            )
        )

        if lot != "All":

            df = df[
                df["LOT"]
                .astype(str)
                == lot
            ]

    if "BLEND" in df.columns:

        blend = st.sidebar.selectbox(
            "Blend",
            ["All"] +
            sorted(
                df["BLEND"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        if blend != "All":

            df = df[
                df["BLEND"]
                == blend
            ]

    if "Product" in df.columns:

        product = st.sidebar.selectbox(
            "Product",
            ["All"] +
            sorted(
                df["Product"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        if product != "All":

            df = df[
                df["Product"]
                == product
            ]

    st.header(f"📊 {stage}")

    # =====================
    # KPI
    # =====================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Records",
        len(df)
    )

    if "C.V" in df.columns:

        c2.metric(
            "CV Avg",
            round(
                df["C.V"].mean(),
                2
            )
        )

    elif "C.V m" in df.columns:

        c2.metric(
            "CVm Avg",
            round(
                df["C.V m"].mean(),
                2
            )
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

    # =====================
    # CARD RANKING
    # =====================

    if (
        "M.C" in df.columns
        and
        "C.V" in df.columns
    ):

        ranking = (
            df.groupby("M.C")
            .agg({
                "C.V": "mean",
                **(
                    {"NEPS": "mean"}
                    if "NEPS" in df.columns
                    else {}
                )
            })
            .reset_index()
        )

        top5 = ranking.nsmallest(
            5,
            "C.V"
        )

        worst5 = ranking.nlargest(
            5,
            "C.V"
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

        # =====================
        # STATUS
        # =====================

        if "NEPS" in ranking.columns:

            ranking["Status"] = ranking.apply(
                lambda row:
                "🟢 Good"
                if (
                    row["C.V"] <= 3.5
                    and row["NEPS"] <= 100
                )
                else "🔴 Out Of Spec",
                axis=1
            )

            st.subheader(
                "🎯 Machine Status"
            )

            st.dataframe(
                ranking,
                use_container_width=True
            )

        # =====================
        # CHART
        # =====================

        st.subheader(
            "📈 Average CV By Machine"
        )

        fig = px.bar(
            ranking.sort_values(
                "C.V"
            ),
            x="M.C",
            y="C.V",
            color="C.V",
            text_auto=".2f",
            color_continuous_scale="RdYlGn_r"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================
    # RAW DATA
    # =====================

    with st.expander(
        "📋 Raw Data"
    ):

        st.dataframe(
            df,
            use_container_width=True
        )
