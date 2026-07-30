import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(
    page_title="Yarn Quality Intelligence",
    layout="wide"
)

st.title("🧵 Yarn Quality Intelligence System")

uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True
)

# ==========================================
# COLUMN STANDARDIZATION
# ==========================================

COLUMN_MAP = {

    "C.V m": "CVm",
    "CV": "CVm",
    "BLEND": "Blend",
    "Product": "Product",
    "PRODUCT": "Product"

}

# ==========================================
# LOAD FILES
# ==========================================

def load_data(files):

    all_frames = []

    for file in files:

        sheets = pd.read_excel(
            file,
            sheet_name=None
        )

        for sheet_name, df in sheets.items():

            df = df.rename(
                columns=COLUMN_MAP
            )

            df["Stage"] = file.name
            df["Sheet"] = sheet_name

            all_frames.append(df)

    return pd.concat(
        all_frames,
        ignore_index=True
    )

# ==========================================
# SCORE
# ==========================================

def calculate_score(df):

    required = [
        "CVm",
        "IPI",
        "NEPS",
        "RKM",
        "ELG",
        "Bforce"
    ]

    for col in required:

        if col not in df.columns:

            df[col] = 0

    raw_score = (

        (df["RKM"] * 3)

        + (df["ELG"] * 2)

        + (df["Bforce"] / 20)

        - (df["CVm"] * 2)

        - (df["IPI"] * 0.05)

        - (df["NEPS"] * 0.02)

    )

    raw_score = raw_score.fillna(0)

    score = (

        (raw_score - raw_score.min())

        /

        (raw_score.max() - raw_score.min() + 0.0001)

    ) * 100

    df["Quality_Score"] = score

    def grade(x):

        if x >= 90:
            return "A+"

        elif x >= 80:
            return "A"

        elif x >= 70:
            return "B"

        elif x >= 60:
            return "C"

        else:
            return "D"

    df["Quality_Grade"] = score.apply(grade)

    return df

# ==========================================
# ROOT CAUSE
# ==========================================

def root_cause(row):

    text = []

    if row.get("NEPS", 0) > 150:
        text.append("Carding Issue")

    if row.get("THICK", 0) > 150:
        text.append("Drafting Issue")

    if row.get("CVm", 0) > 14:
        text.append("Mass Variation")

    if row.get("RKM", 100) < 15:
        text.append("Low Strength")

    if len(text) == 0:
        text.append("Stable Process")

    return " | ".join(text)

# ==========================================
# RUN
# ==========================================

if uploaded_files:

    df = load_data(uploaded_files)

    df = calculate_score(df)

    df["Root_Cause"] = df.apply(
        root_cause,
        axis=1
    )

    st.success(
        f"Records Loaded : {len(df):,}"
    )

    st.subheader("Executive Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Avg Score",
        round(
            df["Quality_Score"].mean(),
            2
        )
    )

    c2.metric(
        "Avg IPI",
        round(
            df["IPI"].mean(),
            2
        )
    )

    c3.metric(
        "Avg RKM",
        round(
            df["RKM"].mean(),
            2
        )
    )

    if "Product" in df.columns:

        product_summary = (

            df.groupby("Product")

            .agg({

                "Quality_Score":"mean",
                "CVm":"mean",
                "IPI":"mean",
                "RKM":"mean"

            })

            .round(2)

            .sort_values(
                "Quality_Score",
                ascending=False
            )

        )

        st.subheader(
            "Product Ranking"
        )

        st.dataframe(
            product_summary
        )

    if "Blend" in df.columns:

        blend_summary = (

            df.groupby("Blend")

            .agg({

                "Quality_Score":"mean",
                "CVm":"mean",
                "IPI":"mean",
                "RKM":"mean"

            })

            .round(2)

            .sort_values(
                "Quality_Score",
                ascending=False
            )

        )

        st.subheader(
            "Blend Ranking"
        )

        st.dataframe(
            blend_summary
        )

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Raw_Data",
            index=False
        )

        if "Product" in df.columns:

            product_summary.to_excel(
                writer,
                sheet_name="Product_Summary"
            )

        if "Blend" in df.columns:

            blend_summary.to_excel(
                writer,
                sheet_name="Blend_Summary"
            )

    st.download_button(

        label="📥 Download Report",

        data=output.getvalue(),

        file_name="Quality_Report.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

else:

    st.info(
        "Upload your excel file/files to start analysis"
    )
