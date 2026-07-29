import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Carding Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Carding Quality Dashboard")

# ==================================================
# UPLOAD FILE
# ==================================================

uploaded_file = st.file_uploader(
    "Upload Excel Workbook",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.info("Upload your Carding Workbook")
    st.stop()

# ==================================================
# READ DATA
# ==================================================

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

# ==================================================
# CLEAN COLUMN NAMES
# ==================================================

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

# ==================================================
# NUMERIC CONVERSION
# ==================================================

df["Count"] = pd.to_numeric(df["Count"], errors="coerce")
df["CV"] = pd.to_numeric(df["CV"], errors="coerce")
df["Neps"] = pd.to_numeric(df["Neps"], errors="coerce")
df["Ner%"] = pd.to_numeric(df["Ner%"], errors="coerce")

# لو الكفاءة 0.75 تتحول 75%

if df["Ner%"].max() <= 1:
    df["Ner%"] = df["Ner%"] * 100

# ==================================================
# KPI
# ==================================================

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

# ==================================================
# QUALITY SCORE
# ==================================================

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

# ==================================================
# MACHINE SUMMARY
# ==================================================

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

ranking = machine_summary.sort_values(
    by="Ner%",
    ascending=False
).reset_index(drop=True)

ranking.index += 1

# ==================================================
# MACHINE RANKING
# ==================================================

st.header("🏅 Machine Ranking")

st.dataframe(
    ranking,
    use_container_width=True
)

# ==================================================
# BEST & WORST MACHINE
# ==================================================

best_machine = ranking.iloc[0]
worst_machine = ranking.iloc[-1]

col1, col2 = st.columns(2)

with col1:

    st.success(
        f"""
🏆 أفضل ماكينة

رقم الماكينة : {best_machine['M.C']}

الكفاءة : {best_machine['Ner%']:.1f}%

CV : {best_machine['CV']:.2f}

Neps : {best_machine['Neps']:.0f}
"""
    )

with col2:

    st.error(
        f"""
🔻 أسوأ ماكينة

رقم الماكينة : {worst_machine['M.C']}

الكفاءة : {worst_machine['Ner%']:.1f}%

CV : {worst_machine['CV']:.2f}

Neps : {worst_machine['Neps']:.0f}
"""
    )

# ==================================================
# CHARTS
# ==================================================

st.header("📈 Charts")

c1, c2 = st.columns(2)

with c1:

    fig1 = px.bar(
        ranking,
        x="M.C",
        y="Ner%",
        color="Ner%",
        title="Machine Efficiency %",
        text_auto=".1f"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with c2:

    fig2 = px.bar(
        ranking,
        x="M.C",
        y="CV",
        color="CV",
        title="CV By Machine",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

c3, c4 = st.columns(2)

with c3:

    fig3 = px.bar(
        ranking,
        x="M.C",
        y="Neps",
        color="Neps",
        title="Neps By Machine",
        text_auto=".0f"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

with c4:

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

    fig4 = px.bar(
        blend_summary,
        x="Blend",
        y="Ner%",
        color="Blend",
        title="Blend Efficiency"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# ==================================================
# COUNT VS CV
# ==================================================

st.header("📈 Count vs CV")

fig_scatter = px.scatter(
    df,
    x="Count",
    y="CV",
    color="Blend",
    size="Neps",
    hover_data=["Lot", "M.C"]
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

# ==================================================
# PARETO
# ==================================================

st.header("📊 Pareto Neps Analysis")

pareto = ranking.sort_values(
    "Neps",
    ascending=False
)

fig_pareto = px.bar(
    pareto,
    x="M.C",
    y="Neps",
    color="Neps"
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)

# ==================================================
# EXECUTIVE SUMMARY
# ==================================================

st.header("📌 Executive Summary")

if quality_score >= 85:

    st.success(
        "✅ جودة مرحلة الكارد ممتازة"
    )

elif quality_score >= 70:

    st.warning(
        "⚠️ جودة مرحلة الكارد جيدة وتحتاج متابعة"
    )

else:

    st.error(
        "❌ توجد مشكلات تحتاج مراجعة"
    )

# ==================================================
# DATA
# ==================================================

st.header("📋 Data")

st.dataframe(
    df,
    use_container_width=True
)

# ==================================================
# DOWNLOAD
# ==================================================

csv = df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 Download Report",
    data=csv,
    file_name="Carding_Report.csv",
    mime="text/csv"
)
