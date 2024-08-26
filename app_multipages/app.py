import streamlit as st
from app_pages.multipage import MultiPage

# load pages scripts
from app_pages.page_summary import page_summary_body
from app_pages.page_LLM import *
# from app_pages.page_plant_disease_detector import page_plant_disease_detector_body
# from app_pages.page_project_hypothesis import page_project_hypothesis_body
# from app_pages.page_machine_learning_performance import page_machine_learning_performance_metrics

app = MultiPage(app_name="MetaData Retrieval")  # Create an instance of the app

# Add your app pages here using .add_page()
app.add_page("Quick Project Summary", page_summary_body)
app.add_page("Using LLM for MetaData Retrieval", main)
# app.add_page("Plant Disease Detection", page_plant_disease_detector_body)
# app.add_page("Project Hypothesis", page_project_hypothesis_body)
# app.add_page("Machine Learning Performance", page_machine_learning_performance_metrics)

# page_bg_img = '''
# <style>
# [data-testid="stReportViewContainer"]{
# background-image: url("https://res.cloudinary.com/dlthn5m1i/image/upload/v1708424801/background_tmh3qe.webp");
# background-size: cover;
# }
# [data-testid="stSidebar"] > div:first-child {
# background-image: url("https://res.cloudinary.com/dlthn5m1i/image/upload/v1708609849/flower-4905417_1280_errckh.jpg");
# }
# </style>
# '''
# st.markdown(page_bg_img, unsafe_allow_html=True)

app.run()  # Run the app