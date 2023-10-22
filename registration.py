import pandas as pd
import streamlit as st
import hashlib
import sqlite3


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def add_userdata(username, password):
    # Todo: Ensure that the username is unique
    conn = sqlite3.connect('database/db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO users(username,password) VALUES (?,?)', (username, password))
    conn.commit()


def check_hashes(password, hashed_pswd):
    if make_hashes(password) == hashed_pswd:
        return hashed_pswd
    return False


def view_all_users():
    conn = sqlite3.connect('database/db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    conn.close()
    return data


def check_credentials(username, password):
    conn = sqlite3.connect('database/db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    hashed_password = c.fetchone()
    conn.close()
    return check_hashes(password, hashed_password[0])


def registration_page():
    st.title("Simple User Registration App")

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "SignUp":
        st.subheader("Create New Account")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')

        if st.button("Signup"):
            hashed_password = make_hashes(password)
            add_userdata(username, hashed_password)
            st.success("You have successfully created an account")

    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            if check_credentials(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Logged In as {}".format(username))
            else:
                st.warning("Incorrect Username/Password")


if __name__ == '__main__':
    registration_page()
