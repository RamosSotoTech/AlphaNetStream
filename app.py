import streamlit as st
from st_pages import show_pages_from_config, add_page_title
from streamlit_extras.switch_page_button import switch_page
from utils.streamlit_utils import load_pages


def main():
    add_page_title()

    switch_page("Welcome")


if __name__ == '__main__':
    load_pages()
    main()
