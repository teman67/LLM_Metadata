import streamlit as st
from dotenv import load_dotenv
import os
import time

def login():
    # Use st.empty() to manage the display of the title
    title_placeholder = st.empty()
    title_placeholder.title("Login")

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve credentials from environment variables
    USERNAME = os.getenv("APP_USERNAME")
    PASSWORD = os.getenv("APP_PASSWORD")

    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Check if user is already logged in
    if st.session_state.logged_in:
        success_message = st.empty()
        success_message.success("You are already logged in!")
        time.sleep(2)
        success_message.empty()  # Clear the success message after 2 seconds
        title_placeholder.empty()  # Clear the title after 2 seconds
        return True

    # Display login form
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if username == USERNAME and password == PASSWORD:
                st.session_state.logged_in = True
                title_placeholder.empty()  # Clear the title on successful login
                st.success("Login successful!")
                return True
            else:
                st.error("Invalid username or password")

    return False

# Example usage of login function in the main part of your Streamlit app
if __name__ == "__main__":
    if login():
        st.write("Welcome to the app!")  # Content for logged-in users
