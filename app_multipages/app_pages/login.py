import streamlit as st
from dotenv import load_dotenv
import os

def login():
    st.title("Login")

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve credentials from environment variables
    USERNAME = os.getenv("APP_USERNAME")
    PASSWORD = os.getenv("APP_PASSWORD")

    # Debug: Print loaded environment variables to ensure they are correct
    # st.write(f"Loaded USERNAME: {USERNAME}")
    # st.write(f"Loaded PASSWORD: {PASSWORD}")

    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # # Debug: Print session state
    # st.write(f"Session state logged_in: {st.session_state.logged_in}")

    # Check if user is already logged in
    if st.session_state.logged_in:
        st.success("You are already logged in!")
        return True

    # Display login form
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            st.write(f"Submitted username: {username}")  # Debug: Print entered username
            if username == USERNAME and password == PASSWORD:
                st.session_state.logged_in = True
                st.success("Login successful!")
                return True
            else:
                st.error("Invalid username or password")

    return False

# Example usage of login function in the main part of your Streamlit app
if __name__ == "__main__":
    if login():
        st.write("Welcome to the app!")  # Content for logged-in users
