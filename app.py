import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Carding Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 CARDING QUALITY DASHBOARD")

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "Upload Excel Workbook",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.stop()

# =====================================================
# READ DATA
# =====================================================

try:

    if uploaded_file.name.endswith(".csv"):

        df = pd.read_csv(uploaded_file)

    else:

        sheets = pd.read_excel(
            uploaded_file,
            sheet_name=None
        )

        df = pd.concat(
            [
                sheet.assign(SHEET=name)
                for name, sheet in sheets.items()
            ],
            ignore_index=True
        )

except Exception as e:

    st.error(str(e))
    st.stop()

# =====================================================
# CLEAN COLUMN NAMES
# =====================================================

df.columns = df.columns.str.strip()

required_columns = [
    "M.C",
    "Lot",
    "Count",
    "CV",
    "Neps",
    "Ner%",
    "Blend"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:

    st.error(f"Missing Columns: {missing}")
    st.write(df.columns.tolist())
    st.stop()

# =====================================================
# CONVERT DATA TYPES
# =====================================================

df["Count"] = pd.to_numeric(df["Count"], errors="coerce")
df["CV"] = pd.to_numeric(df["CV"], errors="coerce")
df["Neps"] = pd.to_numeric(df["Neps"], errors="coerce")
df["Ner%"] = pd.to_numeric(df["Ner%"], errors="coerce")

# لو الكفاءة مخزنة 0.75
if df["Ner%"].max() <= 1:
    df["Ner%"] = df["Ner%"] * 100

# =====================================================
# QUALITY SCORE
# =====================================================

avg_cv = df["CV"].mean()
avg_neps = df["Neps"].mean()
avg_eff = df["Ner%"].mean()

quality_score = 100

if avg_cv > 4:
    quality_score -= 30

if avg_neps > 120:
    quality_score -= 30

if avg_eff < 75:
    quality_score -= 40

quality_score = max(0, quality_score)

# =====================================================
# KPI
# =====================================================

st.header("📊 KPI")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Average Count",
        f"{df['Count'].mean():.2f}"
    )

with k2:
    st.metric(
        "Average CV",
        f"{df['CV'].mean():.2f}"
    )

with k3:
    st.metric(
        "Average Neps",
        f"{df['Neps'].mean():.0f}"
    )

with k4:
    st.metric(
        "Average Efficiency",
        f"{df['Ner%'].mean():.1f}%"
    )

# =====================================================
# QUALITY SCORE GAUGE
# =====================================================

st.header("🎯 Quality Score")

fig_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=quality_score,
        title={"text": "Quality Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 50], "color": "red"},
                {"range": [50, 75], "color": "orange"},
                {"range": [75, 100], "color": "green"}
            ]
        }
    )
)

st.plotly_chart(
    fig_gauge,
    use_container_width=True
)

# =====================================================
# MACHINE SUMMARY
# =====================================================

machine_summary = (
    df.groupby("M.C")
    .agg({
        "Count": "mean",
        "CV": "mean",
        "Neps": "mean",
        "Ner%": "mean"
    })
    .round(2)
    .reset_index()
)

# =====================================================
# TOP / BOTTOM MACHINES
# =====================================================

st.header("🏆 Machine Ranking")

c1, c2 = st.columns(2)

with c1:

    st.subheader("Top Machines")

    top5 = machine_summary.sort_values(
        "Ner%",
        ascending=False
    ).head(5)

    st.dataframe(
        top5,
        use_container_width=True
    )

with c2:

    st.subheader("Worst Machines")

    bottom5 = machine_summary.sort_values(
        "Ner%",
        ascending=True
    ).head(5)

    st.dataframe(
        bottom5,
        use_container_width=True
    )

# =====================================================
# CHART ROW 1
# =====================================================

col1, col2 = st.columns(2)

with col1:

    fig_eff = px.bar(
        machine_summary,
        x="M.C",
        y="Ner%",
        color="Ner%",
        title="Machine Efficiency %",
        text_auto=".1f"
    )

    st.plotly_chart(
        fig_eff,
        use_container_width=True
    )

with col2:

    fig_cv = px.bar(
        machine_summary,
        x="M.C",
        y="CV",
        color="CV",
        title="CV By Machine",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig_cv,
        use_container_width=True
    )

# =====================================================
# CHART ROW 2
# =====================================================

col3, col4 = st.columns(2)

with col3:

    fig_neps = px.bar(
        machine_summary,
        x="M.C",
        y="Neps",
        color="Neps",
        title="Neps By Machine",
        text_auto=".0f"
    )

    st.plotly_chart(
        fig_neps,
        use_container_width=True
    )

with col4:

    blend_summary = (
        df.groupby("Blend")
        .agg({
            "CV": "mean",
            "Neps": "mean",
            "Ner%": "mean"
        })
        .round(2)
        .reset_index()
    )

    fig_blend = px.pie(
        blend_summary,
        names="Blend",
        values="Ner%",
        title="Blend Distribution"
    )

    st.plotly_chart(
        fig_blend,
        use_container_width=True
    )

# =====================================================
# SCATTER
# =====================================================

st.header("📈 Count vs CV")

fig_scatter = px.scatter(
    df,
    x="Count",
    y="CV",
    color="Blend",
    size="Neps",
    hover_data=["Lot", "M.C"],
    title="Count vs CV"
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

# =====================================================
# PARETO
# =====================================================

st.header("📊 Pareto Neps")

pareto = machine_summary.sort_values(
    "Neps",
    ascending=False
)

fig_pareto = px.bar(
    pareto,
    x="M.C",
    y="Neps",
    color="Neps",
    title="Pareto Analysis"
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)

# =====================================================
# SHEET ANALYSIS
# =====================================================

if "SHEET" in df.columns:

    st.header("📑 Workbook Sheets")

    sheet_summary = (
        df.groupby("SHEET")
        .agg({
            "CV": "mean",
            "Neps": "mean",
            "Ner%": "mean"
        })
        .round(2)
        .reset_index()
    )

    st.dataframe(
        sheet_summary,
        use_container_width=True
    )

# =====================================================
# EXECUTIVE SUMMARY
# =====================================================

st.header("📌 Executive Summary")

best_machine = machine_summary.loc[
    machine_summary["Ner%"].idxmax()
]

worst_machine = machine_summary.loc[
    machine_summary["Ner%"].idxmin()
]

st.success(
    f"""
أفضل ماكينة: {best_machine['M.C']}
|
الكفاءة: {best_machine['Ner%']:.1f}%
|
CV: {best_machine['CV']:.2f}
|
Neps: {best_machine['Neps']:.0f}
"""
)

st.error(
    f"""
أسوأ ماكينة: {worst_machine['M.C']}
|
الكفاءة: {worst_machine['Ner%']:.1f}%
|
CV: {worst_machine['CV']:.2f}
|
Neps: {worst_machine['Neps']:.0f}
"""
)

# =====================================================
# DATA TABLE
# =====================================================

st.header("📋 Data")

st.dataframe(
    df,
    use_container_width=True
)

# =====================================================
# DOWNLOAD
# =====================================================

csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "📥 Download Report",
    data=csv,
    file_name="Carding_Report.csv",
    mime="text/csv"
)
