import streamlit as st
import hashlib  # For hashing passwords
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from email.utils import parseaddr

load_dotenv()

# Define the database URL
DATABASE_URL = os.getenv('POSTGRESQL_Pass_URL') 

# Create a new SQLAlchemy engine (No need for connect_args in PostgreSQL)
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

# Create the users table
Base.metadata.create_all(engine)

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for getting a new session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def register_user(username, password, email):
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Get a session
    db = next(get_db())
    
    # Check if username or email already exists
    user_exists = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if user_exists:
        return False  # Username or email already exists

    # Create a new user
    new_user = User(username=username, password=hashed_password, email=email)
    
    # Add the new user to the session and commit
    db.add(new_user)
    db.commit()
    return True

def is_valid_email(email):
    """Check if the email address is valid."""
    return '@' in parseaddr(email)[1]

def registration_page():

# The rest of your main app logic goes here...
    page_bg_img = '''
    <style>
    [data-testid="stApp"]{
        background-image: url("https://cdn.pixabay.com/photo/2019/12/16/04/05/binary-4698413_1280.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.title('Register')
    
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    email = st.text_input('Email')

    if st.button('Register'):
        # Ensure that all fields are filled
        if not username or not password or not email:
            st.error('Please fill in all the fields.')
        elif not is_valid_email(email):
            st.error('Please enter a valid email address.')
        else:
            if register_user(username, password, email):
                st.success('Account created successfully!')
                st.success('Please go to LLM page to continue.')
            else:
                st.error('Username or email already exists.')

