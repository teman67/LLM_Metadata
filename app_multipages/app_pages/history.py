import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the PostgreSQL URL from the environment variables
POSTGRESQL_URL = os.getenv('POSTGRESQL_URL')

# Debugging: Check if POSTGRESQL_URL is loaded
if POSTGRESQL_URL is None:
    raise ValueError("Error: POSTGRESQL_URL is missing or empty in the environment variables.")
else:
    print(f"Loaded POSTGRESQL_URL: {POSTGRESQL_URL}")

# Define the database engine using the PostgreSQL URL
engine = create_engine(POSTGRESQL_URL)
Base = declarative_base()

# Define the Conversation model
class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
Session = scoped_session(sessionmaker(bind=engine))

# Function to get conversation history
def get_conversation_history():
    session = Session()
    try:
        history = session.query(Conversation).order_by(Conversation.timestamp).all()
        return history
    except Exception as e:
        session.rollback()
        st.error(f"An error occurred: {e}")
        return []
    finally:
        session.close()

# Function to display conversation history
def display_conversation_history():
    page_bg_img = '''
    <style>
    [data-testid="stApp"]{
        background-image: url("https://res.cloudinary.com/dlthn5m1i/image/upload/v1725435253/lake-4541454_1920_yjpcug.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.write("### Conversation History")
    history = get_conversation_history()
    if not history:
        st.info("No conversation history found.")
    else:
        colors = ["#fc9642", "#5aad78", "#416a96", "#8f894a", "#9e3c72", "#7e5dc2", "#8c1416"]
        for idx, conv in enumerate(history):
            color = colors[idx % len(colors)]
            role = "User" if conv.role == "user" else "Assistant"
            st.markdown(f"""
                <div style="background-color: {color}; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                    <strong>{role}:</strong> {conv.content} <br> <small>{conv.timestamp}</small>
                </div>
                """, unsafe_allow_html=True)

