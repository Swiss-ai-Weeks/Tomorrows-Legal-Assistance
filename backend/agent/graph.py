from typing import Any
from langgraph.graph import StateGraph

from backend.agent.state import LegalAgentState
from backend.utils import markdown_to_prompt_template
from apertus.apertus import LangchainApertus


classify_legal_field_prompt = markdown_to_prompt_template(
    "agent/prompts/classify_legal_field_prompt.md"
)


# Create the runnable with the prompt and model
classify_legal_field_runnable = classify_legal_field_prompt | LangchainApertus(
    api_key="todo"
)


def classify_legal_field(state: LegalAgentState) -> dict[str, Any]:
    result = classify_legal_field_runnable.invoke(
        {"question": state.question, "additional_context": ""}
    )
    return {"legal_field": result}


# Create the workflow graph
workflow = StateGraph(LegalAgentState)

# Add nodes
workflow.add_node("classify_legal_field", classify_legal_field)
