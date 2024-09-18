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

# # Debugging: Check if POSTGRESQL_URL is loaded
# if POSTGRESQL_URL is None:
#     raise ValueError("Error: POSTGRESQL_URL is missing or empty in the environment variables.")
# else:
#     print(f"Loaded POSTGRESQL_URL: {POSTGRESQL_URL}")

# Define the database engine using the PostgreSQL URL
engine = create_engine(POSTGRESQL_URL)
Base = declarative_base()

# Define the Conversation model
class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    model_name = Column(String, nullable=True)
    token_usage = Column(Integer, nullable=True)
    elapsed_time = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(microsecond=0))
    username = Column(String, nullable=False)  # Add a username column to track conversations by user

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
Session = scoped_session(sessionmaker(bind=engine))

# Initialize session state for login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Function to get conversation history
def get_conversation_history():
    session = Session()
    try:
        # Filter conversations by username
        history = session.query(Conversation).filter(Conversation.username == st.session_state.username).order_by(Conversation.timestamp.desc()).all()
        return history
    except Exception as e:
        session.rollback()
        st.error(f"An error occurred: {e}")
        return []
    finally:
        session.close()


def delete_conversation(conv_id):
    session = Session()
    try:
        # Find the conversation to delete by username
        user_message = session.query(Conversation).filter(
            Conversation.id == conv_id,
            Conversation.username == st.session_state.username  # Ensure ownership
        ).first()

        if user_message:
            # Delete the user message and the next assistant message (if present)
            assistant_message = session.query(Conversation).filter(
                Conversation.timestamp > user_message.timestamp, 
                Conversation.role == 'assistant',
                Conversation.username == st.session_state.username  # Ensure ownership
            ).first()

            # Delete both messages
            session.delete(user_message)
            if assistant_message:
                session.delete(assistant_message)

            session.commit()
            st.success("Message deleted successfully.")
            
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
    # Ensure that session state variables are initialized at the very beginning
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'file_content' not in st.session_state:
        st.session_state.file_content = None
    if 'warning_shown' not in st.session_state:
        st.session_state.warning_shown = False

    # Create a placeholder for the loading message
    loading_message = st.empty()

    # Display "loading" message in the placeholder
    loading_message.markdown("""
    <style>
    .spinner {
        margin: 0 auto;
        border: 5px solid #f3f3f3; /* Light grey */
        border-top: 5px solid #3498db; /* Blue */
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 2s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    <div style="text-align:center;">
        <h3>History is loading. Please wait a moment...</h3>
        <div class="spinner"></div>
    </div>
    """, unsafe_allow_html=True)

    # Add 2-second pause
    time.sleep(2)

    # Remove the loading message after 2 seconds
    loading_message.empty()

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
                        <strong>User:</strong> {user_message[1]} <br> <small>Date and Time: {user_message[2]}</small>
                    </div>
                    """, unsafe_allow_html=True)

                if st.session_state.logged_in:  # Only show delete button if logged in
                    if cols[2].button(f"Delete", key=f"del_{user_message[0]}"):
                        delete_conversation(user_message[0])
                        # st.experimental_rerun()  # Refresh the page after deletion

            if assistant_message[0]:
                cols[1].markdown(f"""
                    <div style="background-color: #5aad78; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                        <strong>Assistant:</strong> {assistant_message[0]} <br> 
                        <small>Date and Time: {assistant_message[1]}</small><br>
                        <small>Model: {assistant_message[2] if assistant_message[2] else 'Unknown'}</small><br>
                        <small>Token_usage: {assistant_message[3] if assistant_message[3] else 'Unknown'} </small> ---
                        <small>Elapsed Time: {assistant_message[4] if assistant_message[4] else 'Unknown'} </small>
                    </div>
                    """, unsafe_allow_html=True)
