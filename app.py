import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="BELYARN Quality System",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 BELYARN")
st.subheader("Quality Control Weekly Analysis")

uploaded_file = st.file_uploader(
    "Upload Weekly Report",
    type=["xlsx","xls","csv"]
)

if uploaded_file is not None:

    try:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ File Uploaded Successfully")

        st.header("📋 Data Preview")

        st.dataframe(
            df,
            use_container_width=True
        )

        st.header("📊 Report Information")

        col1,col2,col3 = st.columns(3)

        col1.metric(
            "Records",
            len(df)
        )

        col2.metric(
            "Columns",
            len(df.columns)
        )

        col3.metric(
            "Machines",
            df.iloc[:,0].nunique()
        )

    except Exception as e:

        st.error(f"Error : {e}")
