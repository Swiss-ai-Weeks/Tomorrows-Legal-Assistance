from typing import Any
from langgraph.graph import START, StateGraph

from backend.agent.state import LegalAgentState
from backend.utils import markdown_to_prompt_template
from apertus.apertus import LangchainApertus
from core.config import settings


classify_legal_field_prompt = markdown_to_prompt_template(
    "agent/prompts/classify_legal_field_prompt.md"
)


# Create the runnable with the prompt and model
classify_legal_field_runnable = classify_legal_field_prompt | LangchainApertus(
    api_key=settings.APERTUS_API_KEY
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

# Add edges
workflow.add_edge(START, "classify_legal_field")


# Compile the workflow
legal_agent = workflow.compile().with_config({"tags": ["legal-agent-v0"]})


if __name__ == "__main__":
    response = legal_agent.invoke(
        {
            "question": "I was caught speeding 20 km/h over the limit outside a built-up area. I received a fine and wonder if it makes sense to contest it."
        }
    )
    print(response)
