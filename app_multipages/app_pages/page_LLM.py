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

# Define the database engine using the PostgreSQL URL
engine = create_engine(POSTGRESQL_URL)
Base = declarative_base()

# Define the Conversation model
class Conversation(Base):
    """
    Represents a conversation message stored in the database.

    Attributes:
        id (int): Primary key, autoincremented.
        role (str): Role of the speaker (e.g., user or assistant).
        content (str): The message content.
        model_name (str): Name of the model used to generate the response.
        token_usage (int): Number of tokens used in the response.
        elapsed_time (float): Time taken to generate the response.
        timestamp (datetime): Timestamp of when the message was created.
        username (str): Username of the user who initiated the conversation.
    """

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
    """
    Saves a message to the database.

    Args:
        role (str): The role of the speaker (e.g., user or assistant).
        content (str): The content of the message.
        model_name (str, optional): The name of the model used for the response.
        elapsed_time (float, optional): Time taken to generate the response.
        token_usage (int, optional): Number of tokens used in the response.
    """

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


def count_tokens(text):
    """
    Counts the number of tokens in a text based on whitespace.

    Args:
        text (str): The input text.

    Returns:
        int: Number of tokens in the text.
    """

    """Simple function to count tokens based on whitespace."""
    return len(text.split())

def compress_response(content, model, target_token_count):
    """
    Compresses a response to fit within the target token count while keeping coherence.

    Args:
        content (str): The original response content.
        model (str): The model used for generating responses.
        target_token_count (int): The desired number of tokens.

    Returns:
        str: The compressed response.
    """

    """Compresses the response to fit within the target token count while trying to maintain coherence."""
    def split_content(content, chunk_size):
        """Splits content into chunks of specified size."""
        return [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

    chunk_size = min(target_token_count * 2, len(content.split()))
    chunks = split_content(content, chunk_size)
    compressed_content = ""
    
    for chunk in chunks:
        summary_prompt = f"Summarize the following text to approximately {target_token_count} tokens or less, making sure to keep the response coherent and complete:\n\n{chunk}"
        response = query_api(messages=[{"role": "user", "content": summary_prompt}], model=model, max_tokens=target_token_count)
        
        if 'error' in response:
            return content  # Return the current content if there's an error
        
        compressed_content += response['content'] + " "
        if count_tokens(compressed_content) >= target_token_count:
            break
    
    # Ensure the response ends with a coherent conclusion if necessary
    if count_tokens(compressed_content) < target_token_count:
        final_summary_prompt = f"Please provide a final, coherent summary of the following text to complete the response:\n\n{compressed_content}"
        final_summary = query_api(messages=[{"role": "user", "content": final_summary_prompt}], model=model, max_tokens=target_token_count - count_tokens(compressed_content))
        compressed_content += final_summary.get('content', '')

    return compressed_content.strip()

def query_api(messages, model, temperature=0.7, max_tokens=600, top_k=40, top_p=0.9):
    """
    Queries an external API to get a response based on provided messages and model.

    Args:
        messages (list): List of message dictionaries.
        model (str): The model to be used.
        temperature (float, optional): The randomness in the response.
        max_tokens (int, optional): Maximum number of tokens in the response.
        top_k (int, optional): Limits the sampling pool to the top-k tokens.
        top_p (float, optional): Nucleus sampling for choosing from the top tokens.

    Returns:
        dict: API response data, including content, token usage, and errors (if any).
    """

    url = os.getenv('API_URL')
    headers = {"Authorization": f"Bearer {'API_KEY'}"}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_k": top_k,
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
                response_tokens = count_tokens(response_content)
                
                if response_tokens > max_tokens:
                    response_content = compress_response(response_content, model, max_tokens)
                
                prompt_tokens = count_tokens('\n'.join([msg['content'] for msg in messages]))
                total_tokens = prompt_tokens + response_tokens
                
                return {
                    "response": response_json,
                    "elapsed_time": elapsed_time,
                    "prompt_tokens": prompt_tokens,
                    "response_tokens": response_tokens,
                    "total_tokens": total_tokens,
                    "content": response_content
                }
            else:
                return {
                    "error": "API response missing 'message' or 'content' key",
                    "elapsed_time": elapsed_time,
                    "prompt_tokens": 0,
                    "response_tokens": 0,
                    "total_tokens": 0
                }
        else:
            return {
                "error": "API response missing 'choices' key or empty 'choices'",
                "elapsed_time": elapsed_time,
                "prompt_tokens": 0,
                "response_tokens": 0,
                "total_tokens": 0
            }
    else:
        return {
            "error": f"Failed with status code {response.status_code}",
            "elapsed_time": elapsed_time,
            "prompt_tokens": 0,
            "response_tokens": 0,
            "total_tokens": 0
        }

def display_response(response_content):
    """
    Displays the model's response in the Streamlit app.

    Args:
        response_content (str): The content of the response.
    """

    st.subheader("Response from the Model:")
    st.write(response_content)

def compare_models(messages, selected_model):
    """
    Fetches and compares responses from different models.

    Args:
        messages (list): List of user input messages.
        selected_model (str): The model to be compared.
    """

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
                response_content = results[model]['content']
                elapsed_time = results[model]['elapsed_time']
                response_tokens = results[model]['response_tokens']
                # Save response to the database with model details
                save_message_to_db(
                    role="assistant", 
                    content=response_content, 
                    model_name=model, 
                    elapsed_time=elapsed_time, 
                    token_usage=response_tokens
                )
                st.write(f"⏱ **Time taken:** {elapsed_time:.2f} seconds")
                st.write(f"🔢 **Total tokens used (response only):** {response_tokens}")
                st.subheader("Response from the Model:")
                write(response_content)

def display_conversation_history():
    """
    Displays the conversation history stored in session state.
    """

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
    """
    Provides a download option for the conversation history as a text file.
    """

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


predefined_prompt = (
    "Create a non-populated metadata schema for a tensile test using the uploaded raw data. "
    "The metadata schema should follow JSON schema standards, as documented in https://json-schema.org/"
)


def main():
    """
    Main function for the Streamlit app, handling user input, model selection, 
    and response generation.
    """

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'file_content' not in st.session_state:
        st.session_state.file_content = None
    if 'warning_shown' not in st.session_state:
        st.session_state.warning_shown = False

    if not login():
        return

    st.sidebar.header("Model Parameters")
    st.sidebar.write("Adjust the model parameters below to customize the response generation. See [Ollama Python Package](https://pypi.org/project/ollama-python/) for more details.")
    max_tokens = st.sidebar.slider("Max Tokens", 1, 5000, 600)
    # max_tokens = st.sidebar.number_input("Max Tokens", min_value=1, max_value=4000, value=600)
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
    top_k = st.sidebar.slider("Top-k", 1, 100, 40)
    # top_k = st.sidebar.number_input("Top-k", min_value=1, max_value=100, value=40)
    top_p = st.sidebar.slider("Top-p", 0.0, 1.0, 0.9)
    # List of available models
    models = ['mixtral:latest', 'mistral-large:latest', 'llama3.1:latest', 'llama3.1:70b', 'llama3.1:70b-instruct-q8_0']
    # Create a sidebar with a selectbox for model selection
    selected_model = st.sidebar.selectbox('Select a LLM model', models)

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

    # selected_model = st.selectbox("Select LLM Model:", models)

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

        # Add a checkbox for using the predefined prompt
        use_predefined_prompt = st.checkbox("Use predefined prompt for metadata schema", value=False)

        # Predefined prompt text
        predefined_prompt = (
            "Create a non-populated metadata schema for a tensile test using the uploaded row data. "
            "The metadata schema should follow JSON schema standards, as documented in https://json-schema.org/"
        )

        # Populate the text area based on the checkbox selection
        user_question_file = st.text_area(
            "Ask a question about the uploaded file:", 
            value=predefined_prompt if use_predefined_prompt else "", 
            help="Enter a question related to the content of the uploaded file."
        )

        language = st.selectbox("Select the language for the answer:", languages, index=languages.index(default_language), key="language_file")

        if st.button("Submit Question about Uploaded File"):
            if st.session_state.file_content is None:
                st.warning("Please upload a file before asking a question.")
            elif user_question_file.strip() == "":
                st.warning("Please enter a question.")
            else:
                api_messages = [{"role": "user", "content": f"File content: {st.session_state.file_content}\n\n{user_question_file}\n\nPlease answer in {language}."}]
                
                try:
                    result = query_api(messages=api_messages, model=selected_model, temperature=temperature, max_tokens=max_tokens, top_k=top_k, top_p=top_p)

                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        response = result['content']
                        elapsed_time = result['elapsed_time']
                        response_tokens = result['response_tokens']
                        st.session_state.messages.append({"role": "user", "content": f"File content: {st.session_state.file_content}\n\n{user_question_file}\n\nPlease answer in {language}."})
                        save_message_to_db("user", f"File content: {st.session_state.file_content}\n\n{user_question_file}\n\nPlease answer in {language}.")
                        
                        # Save the assistant's response if there is one
                        if response:
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            save_message_to_db("assistant", response, model_name=selected_model, elapsed_time=elapsed_time, token_usage=response_tokens)
                            st.write(f"⏱ **Time taken:** {elapsed_time:.2f} seconds")
                            st.write(f"🔢 **Total tokens used (response only):** {response_tokens}")
                            display_conversation_history()

                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    st.markdown("❌ Unable to connect to the model. Please contact admin: amirhossein.bayani@gmail.com", unsafe_allow_html=True)
                    print(f"Connection error: {e}")
                except Exception as e:
                    st.error("❌ Unable to connect to the model. Please contact admin: amirhossein.bayani@gmail.com")
                    

    with st.expander("💬 Ask a Question Directly"):
        direct_question = st.text_area("Type your question here:", help="Enter any question you have.")
        language_direct = st.selectbox("Select the language for the answer:", languages, index=languages.index(default_language), key="language_direct")
        
        if st.button("Submit Question Directly"):
            if direct_question.strip() == "":
                st.warning("Please enter a question.")
            else:
                
                api_messages = [{"role": "user", "content": f"File content: {st.session_state.file_content}\n\n{user_question_file}\n\nPlease answer in {language}."}]
                try:

                    result = query_api(messages=api_messages, model=selected_model, temperature=temperature, max_tokens=max_tokens, top_k=top_k, top_p=top_p)

                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        response = result['content']
                        elapsed_time = result['elapsed_time']
                        response_tokens = result['response_tokens']
                        
                        # Save the user input if a response is received
                        st.session_state.messages.append({"role": "user", "content": f"{direct_question}\n\nPlease answer in {language_direct}."})
                        save_message_to_db("user", f"{direct_question}\n\nPlease answer in {language_direct}.")

                        # Save the assistant's response if there is one
                        if response:
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            save_message_to_db("assistant", response, model_name=selected_model, elapsed_time=elapsed_time, token_usage=response_tokens)
                            st.write(f"⏱ **Time taken:** {elapsed_time:.2f} seconds")
                            st.write(f"🔢 **Total tokens used (response only):** {response_tokens}")
                            display_conversation_history()
                
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    st.markdown("❌ Unable to connect to the model. Please contact admin: amirhossein.bayani@gmail.com", unsafe_allow_html=True)
                    print(f"Connection error: {e}")
                except Exception as e:
                    st.error("❌ Unable to connect to the model. Please contact admin: amirhossein.bayani@gmail.com")
        


    download_conversation_history()

