import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ======================================
# PAGE CONFIG
# ======================================

st.set_page_config(
    page_title="Carding Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 CARDING QUALITY DASHBOARD")

# ======================================
# UPLOAD FILE
# ======================================

uploaded_file = st.file_uploader(
    "تحميل ملف الكارد",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.info("قم برفع ملف البيانات")
    st.stop()

# ======================================
# READ FILE
# ======================================

if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

df.columns = df.columns.str.strip()

# ======================================
# REQUIRED COLUMNS
# ======================================

required = [
    "M.C",
    "Lot",
    "Count",
    "CV",
    "Neps",
    "Ner%",
    "Blend"
]

missing = [c for c in required if c not in df.columns]

if missing:

    st.error(f"الأعمدة غير موجودة : {missing}")
    st.write(df.columns.tolist())
    st.stop()

# ======================================
# DATA TYPES
# ======================================

df["Count"] = pd.to_numeric(df["Count"], errors="coerce")
df["CV"] = pd.to_numeric(df["CV"], errors="coerce")
df["Neps"] = pd.to_numeric(df["Neps"], errors="coerce")

# لو البيانات 0.77

if df["Ner%"].max() <= 1:
    df["Ner%"] = pd.to_numeric(df["Ner%"], errors="coerce") * 100
else:
    df["Ner%"] = pd.to_numeric(df["Ner%"], errors="coerce")

# ======================================
# KPI
# ======================================

st.header("📊 KPI")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "متوسط النمرة",
    f"{df['Count'].mean():.2f}"
)

k2.metric(
    "متوسط CV",
    f"{df['CV'].mean():.2f}"
)

k3.metric(
    "متوسط Neps",
    f"{df['Neps'].mean():.0f}"
)

k4.metric(
    "متوسط الكفاءة",
    f"{df['Ner%'].mean():.1f}%"
)

# ======================================
# QUALITY SCORE
# ======================================

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

st.header("🎯 Quality Score")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=quality_score,
    title={'text': "Quality Score"},
    gauge={
        'axis': {'range': [0,100]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range':[0,50],'color':'red'},
            {'range':[50,75],'color':'orange'},
            {'range':[75,100],'color':'green'}
        ]
    }
))

st.plotly_chart(
    fig,
    use_container_width=True
)

# ======================================
# TABS
# ======================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Overview",
        "🧪 Blend",
        "⚙️ Machines",
        "📋 Details"
    ]
)

# ======================================
# OVERVIEW
# ======================================

with tab1:

    st.subheader("CV حسب الخلطة")

    cv_summary = (
        df.groupby("Blend")["CV"]
        .mean()
        .reset_index()
    )

    fig_cv = px.bar(
        cv_summary,
        x="Blend",
        y="CV",
        color="CV",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig_cv,
        use_container_width=True
    )

    st.subheader("Neps حسب الخلطة")

    neps_summary = (
        df.groupby("Blend")["Neps"]
        .mean()
        .reset_index()
    )

    fig_neps = px.bar(
        neps_summary,
        x="Blend",
        y="Neps",
        color="Neps",
        text_auto=".0f"
    )

    st.plotly_chart(
        fig_neps,
        use_container_width=True
    )

# ======================================
# BLEND
# ======================================

with tab2:

    blend_summary = (
        df.groupby("Blend")
        .agg({
            "Count":"mean",
            "CV":"mean",
            "Neps":"mean",
            "Ner%":"mean"
        })
        .round(2)
        .reset_index()
    )

    st.dataframe(
        blend_summary,
        use_container_width=True
    )

    fig = px.pie(
        df,
        names="Blend",
        title="توزيع الخلطات"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ======================================
# MACHINES
# ======================================

with tab3:

    machine_summary = (
        df.groupby("M.C")
        .agg({
            "Count":"mean",
            "CV":"mean",
            "Neps":"mean",
            "Ner%":"mean"
        })
        .round(2)
        .reset_index()
    )

    st.dataframe(
        machine_summary,
        use_container_width=True
    )

    fig_machine = px.bar(
        machine_summary,
        x="M.C",
        y="Ner%",
        color="Ner%",
        text_auto=".1f",
        title="كفاءة الماكينات"
    )

    st.plotly_chart(
        fig_machine,
        use_container_width=True
    )

    best_machine = machine_summary.loc[
        machine_summary["Ner%"].idxmax()
    ]

    worst_machine = machine_summary.loc[
        machine_summary["Ner%"].idxmin()
    ]

    c1, c2 = st.columns(2)

    with c1:
        st.success(
            f"أفضل ماكينة : {best_machine['M.C']} | {best_machine['Ner%']:.1f}%"
        )

    with c2:
        st.error(
            f"أقل ماكينة : {worst_machine['M.C']} | {worst_machine['Ner%']:.1f}%"
        )

# ======================================
# DETAILS
# ======================================

with tab4:

    st.subheader("العلاقة بين النمرة والانتظامية")

    fig_scatter = px.scatter(
        df,
        x="Count",
        y="CV",
        color="Blend",
        size="Neps",
        hover_data=["Lot","M.C"]
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

    selected_machine = st.selectbox(
        "اختر ماكينة",
        sorted(df["M.C"].unique())
    )

    filtered = df[
        df["M.C"] == selected_machine
    ]

    st.dataframe(
        filtered,
        use_container_width=True
    )

# ======================================
# EXECUTIVE VIEW
# ======================================

st.header("📌 الرؤية العامة")

if quality_score >= 85:

    st.success(
        "✅ مرحلة الكارد مستقرة والجودة ممتازة"
    )

elif quality_score >= 70:

    st.warning(
        "⚠️ الأداء جيد ويحتاج متابعة"
    )

else:

    st.error(
        "❌ توجد مشكلات تستدعي مراجعة الماكينات والخلطات"
    )

# ======================================
# DOWNLOAD
# ======================================

csv = df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 تحميل التقرير",
    data=csv,
    file_name="Carding_Report.csv",
    mime="text/csv"
)
