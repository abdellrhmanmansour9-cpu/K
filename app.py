# =====================================
# KPI
# =====================================

st.header("📊 KPI")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Average Count",
    f"{df['Count'].mean():.2f}"
)

k2.metric(
    "Average CV",
    f"{df['CV'].mean():.2f}"
)

k3.metric(
    "Average Neps",
    f"{df['Neps'].mean():.0f}"
)

k4.metric(
    "Average Efficiency",
    f"{df['Ner%'].mean():.1f}%"
)

# =====================================
# QUALITY SCORE
# =====================================

st.header("🎯 Quality Score")

fig_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=quality_score,
        title={"text":"Quality Score"},
        gauge={
            "axis":{"range":[0,100]},
            "steps":[
                {"range":[0,50],"color":"red"},
                {"range":[50,75],"color":"orange"},
                {"range":[75,100],"color":"green"}
            ]
        }
    )
)

st.plotly_chart(
    fig_gauge,
    use_container_width=True
)

# =====================================
# MACHINE RANKING
# =====================================

machine_summary = (
    df.groupby("M.C")
    .agg({
        "CV":"mean",
        "Neps":"mean",
        "Ner%":"mean"
    })
    .reset_index()
)

st.header("🏆 Ranking")

c1, c2 = st.columns(2)

with c1:

    st.subheader("أفضل الماكينات")

    top5 = machine_summary.sort_values(
        "Ner%",
        ascending=False
    ).head(5)

    st.dataframe(top5)

with c2:

    st.subheader("أسوأ الماكينات")

    bottom5 = machine_summary.sort_values(
        "Ner%",
        ascending=True
    ).head(5)

    st.dataframe(bottom5)

# =====================================
# CHARTS ROW 1
# =====================================

c1, c2 = st.columns(2)

with c1:

    fig1 = px.bar(
        machine_summary,
        x="M.C",
        y="Ner%",
        color="Ner%",
        title="Machine Efficiency"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with c2:

    fig2 = px.bar(
        machine_summary,
        x="M.C",
        y="CV",
        color="CV",
        title="CV By Machine"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =====================================
# CHARTS ROW 2
# =====================================

c1, c2 = st.columns(2)

with c1:

    fig3 = px.bar(
        machine_summary,
        x="M.C",
        y="Neps",
        color="Neps",
        title="Neps By Machine"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

with c2:

    blend_summary = (
        df.groupby("Blend")
        .agg({
            "CV":"mean",
            "Neps":"mean",
            "Ner%":"mean"
        })
        .reset_index()
    )

    fig4 = px.pie(
        blend_summary,
        names="Blend",
        values="Ner%",
        title="Blend Distribution"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# =====================================
# SCATTER
# =====================================

st.header("📈 Count vs CV")

fig5 = px.scatter(
    df,
    x="Count",
    y="CV",
    color="Blend",
    size="Neps",
    hover_data=["M.C","Lot"]
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# =====================================
# PARETO
# =====================================

st.header("📊 Pareto Neps")

pareto = machine_summary.sort_values(
    "Neps",
    ascending=False
)

fig6 = px.bar(
    pareto,
    x="M.C",
    y="Neps",
    color="Neps"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# =====================================
# EXECUTIVE SUMMARY
# =====================================

st.header("📌 Executive Summary")

best_machine = machine_summary.loc[
    machine_summary["Ner%"].idxmax()
]

worst_machine = machine_summary.loc[
    machine_summary["Ner%"].idxmin()
]

st.success(
    f"""
أفضل ماكينة: {best_machine['M.C']}

الكفاءة: {best_machine['Ner%']:.1f}%

CV: {best_machine['CV']:.2f}

Neps: {best_machine['Neps']:.0f}
"""
)

st.error(
    f"""
أسوأ ماكينة: {worst_machine['M.C']}

الكفاءة: {worst_machine['Ner%']:.1f}%

CV: {worst_machine['CV']:.2f}

Neps: {worst_machine['Neps']:.0f}
"""
)

# =====================================
# DATA TABLE
# =====================================

st.header("📋 Data")

st.dataframe(
    df,
    use_container_width=True
)
