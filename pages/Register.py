import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import show_pages_from_config, add_page_title
from utils.streamlit_utils import with_sidebar
from utils.db_utils import add_userdata, make_hashes


@with_sidebar
def render():
    add_page_title()

    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        switch_page("Pipeline")

    st.title("Sign Up")
    st.subheader("Create New Account")
    username = st.text_input("User Name")
    password = st.text_input("Password", type='password')

    if st.button("Signup", key="signup"):
        hashed_password = make_hashes(password)
        add_userdata(username, hashed_password)


if __name__ == '__main__':
    render()
