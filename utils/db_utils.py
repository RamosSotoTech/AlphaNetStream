import streamlit as st
import hashlib

conn = st.experimental_connection("db", type="sql")


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def log_to_db(message):
    with conn.session as s:
        # Query the UserID table to get the user_id associated with the username
        query = s.execute(
            'SELECT id FROM User WHERE Username = :username',
            {'username': st.session_state['username']}
        )
        user_id_result = query.fetchone()
        if user_id_result:
            user_id = user_id_result[0]
            # Insert the message along with the user_id into the activity_log table
            s.execute(
                'INSERT INTO activity_log (message, user_id) VALUES (:message, :user_id)',
                {'message': message, 'user_id': user_id}
            )
            s.commit()
        else:
            st.error("User not found in the UserID table.")


def username_exists(username):
    with conn.session as s:
        query = s.execute('SELECT 1 FROM User WHERE Username = :username', {'username': username})
        result = query.fetchone()
        return result is not None


def add_userdata(username, password):
    # Todo: Ensure that the username is unique
    if username_exists(username):
        st.error("Username already exists. Please choose a different username.")
    else:
        with conn.session as s:
            s.execute('INSERT INTO User(Username,Password) VALUES (:username,:password)',
                      {'username': username, 'password': password})
            s.commit()
        st.success("You have successfully created an account")


def check_hashes(password, hashed_pswd):
    if make_hashes(password) == hashed_pswd:
        return hashed_pswd
    return False


def view_all_users():
    with conn.session as s:
        query = s.execute('SELECT * FROM User')
        data = query.fetchall()
        return data


def check_credentials(username, password):
    with conn.session as s:
        # Query the User table for the specified username
        query = s.execute(f'SELECT password FROM User WHERE username = :username', {'username': username})
        result = query.fetchone()

        if result:
            hashed_password = result[0]
            # Use your check_hashes function to validate the password
            return check_hashes(password, hashed_password)
        else:
            return False