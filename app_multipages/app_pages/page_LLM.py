import streamlit as st
import requests
import logging
from streamlit_extras.streaming_write import write
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import time
from .login import login
from pytz import timezone

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
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone('UTC')).astimezone(timezone('Europe/Berlin')).replace(microsecond=0))
    username = Column(String, nullable=False)  

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
SessionFactory = sessionmaker(bind=engine)

def save_message_to_db(role, content, model_name=None, elapsed_time=None, token_usage=None):
    session = SessionFactory()
    try:
        conversation = Conversation(
            role=role, 
            content=content, 
            model_name=model_name, 
            elapsed_time=elapsed_time, 
            token_usage=token_usage,
            username=st.session_state.username  
        )
        session.add(conversation)
        session.commit()
    except Exception as e:
        session.rollback()
        st.error(f"An error occurred while saving to the database: {e}")
    finally:
        session.close()

# Initialize session state for messages and file content if not already present
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'file_content' not in st.session_state:
    st.session_state.file_content = None

# Predefined list of colors for alternating boxes
colors = ["#fc9642", "#5aad78", "#416a96", "#8f894a", "#9e3c72", "#7e5dc2", "#8c1416"]

# List of available models
models = ['mixtral:latest', 'llama3.1:latest', 'llama3.1:70b', 'llama3.1:70b-instruct-q8_0']

def count_tokens(text):
    """Simple function to count tokens based on whitespace."""
    return len(text.split())

def query_api(messages, model, tempreture=0.7, max_tokens=300, top_p=0.9):
    url = os.getenv('API_URL')
    headers = {"Authorization": f"Bearer {'API_KEY'}"}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": tempreture,
        "max_tokens": max_tokens,
        "top_p": top_p
    }

    start_time = time.time()
    response = requests.post(url, json=payload, headers=headers)
    elapsed_time = time.time() - start_time

    response_json = response.json()
    
    if response.status_code == 200:
        if 'choices' in response_json and len(response_json['choices']) > 0:
            choice = response_json['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                response_content = choice['message']['content']
                prompt_tokens = count_tokens('\n'.join([msg['content'] for msg in messages]))
                response_tokens = count_tokens(response_content)
                total_tokens = prompt_tokens + response_tokens
                
                return {
                    "response": response_json,
                    "elapsed_time": elapsed_time,
                    "total_tokens": total_tokens,
                    "content": response_content
                }
            else:
                return {
                    "error": "API response missing 'message' or 'content' key",
                    "elapsed_time": elapsed_time,
                    "total_tokens": 0
                }
        else:
            return {
                "error": "API response missing 'choices' key or empty 'choices'",
                "elapsed_time": elapsed_time,
                "total_tokens": 0
            }
    else:
        return {
            "error": f"Failed with status code {response.status_code}",
            "elapsed_time": elapsed_time,
            "total_tokens": 0
        }



def compare_models(messages, selected_model):
    results = {}

    st.write("### Model Comparison Results")
    with st.spinner("Fetching responses from models..."):
        result = query_api(messages=messages, model=selected_model)
        results[selected_model] = result

    cols = st.columns(1)
    for idx, model in enumerate([selected_model]):
        with cols[idx]:
            st.write(f"**Model: {model}**")
            if 'error' in results[model]:
                st.error(results[model]['error'])
            else:
                response_content = results[model]['response']['choices'][0]['message']['content']
                elapsed_time = results[model]['elapsed_time']
                total_tokens = results[model]['total_tokens']
                # Save response to the database with model details
                save_message_to_db(
                    role="assistant", 
                    content=response_content, 
                    model_name=model, 
                    elapsed_time=elapsed_time, 
                    token_usage=total_tokens
                )
                st.write(f"⏱ **Time taken:** {results[model]['elapsed_time']:.2f} seconds")
                st.write(f"🔢 **Total tokens used:** {results[model]['total_tokens']}")
                response_content = results[model]['response']['choices'][0]['message']['content']
                st.subheader("Response from the Model:")
                write(response_content)

def display_conversation_history():
    st.write("### Conversation History")
    for idx, msg in enumerate(st.session_state.messages):
        # Alternate colors based on the index
        color = colors[idx % len(colors)]
        role = "User" if msg['role'] == "user" else "Assistant"
        st.markdown(f"""
            <div style="background-color: {color}; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                <strong>{role}:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)

def download_conversation_history():
    # Format the conversation history
    history_text = ""
    for msg in st.session_state.messages:
        role = "User" if msg['role'] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n\n"

    # Provide a download button
    st.download_button(
        label="Download Conversation History",
        data=history_text,
        file_name="conversation_history.txt",
        mime="text/plain"
    )

def main():
    # Ensure that session state variables are initialized at the very beginning
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'file_content' not in st.session_state:
        st.session_state.file_content = None
    if 'warning_shown' not in st.session_state:
        st.session_state.warning_shown = False

    # Add login check
    if not login():
        return  # Stop the app if the user is not logged in

    # Add widgets for setting parameters
    st.sidebar.header("Model Parameters")
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
    max_tokens = st.sidebar.number_input("Max Tokens", min_value=1, max_value=2000, value=300)
    top_p = st.sidebar.slider("Top-p", 0.0, 1.0, 0.9)

    # The rest of your main app logic goes here...
    page_bg_img = '''
    <style>
    [data-testid="stApp"]{
        background-image: url("https://miro.medium.com/v2/resize:fit:960/1*5UvMSNiSNFiMO1OE_xeJJA.png");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.header("Choose How to Ask Your Question")
    st.write("Explore the options below to either upload a file and ask a related question, or simply ask a question directly.")

    selected_model = st.selectbox("Select LLM Model:", models)

    languages = ["English", "German"]
    default_language = "English"

    with st.expander("📄 Upload a File and Ask a Question"):
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx", "json", "dat"])
        
        if uploaded_file is not None:
            try:
                st.session_state.file_content = uploaded_file.read().decode("utf-8")
                st.success("File uploaded successfully. You can now ask questions about this file.")
            except Exception as e:
                st.error(f"An error occurred while reading the file: {e}")

        user_question_file = st.text_area("Ask a question about the uploaded file:", help="Enter a question related to the content of the uploaded file.")
        language = st.selectbox("Select the language for the answer:", languages, index=languages.index(default_language), key="language_file")

        if st.button("Submit Question about Uploaded File"):
            if st.session_state.file_content is None:
                st.warning("Please upload a file before asking a question.")
            elif user_question_file.strip() == "":
                st.warning("Please enter a question.")
            else:
                st.session_state.messages.append({"role": "user", "content": f"Question about the uploaded file: {user_question_file}\n\nPlease answer in {language}."})
                save_message_to_db("user", f"Question about the uploaded file: {user_question_file}\n\nPlease answer in {language}.")
                # display_conversation_history()
                
                api_messages = [{"role": "user", "content": f"File content: {st.session_state.file_content}\n\nQuestion: {user_question_file}\n\nPlease answer in {language}."}]
                result = query_api(messages=api_messages, model=selected_model, tempreture=temperature, max_tokens=max_tokens, top_p=top_p)
                
                if 'error' in result:
                    st.error(result['error'])
                else:                                   
                    response = result['content']
                    elapsed_time = result['elapsed_time']
                    total_tokens = result['total_tokens']
                    # Save assistant response with model info
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    save_message_to_db("assistant", response, model_name=selected_model, elapsed_time=elapsed_time, token_usage=total_tokens)
                    # Display results
                    st.write(f"⏱ **Time taken:** {elapsed_time:.2f} seconds")
                    st.write(f"🔢 **Total tokens used:** {total_tokens}")
                    display_conversation_history()
                    

    with st.expander("💬 Ask a Question Directly"):
        direct_question = st.text_area("Type your question here:", help="Enter any question you have.")
        language_direct = st.selectbox("Select the language for the answer:", languages, index=languages.index(default_language), key="language_direct")
        
        if st.button("Submit Question Directly"):
            if direct_question.strip() == "":
                st.warning("Please enter a question.")
            else:
                st.session_state.messages.append({"role": "user", "content": f"{direct_question}\n\nPlease answer in {language_direct}."})
                save_message_to_db("user", f"{direct_question}\n\nPlease answer in {language_direct}.")
                # display_conversation_history()
                
                api_messages = st.session_state.messages
                result = query_api(messages=api_messages, model=selected_model, tempreture=temperature, max_tokens=max_tokens, top_p=top_p)
                
                if 'error' in result:
                    st.error(result['error'])
                else:
                    response = result['content']
                    elapsed_time = result['elapsed_time']
                    total_tokens = result['total_tokens']
                    # Save assistant response with model info
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    save_message_to_db("assistant", response, model_name=selected_model, elapsed_time=elapsed_time, token_usage=total_tokens)
                    # Display results
                    st.write(f"⏱ **Time taken:** {elapsed_time:.2f} seconds")
                    st.write(f"🔢 **Total tokens used:** {total_tokens}")
                    display_conversation_history()
                    
                    
    # Add the download button for conversation history
    download_conversation_history()

if __name__ == "__main__":
    main()
