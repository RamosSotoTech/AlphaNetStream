import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_page_title
from utils.streamlit_utils import with_sidebar
from utils.db_utils import check_credentials


@with_sidebar
def render():
    add_page_title()

    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        switch_page("Pipeline")

    st.subheader("Login to Your Account")
    username = st.text_input("User Name")
    password = st.text_input("Password", type='password')

    def on_login_click():
        if check_credentials(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success("Logged In as {}".format(username))
            st.experimental_set_query_params(page="Pipeline")
        else:
            st.warning("Incorrect Username/Password")

    st.button("Login", on_click=on_login_click, key="login")


if __name__ == '__main__':
    render()
