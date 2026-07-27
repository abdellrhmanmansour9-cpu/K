import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================
# إعداد الصفحة
# ==========================
st.set_page_config(
    page_title="Yarn Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Yarn Quality Dashboard")
st.subheader("تحليل جودة الخيوط - إدارة الجودة")

# ==========================
# رفع الملف
# ==========================
uploaded_file = st.file_uploader(
    "📂 اختر ملف الجودة",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.info("⬆️ قم برفع ملف الجودة أولاً")
    st.stop()

# ==========================
# قراءة الملف
# ==========================
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:
    st.error(f"خطأ في قراءة الملف: {e}")
    st.stop()

# ==========================
# عرض البيانات
# ==========================
st.success("✅ تم تحميل الملف بنجاح")

st.write("### البيانات الأصلية")
st.dataframe(df, use_container_width=True)

# ==========================
# تنظيف أسماء الأعمدة
# ==========================
df.columns = df.columns.str.strip()

required_columns = [
    "Product",
    "Act.Count",
    "THIN",
    "THICK",
    "NEPS",
    "IPI",
    "RKM",
    "ELG",
    "Bforce",
    "C.V m"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"الأعمدة التالية غير موجودة: {missing_columns}")
    st.stop()

# ==========================
# مؤشرات KPI
# ==========================
st.markdown("---")
st.header("📊 مؤشرات الجودة الرئيسية")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "متوسط IPI",
    round(df["IPI"].mean(), 0)
)

col2.metric(
    "متوسط RKM",
    round(df["RKM"].mean(), 2)
)

col3.metric(
    "متوسط Bforce",
    round(df["Bforce"].mean(), 0)
)

col4.metric(
    "متوسط CVm%",
    round(df["C.V m"].mean(), 2)
)

col5.metric(
    "عدد المنتجات",
    df["Product"].nunique()
)

# ==========================
# تحليل المنتجات
# ==========================
st.markdown("---")
st.header("📈 التحليل حسب المنتج")

summary = df.groupby("Product").agg({
    "Act.Count": "mean",
    "THIN": "mean",
    "THICK": "mean",
    "NEPS": "mean",
    "IPI": "mean",
    "RKM": "mean",
    "ELG": "mean",
    "Bforce": "mean",
    "C.V m": "mean"
}).reset_index()

# ==========================
# تقييم الجودة
# ==========================
def quality_rating(row):

    score = 100

    if row["IPI"] > 250:
        score -= 25

    if row["C.V m"] > 14:
        score -= 20

    if row["RKM"] < 15:
        score -= 20

    if row["Bforce"] < 300:
        score -= 20

    if row["THICK"] > 100:
        score -= 10

    if row["THIN"] > 5:
        score -= 5

    if score >= 85:
        return "ممتاز"

    elif score >= 70:
        return "جيد"

    elif score >= 50:
        return "مقبول"

    else:
        return "ضعيف"

summary["التقييم"] = summary.apply(
    quality_rating,
    axis=1
)

st.dataframe(
    summary,
    use_container_width=True
)

# ==========================
# الاستنتاجات
# ==========================
st.markdown("---")
st.header("📋 الاستنتاجات")

for _, row in summary.iterrows():

    notes = []

    if row["IPI"] > 250:
        notes.append("ارتفاع مؤشر العيوب IPI")

    if row["THIN"] > 5:
        notes.append("زيادة أماكن الرفيع")

    if row["THICK"] > 100:
        notes.append("زيادة أماكن السميك")

    if row["NEPS"] > 150:
        notes.append("زيادة النبس")

    if row["RKM"] < 15:
        notes.append("انخفاض المتانة")

    if row["Bforce"] < 300:
        notes.append("انخفاض قوة الشد")

    if row["C.V m"] > 14:
        notes.append("عدم انتظامية مرتفعة")

    if len(notes) == 0:
        notes.append("الجودة مطابقة للمواصفات")

    st.info(
        f"""
المنتج : {row['Product']}

التقييم : {row['التقييم']}

{" | ".join(notes)}
"""
    )

# ==========================
# الرسوم البيانية
# ==========================
st.markdown("---")
st.header("📊 الرسوم البيانية")

fig1 = px.bar(
    summary,
    x="Product",
    y="IPI",
    color="التقييم",
    title="IPI حسب المنتج"
)

st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(
    summary,
    x="Product",
    y="RKM",
    color="التقييم",
    title="RKM حسب المنتج"
)

st.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(
    summary,
    x="Product",
    y="Bforce",
    color="التقييم",
    title="Bforce حسب المنتج"
)

st.plotly_chart(fig3, use_container_width=True)

# ==========================
# مقارنة LOT
# ==========================
st.markdown("---")
st.header("📦 مقارنة اللوطات")

if "LOT" in df.columns:

    lot_summary = df.groupby("LOT").agg({
        "IPI": "mean",
        "RKM": "mean",
        "Bforce": "mean"
    }).reset_index()

    st.dataframe(
        lot_summary,
        use_container_width=True
    )

    fig4 = px.bar(
        lot_summary,
        x="LOT",
        y="IPI",
        color="LOT",
        title="مقارنة IPI بين اللوطات"
    )

    st.plotly_chart(fig4, use_container_width=True)

# ==========================
# مقارنة الخلطات
# ==========================
st.markdown("---")
st.header("🧪 تحليل الخلطات")

if "BLEND" in df.columns:

    blend_summary = df.groupby("BLEND").agg({
        "IPI": "mean",
        "RKM": "mean",
        "Bforce": "mean"
    }).reset_index()

    st.dataframe(
        blend_summary,
        use_container_width=True
    )

# ==========================
# تصفية حسب المنتج
# ==========================
st.markdown("---")
st.header("🔍 عرض تفاصيل منتج")

selected_product = st.selectbox(
    "اختر المنتج",
    df["Product"].unique()
)

filtered = df[df["Product"] == selected_product]

st.dataframe(
    filtered,
    use_container_width=True
)

# ==========================
# تحميل CSV
# ==========================
csv = filtered.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 تحميل البيانات",
    csv,
    "quality_report.csv",
    "text/csv"
)
