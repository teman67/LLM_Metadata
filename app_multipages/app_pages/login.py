import streamlit as st
from dotenv import load_dotenv
import os
import time

def login():
    # Initialize session state for login status if not already present
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Check if user is already logged in
    if st.session_state.logged_in:
        # Skip the login form and show a message or redirect as needed
        st.write("You are already logged in!")
        return True

    # Use st.empty() to manage the display of the title
    title_placeholder = st.empty()
    title_placeholder.title("Login")

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve credentials from environment variables
    USERNAME = os.getenv("APP_USERNAME")
    PASSWORD = os.getenv("APP_PASSWORD")

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
                # Optionally, use a method to redirect or update the UI
                # st.experimental_rerun()  # Rerun the app to reflect the updated state
                st.rerun()  # Trigger a rerun to apply the query parameter change
                # return True
            else:
                st.error("Invalid username or password")

    return False

# Example usage of login function in the main part of your Streamlit app
if __name__ == "__main__":
    if login():
        st.write("Welcome to the app!")  # Content for logged-in users
