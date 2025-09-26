# Gemini Context: Tomorrow's Legal Assistance Frontend

This directory contains the Streamlit frontend for the "Tomorrow's Legal Assistance" application.

## Project Overview

The frontend is a Streamlit application that provides a chat interface for users to describe their legal situation. It communicates with a backend service (presumably using the `apertus` library) to get a legal analysis, including the likelihood of winning, cost range, and next steps.

**Key Technologies:**

*   **Framework:** Streamlit
*   **Language:** Python
*   **Dependencies:**
    *   `streamlit`
    *   `langchain`
    *   `python-dotenv`
    *   `uvicorn`

## Running the Application

1.  **Install dependencies:**
    As described in README.md

2.  **Set up environment variables:**
    Create a `.env` file by copying `.env.example` and add your `APERTUS_API_KEY`.

3.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

## Development Conventions

*   The main application logic is in `app.py`.
*   Dependencies are managed in `pyproject.toml`.
*   Environment variables are loaded from a `.env` file.
*   The application uses the `apertus` library to communicate with the backend.
