import streamlit as st
import streamlit.components.v1 as components
import requests
import logging
from streamlit_extras.streaming_write import write
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Initialize session state for messages if not already present
if 'messages' not in st.session_state:
    st.session_state.messages = []

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

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed with status code {response.status_code}"}

def main():
    html_component = """
    <div style="background-color: #374C9D; padding: 10px; text-align: center;">
        <h1 style="color: white; font-weight: bold;">Meta data management</h1>
    </div>
    """
    components.html(html_component)

    # tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])

    # with tab1:
    #     st.title("A cat")
    #     st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
    # with tab2:
    #     st.header("A dog")
    #     st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
    # with tab3:
    #     st.header("An owl")
    #     st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
    
    # # Preprocessing Section
    # col1, col2 = st.columns(2)

    # with col1:
    #     st.text_input("Researcher Name", key="operator_name")
    #     st.text_input("Date", key="date")
    #     st.text_input("Experiment Name", key="experiment_name")
    #     st.text_input("Sample ID", key="sample_id")
    #     st.text_input("Sample Type", key="sample_type")
    #     st.text_input("Sample Length", key="sample_length")
    #     st.text_input("Sample Thickness", key="sample_thickness")
    #     st.text_input("Tools used", key="tool")
    #     st.selectbox("Dropdown 1", options=["Option 1", "Option 2"], key="dropdown1")
        
    # with col2:
    #     st.text_input("Researcher ID", key="operator_id")
    #     st.text_input("Time", key="time")
    #     st.text_input("Machine used", key="machine")
    #     st.text_input("Sample Name", key="sample_name")
    #     st.text_input("Sample size", key="sample_size")
    #     st.text_input("Sample Width", key="sample_width")
    #     st.text_input("Sample Weight", key="sample_weight")
    #     st.text_input("Experiment run time", key="experiment_run_time")
    #     st.selectbox("Dropdown 2", options=["Option A", "Option B"], key="dropdown2")

    # Question Input Section
    st.header("Ask a Question")
    user_question = st.text_area("Type your question here:")

    # Button to submit the question
    if st.button("Submit Question"):
        if user_question.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Query the API with the user's question
            response = query_api(prompt=user_question, model='gemma2:27b')

            if 'error' in response:
                st.error(response['error'])
            else:
                # Assuming the response format contains the generated text in the key 'choices'
                generated_text = response['choices'][0]['message']['content']
                st.subheader("Response from the Model:")
                write(generated_text)

if __name__ == "__main__":
    main()
