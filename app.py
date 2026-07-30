import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from io import BytesIO

st.set_page_config(
    page_title="Yarn Quality Intelligence",
    layout="wide"
)

st.title("🧵 Yarn Quality Intelligence Dashboard")

# ------------------------------------------------
# LOAD
# ------------------------------------------------

files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True
)

if not files:
    st.stop()

# ------------------------------------------------
# READ FILES
# ------------------------------------------------

frames = []

for file in files:

    sheets = pd.read_excel(
        file,
        sheet_name=None
    )

    for sheet_name, df in sheets.items():

        df.columns = [str(c).strip() for c in df.columns]

        rename_dict = {
            "C.V m": "CVm",
            "BLEND": "Blend",
            "PRODUCT": "Product"
        }

        df = df.rename(columns=rename_dict)

        df["Source_File"] = file.name
        df["Sheet"] = sheet_name

        frames.append(df)

df = pd.concat(frames, ignore_index=True)

# ------------------------------------------------
# REQUIRED COLUMNS
# ------------------------------------------------

required = [
    "CVm",
    "IPI",
    "NEPS",
    "RKM",
    "ELG",
    "Bforce"
]

for col in required:
    if col not in df.columns:
        df[col] = 0

# ------------------------------------------------
# QUALITY SCORE
# ------------------------------------------------

raw_score = (

    (df["RKM"] * 3)
    + (df["ELG"] * 2)
    + (df["Bforce"] / 20)

    - (df["CVm"] * 2)
    - (df["IPI"] * 0.05)
    - (df["NEPS"] * 0.02)

)

raw_score = raw_score.fillna(0)

df["Quality_Score"] = (
    (raw_score - raw_score.min())
    /
    (raw_score.max() - raw_score.min() + 0.001)
) * 100


def grade(x):

    if x >= 90:
        return "A+"

    if x >= 80:
        return "A"

    if x >= 70:
        return "B"

    if x >= 60:
        return "C"

    return "D"


df["Grade"] = df["Quality_Score"].apply(grade)

# ------------------------------------------------
# ROOT CAUSE
# ------------------------------------------------

def root_cause(row):

    causes = []

    if row.get("NEPS", 0) > 150:
        causes.append("Carding Issue")

    if row.get("THICK", 0) > 150:
        causes.append("Drafting Issue")

    if row.get("THIN", 0) > 10:
        causes.append("Material Variation")

    if row.get("CVm", 0) > 14:
        causes.append("Mass Variation")

    if row.get("RKM", 100) < 15:
        causes.append("Low Strength")

    if not causes:
        causes.append("Stable")

    return " | ".join(causes)


df["Root_Cause"] = df.apply(
    root_cause,
    axis=1
)

# ------------------------------------------------
# ANOMALY DETECTION
# ------------------------------------------------

features = [
    "CVm",
    "IPI",
    "NEPS",
    "RKM",
    "ELG",
    "Bforce"
]

model = IsolationForest(
    contamination=0.05,
    random_state=42
)

df["Anomaly"] = model.fit_predict(
    df[features].fillna(0)
)

df["Anomaly"] = df["Anomaly"].map(
    {-1: "Risk", 1: "Normal"}
)

# ------------------------------------------------
# KPI
# ------------------------------------------------

st.header("📊 Executive Dashboard")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Quality Score",
    round(df["Quality_Score"].mean(), 2)
)

c2.metric(
    "Avg IPI",
    round(df["IPI"].mean(), 2)
)

c3.metric(
    "Avg CVm",
    round(df["CVm"].mean(), 2)
)

c4.metric(
    "Avg RKM",
    round(df["RKM"].mean(), 2)
)

# ------------------------------------------------
# PRODUCT ANALYSIS
# ------------------------------------------------

if "Product" in df.columns:

    st.header("🏆 Product Ranking")

    product_summary = (

        df.groupby("Product")

        .agg({
            "Quality_Score": "mean",
            "IPI": "mean",
            "CVm": "mean",
            "RKM": "mean"
        })

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

# ------------------------------------------------
# BLEND ANALYSIS
# ------------------------------------------------

if "Blend" in df.columns:

    st.header("🧪 Blend Analysis")

    blend_summary = (

        df.groupby("Blend")

        .agg({
            "Quality_Score": "mean"
        })

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

# ------------------------------------------------
# LOT TREND
# ------------------------------------------------

if "LOT" in df.columns:

    st.header("📈 Quality Trend By Lot")

    lot_summary = (

        df.groupby("LOT")

        .agg({
            "Quality_Score": "mean"
        })

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

# ------------------------------------------------
# HEATMAP
# ------------------------------------------------

if "LOT" in df.columns and "Product" in df.columns:

    st.header("🔥 Product vs LOT Heatmap")

    heat = pd.pivot_table(
        df,
        values="Quality_Score",
        index="Product",
        columns="LOT",
        aggfunc="mean"
    )

    fig = px.imshow(
        heat,
        aspect="auto",
        color_continuous_scale="RdYlGn"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ------------------------------------------------
# PARETO
# ------------------------------------------------

st.header("⚠ Root Cause Pareto")

root = pd.DataFrame()

root["Cause"] = (

    df["Root_Cause"]

    .str.split("|")

    .explode()

    .str.strip()

)

root = (

    root["Cause"]

    .value_counts()

    .reset_index()

)

root.columns = [
    "Cause",
    "Count"
]

fig = px.bar(
    root,
    x="Cause",
    y="Count",
    color="Count"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ------------------------------------------------
# ANOMALY
# ------------------------------------------------

st.header("🚨 Critical Lots")

risk = df[
    df["Anomaly"] == "Risk"
]

st.dataframe(
    risk.head(100)
)

# ------------------------------------------------
# RADAR CHART
# ------------------------------------------------

if "Product" in df.columns:

    st.header("🎯 Product Radar Chart")

    product = st.selectbox(
        "Select Product",
        sorted(
            df["Product"]
            .dropna
