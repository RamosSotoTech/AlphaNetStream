import streamlit as st
from st_pages import show_pages_from_config, Page, show_pages, Section, hide_pages
from streamlit_extras.switch_page_button import switch_page
import os

pages_dir = "pages"

# List all files in the pages directory
all_files = os.listdir(pages_dir)

all_pages = None
all_user_pages = ['Welcome', 'Login', 'Register', 'About Us']
logged_in_pages = ['Welcome', 'Pipeline', 'About Us']


def load_pages():
    global all_pages  # Declare all_pages as global
    if all_pages is None:  # Check if pages have already been loaded
        # Create a list of Page objects dynamically
        all_pages = [Page(f"{pages_dir}/{file}", file.replace('_', ' ').replace('.py', ''))
                     for file in all_files
                     if file.endswith(".py") and file != "__init__.py"]
    return all_pages


def get_page_files(page_names):
    pages = load_pages()  # Load pages, if necessary
    page_files = [page for page in pages if page.name in page_names]
    return page_files


def create_sidebar():
    with st.sidebar:
        if 'logged_in' in st.session_state and st.session_state['logged_in']:
            st.write(f"Welcome, {st.session_state['username']}!")
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                switch_page("Welcome")
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login"):
                    switch_page("Login")
            with col2:
                if st.button("Register"):
                    switch_page("Register")


# Decorator to show the pages in the sidebar
def with_sidebar(f):
    def wrapper(*args, **kwargs):
        if 'logged_in' in st.session_state and st.session_state['logged_in']:
            pages_to_show = get_page_files(logged_in_pages)
        else:
            pages_to_show = get_page_files(all_user_pages)
        show_pages(pages_to_show)
        create_sidebar()
        return f(*args, **kwargs)
    return wrapper
