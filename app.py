import streamlit as st

st.set_page_config(
    page_title="Quality Control System",
    page_icon="🧵",
    layout="wide"
)

st.title("🧵 Quality Control System")

st.subheader("Quality Control Login")

username = st.text_input(
    "Username"
)

password = st.text_input(
    "Password",
    type="password"
)

if st.button("Login"):

    if username == "admin" and password == "1234":

        st.success("Login Successfully ✅")

    else:

        st.error(
            "Wrong Username Or Password"
        )
