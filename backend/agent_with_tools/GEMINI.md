# Gemini Context: Swiss Legal Case Analysis Agent

## Project Overview

This directory contains a sophisticated AI agent for analyzing Swiss legal cases. Built with Python and the `langgraph` library, the agent processes a user's description of a legal situation and returns a structured analysis including the case category, estimated likelihood of winning, and projected time and cost.

The agent's workflow is structured as a state graph:

1.  **Ingest**: Receives the case details.
2.  **Categorize**: Classifies the case into a legal domain (e.g., `Arbeitsrecht`, `Immobilienrecht`, `Strafverkehrsrecht`, or `Andere`). It uses a dedicated tool and can ask the user for clarification if confidence is low.
3.  **Conditional Analysis**:
    *   If the category is `Andere`, the analysis is skipped.
    *   Otherwise, it proceeds to the analysis nodes.
4.  **Win Likelihood & Time/Cost**: These nodes execute to analyze the case. The `win_likelihood_node` uses a ReAct-style loop with tools to query a RAG pipeline over Swiss legal documents (`rag_swiss_law`) and a database of historical cases (`historic_cases`).
5.  **Aggregate**: The final node consolidates all generated information into a single, validated JSON object.

## Key Technologies

*   **Orchestration**: `langgraph`
*   **LLM**: `Apertus LLM` (a Swiss AI model)
*   **Data Validation**: `pydantic`
*   **RAG Backend**: The `rag_swiss_law` tool integrates with a ChromaDB vector store and Gemini embeddings, implemented in a separate part of the project.

## Building and Running

### Environment Setup

1.  **Install Dependencies**: The core dependencies are `langgraph`, `langchain`, and `pydantic`. Install them as specified in the main project `pyproject.toml`.
    ```bash
    # From the root of the Tomorrows-Legal-Assistance project
    uv sync
    ```

2.  **Set API Key**: The agent requires an API key for the Apertus LLM.
    ```bash
    export APERTUS_API_KEY="your-apertus-api-key"
    ```
    You can also place this in a `.env` file in the `backend/` directory.

### Running the Agent

The agent can be executed directly from Python. The `demo.py` file provides a comprehensive example.

```python
# Example from demo.py
from backend.agent_with_tools import create_legal_agent, run_case_analysis
from backend.agent_with_tools.schemas import CaseInput

# The demo file patches the tools with mock implementations
# for a self-contained execution example.

# To run the full agent with real tools:
agent = create_legal_agent(api_key="your-apertus-key")

case_input = CaseInput(
    text="I was terminated from my job without proper notice...",
    metadata={
        "language": "en",
        "court_level": "district",
        "preferred_units": "months"
    }
)

result = agent.invoke({"case_input": case_input})
print(result["result"])
```

### Testing

The `README.md` specifies how to run tests:

```bash
pytest backend/agent/test_agent.py -v
```

## Development Conventions

*   **Modular Structure**: The agent is organized into distinct components:
    *   `graph.py`: Defines the main LangGraph workflow.
    *   `nodes/`: Each file corresponds to a logical step (node) in the graph.
    *   `tools/`: Each file implements a specific capability the agent can use (e.g., RAG, cost estimation).
    *   `schemas.py`: Centralizes all Pydantic data models for state and inputs/outputs.
    *   `policies.py`: Contains all prompts, system messages, and business rule constants (e.g., confidence thresholds, tool call limits).
*   **Type Safety**: The project heavily relies on `pydantic` and type hints for robust data validation and clear interfaces between components.
*   **Tool Implementation**: Tools are designed to be plug-and-play. The `demo.py` file shows how they can be mocked for testing. Real implementations are expected to connect to external services or databases.
*   **Prompts and Logic**: All prompts and business logic constants are centralized in `policies.py` for easy configuration and tuning.
*   **Diagrams**: The project includes utilities in `graph.py` to generate and view a Mermaid diagram of the agent's workflow, which is useful for visualization and documentation.
