import streamlit as st
import pandas as pd

# =============================
# إعداد الصفحة
# =============================

st.set_page_config(
    page_title="Carding Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Carding Quality Dashboard")
st.markdown("### تحليل جودة مرحلة الكارد")

# =============================
# رفع الملف
# =============================

uploaded_file = st.file_uploader(
    "تحميل ملف البيانات",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.info("قم برفع ملف البيانات أولاً")
    st.stop()

# =============================
# قراءة الملف
# =============================

try:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(f"خطأ في قراءة الملف: {e}")
    st.stop()

# =============================
# تنظيف الأعمدة
# =============================

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

missing = [c for c in required_columns if c not in df.columns]

if missing:
    st.error(f"الأعمدة غير موجودة: {missing}")
    st.write("الأعمدة الموجودة:")
    st.write(df.columns.tolist())
    st.stop()

# =============================
# تحويل البيانات
# =============================

df["Count"] = pd.to_numeric(df["Count"], errors="coerce")

df["CV"] = pd.to_numeric(df["CV"], errors="coerce")

df["Neps"] = pd.to_numeric(df["Neps"], errors="coerce")

df["Ner%"] = pd.to_numeric(
    df["Ner%"].astype(str).str.replace("%", ""),
    errors="coerce"
)

# =============================
# عرض البيانات
# =============================

st.header("📋 البيانات")

st.dataframe(
    df,
    use_container_width=True
)

# =============================
# KPIs
# =============================

st.header("📊 مؤشرات الجودة")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "متوسط النمرة",
        f"{df['Count'].mean():.2f}"
    )

with k2:
    st.metric(
        "متوسط CV",
        f"{df['CV'].mean():.2f}"
    )

with k3:
    st.metric(
        "متوسط Neps",
        f"{df['Neps'].mean():.0f}"
    )

with k4:
    st.metric(
        "متوسط الكفاءة",
        f"{df['Ner%'].mean():.1f}%"
    )

# =============================
# تحليل الخلطات
# =============================

st.header("🧪 تحليل الخلطات")

blend_summary = (

    df.groupby("Blend")
    .agg(
        {
            "Count": "mean",
            "CV": "mean",
            "Neps": "mean",
            "Ner%": "mean"
        }
    )
    .reset_index()

)

blend_summary = blend_summary.round(2)

st.dataframe(
    blend_summary,
    use_container_width=True
)

# =============================
# رسوم بيانية للخلطات
# =============================

st.header("📈 رؤية الخلطات")

c1, c2 = st.columns(2)

with c1:

    st.write("CV حسب الخلطة")

    cv_chart = (
        df.groupby("Blend")["CV"]
        .mean()
        .sort_values()
    )

    st.bar_chart(cv_chart)

with c2:

    st.write("Neps حسب الخلطة")

    neps_chart = (
        df.groupby("Blend")["Neps"]
        .mean()
        .sort_values()
    )

    st.bar_chart(neps_chart)

# =============================
# أداء الماكينات
# =============================

st.header("⚙️ أداء الماكينات")

machine_summary = (

    df.groupby("M.C")
    .agg(
        {
            "Count": "mean",
            "CV": "mean",
            "Neps": "mean",
            "Ner%": "mean"
        }
    )
    .reset_index()

)

machine_summary = machine_summary.round(2)

st.dataframe(
    machine_summary,
    use_container_width=True
)

# =============================
# رسم بياني للماكينات
# =============================

st.subheader("مقارنة الماكينات")

machine_chart = (

    df.groupby("M.C")
    .agg(
        {
            "CV": "mean",
            "Neps": "mean",
            "Ner%": "mean"
        }
    )

)

st.bar_chart(machine_chart)

# =============================
# أفضل وأسوأ ماكينة
# =============================

st.header("🏆 تقييم الماكينات")

machine_eff = (

    df.groupby("M.C")["Ner%"]
    .mean()

)

best_machine = machine_eff.idxmax()
worst_machine = machine_eff.idxmin()

b1, b2 = st.columns(2)

with b1:
    st.success(
        f"أفضل ماكينة: {best_machine} ({machine_eff.max():.1f}%)"
    )

with b2:
    st.error(
        f"أقل ماكينة: {worst_machine} ({machine_eff.min():.1f}%)"
    )

# =============================
# تقييم الجودة
# =============================

st.header("📋 تقييم الجودة")

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

st.dataframe(
    blend_summary,
    use_container_width=True
)

# =============================
# الاستنتاجات
# =============================

st.header("🎯 الاستنتاجات")

for _, row in blend_summary.iterrows():

    notes = []

    if row["CV"] > 4:
        notes.append("ارتفاع الانتظامية")

    if row["Neps"] > 120:
        notes.append("ارتفاع النبس")

    if row["Ner%"] < 75:
        notes.append("انخفاض الكفاءة")

    if len(notes) == 0:
        notes.append("الجودة مستقرة")

    st.info(
        f"""
الخلطة: {row['Blend']}

التقييم: {row['التقييم']}

الملاحظات:
{' | '.join(notes)}
"""
    )

# =============================
# الرؤية العامة
# =============================

st.header("📌 الرؤية العامة")

avg_cv = df["CV"].mean()
avg_neps = df["Neps"].mean()
avg_eff = df["Ner%"].mean()

if avg_eff >= 80 and avg_cv <= 4 and avg_neps <= 120:

    st.success(
        "✅ جودة مرحلة الكارد ممتازة والكفاءة مرتفعة"
    )

elif avg_eff >= 75:

    st.warning(
        "⚠️ الجودة جيدة لكن تحتاج متابعة النبس والانتظامية"
    )

else:

    st.error(
        "❌ توجد مشكلات تستدعي مراجعة الماكينات والخلطات"
    )

# =============================
# فلترة الماكينات
# =============================

st.header("🔍 تفاصيل ماكينة")

selected_machine = st.selectbox(
    "اختر الماكينة",
    sorted(df["M.C"].unique())
)

machine_data = df[
    df["M.C"] == selected_machine
]

st.dataframe(
    machine_data,
    use_container_width=True
)

# =============================
# تحميل التقرير
# =============================

csv = machine_data.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 تحميل التقرير",
    data=csv,
    file_name="Carding_Report.csv",
    mime="text/csv"
)
