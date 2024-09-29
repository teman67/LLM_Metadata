import streamlit as st
import json

def json_viewer():
    """
    A Streamlit-based JSON file visualizer and editor.

    Features:
    - Displays a custom background image using CSS.
    - Allows users to upload a JSON file for viewing and editing.
    - Displays the uploaded JSON file in raw format.
    - If the JSON file is a list of dictionaries, it can also be displayed as a table.
    - Provides an editable text area for modifying the JSON content.
    - Validates the edited JSON and provides a download button for the modified file.

    Functionality:
    - File uploader: Allows users to upload a JSON file.
    - Raw JSON Display: Shows the uploaded JSON data in a readable format.
    - Editable JSON: Provides a text area to edit the uploaded JSON content.
    - Download Edited JSON: Users can download the edited JSON file.

    Error Handling:
    - Catches `json.JSONDecodeError` to handle invalid JSON format in both uploaded and edited files.
    """


    page_bg_img = '''
    <style>
    [data-testid="stApp"]{
        background-image: url("https://cdn.pixabay.com/photo/2022/12/09/03/51/big-data-7644530_1280.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
    st.title("JSON File Visualizer and Editor")

    # File uploader for JSON file
    uploaded_file = st.file_uploader("Choose a JSON file", type="json")
    
    if uploaded_file is not None:
        # Read the file and parse JSON
        try:
            json_data = json.load(uploaded_file)
            
            # Display the raw JSON data
            st.subheader("Raw JSON Data")
            st.json(json_data)

            # If the JSON is a list of dictionaries, show it as a table
            if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
                st.subheader("JSON as a Table")
                st.write(json_data)

            # Editable JSON section
            st.subheader("Edit JSON")
            edited_json = st.text_area("Edit JSON content", value=json.dumps(json_data, indent=4), height=300)

            # Parse the edited JSON
            try:
                # Attempt to parse the edited JSON
                parsed_json = json.loads(edited_json)

                # Download button for the edited JSON
                st.download_button(
                    label="Download Edited JSON",
                    data=json.dumps(parsed_json, indent=4),
                    file_name='edited_data.json',
                    mime='application/json'
                )

            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please correct the errors in the JSON content.")
            
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid JSON file.")


