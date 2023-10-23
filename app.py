import streamlit as st
from registration import registration_page
from user_pipeline_app import pipeline_process

conn = st.experimental_connection("db", type="sql")


def display_app():
    username = st.session_state.get('username', 'Guest')
    st.subheader(f"Welcome to the main app, {username}!")
    st.button("Next Page", on_click=lambda: st.experimental_set_query_params(page="pipeline"), key="to_pipeline")


def main():
    query_params = st.experimental_get_query_params()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    current_page = query_params.get("page", ["registration"])[0]  # default to "registration" if no page param

    if current_page == "registration":
        registration_page()
    elif current_page == "main":
        display_app()
        # todo: welcome_page()
    elif current_page == "pipeline":
        pipeline_process()


if __name__ == '__main__':
    main()
