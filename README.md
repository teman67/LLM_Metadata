# Metadata Schema Builder Interface

### Live link [Metadata Retrieval](https://llm-metadata-9be4a58fb16b.herokuapp.com/)

## Overview

Welcome to the Metadata Schema Builder Interface! This web application allows users to generate a metadata schema based on an uploaded experimental machine data file. By leveraging the power of a large language model (LLM), the interface processes the input data and outputs a JSON file that represents the metadata schema. This tool is designed to simplify the creation of metadata schemas, making it easier to standardize data across experiments and systems.

## Features

- **File Upload:** Upload your experimental machine data file in the supported format.
- **Automated Schema Generation:** The interface uses an LLM model to analyze the uploaded data and generate a metadata schema in JSON format.
- **JSON Output:** Download the generated metadata schema as a JSON file for further use or integration.
- **User-Friendly Interface:** The web interface is designed to be intuitive and easy to use, even for users with minimal technical expertise.

## Getting Started

### Prerequisites

Before using the Metadata Schema Builder Interface, ensure you have the following:

- A modern web browser (e.g., Chrome, Firefox, Edge).
- An experimental machine data file in a supported format (e.g., CSV, TSV, Excel).

### Installation

If you're running this interface locally, follow these steps to set it up:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/metadata-schema-builder.git
   cd metadata-schema-builder
   ```

2. **Install Dependencies:**

   Ensure you have Node.js and npm installed. Then, run:

   ```bash
   npm install
   ```

3. **Run the Application:**

   Start the development server:

   ```bash
   npm start
   ```

   The application will be available at `http://localhost:3000`.

### Usage

1. **Access the Interface:**

   Open the web interface in your browser.

2. **Upload a File:**

   - Click the "Upload" button.
   - Select your experimental machine data file from your local machine.

3. **Generate Metadata Schema:**

   - Click the "Generate Schema" button.
   - The interface will process the uploaded file and display the resulting metadata schema.

4. **Download JSON File:**

   - Click the "Download JSON" button to save the generated metadata schema to your local machine.

## File Formats

The interface currently supports the following file formats for upload:

- CSV (Comma-Separated Values)
- TSV (Tab-Separated Values)
- Excel (XLSX)

Please ensure that your data file is properly formatted before uploading to avoid any errors during schema generation.

## Contributing

We welcome contributions to enhance the Metadata Schema Builder Interface! To contribute:

1. Fork the repository.
2. Create a new branch with your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add a new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Create a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions, issues, or suggestions, please feel free to reach out:

- **Email:** amirhossein.bayani@gmail.com

---

Thank you for using the Metadata Schema Builder Interface! We hope it simplifies your metadata creation process.