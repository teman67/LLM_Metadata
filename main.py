import streamlit as st
import streamlit.components.v1 as components
import requests
import logging
from streamlit_extras.streaming_write import write

logging.basicConfig(level=logging.INFO)

# Initialize session state for messages if not already present
if 'messages' not in st.session_state:
    st.session_state.messages = []