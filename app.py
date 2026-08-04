import streamlit as st

st.set_page_config(
    page_title="Quality Control System",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Quality Control System")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==================================
# LOGIN
# ==================================

if not st.session_state.logged_in:

    st.subheader("Quality Control Login")

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

# ==================================
# MAIN SYSTEM
# ==================================

else:

    st.success(
        "Welcome To Quality Control System ✅"
    )

    st.header("🧵 Carding Department")

    st.write(
        "مرحلة الكارد"
    )

    if st.button("Logout"):

        st.session_state.logged_in = False

        st.rerun()
