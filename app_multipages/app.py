import streamlit as st
from app_pages.multipage import MultiPage

# Set page configuration here
st.set_page_config(page_title="MetaData Retrieval", page_icon=":star:", layout="wide")

# load pages scripts
from app_pages.page_summary import page_summary_body
from app_pages.page_register import registration_page
from app_pages.page_LLM import *
from app_pages.history import *

app = MultiPage(app_name="MetaData Retrieval")  # Create an instance of the app

# Add your app pages here using .add_page()
app.add_page("Quick Project Summary", page_summary_body)
app.add_page("Registration Page", registration_page)
app.add_page("Using LLM for MetaData Retrieval", main)
app.add_page("History of Conversation", display_conversation_history)

page_bg_img = '''
<style>
[data-testid="stSidebar"] > div:first-child {
background-image: url("https://cdn.pixabay.com/photo/2016/01/02/02/36/sky-1117783_1280.jpg");
background-size: cover;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)


app.run()  # Run the app