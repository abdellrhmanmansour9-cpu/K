import streamlit as st
import pandas as pd
import plotly.express as px

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

    df.columns = [str(col).strip() for col in df.columns]

    st.sidebar.header("Filters")

    product_col = None

    for col in df.columns:
        if str(col).lower() == "product":
            product_col = col

    if product_col:

        products = sorted(
            df[product_col]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_product = st.sidebar.selectbox(
            "Product",
            products
        )

        df = df[
            df[product_col].astype(str)
            == selected_product
        ]

    blend_col = None

    for col in df.columns:
        if str(col).upper() == "BLEND":
            blend_col = col

    if blend_col:

        blends = sorted(
            df[blend_col]
            .dropna()
            .astype(str)
            .unique()
        )

        selected_blend = st.sidebar.selectbox(
            "Blend",
            blends
        )

        df = df[
            df[blend_col].astype(str)
            == selected_blend
        ]

    st.subheader(f"📋 {stage}")

    cv_col = "C.V m"
    ipi_col = "IPI"
    rkm_col = "RKM"
    elg_col = "ELG"
    bf_col = "Bforce"

    col1, col2, col3, col4, col5 = st.columns(5)

    if cv_col in df.columns:
        col1.metric(
            "CV.M",
            round(df[cv_col].mean(), 2)
        )

    if ipi_col in df.columns:
        col2.metric(
            "IPI",
            round(df[ipi_col].mean(), 2)
        )

    if rkm_col in df.columns:
        col3.metric(
            "RKM",
            round(df[rkm_col].mean(), 2)
        )

    if elg_col in df.columns:
        col4.metric(
            "ELG",
            round(df[elg_col].mean(), 2)
        )

    if bf_col in df.columns:
        col5.metric(
            "BForce",
            round(df[bf_col].mean(), 2)
        )

    st.markdown("---")

    st.subheader("📊 KPI Statistics")

    stat_cols = st.columns(5)

    for i, metric in enumerate(
        [cv_col, ipi_col, rkm_col, elg_col, bf_col]
    ):

        if metric in df.columns:

            stat_cols[i].write(f"### {metric}")

            stat_cols[i].write(
                f"Min: {round(df[metric].min(),2)}"
            )

            stat_cols[i].write(
                f"Avg: {round(df[metric].mean(),2)}"
            )

            stat_cols[i].write(
                f"Max: {round(df[metric].max(),2)}"
            )

    st.markdown("---")

    st.subheader("📈 CV.M Trend")

    if "LOT" in df.columns and cv_col in df.columns:

        fig = px.line(
            df.sort_values("LOT"),
            x="LOT",
            y=cv_col,
            markers=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("📈 IPI Trend")

    if "LOT" in df.columns and ipi_col in df.columns:

        fig2 = px.line(
            df.sort_values("LOT"),
            x="LOT",
            y=ipi_col,
            markers=True
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.subheader("📈 RKM Trend")

    if "LOT" in df.columns and rkm_col in df.columns:

        fig3 = px.line(
            df.sort_values("LOT"),
            x="LOT",
            y=rkm_col,
            markers=True
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    st.markdown("---")

    st.subheader("📄 Detailed Results")

    display_cols = []

    wanted_cols = [
        "LOT",
        "Act.Count",
        "C.V m",
        "IPI",
        "RKM",
        "ELG",
        "Bforce",
        "BLEND"
    ]

    for c in wanted_cols:
        if c in df.columns:
            display_cols.append(c)

    st.dataframe(
        df[display_cols],
        use_container_width=True
    )

else:

    st.info(
        "Upload Report Of Quality Control BeLYarn.xlsx"
    )
