import streamlit as st
from app_pages.multipage import MultiPage

# load pages scripts
from app_pages.page_summary import page_summary_body
from app_pages.page_LLM import *


app = MultiPage(app_name="MetaData Retrieval")  # Create an instance of the app
st.set_page_config(layout="wide")

# Add your app pages here using .add_page()
app.add_page("Quick Project Summary", page_summary_body)
app.add_page("Using LLM for MetaData Retrieval", main)


app.run()  # Run the app