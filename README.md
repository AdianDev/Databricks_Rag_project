🔧 Microcontroller RAG Assistant

A Retrieval-Augmented Generation (RAG) application built with Databricks to answer technical questions about the Raspberry Pi RP2040 and RP2350 microcontrollers using retrieved Raspberry Pi documentation.

The application combines Databricks Vector Search, Databricks SQL, and a Databricks-hosted language model to generate documentation-grounded answers with source references.

📌 Overview

Understanding microcontroller documentation can involve searching through lengthy technical manuals, datasheets, and reference documents. This project provides a conversational interface for asking questions about RP2040, RP2350, and related Raspberry Pi documentation.

Instead of relying only on a language model's general knowledge, the application retrieves relevant document passages and uses them as context when generating an answer.

✨ Key Features
Documentation-based question answering: Ask technical questions about RP2040, RP2350, and related Raspberry Pi documentation.
Retrieval-Augmented Generation: Retrieve relevant document chunks using Databricks Vector Search.
Databricks integration: Execute retrieval and model inference through Databricks SQL.
Source-aware responses: Instruct the model to cite supporting document filenames and page numbers.
Grounded answers: Instruct the model not to invent technical details or use unsupported outside knowledge.
Conversational interface: Interact with the assistant through a Streamlit chat interface.
Conversation management: Review previous messages in the current session and clear the conversation when needed.
Fallback handling: Return a predefined response when the retrieved documentation does not contain enough information to answer a question.
🏗️ Architecture

The application follows a retrieval-augmented question-answering workflow.

flowchart TD
    A[User asks a question] --> B[Streamlit Chat Interface]
    B --> C[Databricks App Authentication]
    C --> D[Databricks SQL Warehouse]
    D --> E[Databricks Vector Search]
    E --> F[Retrieve Top 5 Document Chunks]
    F --> G[Build Retrieved Context]
    G --> H[Databricks AI Query]
    H --> I[databricks-gpt-oss-20b]
    I --> J[Generate Grounded Answer]
    J --> K[Display Answer with Source References]

How It Works
Question input: The user submits a technical question through the Streamlit chat interface.
Databricks connection: The application connects to a Databricks SQL Warehouse using the Databricks SDK configuration and application authentication.
Document retrieval: Databricks Vector Search retrieves the five most relevant document chunks for the user's question.
Context construction: The application combines retrieved text with document filenames, page numbers, product names, and document types.
Answer generation: The ai_query() SQL function invokes the databricks-gpt-oss-20b model with the question and retrieved context.
Source-aware response: The model is instructed to answer using the retrieved documentation and cite the relevant filenames and page numbers.
Response display: The answer is displayed in the Streamlit interface and added to the current conversation.

Important: This repository contains the application layer. The documentation ingestion, chunking, embedding generation, and vector index creation processes are not demonstrated in the visible app.py file and must be configured separately if they are not already available in the Databricks workspace.

🛠️ Technology Stack
Technology	Purpose
Python	Application programming language
Streamlit	Interactive chat interface
Databricks Apps	Application deployment environment
Databricks SDK	Workspace configuration and authentication
Databricks SQL Connector	Connects the application to a SQL Warehouse
Databricks Vector Search	Retrieves relevant documentation chunks
Databricks SQL ai_query()	Invokes the configured language model
databricks-gpt-oss-20b	Language model specified in the application code
Retrieval-Augmented Generation (RAG)	Grounds generated answers in retrieved documentation
📂 Repository Structure
Databricks_Rag_project/
├── app.py
├── app.yaml
├── requirements.txt
├── Databricks_Rag_project.zip
└── README.md

File Descriptions
app.py — Implements the Streamlit interface, Databricks SQL connection, vector retrieval query, model invocation, response handling, and session-based conversation history.
app.yaml — Configures the Streamlit application command and references the SQL Warehouse resource through DATABRICKS_WAREHOUSE_ID.
requirements.txt — Lists the Python dependencies required by the application.
Databricks_Rag_project.zip — Project archive. Its contents and role have not been verified here.
README.md — Project documentation.
⚙️ Prerequisites

Before deploying the application, ensure that you have:

Access to a Databricks workspace.
Permission to create or deploy a Databricks App.
A configured Databricks SQL Warehouse.
A Vector Search index named microcontrollers.rag_project.document_search.
A compatible Databricks-hosted model endpoint or model configuration supporting the ai_query() invocation used by the application.
Appropriate permissions for the application's identity to access the SQL Warehouse, Vector Search index, and model.
An initialized document index containing relevant Raspberry Pi documentation.

The required workspace resources must exist and be accessible before the application can answer questions successfully.

🚀 Installation and Deployment
1. Clone the repository
git clone https://github.com/AdianDev/Databricks_Rag_project.git
cd Databricks_Rag_project

2. Install dependencies

Create and activate a Python virtual environment if you are running the application locally.

python -m venv .venv


Activate it:

Windows PowerShell

.venv\Scripts\Activate.ps1


Linux/macOS

source .venv/bin/activate


Install the project dependencies:

pip install -r requirements.txt

3. Configure Databricks resources

The application expects the following Vector Search index:

microcontrollers.rag_project.document_search


The index is referenced directly in the SQL query inside app.py.

The application also expects the SQL Warehouse resource to provide the DATABRICKS_WAREHOUSE_ID environment variable. The supplied app.yaml declares this resource reference:

command:
  - streamlit
  - run
  - app.py

env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql-warehouse


Ensure that the corresponding SQL Warehouse resource is configured correctly in your Databricks App deployment environment.

Note: The model name and Vector Search index are hardcoded in the application. If your workspace uses different names, update the relevant references in app.py.

4. Deploy as a Databricks App

The repository is configured to launch Streamlit using app.yaml.

To deploy:

Open your Databricks workspace.
Navigate to Databricks Apps.
Create or configure an app using this repository's application files.
Configure the SQL Warehouse resource expected by app.yaml.
Grant the application identity the necessary permissions to access the SQL Warehouse, Vector Search index, and model.
Deploy or restart the app and open its application URL.

Exact deployment steps may vary depending on your workspace configuration and permissions. The app has not been independently deployed or tested as part of preparing this README.

5. Run locally (optional)

The application can be launched with Streamlit:

streamlit run app.py


However, successful local execution is not guaranteed by the repository configuration alone. You must provide a compatible Databricks workspace configuration, authentication, access to the required resources, and the expected SQL Warehouse environment variable. The provided app.yaml is designed around the Databricks App environment.

💬 Example Questions

Once the application is connected to a populated documentation index, you can try questions such as:

What are the main features of the RP2040 microcontroller?
What are the key specifications of the RP2350?
What does the documentation say about the microcontroller's architecture?
Which document describes a particular peripheral or hardware feature?
Which page contains information about a specific technical specification?
What differences between RP2040 and RP2350 are documented in the retrieved sources?

These are example prompts, not verified test results. The quality and completeness of responses depend on the documents available in the configured Vector Search index.

🔍 Answer Grounding and Source References

The application includes instructions intended to improve technical accuracy:

Use only information contained in the retrieved documentation.
Avoid unsupported assumptions and invented technical details.
Cite the source filename and page number for factual claims.
Prefer the most relevant sources instead of citing every retrieved chunk.
Return a fallback message when the retrieved documentation does not provide enough information.

The configured fallback response is:

The retrieved documentation does not contain enough information to answer this question.

These safeguards are implemented through the model prompt. They encourage grounded responses but do not guarantee that every generated answer or citation will be correct.

🔐 Configuration and Security

The application uses the Databricks SDK configuration to determine the workspace host and authenticate its SQL connection through the Databricks App environment.

For a secure deployment:

Grant the application's identity only the permissions it needs.
Keep credentials, access tokens, and other secrets out of source control.
Configure workspace resources and access policies through the appropriate Databricks settings.
Avoid exposing sensitive technical details when sharing error logs.
Review model and SQL Warehouse permissions before deploying the application.
⚠️ Current Limitations
Answers depend on the coverage and quality of the indexed documentation.
The application retrieves a fixed number of five document chunks per question.
The Vector Search index and model name are hardcoded in the SQL query.
The visible application code does not include the document ingestion or index-building pipeline.
Conversation history is maintained in Streamlit session state and is not shown to persist across sessions.
Source citations are generated according to model instructions and are not independently validated by the application.
Automated tests, performance benchmarks, and deployment verification are not included in the currently documented implementation.
🛣️ Potential Future Improvements
Add a reproducible document ingestion and indexing pipeline.
Support configurable retrieval parameters and result counts.
Display retrieved source documents and page references separately from generated answers.
Add filters for microcontroller model, document type, or source document.
Introduce automated tests for retrieval, answer grounding, and error handling.
Add evaluation metrics for retrieval relevance and answer quality.
Improve observability with structured logging and performance monitoring.
Add example screenshots and verified deployment instructions.

These are potential enhancements, not claims about existing functionality.

📚 Resources
Project Repository
Databricks Documentation
Databricks Apps Documentation
Databricks Vector Search Documentation
Databricks AI Functions Documentation
Raspberry Pi Documentation
RP2040 Datasheet
RP2350 Datasheet
🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

Fork the repository.
Create a feature branch.
Make your changes and test them in an appropriately configured environment.
Submit a pull request describing the changes.
📄 License

No license has been verified for this repository. Add a LICENSE file and update this section once you have selected a license for the project.

Built with Python, Streamlit, and Databricks to make Raspberry Pi microcontroller documentation easier to explore through conversational AI.
