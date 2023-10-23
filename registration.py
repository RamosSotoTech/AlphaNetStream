import streamlit as st
import hashlib


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def log_to_db(message):
    with st.experimental_connection("db", type="sql").session as s:
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
    with st.experimental_connection("db", type="sql").session as s:
        query = s.execute('SELECT 1 FROM User WHERE Username = :username', {'username': username})
        result = query.fetchone()
        return result is not None


def add_userdata(username, password):
    # Todo: Ensure that the username is unique
    if username_exists(username):
        st.error("Username already exists. Please choose a different username.")
    else:
        with st.experimental_connection("db", type="sql").session as s:
            s.execute('INSERT INTO User(Username,Password) VALUES (:username,:password)',
                      {'username': username, 'password': password})
            s.commit()
        st.success("You have successfully created an account")


def check_hashes(password, hashed_pswd):
    if make_hashes(password) == hashed_pswd:
        return hashed_pswd
    return False


def view_all_users():
    with st.experimental_connection("db", type="sql").session as s:
        query = s.execute('SELECT * FROM User')
        data = query.fetchall()
        return data


def check_credentials(username, password):
    with st.experimental_connection("db", type="sql").session as s:
        # Query the User table for the specified username
        query = s.execute(f'SELECT password FROM User WHERE username = :username', {'username': username})
        result = query.fetchone()

        if result:
            hashed_password = result[0]
            # Use your check_hashes function to validate the password
            return check_hashes(password, hashed_password)
        else:
            return False


def registration_page():
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.experimental_set_query_params(page="main")  # If logged in, go to main page
        return

    st.title("Simple User Registration App")

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "SignUp":
        st.subheader("Create New Account")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')

        if st.button("Signup", key="signup"):
            hashed_password = make_hashes(password)
            add_userdata(username, hashed_password)

    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("User Name")
        password = st.text_input("Password", type='password')

        def on_login_click():
            if check_credentials(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Logged In as {}".format(username))
                st.experimental_set_query_params(page="main")
            else:
                st.warning("Incorrect Username/Password")

        st.button("Login", on_click=on_login_click, key="login")


if __name__ == '__main__':
    registration_page()
