# =====================================
# EDIT & DELETE
# =====================================

st.header("✏️ Edit / Delete Records")

df_display = df.reset_index()

selected_row = st.selectbox(
    "Select Record",
    df_display.index
)

selected_data = df_display.loc[selected_row]

st.write("Selected Record")

st.dataframe(
    pd.DataFrame([selected_data]),
    use_container_width=True
)

col1, col2 = st.columns(2)

with col1:

    if st.button("🗑 Delete Record"):

        st.session_state.card_data.pop(
            selected_row
        )

        st.success(
            "Record Deleted Successfully ✅"
        )

        st.rerun()

with col2:

    if st.button("✏️ Edit Record"):

        st.session_state.edit_index = selected_row

# =====================================
# EDIT FORM
# =====================================

if "edit_index" in st.session_state:

    row = st.session_state.card_data[
        st.session_state.edit_index
    ]

    st.header("✏️ Update Record")

    with st.form("edit_form"):

        new_count = st.number_input(
            "Count",
            value=float(row["Count"]),
            format="%.2f"
        )

        new_cv = st.number_input(
            "CV",
            value=float(row["CV"]),
            format="%.2f"
        )

        new_feed = st.number_input(
            "Feed Neps",
            value=float(row["Feed Neps"])
        )

        new_card = st.number_input(
            "Card Neps",
            value=float(row["Card Neps"])
        )

        if new_feed > 0:

            new_eff = (
                (
                    new_feed
                    - new_card
                )
                / new_feed
            ) * 100

        else:

            new_eff = 0

        st.metric(
            "Efficiency",
            f"{new_eff:.2f}%"
        )

        update = st.form_submit_button(
            "💾 Update"
        )

    if update:

        st.session_state.card_data[
            st.session_state.edit_index
        ]["Count"] = new_count

        st.session_state.card_data[
            st.session_state.edit_index
        ]["CV"] = new_cv

        st.session_state.card_data[
            st.session_state.edit_index
        ]["Feed Neps"] = new_feed

        st.session_state.card_data[
            st.session_state.edit_index
        ]["Card Neps"] = new_card

        st.session_state.card_data[
            st.session_state.edit_index
        ]["Efficiency"] = new_eff

        del st.session_state.edit_index

        st.success(
            "Record Updated Successfully ✅"
        )

        st.rerun()
