import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Carding Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Carding Quality Dashboard")
st.subheader("تحليل جودة مرحلة الكارد")

uploaded_file = st.file_uploader(
    "تحميل ملف بيانات الكارد",
    type=["xlsx","xls","csv"]
)

if uploaded_file is None:
    st.info("قم برفع ملف البيانات")
    st.stop()

try:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:
    st.error(str(e))
    st.stop()

st.success("تم تحميل البيانات بنجاح")

st.dataframe(df)

# KPI

st.header("📊 مؤشرات الأداء")

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.metric(
        "متوسط CV%",
        round(df["CV"].mean(),2)
    )

with col2:
    st.metric(
        "متوسط Neps",
        round(df["Neps"].mean(),0)
    )

with col3:
    st.metric(
        "متوسط الكفاءة",
        round(df["Efficiency"].mean(),1)
    )

with col4:
    st.metric(
        "عدد النمر",
        df["Count"].nunique()
    )

# تحليل النمر

st.header("📈 تحليل النمر")

summary = df.groupby("Count").agg({
    "CV":"mean",
    "Neps":"mean",
    "Efficiency":"mean"
}).reset_index()

def rating(row):

    score = 100

    if row["CV"] > 4.5:
        score -= 30

    if row["Neps"] > 150:
        score -= 30

    if row["Efficiency"] < 85:
        score -= 40

    if score >= 85:
        return "ممتاز"

    elif score >= 70:
        return "جيد"

    elif score >= 50:
        return "مقبول"

    else:
        return "ضعيف"

summary["التقييم"] = summary.apply(
    rating,
    axis=1
)

st.dataframe(summary)

# الاستنتاجات

st.header("📋 استنتاجات الجودة")

for _, row in summary.iterrows():

    notes = []

    if row["CV"] > 4.5:
        notes.append("ارتفاع CV يدل على عدم انتظام الشعيرات")

    if row["Neps"] > 150:
        notes.append("ارتفاع النبس يحتاج مراجعة الكارد")

    if row["Efficiency"] < 85:
        notes.append("انخفاض كفاءة الماكينة")

    if not notes:
        notes.append("جودة مستقرة")

    st.info(
        f"""
نمرة {row['Count']}

التقييم : {row['التقييم']}

{' | '.join(notes)}
"""
    )

# مقارنة الخلطات

st.header("🧪 تحليل الخلطات")

blend_summary = df.groupby("Blend").agg({
    "CV":"mean",
    "Neps":"mean",
    "Efficiency":"mean"
}).reset_index()

st.dataframe(blend_summary)

# مقارنة الماكينات

if "Machine" in df.columns:

    st.header("⚙️ أداء الماكينات")

    machine_summary = df.groupby("Machine").agg({
        "CV":"mean",
        "Neps":"mean",
        "Efficiency":"mean"
    }).reset_index()

    st.dataframe(machine_summary)

# فلتر النمرة

st.header("🔍 تفاصيل نمرة")

selected_count = st.selectbox(
    "اختر النمرة",
    sorted(df["Count"].unique())
)

filtered = df[
    df["Count"] == selected_count
]

st.dataframe(filtered)

# تحميل

csv = filtered.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 تحميل التقرير",
    csv,
    "carding_report.csv",
    "text/csv"
)
