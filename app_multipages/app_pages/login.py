import streamlit as st
from dotenv import load_dotenv
import os
import hashlib
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

# Load environment variables
load_dotenv()

# Define the database URL
DATABASE_URL = os.getenv('POSTGRESQL_Pass_URL')

# Create a new SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a base class for the models
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_credentials(username, password):
    """Check if the provided username and password are correct."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    db = next(get_db())
    user = db.query(User).filter(User.username == username, User.password == hashed_password).first()
    return user is not None

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

    # Display login form
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if check_credentials(username, password):
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
