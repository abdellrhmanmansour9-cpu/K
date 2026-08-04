import streamlit as st
import pandas as pd
from datetime import date

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Quality Control System",
    page_icon="🧵",
    layout="wide"
)

# =====================================
# LOGIN SESSION
# =====================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "card_data" not in st.session_state:
    st.session_state.card_data = []

# =====================================
# LOGIN PAGE
# =====================================

if not st.session_state.logged_in:

    st.title("🧵 BELYARN")
    st.subheader("Quality Control System")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if username == "admin" and password == "1234":

            st.session_state.logged_in = True
            st.rerun()

        else:

            st.error(
                "Wrong Username Or Password"
            )

# =====================================
# MAIN SYSTEM
# =====================================

else:

    st.title("🧵 BELYARN")
    st.subheader("Quality Control Department")

    st.header("Carding Data Entry")

    # =====================================
    # HALL SELECTION
    # =====================================

    hall = st.selectbox(
        "Select Hall",
        [
            "Hall 1",
            "Hall 2"
        ]
    )

    # =====================================
    # MACHINES
    # =====================================

    if hall == "Hall 1":

        machines = [str(i) for i in range(1, 25)]

    else:

        machine_group = st.selectbox(
            "Machine Group",
            [
                "C Machines",
                "M Machines",
                "P Machines"
            ]
        )

        if machine_group == "C Machines":

            machines = [
                "C1","C2","C3","C4",
                "C5","C6","C7","C8"
            ]

        elif machine_group == "M Machines":

            machines = [
                "M1","M2","M3","M4",
                "M5","M6","M7"
            ]

        else:

            machines = [
                "P1","P2","P3","P4",
                "P5","P6","P7"
            ]

    # =====================================
    # FORM
    # =====================================

    with st.form("card_form"):

        col1, col2 = st.columns(2)

        with col1:

            report_date = st.date_input(
                "Date",
                value=date.today()
            )

            shift = st.selectbox(
                "Shift",
                ["A", "B", "C"]
            )

            machine = st.selectbox(
                "Machine",
                machines
            )

            lot = st.text_input("LOT")

            blend = st.text_input("Blend")

        with col2:

            count = st.number_input(
                "Count",
                format="%.2f"
            )

            cv = st.number_input(
                "CV",
                format="%.2f"
            )

            feed_neps = st.number_input(
                "Feed Neps",
                min_value=0.0
            )

            card_neps = st.number_input(
                "Card Neps",
                min_value=0.0
            )

            nre = st.number_input(
                "NRE %",
                min_value=0.0,
                format="%.2f"
            )

            sfc = st.number_input(
                "SFC %",
                min_value=0.0,
                format="%.2f"
            )

            trash = st.number_input(
                "Trash %",
                min_value=0.0,
                format="%.2f"
            )

        # =====================================
        # CARD EFFICIENCY
        # =====================================

        if feed_neps > 0:

            efficiency = (
                (feed_neps - card_neps)
                / feed_neps
            ) * 100

        else:

            efficiency = 0

        st.metric(
            "Card Efficiency %",
            f"{efficiency:.2f}%"
        )

        submit = st.form_submit_button(
            "💾 Save Data"
        )

    # =====================================
    # SAVE
    # =====================================

    if submit:

        st.session_state.card_data.append({

            "Date": str(report_date),
            "Hall": hall,
            "Shift": shift,
            "Machine": machine,
            "LOT": lot,
            "Blend": blend,
            "Count": count,
            "CV": cv,
            "Feed Neps": feed_neps,
            "Card Neps": card_neps,
            "Efficiency": efficiency,
            "NRE %": nre,
            "SFC %": sfc,
            "Trash %": trash

        })

        st.success(
            "Data Saved Successfully ✅"
        )

    # =====================================
    # DASHBOARD
    # =====================================

    if len(st.session_state.card_data) > 0:

        df = pd.DataFrame(
            st.session_state.card_data
        )

        st.header("📊 Carding Dashboard")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Avg Count",
            f"{df['Count'].mean():.2f}"
        )

        c2.metric(
            "Avg CV",
            f"{df['CV'].mean():.2f}"
        )

        c3.metric(
            "Avg Neps",
            f"{df['Card Neps'].mean():.0f}"
        )

        c4.metric(
            "Avg Efficiency",
            f"{df['Efficiency'].mean():.1f}%"
        )

        # =====================================
        # MACHINE RANKING
        # =====================================

        machine_summary = (
            df.groupby("Machine")
            .agg({
                "CV": "mean",
                "Card Neps": "mean",
                "Efficiency": "mean"
            })
            .reset_index()
        )

        machine_summary["Quality Score"] = (
            (100 - machine_summary["Card Neps"])
            +
            (100 - (machine_summary["CV"] * 10))
            +
            machine_summary["Efficiency"]
        )

        machine_summary = machine_summary.sort_values(
            "Quality Score",
            ascending=False
        )

        st.header("🏆 Machine Ranking")

        st.dataframe(
            machine_summary,
            use_container_width=True
        )

        best_machine = machine_summary.iloc[0]

        worst_machine = machine_summary.iloc[-1]

        col1, col2 = st.columns(2)

        with col1:

            st.success(
                f"""
أفضل ماكينة

Machine : {best_machine['Machine']}

Neps : {best_machine['Card Neps']:.0f}

CV : {best_machine['CV']:.2f}

Efficiency : {best_machine['Efficiency']:.2f}%
"""
            )

        with col2:

            st.error(
                f"""
أسوأ ماكينة

Machine : {worst_machine['Machine']}

Neps : {worst_machine['Card Neps']:.0f}

CV : {worst_machine['CV']:.2f}

Efficiency : {worst_machine['Efficiency']:.2f}%
"""
            )

        st.header("📋 Saved Records")

        st.dataframe(
            df,
            use_container_width=True
        )

    # =====================================
    # LOGOUT
    # =====================================

    st.divider()

    if st.button("Logout"):

        st.session_state.logged_in = False
        st.rerun()
