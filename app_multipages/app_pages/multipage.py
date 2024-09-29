import streamlit as st


# Class to generate multiple Streamlit pages using an object oriented approach
class MultiPage:
    """
    A class to generate multiple Streamlit pages using an object-oriented approach.

    Attributes:
        pages (list): A list to store the pages added to the app.
        app_name (str): The name of the application.
    """    

    def __init__(self, app_name) -> None:
        """
        Initializes the MultiPage class with the application name.

        Args:
            app_name (str): The name of the application.
        """
        self.pages = []
        self.app_name = app_name

        # st.set_page_config(
        #     page_title=self.app_name,
        #     page_icon="🖥️")  # You may add an icon, to personalize your App
        # # check links below for additional icons reference
        # # https://docs.streamlit.io/en/stable/api.html#streamlit.set_page_config
        # # https://twemoji.maxcdn.com/2/test/preview.html

    def add_page(self, title, func) -> None:
        """
        Adds a new page to the application.

        Args:
            title (str): The title of the page to be added.
            func (callable): The function that renders the content of the page.
        """
        self.pages.append({"title": title, "function": func})

    def run(self):
        """
        Runs the application, displaying the selected page based on user input.

        The title of the application is displayed at the top, and a sidebar menu 
        is created for page navigation.
        """
        st.title(self.app_name)
        page = st.sidebar.radio('Menu', self.pages, format_func=lambda page: page['title'])
        page['function']()