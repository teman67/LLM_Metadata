import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import time  # Import time module

# Load environment variables from .env file
load_dotenv()

# Get the PostgreSQL URL from the environment variables
POSTGRESQL_URL = os.getenv('POSTGRESQL_URL')

# Debugging: Check if POSTGRESQL_URL is loaded
if POSTGRESQL_URL is None:
    raise ValueError("Error: POSTGRESQL_URL is missing or empty in the environment variables.")

# Define the database engine using the PostgreSQL URL
engine = create_engine(POSTGRESQL_URL)
Base = declarative_base()

# Define the Conversation model
class Conversation(Base):
    """
    ORM model representing the 'conversations' table in the PostgreSQL database.
    """
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    model_name = Column(String, nullable=True)
    token_usage = Column(Integer, nullable=True)
    elapsed_time = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(microsecond=0))
    username = Column(String, nullable=False)  # Track conversations by user

# Create the table if it doesn't exist, with error handling
try:
    Base.metadata.create_all(engine)
except Exception as e:
    st.error(f"Error creating the table: {e}")

# Create a session factory
Session = scoped_session(sessionmaker(bind=engine))

# Initialize session state for login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Function to get conversation history
def get_conversation_history():
    """
    Retrieves the conversation history for the currently logged-in user from the PostgreSQL database.
    """
    session = Session()
    try:
        history = session.query(Conversation).filter(
            Conversation.username == st.session_state.username
        ).order_by(Conversation.timestamp.desc()).all()
        return history
    except Exception as e:
        session.rollback()
        st.error(f"An error occurred: {e}")
        return []
    finally:
        session.close()

# Function to delete a conversation
def delete_conversation(conversation_id):
    """
    Deletes a user conversation and the corresponding assistant response from the database.

    Parameters:
    - conversation_id (int): The unique ID of the user message to be deleted.

    Behavior:
    - Deletes both the user message and the next assistant message if present.
    - Ensures only the owner of the conversation (based on the username) can delete messages.
    """
    session = Session()
    try:
        # Find the user message by ID and ensure it belongs to the logged-in user
        user_message = session.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.username == st.session_state.username  # Ensure ownership
        ).first()

        if user_message:
            # Delete the user message
            session.delete(user_message)

            # Find and delete the next assistant message (response) after the user's message
            assistant_message = session.query(Conversation).filter(
                Conversation.timestamp > user_message.timestamp,  # Must be after the user message
                Conversation.role == 'assistant',                 # Must be an assistant's message
                Conversation.username == st.session_state.username  # Ensure ownership
            ).order_by(Conversation.timestamp.asc()).first()  # Get the next message chronologically

            if assistant_message:
                session.delete(assistant_message)

            session.commit()
            st.success("Message and response deleted successfully.")
        else:
            st.error("Message not found or you do not have permission to delete this message.")
    except Exception as e:
        session.rollback()
        st.error(f"An error occurred: {e}")
    finally:
        session.close()
        st.rerun()  # Refresh the page after deletion


# Function to display conversation history
def display_conversation_history():
    """
    Displays the conversation history for the currently logged-in user in the Streamlit app.
    """

    # Ensure that session state variables are initialized
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'file_content' not in st.session_state:
        st.session_state.file_content = None
    if 'warning_shown' not in st.session_state:
        st.session_state.warning_shown = False

    # Add loading spinner using Streamlit's built-in spinner
    with st.spinner("History is loading. Please wait a moment..."):
        time.sleep(2)  # Simulate loading time

    # Load the rest of the page content
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

    if not st.session_state.logged_in or not st.session_state.username:
        st.warning("Please log in to view your conversation history.")
        return

    st.write("### Conversation History")
    history = get_conversation_history()
    if not history:
        st.info("No conversation history found.")
    else:
        messages = {"user": [], "assistant": []}

        for conv in history:
            role = "user" if conv.role == "user" else "assistant"
            if role == "user":
                messages["user"].append((conv.id, conv.content, conv.timestamp))
            else:
                messages["assistant"].append((conv.content, conv.timestamp, conv.model_name, conv.token_usage, conv.elapsed_time))

        max_len = max(len(messages["user"]), len(messages["assistant"]))

        for i in range(max_len):
            cols = st.columns([4, 4, 2])  # Add extra column for the delete button
            user_message = messages["user"][i] if i < len(messages["user"]) else (None, None, None)
            assistant_message = messages["assistant"][i] if i < len(messages["assistant"]) else (None, None, None, None, None)

            if user_message[1]:
                cols[0].markdown(f"""
                    <div style="background-color: #ad6a5a; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                        <strong>User:</strong> {user_message[1]} <br> <small>Date and Time in UTC: {user_message[2]}</small>
                    </div>
                    """, unsafe_allow_html=True)

                if st.session_state.logged_in:  # Only show delete button if logged in
                    if cols[2].button(f"Delete", key=f"del_{user_message[0]}"):
                        delete_conversation(user_message[0])

            if assistant_message[0]:
                cols[1].markdown(f"""
                    <div style="background-color: #5aad78; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                        <strong>Assistant:</strong> {assistant_message[0]} <br> 
                        <small>Date and Time in UTC: {assistant_message[1]}</small><br>
                        <small>Model: {assistant_message[2] if assistant_message[2] else 'Unknown'}</small><br>
                        <small>Token_usage: {assistant_message[3] if assistant_message[3] else 'Unknown'} </small> ---
                        <small>Elapsed Time: {assistant_message[4] if assistant_message[4] else 'Unknown'} </small>
                    </div>
                    """, unsafe_allow_html=True)
