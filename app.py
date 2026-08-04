import plotly.graph_objects as go

if "NEPS" in df.columns:

    score = 100 - df["NEPS"].dropna().mean()

    score = max(0, min(100, score))

    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Quality Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "steps": [
                    {"range": [0, 50], "color": "red"},
                    {"range": [50, 75], "color": "orange"},
                    {"range": [75, 100], "color": "green"},
                ],
            },
        )
    )

    st.plotly_chart(
        fig_gauge,
        use_container_width=True
    )
    import plotly.express as px

if "M.C" in df.columns and "C.V" in df.columns:

    fig_cv = px.bar(
        df,
        x="M.C",
        y="C.V",
        color="C.V",
        text_auto=".2f",
        title="CV By Machine"
    )

    st.plotly_chart(
        fig_cv,
        use_container_width=True
    )
    if "M.C" in df.columns and "NEPS" in df.columns:

    fig_neps = px.bar(
        df,
        x="M.C",
        y="NEPS",
        color="NEPS",
        text_auto=".0f",
        title="Neps By Machine"
    )

    st.plotly_chart(
        fig_neps,
        use_container_width=True
    )
    if (
    "M.C" in df.columns
    and "LOT" in df.columns
    and "NEPS" in df.columns
):

    heat = px.density_heatmap(
        df,
        x="M.C",
        y="LOT",
        z="NEPS",
        color_continuous_scale="RdYlGn_r",
        title="Neps Heatmap"
    )

    st.plotly_chart(
        heat,
        use_container_width=True
    )
    if "BLEND" in df.columns:

    st.subheader("📊 Blend Pivot")

    pivot = pd.pivot_table(
        df,
        values=[
            c for c in df.columns
            if c not in ["LOT", "BLEND", "M.C"]
        ],
        index="BLEND",
        aggfunc="mean"
    )

    st.dataframe(
        pivot,
        use_container_width=True
    )
    st.subheader("📌 Executive Summary")

if "NEPS" in df.columns:

    best = df.loc[df["NEPS"].idxmin()]

    worst = df.loc[df["NEPS"].idxmax()]

    st.success(
        f"🏆 Best Machine : {best['M.C']}"
    )

    st.error(
        f"🔻 Worst Machine : {worst['M.C']}"
    )
