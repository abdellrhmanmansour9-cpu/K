import streamlit as st
import pandas as pd

# ==========================
# Page Config
# ==========================

st.set_page_config(
    page_title="Carding Quality Dashboard",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Carding Quality Dashboard")
st.write("تحليل جودة مرحلة الكارد")

# ==========================
# Upload File
# ==========================

uploaded_file = st.file_uploader(
    "تحميل ملف البيانات",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file is None:
    st.info("قم برفع ملف البيانات أولاً")
    st.stop()

# ==========================
# Read File
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
# Clean Columns
# ==========================

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
    st.error(f"الأعمدة المفقودة: {missing}")
    st.write(df.columns.tolist())
    st.stop()

# ==========================
# Convert Data
# ==========================

df["Count"] = pd.to_numeric(
    df["Count"],
    errors="coerce"
)

df["CV"] = pd.to_numeric(
    df["CV"],
    errors="coerce"
)

df["Neps"] = pd.to_numeric(
    df["Neps"],
    errors="coerce"
)

df["Ner%"] = pd.to_numeric(
    df["Ner%"],
    errors="coerce"
) * 100

# ==========================
# Data View
# ==========================

st.header("📋 البيانات")

st.dataframe(
    df,
    use_container_width=True
)

# ==========================
# KPI
# ==========================

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

# ==========================
# Blend Analysis
# ==========================

st.header("🧪 تحليل الخلطات")

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

blend_summary = blend_summary.round(2)

st.dataframe(
    blend_summary,
    use_container_width=True
)

# ==========================
# Charts
# ==========================

st.header("📈 الرسوم البيانية")

col1, col2 = st.columns(2)

with col1:

    st.subheader("CV حسب الخلطة")

    cv_chart = (
        df.groupby("Blend")["CV"]
        .mean()
    )

    st.bar_chart(cv_chart)

with col2:

    st.subheader("Neps حسب الخلطة")

    neps_chart = (
        df.groupby("Blend")["Neps"]
        .mean()
    )

    st.bar_chart(neps_chart)

# ==========================
# Machine Analysis
# ==========================

st.header("⚙️ أداء الماكينات")

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

machine_summary = machine_summary.round(2)

st.dataframe(
    machine_summary,
    use_container_width=True
)

st.subheader("مقارنة الماكينات")

machine_chart = (
    df.groupby("M.C")
    .agg({
        "CV": "mean",
        "Neps": "mean",
        "Ner%": "mean"
    })
)

st.bar_chart(machine_chart)

# ==========================
# Best & Worst Machine
# ==========================

st.header("🏆 تقييم الماكينات")

machine_eff = (
    df.groupby("M.C")["Ner%"]
    .mean()
)

best_machine = machine_eff.idxmax()
worst_machine = machine_eff.idxmin()

c1, c2 = st.columns(2)

with c1:

    st.success(
        f"أفضل ماكينة : {best_machine} | {machine_eff.max():.1f}%"
    )

with
