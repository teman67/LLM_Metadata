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

    # # Debug: Print loaded environment variables to ensure they are correct
    # st.write(f"Loaded USERNAME: {USERNAME}")
    # st.write(f"Loaded PASSWORD: {PASSWORD}")
     
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        st.success("You are already logged in!")
        return True

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful!")
            return True
        else:
            st.error("Invalid username or password")

    return False
