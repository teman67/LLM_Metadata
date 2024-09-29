import streamlit as st
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import logging
from dotenv import load_dotenv
import os
import time

# Function to show the warning message
def show_warning_message():
    '''
    Displays the warning message recommending dark mode over light mode.
    '''

    if not st.session_state.warning_shown:
        placeholder = st.empty()
        placeholder.markdown('<div style="background-color: #FFEEEB; padding: 30px; margin-top: 40px; border-radius: 5px; text-align: center;"><p style="font-size: 20px; color: #333333"><strong>For better visualization, it is recommended to use Dark mode instead of Light mode in Settings.</strong></p></div>', unsafe_allow_html=True)
        st.session_state.warning_shown = True

        time.sleep(5)  # Wait for 5 seconds
        placeholder.empty()

# Set page configuration with a more visually appealing layout
st.set_page_config(page_title="MetaData Retrieval", layout="wide")

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Initialize session state for messages and file content if not already present
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'file_content' not in st.session_state:
    st.session_state.file_content = None

# Load MatSciBERT model and tokenizer
model_name = "m3rg-iitd/matscibert"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

def predict(text):
    """Function to get prediction from MatSciBERT."""
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.logits.argmax().item()

def compare_models(prompt, language):
    """Function to get responses from MatSciBERT model."""
    st.write("### Model Results")
    with st.spinner("Fetching response from MatSciBERT..."):
        result = predict(prompt)
        st.write(f"**MatSciBERT Result:** {result}")

def main():

    if 'warning_shown' not in st.session_state:
        st.session_state.warning_shown = False

    # CSS to set the background image
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
    
    # Inject CSS
    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Custom CSS for increasing font size
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

    # Call the function to display the warning message
    show_warning_message()

    # Improved header with consistent and appealing design
    st.markdown("""
        <div style="padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; font-weight: bold; font-size: 3em;">MetaData Retrieval</h1>
        </div>
    """, unsafe_allow_html=True)

    st.header("Choose How to Ask Your Question")
    st.write("Explore the options below to either upload a file and ask a related question, or simply ask a question directly.")

    # Language Options with better default language and tooltips
    languages = ["English", "Spanish", "French", "German", "Chinese", "Persian", "Hindi", "Russian"]
    default_language = "English"

    # Tab for File Upload and Questions
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

    # Tab for Direct Question Input
    with st.expander("💬 Ask a Question Directly"):
        direct_question = st.text_area("Type your question here:", help="Enter any question you have.")
        language_direct = st.selectbox("Select the language for the answer:", languages, index=languages.index(default_language), key="language_direct")
        
        if st.button("Submit Question Directly"):
            if direct_question.strip() == "":
                st.warning("Please enter a question.")
            else:
                direct_prompt = f"{direct_question}\n\nPlease answer in {language_direct}."
                compare_models(direct_prompt, language_direct)


if __name__ == "__main__":
    main()
