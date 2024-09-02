# Metadata Schema Builder Interface

### Live link [Metadata Retrieval](https://llm-metadata-9be4a58fb16b.herokuapp.com/)


## Overview

Welcome to the Metadata Schema Builder Interface! This web application allows users to generate a metadata schema based on an uploaded experimental machine data file. By leveraging the power of a large language model (LLM), the interface processes the input data and outputs a JSON file that represents the metadata schema. This tool is designed to simplify the creation of metadata schemas, making it easier to standardize data across experiments and systems.

## Features

- **File Upload:** Upload your experimental machine data file in the supported format.
- **Automated Schema Generation:** The interface uses an LLM model to analyze the uploaded data and generate a metadata schema.
- **Language Selection**: Choose the language for the responses.
- **Output:** Download the generated metadata schema as a file for further use or integration.
- **User-Friendly Interface:** The web interface is designed to be intuitive and easy to use, even for users with minimal technical expertise.

## Installation

### Clone the Repository

```bash
git clone https://github.com/teman67/LLM_Metadata.git
cd LLM_Metadata
```

### Set Up a Virtual Environment (Optional but Recommended)

```bash
python -m .venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the root directory with the following content:

```env
API_KEY=your_api_key
API_URL=your_api_url
```

Replace `your_api_key` and `your_api_url` with your actual API key and URL.

## Usage

### Run the Application

```bash
streamlit run app.py
```

### Access the App

Open your web browser and go to `http://localhost:8501`.

## How to Use

### Upload a File and Ask a Question

1. Upload a file (supports `.txt`, `.docx`, `.json`, `.dat`).
2. Enter your question about the file.
3. Select the language for the response.
4. Click "Submit Question about Uploaded File" to get the response.

### Ask a Question Directly

1. Enter your question in the text area.
2. Select the language for the response.
3. Click "Submit Question Directly" to receive the answer.

### Model Selection

- Choose a model from the dropdown menu.

### Conversation History

- View and download the conversation history using the provided button.

## Configuration

- **API Key**: Ensure your API key is set in the `.env` file.
- **API URL**: Specify the API endpoint URL in the `.env` file.
- **Models**: Modify the list of available models in the source code as needed.

## Troubleshooting

- **Missing API Key**: Make sure the `API_KEY` is correctly set in the `.env` file.
- **File Upload Issues**: Verify file format and encoding, and ensure the file is correctly processed.
- **Model Errors**: Confirm that the API URL and model configurations are accurate.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please contact [amirhossein.bayani@gmail.com](mailto:amirhossein.bayani@gmail.com).

---

Enjoy exploring different language models with this app!
