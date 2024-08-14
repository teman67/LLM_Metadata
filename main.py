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

# Initialize session state for messages if not already present
if 'messages' not in st.session_state:
    st.session_state.messages = []

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

    # File Upload Section
    st.header("Upload a File for Analysis")
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        # Read the content of the uploaded file
        file_content = uploaded_file.read().decode("utf-8")
        st.write("File content preview:")
        st.write(file_content[:2000])  # Show a preview of the file content

        # Process the file content with the API
        if st.button("Analyze File"):
            result = query_api(prompt=file_content, model='gemma2:27b')

            if 'error' in result:
                st.error(result['error'])
            else:
                # Display elapsed time and token count
                st.write(f"Time taken: {result['elapsed_time']:.2f} seconds")
                st.write(f"Total tokens used: {result['total_tokens']}")
                
                response_content = result['response']['choices'][0]['message']['content']
                st.subheader("Response from the Model:")
                write(response_content)

    # Question Input Section
    st.header("Ask a Question")
    user_question = st.text_area("Type your question here:")

    # Button to submit the question
    if st.button("Submit Question"):
        if user_question.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Query the API with the user's question
            result = query_api(prompt=user_question, model='gemma2:27b')

            if 'error' in result:
                st.error(result['error'])
            else:
                # Display elapsed time and token count
                st.write(f"Time taken: {result['elapsed_time']:.2f} seconds")
                st.write(f"Total tokens used: {result['total_tokens']}")
                
                response_content = result['response']['choices'][0]['message']['content']
                st.subheader("Response from the Model:")
                write(response_content)

if __name__ == "__main__":
    main()
