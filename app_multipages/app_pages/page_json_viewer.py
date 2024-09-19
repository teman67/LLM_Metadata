import streamlit as st
import json

def json_viewer():
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


