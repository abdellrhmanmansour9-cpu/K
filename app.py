import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Carding Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 تحليل جودة مرحلة الكارد")

uploaded_file = st.file_uploader(
    "تحميل ملف البيانات",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.warning("قم برفع ملف البيانات أولاً")
    st.stop()

# قراءة الملف
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"خطأ في قراءة الملف: {e}")
    st.stop()

# تنظيف أسماء الأعمدة
df.columns = df.columns.str.strip()

# التحقق من الأعمدة المطلوبة
required_columns = [
    "M.C",
    "Lot",
    "Count",
    "CV",
    "Neps",
    "Ner%",
    "Blend"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error(f"الأعمدة المفقودة: {missing}")
    st.write("الأعمدة الموجودة:")
    st.write(df.columns.tolist())
    st.stop()

# عرض البيانات
st.subheader("📋 البيانات الأصلية")
st.dataframe(df, use_container_width=True)

# KPI
st.subheader("📊 مؤشرات الجودة")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("متوسط النمرة", round(df["Count"].mean(), 2))

with col2:
    st.metric("متوسط CV", round(df["CV"].mean(), 2))

with col3:
    st.metric("متوسط Neps", round(df["Neps"].mean(), 0))

with col4:
    st.metric("متوسط الكفاءة", round(df["Ner%"].mean(), 1))

# تحليل الخلطات
st.subheader("🧪 تحليل الخلطات")

blend_summary = (
    df.groupby("Blend")
    .agg({
        "Count": "mean",
        "CV": "mean",
        "Neps": "mean",
        "Ner%": "mean"
    })
    .reset_index()
)

st.dataframe(blend_summary, use_container_width=True)

# تقييم الجودة
st.subheader("📈 تقييم الجودة")

def evaluate(row):

    score = 100

    if row["CV"] > 4:
        score -= 30

    if row["Neps"] > 120:
        score -= 30

    if row["Ner%"] < 75:
        score -= 40

    if score >= 85:
        return "ممتاز"
    elif score >= 70:
        return "جيد"
    elif score >= 50:
        return "مقبول"
    else:
        return "يحتاج تحسين"

blend_summary["التقييم"] = blend_summary.apply(
    evaluate,
    axis=1
)

st.dataframe(blend_summary, use_container_width=True)

# الاستنتاجات
st.subheader("📋 الاستنتاجات")

for _, row in blend_summary.iterrows():

    notes = []

    if row["CV"] > 4:
        notes.append("ارتفاع قيمة CV")

    if row["Neps"] > 120:
        notes.append("ارتفاع النبس")

    if row["Ner%"] < 75:
        notes.append("انخفاض الكفاءة")

    if not notes:
        notes.append("الجودة مستقرة")

    st.info(
        f"الخلطة: {row['Blend']} | التقييم: {row['التقييم']} | {' | '.join(notes)}"
    )

# تحليل الماكينات
st.subheader("⚙️ أداء الماكينات")

machine_summary = (
    df.groupby("M.C")
    .agg({
        "Count": "mean",
        "CV": "mean",
        "Neps": "mean",
        "Ner%": "mean"
    })
    .reset_index()
)

st.dataframe(machine_summary, use_container_width=True)

# فلترة حسب الماكينة
st.subheader("🔍 تفاصيل ماكينة")

selected_machine = st.selectbox(
    "اختر الماكينة",
    sorted(df["M.C"].unique())
)

machine_data = df[df["M.C"] == selected_machine]

st.dataframe(machine_data, use_container_width=True)

# تحميل التقرير
csv = machine_data.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 تحميل التقرير",
    data=csv,
    file_name="Carding_Report.csv",
    mime="text/csv"
)
