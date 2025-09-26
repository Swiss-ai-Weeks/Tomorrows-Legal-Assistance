# Gemini Context: Tomorrow's Legal Assistance

## Use Case Description
### Problem
Imagine facing a legal issue, but everything feels unclear. Emotionally caught up, all you want is to beright – but you have no idea if it’s even worth pursuing. Most people don’t know how much time andmoney such a process will cost. They have no clear idea of their chances of winning. Instead, they faceuncertainty and frustration when making decisions.​

### Objective​
Your solution aims to help individuals understand what they are getting into by providing a clearoverview of their legal situation. The solution should display the following features:​
- Likelihood of winning the case​
- Cost range (estimated financial effort)​
- Timeframe until the case is resolved

### Scope
In den Rechtsgebieten Verkehrs- und Strafrecht sowie Arbeitsrecht soll den Usern folgendesangeboten werden. Gestartet wird mit Verkehrs- und Strafrecht, sofern Zeit bleibt zusätzlichArbeitsrecht.​
Sie erhalten eine Antwort, ob sie ihr Anliegen weiterverfolgen sollen (Prozent / Score) mitBegründung.​
Cost Range: Kosten Anwalt (Pauschale AXA-ARAG), Gebühren, Gerichtskosten​
Next Steps​
Anleitung über die nächsten Schritte, z.B. Brief an Arbeitgeber oder auch wo man Hilfebekommen kann​
Timeframe als Teil der Next Steps (eher nur ein Hinweis auf Durchschnittsdauer)​
 
### Work Packets
- Orchestration (e.g. LangGraph)​
- Frontend (e.g. Streamlit)​
- Classifier Rechtsgebiet​
- RAG Base​
- Experts (Einschätzung, Timeline, Kosten)​
    - Arbeitsrecht​
    - Strafrecht​
    - Verkehrsrecht​
    - Immobilienrecht (Stretch)​
- Guardrailing (Stretch)​


## Development Project Overview

This is a Python-based project for the "Tomorrow's Legal Assistance" hackathon. It's designed to provide legal assistance by leveraging a vector search over a collection of legal documents. The project is composed of two main parts:

1.  **FastAPI Backend (`backend/`)**: A web server that exposes an API for legal queries. It's built with FastAPI and serves as the main entry point for the application.
2.  **Legal Vectorizer (`legal_vectors/`)**: A separate component responsible for processing PDF legal documents. It extracts text, generates embeddings using `sentence-transformers`, and stores them in a ChromaDB vector database for efficient similarity search.

The project uses `uv` for package and environment management, with separate dependencies for the backend and the vectorizer.

## Building and Running

The project is divided into two main components, each with its own setup and execution process.

### Environment Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python package management.

1.  **Install `uv`**: Follow the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).
2.  **Create and activate the virtual environment**:
    ```bash
    # Create virtual environment and install dependencies for the backend
    uv sync

    # Activate the virtual environment
    source .venv/bin/activate  # On Linux/macOS
    # or
    .venv\Scripts\activate     # On Windows
    ```

### Running the FastAPI Backend

The backend server provides the main API for the application.

1.  **Start the server**:
    ```bash
    ./start_backend.sh
    ```
    This script navigates to the `backend` directory and starts the `uvicorn` server.

2.  **Access the API**:
    *   **API**: `http://localhost:8000`
    *   **Interactive Docs (Swagger)**: `http://localhost:8000/docs`

### Managing the Vector Store (`legal_vectors/`)

The `legal_vectors` component handles the creation and querying of the legal document vector store. The dependencies for this component are managed separately.

1.  **Install Dependencies**: Navigate to the `legal_vectors` directory and run `uv sync`.
    ```bash
    cd legal_vectors
    uv sync
    cd ..
    ```

2.  **Generate the Vector Store**: The `generate_vector_store.py` script processes PDFs from the `legal_vectors/data/` directory and populates the ChromaDB database in `legal_vectors/chroma_db/`.
    ```bash
    uv run python legal_vectors/legal_vectorizer/generate_vector_store.py
    ```

3.  **Query the Vector Store**: You can perform similarity searches on the indexed documents using the `query.py` script.
    ```bash
    uv run python legal_vectors/legal_vectorizer/query.py "Your legal question here"
    ```

## Development Conventions

*   **Modular Structure**: The project is split into a `backend` application and a `legal_vectors` data processing pipeline, each with its own `pyproject.toml`.
*   **Package Management**: `uv` is the standard for managing dependencies. Remember to `uv sync` in the respective directories (`/` or `legal_vectors/`) when dependencies change.
*   **API**: The FastAPI application in `backend/` contains the core API logic. New endpoints should be added in `backend/api/routes.py`.
*   **Vectorization**: The logic for creating and querying the vector store is located in the `legal_vectors/legal_vectorizer/` directory.
*   **Configuration**: The backend can be configured using environment variables defined in a `.env` file (copied from `.env.example`).
