import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timezone
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
    model_name = Column(String, nullable=True)
    token_usage = Column(Integer, nullable=True)
    elapsed_time = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(microsecond=0))

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
Session = scoped_session(sessionmaker(bind=engine))

# Function to get conversation history
def get_conversation_history():
    session = Session()
    try:
        history = session.query(Conversation).order_by(Conversation.timestamp.desc()).all()
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
        # Prepare a dictionary to hold user and assistant messages
        messages = {"user": [], "assistant": []}

        # Organize messages into user and assistant lists, including model_name for assistants
        for conv in history:
            role = "user" if conv.role == "user" else "assistant"
            if role == "user":
                messages["user"].append((conv.content, conv.timestamp))
            else:
                messages["assistant"].append((conv.content, conv.timestamp, conv.model_name, conv.token_usage, conv.elapsed_time))

        # Determine the maximum number of messages between user and assistant
        max_len = max(len(messages["user"]), len(messages["assistant"]))

        # Display messages side by side
        for i in range(max_len):
            cols = st.columns(2)
            user_message = messages["user"][i] if i < len(messages["user"]) else (None, None)
            assistant_message = messages["assistant"][i] if i < len(messages["assistant"]) else (None, None, None)
            
            # Display user message
            if user_message[0]:
                cols[0].markdown(f"""
                    <div style="background-color: #ad6a5a; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                        <strong>User:</strong> {user_message[0]} <br> <small>Date and Time: {user_message[1]}</small>
                    </div>
                    """, unsafe_allow_html=True)

            # Display assistant message with model name
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



