import streamlit as st
from st_pages import add_page_title
from streamlit_extras.switch_page_button import switch_page
from utils.streamlit_utils import with_sidebar


@with_sidebar
def render():
    add_page_title()
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", key="login"):
            switch_page('Login')

    with col2:
        if st.button("Register", key="register"):
            switch_page('Register')


if __name__ == '__main__':
    render()
