import streamlit as st
from dotenv import load_dotenv
import os
# import hashlib
from argon2 import PasswordHasher
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
    """
    ORM model representing the 'users' table in the PostgreSQL database.

    Columns:
    - id (Integer, primary key): Unique identifier for each user.
    - username (String, unique, non-nullable): The username of the user (must be unique).
    - password (String, non-nullable): The hashed password of the user.
    - email (String, unique, non-nullable): The email address of the user (must be unique).
    """

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Provides a database session for querying the PostgreSQL database.

    Yields:
    - db (Session): An active database session.

    After the function finishes, the database session is closed to ensure proper resource handling.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_credentials(username, password):
    """
    Verifies if the provided username and password match a record in the database.

    Parameters:
    - username (str): The username input by the user.
    - password (str): The password input by the user.

    Returns:
    - bool: True if the username and password combination is correct, False otherwise.

    Hashing:
    - The password is hashed using SHA-256 before comparison with the stored hashed password in the database.
    """

    """Check if the provided username and password are correct."""
    # hashed_password = hashlib.sha256(password.encode()).hexdigest()
     # Get a database session
    db = next(get_db())
    
    # Retrieve the user from the database by username
    user = db.query(User).filter(User.username == username).first()
    
    # If user exists, verify the password
    if user:
        ph = PasswordHasher()
        try:
            # Verify the password against the stored hash
            ph.verify(user.password, password)
            return True
        except Exception as e:
            return False
    
    return False

def login():
    """
    Manages the login process for the Streamlit app.

    Features:
    - Displays a login form where users can input their username and password.
    - Verifies credentials using the `check_credentials` function.
    - Stores the login status and username in Streamlit's session state.

    Behavior:
    - If the user is already logged in, a message is displayed with the option to log out.
    - If login is successful, a success message is shown, and the user is logged in.
    - If login fails, an error message is shown.

    Returns:
    - bool: True if the user is logged in, False otherwise.

    Session State:
    - `logged_in`: Tracks whether the user is logged in (True or False).
    - `username`: Stores the logged-in user's username.
    """

    # Initialize session state for login status if not already present
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None

    # Check if user is already logged in
    if st.session_state.logged_in:
        # Skip the login form and show a message or redirect as needed
        st.write("You are already logged in!")
        
        # Display logout button
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
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
                st.session_state.username = username  # Store the username in session state
                title_placeholder.empty()  # Clear the title on successful login
                st.success("Login successful!")
                # Rerun the app to apply the change
                st.rerun()
            else:
                st.error("Invalid username or password")

    return False



# Example usage of login function in the main part of your Streamlit app
if __name__ == "__main__":
    """
    Main function to check if the user is logged in and display content accordingly.
    
    If the user is logged in:
    - A welcome message is displayed.
    
    If the user is not logged in:
    - The login form is displayed.
    """

    if login():
        st.write("Welcome to the app!")  # Content for logged-in users
