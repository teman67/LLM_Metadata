import streamlit as st
import matplotlib.pyplot as plt
import time

# Function to check if the warning message has been shown
def check_warning_message_state():
    '''
    Checks if the warning message has been shown.
    '''

    if 'warning_shown' not in st.session_state:
        st.session_state.warning_shown = False

# Function to show the warning message
def show_warning_message():
    '''
    Displays the warning message recommending light mode over dark mode.
    '''

    if not st.session_state.warning_shown:
        placeholder = st.empty()
        placeholder.markdown('<div style="background-color: #FFEEEB; padding: 30px; margin-top: 40px; border-radius: 5px; text-align: center;"><p style="font-size: 20px; color: #333333"><strong>For better visualization, it is recommended to use Light mode instead of Dark mode in Settings.</strong></p></div>', unsafe_allow_html=True)
        st.session_state.warning_shown = True

        time.sleep(5)  # Wait for 5 seconds
        placeholder.empty()


def page_summary_body():

    page_bg_img = '''
    <style>
    [data-testid="stApp"]{
        background-image: url("https://res.cloudinary.com/dlthn5m1i/image/upload/v1724674617/rm378-09_xeqzie.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

    '''
    Displays the page summary body including project details and a warning message.
    '''

    check_warning_message_state()
    show_warning_message()

    st.write("### Quick Project Summary")

    st.info(
        f"**Introducing to the Plant Disease Recognition**\n\n"
        f"Welcome to the Metadata Schema Builder Interface! This web application allows users to generate a metadata schema based on an uploaded experimental machine data file. By leveraging the power of a large language model (LLM), the interface processes the input data and outputs a JSON file that represents the metadata schema. This tool is designed to simplify the creation of metadata schemas, making it easier to standardize data across experiments and systems.\n")

    st.write(
        f"* For additional information, please visit and **read** the "
        f"[Project README file](https://github.com/teman67/LLM_Metadata/blob/main/README.md).")
    

    st.success(
        f"Features:\n"
        f"* 1 - File Upload: Upload your experimental machine data file in the supported format.\n"
        f"* 2 - JSON Output: Automated Schema Generation: The interface uses an LLM model to analyze the uploaded data and generate a metadata schema in JSON format.\n"
        f"* 3 - User-Friendly Interface: The web interface is designed to be intuitive and easy to use, even for users with minimal technical expertise."
        )
