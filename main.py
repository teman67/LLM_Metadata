import streamlit as st
import streamlit.components.v1 as components
import requests
import logging
from streamlit_extras.streaming_write import write
from dotenv import load_dotenv
import os
import time  # To measure time

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Initialize session state for messages and file content if not already present
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'file_content' not in st.session_state:
    st.session_state.file_content = None

def count_tokens(text):
    """Simple function to count tokens based on whitespace."""
    return len(text.split())

def query_api(prompt, model='gemma2:27b'):
    url = os.getenv('API_URL')  # Get the URL from an environment variable
    headers = {"Authorization": os.getenv('API_KEY', 'Bearer ignore-me')}  # Get the API key from an environment variable 
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    # Measure the time taken for the request
    start_time = time.time()
    response = requests.post(url, json=payload, headers=headers)
    elapsed_time = time.time() - start_time

    if response.status_code == 200:
        response_json = response.json()
        # Count tokens in the prompt and response
        prompt_tokens = count_tokens(prompt)
        response_tokens = count_tokens(response_json['choices'][0]['message']['content'])
        total_tokens = prompt_tokens + response_tokens
        
        return {
            "response": response_json,
            "elapsed_time": elapsed_time,
            "total_tokens": total_tokens
        }
    else:
        return {
            "error": f"Failed with status code {response.status_code}",
            "elapsed_time": elapsed_time,
            "total_tokens": 0
        }

def main():
    html_component = """
    <div style="background-color: #374C9D; padding: 10px; text-align: center;">
        <h1 style="color: white; font-weight: bold;">Meta data management</h1>
    </div>
    """
    components.html(html_component)

    st.header("Choose How to Ask Your Question")

    # Language Options
    languages = ["English", "Spanish", "French", "German", "Chinese"]

    # Tab for File Upload and Questions
    with st.expander("Upload a File and Ask a Question"):
        uploaded_file = st.file_uploader("Choose a file")
        
        if uploaded_file is not None:
            st.session_state.file_content = uploaded_file.read().decode("utf-8")
            st.write("File content preview:")
            st.write(st.session_state.file_content[:2000])  # Show a preview of the file content
            st.success("File uploaded successfully. You can now ask questions about this file.")
        
        user_question_file = st.text_area("Ask a question about the uploaded file:")
        language = st.selectbox("Select the language for the answer:", languages, key="language_file")

        if st.button("Submit Question about Uploaded File"):
            if st.session_state.file_content is None:
                st.warning("Please upload a file before asking a question.")
            elif user_question_file.strip() == "":
                st.warning("Please enter a question.")
            else:
                file_prompt = f"File content: {st.session_state.file_content}\n\nQuestion: {user_question_file}\n\nPlease answer in {language}."
                result = query_api(prompt=file_prompt, model='gemma2:27b')
                
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.write(f"Time taken: {result['elapsed_time']:.2f} seconds")
                    st.write(f"Total tokens used: {result['total_tokens']}")
                    
                    response_content = result['response']['choices'][0]['message']['content']
                    st.subheader("Response from the Model:")
                    write(response_content)

    # Tab for Direct Question Input
    with st.expander("Ask a Question Directly"):
        direct_question = st.text_area("Type your question here:")
        language_direct = st.selectbox("Select the language for the answer:", languages, key="language_direct")
        
        if st.button("Submit Question Directly"):
            if direct_question.strip() == "":
                st.warning("Please enter a question.")
            else:
                direct_prompt = f"{direct_question}\n\nPlease answer in {language_direct}."
                result = query_api(prompt=direct_prompt, model='gemma2:27b')
                
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.write(f"Time taken: {result['elapsed_time']:.2f} seconds")
                    st.write(f"Total tokens used: {result['total_tokens']}")
                    
                    response_content = result['response']['choices'][0]['message']['content']
                    st.subheader("Response from the Model:")
                    write(response_content)

if __name__ == "__main__":
    main()
