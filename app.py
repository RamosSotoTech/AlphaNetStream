import streamlit as st
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
# from database.db_setup import create_tables
import sqlite3
from registration import registration_page
import sqlalchemy

conn = st.experimental_connection("db", type="sql")


def add_userdata(username, password):
    with conn.session as s:
        c = s.cursor()
        c.execute('INSERT INTO User(Username,Password) VALUES (?,?)', (username, password))
        s.commit()


def main():
    st.title("Multi-Page App")

    # Check if the user is already registered (using session state)
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    registration_page()

    # Welcome Page
    if st.session_state['logged_in']:
        st.subheader(f"Welcome {st.session_state['username']}")
        if st.button("Proceed to URL Input"):
            st.session_state['page'] = "url_input"

    # URL Input Page
    if st.session_state.get('page') == "url_input":
        st.subheader("Enter URL for Analysis")
        url = st.text_input("URL")
        if st.button("Analyze"):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            if sentiment > 0:
                st.write('The sentiment of the webpage is Positive')
            elif sentiment < 0:
                st.write('The sentiment of the webpage is Negative')
            else:
                st.write('The sentiment of the webpage is Neutral')

            st.write("URL Analysis Results")


if __name__ == '__main__':
    main()
