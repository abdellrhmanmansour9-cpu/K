import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Yarn Quality Dashboard",
    layout="wide"
)

st.title("Yarn Quality Intelligence")

uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True
)

if uploaded_files:

    frames = []

    for file in uploaded_files:

        sheets = pd.read_excel(
            file,
            sheet_name=None
        )

        for sheet_name, df in sheets.items():

            df.columns = df.columns.astype(str)

            df = df.rename(
                columns={
                    "C.V m": "CVm",
                    "BLEND": "Blend",
                    "PRODUCT": "Product"
                }
            )

            df["Sheet"] = sheet_name
            df["File"] = file.name

            frames.append(df)

    data = pd.concat(
        frames,
        ignore_index=True
    )

    for col in [
        "CVm",
        "IPI",
        "NEPS",
        "RKM",
        "ELG",
        "Bforce",
    ]:

        if col not in data.columns:
            data[col] = 0

    score = (
        data["RKM"] * 3
        + data["ELG"] * 2
        + data["Bforce"] / 20
        - data["CVm"] * 2
        - data["IPI"] * 0.05
        - data["NEPS"] * 0.02
    )

    score = score.fillna(0)

    data["Quality_Score"] = (
        (score - score.min())
        /
        (score.max() - score.min() + 0.0001)
    ) * 100

    st.header("Executive Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Quality Score",
        round(data["Quality_Score"].mean(), 2)
    )

    c2.metric(
        "Average IPI",
        round(data["IPI"].mean(), 2)
    )

    c3.metric(
        "Average CVm",
        round(data["CVm"].mean(), 2)
    )

    c4.metric(
        "Average RKM",
        round(data["RKM"].mean(), 2)
    )

    if "Product" in data.columns:

        st.header("Product Ranking")

        product_summary = (
            data.groupby("Product")
            .agg(
                {
                    "Quality_Score": "mean",
                    "IPI": "mean",
                    "CVm": "mean",
                    "RKM": "mean"
                }
            )
            .round(2)
            .sort_values(
                "Quality_Score",
                ascending=False
            )
        )

        fig = px.bar(
            product_summary.reset_index(),
            x="Quality_Score",
            y="Product",
            color="Quality_Score",
            orientation="h",
            height=700
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "Blend" in data.columns:

        st.header("Blend Analysis")

        blend_summary = (
            data.groupby("Blend")
            .agg(
                {
                    "Quality_Score": "mean"
                }
            )
            .reset_index()
        )

        fig = px.treemap(
            blend_summary,
            path=["Blend"],
            values="Quality_Score",
            color="Quality_Score"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "LOT" in data.columns:

        st.header("LOT Trend")

        lot_summary = (
            data.groupby("LOT")
            .agg(
                {
                    "Quality_Score": "mean"
                }
            )
            .reset_index()
        )

        fig = px.line(
            lot_summary,
            x="LOT",
            y="Quality_Score",
            markers=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.header("Raw Data")

    st.dataframe(
        data,
        use_container_width=True
    )

else:

    st.info(
        "Upload Excel files to start analysis"
    )
