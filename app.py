import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Carding Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 تحليل جودة مرحلة الكارد")

uploaded_file = st.file_uploader(
    "تحميل ملف البيانات",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.info("قم برفع ملف البيانات")
    st.stop()

# قراءة الملف
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# تنظيف أسماء الأعمدة
df.columns = df.columns.str.strip()

# التحقق من الأعمدة
required = [
    "M.C",
    "Lot",
    "Count",
    "CV",
    "Neps",
    "Ner%",
    "Blend"
]

missing = [x for x in required if x not in df.columns]

if missing:
    st.error(f"الأعمدة غير الموجودة: {missing}")
    st.write(df.columns.tolist())
    st.stop()

# عرض البيانات
st.subheader("البيانات")
st.dataframe(df, use_container_width=True)

# ==========================
# KPI
# ==========================

st.subheader("📊 مؤشرات الجودة")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "متوسط النمرة",
        round(df["Count"].mean(), 2)
    )

with c2:
    st.metric(
        "متوسط CV",
        round(df["CV"].mean(), 2)
    )

with c3:
    st.metric(
        "متوسط Neps",
        round(df["Neps"].mean(), 0)
    )

with c4:
    st.metric(
        "متوسط الكفاءة %",
        round(df["Ner%"].mean(), 1)
    )

# ==========================
# تحليل حسب الخلطة
# ==========================

st.subheader("🧪 تحليل الخلطات")

blend_summary = df.groupby("Blend").agg({
    "Count": "mean",
    "CV": "mean",
    "Neps": "mean",
    "Ner%": "mean"
}).reset_index()

st.dataframe(
    blend_summary,
    use_container
