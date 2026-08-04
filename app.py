# =================================
# CLEANING DATA
# =================================

# تحويل الأعمدة الرقمية

for col in df.columns:

    try:
        df[col] = pd.to_numeric(
            df[col],
            errors="ignore"
        )
    except:
        pass

# =================================
# IGNORE ZERO VALUES
# =================================

for col in df.columns:

    col_name = str(col).upper()

    # تجاهل النبس = 0

    if "NEPS" in col_name:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        df[col] = df[col].replace(
            0,
            pd.NA
        )

    # تجاهل الكفاءة = 0

    if "NER%" in col_name:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        df[col] = df[col].replace(
            0,
            pd.NA
        )

        # لو الكفاءة مخزنة 0.75

        temp = df[col].dropna()

        if len(temp) > 0:

            if temp.max() <= 1:

                df[col] = df[col] * 100

# =================================
# KPI
# =================================

st.header("📊 KPI")

k1, k2, k3, k4 = st.columns(4)

# COUNT

if "COUNT" in df.columns:

    k1.metric(
        "Average Count",
        f"{df['COUNT'].mean():.2f}"
    )

elif "Act.Count" in df.columns:

    k1.metric(
        "Average Count",
        f"{df['Act.Count'].mean():.2f}"
    )

# CV

if "C.V" in df.columns:

    k2.metric(
        "Average CV",
        f"{df['C.V'].mean():.2f}"
    )

elif "C.V m" in df.columns:

    k2.metric(
        "Average CVm",
        f"{df['C.V m'].mean():.2f}"
    )

# NEPS

if "NEPS" in df.columns:

    k3.metric(
        "Average Neps",
        f"{df['NEPS'].dropna().mean():.0f}"
    )

# NER OR RKM

if "NER%" in df.columns:

    k4.metric(
        "Average NER%",
        f"{df['NER%'].dropna().mean():.1f}%"
    )

elif "RKM" in df.columns:

    k4.metric(
        "Average RKM",
        f"{df['RKM'].mean():.2f}"
    )

# =================================
# MACHINE RANKING
# =================================

if "M.C" in df.columns:

    ranking = df.copy()

    if "NEPS" in ranking.columns:

        ranking = ranking[
            ranking["NEPS"].notna()
        ]

    if "NER%" in ranking.columns:

        ranking = ranking[
            ranking["NER%"].notna()
        ]

    # CARD

    if "NER%" in ranking.columns:

        ranking["Quality Score"] = (

            (100 - ranking["NEPS"])

            +

            (100 - ranking["C.V"] * 10)

            +

            ranking["NER%"]

        )

    # BREAKER/FINISHER

    elif "NEPS" in ranking.columns:

        ranking["Quality Score"] = (

            (100 - ranking["NEPS"])

            +

            (100 - ranking["C.V"] * 10)

        )

    else:

        ranking["Quality Score"] = (

            100 - ranking["C.V"] * 10

        )

    ranking = ranking.sort_values(
        "Quality Score",
        ascending=False
    )

    best_machine = ranking.iloc[0]

    worst_machine = ranking.iloc[-1]

    st.header("🏆 Machine Performance")

    c1, c2 = st.columns(2)

    with c1:

        st.success(
            f"""
🏆 Best Machine

Machine : {best_machine['M.C']}

CV : {best_machine['C.V']:.2f}

Neps : {
best_machine['NEPS']
if 'NEPS' in ranking.columns
else 'N/A'
}
"""
        )

    with c2:

        st.error(
            f"""
🔻 Worst Machine

Machine : {worst_machine['M.C']}

CV : {worst_machine['C.V']:.2f}

Neps : {
worst_machine['NEPS']
if 'NEPS' in ranking.columns
else 'N/A'
}
"""
        )

    st.subheader("🏅 Ranking")

    st.dataframe(
        ranking,
        use_container_width=True
    )
