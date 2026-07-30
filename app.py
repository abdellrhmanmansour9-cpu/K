import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Carding Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Carding Quality Dashboard")

uploaded_file = st.file_uploader(
    "تحميل ملف البيانات",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.stop()

# قراءة الملف
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# تنظيف أسماء الأعمدة
df.columns = df.columns.str.strip()

# الأعمدة المطلوبة
required = [
    "M.C",
    "Lot",
    "Count",
    "CV",
    "Neps",
    "Ner%",
    "Blend"
]

for col in required:
    if col not in df.columns:
        st.error(f"العمود غير موجود: {col}")
        st.write(df.columns.tolist())
        st.stop()

# تحويل البيانات

df["Count"] = pd.to_numeric(df["Count"], errors="coerce")
df["CV"] = pd.to_numeric(df["CV"], errors="coerce")
df["Neps"] = pd.to_numeric(df["Neps"], errors="coerce")

# تحويل الكفاءة إلى %

df["Ner%"] = (
    pd.to_numeric(df["Ner%"], errors="coerce")
    * 100
)

# KPI

st.header("📊 مؤشرات الجودة")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "متوسط النمرة",
    f"{df['Count'].mean():.2f}"
)

c2.metric(
    "متوسط CV",
    f"{df['CV'].mean():.2f}"
)

c3.metric(
    "متوسط Neps",
    f"{df['Neps'].mean():.0f}"
)

c4.metric(
    "متوسط الكفاءة",
    f"{df['Ner%'].mean():.1f}%"
)

# عرض البيانات

st.header("📋 البيانات")

st.dataframe(df, use_container_width=True)

# تحليل الخلطات

st.header("🧪 تحليل الخلطات")

blend_summary = (
    df.groupby("Blend")
    .agg({
        "Count": "mean",
        "CV": "mean",
        "Neps": "mean",
        "Ner%": "mean"
    })
    .round(2)
    .reset_index()
)

st.dataframe(
    blend_summary,
    use_container_width=True
)

# رسم بياني CV

st.header("📈 الانتظامية حسب الخلطات")

cv_chart = df.groupby("Blend")["CV"].mean()

st.bar_chart(cv_chart)

# رسم بياني Neps

st.header("📈 النبس حسب الخلطات")

neps_chart = df.groupby("Blend")["Neps"].mean()

st.bar_chart(neps_chart)

# تحليل الماكينات

st.header("⚙️ أداء الماكينات")

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

# أفضل وأسوأ ماكينة

best_machine = machine_summary.loc[
    machine_summary["Ner%"].idxmax()
]

worst_machine = machine_summary.loc[
    machine_summary["Ner%"].idxmin()
]

x1, x2 = st.columns(2)

x1.success(
    f"أفضل ماكينة : {best_machine['M.C']} | {best_machine['Ner%']:.1f}%"
)

x2.error(
    f"أقل ماكينة : {worst_machine['M.C']} | {worst_machine['Ner%']:.1f}%"
)

# الرؤية العامة

st.header("📌 الرؤية العامة")

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

st.metric(
    "Quality Score",
    f"{quality_score}%"
)

st.progress(quality_score / 100)

if quality_score >= 85:

    st.success(
        "✅ جودة مرحلة الكارد ممتازة"
    )

elif quality_score >= 70:

    st.warning(
        "⚠️ الجودة جيدة وتحتاج متابعة"
    )

else:

    st.error(
        "❌ الجودة تحتاج تحسين"
    )

# تفاصيل ماكينة

st.header("🔍 تفاصيل الماكينات")

selected_machine = st.selectbox(
    "اختر ماكينة",
    sorted(df["M.C"].unique())
)

machine_data = df[
    df["M.C"] == selected_machine
]

st.dataframe(
    machine_data,
    use_container_width=True
)

# تحميل التقرير

csv = machine_data.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 تحميل التقرير",
    csv,
    "Carding_Report.csv",
    "text/csv"
)
