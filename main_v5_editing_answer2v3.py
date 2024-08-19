import streamlit as st
import requests
import logging
from streamlit_extras.streaming_write import write
from dotenv import load_dotenv
import os
import time

# Function to show the warning message
def show_warning_message():
    if not st.session_state.warning_shown:
        placeholder = st.empty()
        placeholder.markdown('<div style="background-color: #FFEEEB; padding: 30px; margin-top: 40px; border-radius: 5px; text-align: center;"><p style="font-size: 20px; color: #333333"><strong>For better visualization, it is recommended to use Dark mode instead of Light mode in Settings.</strong></p></div>', unsafe_allow_html=True)
        st.session_state.warning_shown = True
        time.sleep(5)  # Wait for 5 seconds
        placeholder.empty()

# Set page configuration
st.set_page_config(page_title="MetaData Retrieval", layout="wide")

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Get the API key
api_key = os.getenv('API_KEY')
if not api_key:
    st.error("Error: API_KEY is missing or empty in the environment variables.")
    st.stop()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'file_content' not in st.session_state:
    st.session_state.file_content = None

def count_tokens(text):
    return len(text.split())

def query_api(prompt, model='gemma2:27b'):
    url = os.getenv('API_URL')
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    start_time = time.time()
    response = requests.post(url, json=payload, headers=headers)
    elapsed_time = time.time() - start_time

    if response.status_code == 200:
        response_json = response.json()
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

def compare_models(prompt, language):
    models = ['mixtral']
    results = {}

    st.write("### Model Comparison Results")
    with st.spinner("Fetching responses from models..."):
        for model in models:
            result = query_api(prompt=prompt, model=model)
            results[model] = result

    cols = st.columns(1)
    for idx, model in enumerate(models):
        with cols[idx]:
            st.write(f"**Model: {model}**")
            if 'error' in results[model]:
                st.error(results[model]['error'])
            else:
                st.write(f"⏱ **Time taken:** {results[model]['elapsed_time']:.2f} seconds")
                st.write(f"🔢 **Total tokens used:** {results[model]['total_tokens']}")
                response_content = results[model]['response']['choices'][0]['message']['content']
                st.session_state[f'response_{model}'] = response_content  # Store the response
                st.subheader("Response from the Model:")
                write(response_content)
                if st.button(f"Edit Response ({model})", key=f"edit_button_{model}"):
                    st.experimental_set_query_params(page="edit", model=model)
                    st.experimental_rerun()

def edit_page():
    query_params = st.query_params
    model = query_params.get('model', [None])[0]

    if model:
        st.write(f"### Editing Response for Model: {model}")
        original_response = st.session_state.get(f'response_{model}', '')

        if original_response:
            edited_response = st.text_area("Edit the response:", original_response, height=300)
            if st.button("Save Changes"):
                st.session_state[f'response_{model}'] = edited_response
                st.success("Response updated successfully!")
                st.experimental_set_query_params(page="main")
                st.experimental_rerun()
        else:
            st.error("No response found for this model.")
    else:
        st.error("No model selected for editing.")

def main():
    if 'warning_shown' not in st.session_state:
        st.session_state.warning_shown = False

    # CSS for the background image
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

    # Custom CSS for font size
    st.markdown(
        """
        <style>
        body {
            font-size: 1.1em;
        }
        .stTextArea textarea {
            font-size: 1.1em;
        }
        .stButton button {
            font-size: 1.1em;
        }
        .stMarkdown p {
            font-size: 1.1em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display warning message
    show_warning_message()

    # Page Header
    st.markdown("""
        <div style="padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; font-weight: bold; font-size: 3em;">MetaData Retrieval</h1>
        </div>
    """, unsafe_allow_html=True)

    st.header("Choose How to Ask Your Question")
    st.write("Explore the options below to either upload a file and ask a related question, or simply ask a question directly.")

    # Language Options
    languages = ["English", "Spanish", "French", "German", "Chinese", "Persian", "Hindi", "Russian"]
    default_language = "English"

    # File Upload and Question Section
    with st.expander("📄 Upload a File and Ask a Question"):
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx", "pdf"])
        
        if uploaded_file is not None:
            try:
                st.session_state.file_content = uploaded_file.read().decode("utf-8")
                st.write("### File Content Preview:")
                st.text_area("", st.session_state.file_content[:2000], height=200, disabled=True)
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
                file_prompt = f"File content: {st.session_state.file_content}\n\nQuestion: {user_question_file}\n\nPlease answer in {language}."
                compare_models(file_prompt, language)

    # Direct Question Section
    with st.expander("💬 Ask a Question Directly"):
        direct_question = st.text_area("Type your question here:", help="Enter any question you have.")
        language_direct = st.selectbox("Select the language for the answer:", languages, index=languages.index(default_language), key="language_direct")
        
        if st.button("Submit Question Directly"):
            if direct_question.strip() == "":
                st.warning("Please enter a question.")
            else:
                direct_prompt = f"{direct_question}\n\nPlease answer in {language_direct}."
                compare_models(direct_prompt, language_direct)

# Main function to handle page routing
def app():
    query_params = st.query_params
    page = query_params.get('page', [None])[0]

    if page == "edit":
        edit_page()
    else:
        main()

if __name__ == "__main__":
    app()
