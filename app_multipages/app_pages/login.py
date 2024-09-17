import streamlit as st
from dotenv import load_dotenv
import os

def login():
    # Initialize session state for login status if not already present
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Check if user is already logged in
    if st.session_state.logged_in:
        # Skip the login form and show a message or redirect as needed
        st.write("You are already logged in!")
        
        # Display logout button
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.success("You have been logged out.")
            # Rerun the app to reflect the updated state
            st.rerun()
        
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
                # Rerun the app to apply the change
                st.rerun()
            else:
                st.error("Invalid username or password")

    return False

# Example usage of login function in the main part of your Streamlit app
if __name__ == "__main__":
    if login():
        st.write("Welcome to the app!")  # Content for logged-in users
