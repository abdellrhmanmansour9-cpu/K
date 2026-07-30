import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

# =====================================================
# SETTINGS
# =====================================================

DATA_FOLDER = "data"
OUTPUT_FILE = "Quality_Report.xlsx"

# =====================================================
# LOAD DATA
# =====================================================

def load_data(folder):

    dataframes = []

    files = list(Path(folder).glob("*.xlsx"))

    if not files:
        raise Exception("No Excel files found")

    for file in files:

        print(f"Loading : {file.name}")

        try:

            sheets = pd.read_excel(
                file,
                sheet_name=None
            )

            for sheet_name, df in sheets.items():

                df["Stage"] = file.stem
                df["Sheet"] = sheet_name

                dataframes.append(df)

        except Exception:

            df = pd.read_excel(file)

            df["Stage"] = file.stem
            df["Sheet"] = "Data"

            dataframes.append(df)

    return pd.concat(
        dataframes,
        ignore_index=True
    )

# =====================================================
# QUALITY SCORE
# =====================================================

def add_quality_score(df):

    score = (

        (df["RKM"] * 3)

        + (df["ELG"] * 2)

        + (df["Bforce"] / 20)

        - (df["CVm"] * 2)

        - (df["IPI"] * 0.05)

        - (df["NEPS"] * 0.02)

    )

    score = score.fillna(score.mean())

    normalized = (

        (score - score.min())

        / (score.max() - score.min())

    ) * 100

    df["Quality_Score"] = normalized

    conditions = [

        normalized >= 90,
        normalized >= 80,
        normalized >= 70,
        normalized >= 60

    ]

    values = [

        "A+",
        "A",
        "B",
        "C"

    ]

    df["Quality_Grade"] = np.select(
        conditions,
        values,
        default="D"
    )

    return df

# =====================================================
# ROOT CAUSE
# =====================================================

def root_cause(row):

    causes = []

    if row.get("NEPS",0) > 150:
        causes.append("Carding Issue")

    if row.get("THICK",0) > 150:
        causes.append("Drafting Issue")

    if row.get("THIN",0) > 10:
        causes.append("Material Variation")

    if row.get("CVm",0) > 14:
        causes.append("Mass Variation")

    if row.get("RKM",100) < 15:
        causes.append("Low Strength")

    if len(causes) == 0:
        causes.append("Stable Process")

    return " | ".join(causes)

# =====================================================
# ANOMALY DETECTION
# =====================================================

def detect_anomalies(df):

    features = [

        "CVm",
        "IPI",
        "RKM",
        "ELG",
        "Bforce"

    ]

    existing = [
        c for c in features
        if c in df.columns
    ]

    model = IsolationForest(
        contamination=0.05,
        random_state=42
    )

    temp = df[existing].fillna(0)

    df["Anomaly"] = model.fit_predict(temp)

    df["Anomaly"] = df["Anomaly"].replace({
        -1:"Yes",
         1:"No"
    })

    return df

# =====================================================
# SUMMARIES
# =====================================================

def stage_summary(df):

    return (

        df.groupby("Stage")

        .agg({

            "CVm":"mean",
            "IPI":"mean",
            "RKM":"mean",
            "ELG":"mean",
            "Bforce":"mean",
            "Quality_Score":"mean"

        })

        .round(2)

        .sort_values(
            "Quality_Score",
            ascending=False
        )
    )

def product_summary(df):

    if "Product" not in df.columns:
        return pd.DataFrame()

    return (

        df.groupby("Product")

        .agg({

            "CVm":"mean",
            "IPI":"mean",
            "RKM":"mean",
            "ELG":"mean",
            "Bforce":"mean",
            "Quality_Score":"mean"

        })

        .round(2)

        .sort_values(
            "Quality_Score",
            ascending=False
        )
    )

def blend_summary(df):

    blend_col = None

    for c in ["Blend","BLEND"]:
        if c in df.columns:
            blend_col = c

    if blend_col is None:
        return pd.DataFrame()

    return (

        df.groupby(blend_col)

        .agg({

            "CVm":"mean",
            "IPI":"mean",
            "RKM":"mean",
            "ELG":"mean",
            "Bforce":"mean",
            "Quality_Score":"mean"

        })

        .round(2)

        .sort_values(
            "Quality_Score",
            ascending=False
        )
    )

def lot_summary(df):

    if "LOT" not in df.columns:
        return pd.DataFrame()

    return (

        df.groupby("LOT")

        .agg({

            "CVm":"mean",
            "IPI":"mean",
            "RKM":"mean",
            "ELG":"mean",
            "Bforce":"mean",
            "Quality_Score":"mean"

        })

        .round(2)

    )

# =====================================================
# EXECUTIVE SUMMARY
# =====================================================

def executive_summary(df):

    best_product = ""

    if "Product" in df.columns:

        temp = (
            df.groupby("Product")
            ["Quality_Score"]
            .mean()
        )

        best_product = temp.idxmax()

        worst_product = temp.idxmin()

    else:

        best_product = "NA"
        worst_product = "NA"

    summary = pd.DataFrame({

        "Metric":[

            "Total Records",
            "Average Quality Score",
            "Best Product",
            "Worst Product",
            "Average CVm",
            "Average IPI",
            "Average RKM"

        ],

        "Value":[

            len(df),
            round(
                df["Quality_Score"].mean(),
                2
            ),
            best_product,
            worst_product,
            round(
                df["CVm"].mean(),
                2
            ),
            round(
                df["IPI"].mean(),
                2
            ),
            round(
                df["RKM"].mean(),
                2
            )
        ]
    })

    return summary

# =====================================================
# EXPORT
# =====================================================

def export_all(

    summary,
    stage,
    product,
    blend,
    lot,
    anomalies

):

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="xlsxwriter"
    ) as writer:

        summary.to_excel(
            writer,
            sheet_name="Executive",
            index=False
        )

        stage.to_excel(
            writer,
            sheet_name="Stage_Summary"
        )

        product.to_excel(
            writer,
            sheet_name="Product_Summary"
        )

        blend.to_excel(
            writer,
            sheet_name="Blend_Summary"
        )

        lot.to_excel(
            writer,
            sheet_name="Lot_Summary"
        )

        anomalies.to_excel(
            writer,
            sheet_name="Anomalies",
            index=False
        )

# =====================================================
# MAIN
# =====================================================

def main():

    df = load_data(DATA_FOLDER)

    df = add_quality_score(df)

    df["Root_Cause"] = (
        df.apply(
            root_cause,
            axis=1
        )
    )

    df = detect_anomalies(df)

    stage = stage_summary(df)

    product = product_summary(df)

    blend = blend_summary(df)

    lot = lot_summary(df)

    summary = executive_summary(df)

    anomalies = (

        df[df["Anomaly"] == "Yes"]

        .sort_values(
            "Quality_Score"
        )

    )

    export_all(

        summary,
        stage,
        product,
        blend,
        lot,
        anomalies

    )

    print("="*50)
    print("QUALITY ANALYSIS COMPLETED")
    print("="*50)
    print(f"Records : {len(df)}")
    print(f"Average Quality Score : {round(df['Quality_Score'].mean(),2)}")
    print(f"Report Saved : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
