from typing import Any
from langgraph.graph import START, StateGraph

from backend.agent.schema import LegalFieldClassification, CaseCategoryClassification
from backend.agent.state import LegalAgentState
from backend.utils import markdown_to_prompt_template
from apertus.apertus import LangchainApertus
from core.config import settings


classify_legal_field_prompt = markdown_to_prompt_template(
    "agent/prompts/classify_legal_field_prompt.md"
)
classify_case_category_prompt = markdown_to_prompt_template(
    "agent/prompts/classify_case_category_prompt.md"
)


# Create the runnable with the prompt and model
classify_legal_field_runnable = classify_legal_field_prompt | LangchainApertus(
    api_key=settings.APERTUS_API_KEY
).with_structured_output(LegalFieldClassification)

classify_case_category_runnable = classify_case_category_prompt | LangchainApertus(
    api_key=settings.APERTUS_API_KEY
).with_structured_output(CaseCategoryClassification)


def classify_legal_field(state: LegalAgentState) -> dict[str, Any]:
    result: LegalFieldClassification = classify_legal_field_runnable.invoke(
        {"question": state.question, "additional_context": ""}
    )
    return {"legal_field": result.legal_field}


def classify_case_category(state: LegalAgentState) -> dict[str, Any]:
    result: CaseCategoryClassification = classify_case_category_runnable.invoke(
        {"question": state.question, "additional_context": state.legal_field}
    )
    return {"case_category": result.case_category}


# Create the workflow graph
workflow = StateGraph(LegalAgentState)

# Add nodes
workflow.add_node("classify_legal_field", classify_legal_field)
workflow.add_node("classify_case_category", classify_case_category)

# Add edges
workflow.add_edge(START, "classify_legal_field")
workflow.add_edge("classify_legal_field", "classify_case_category")


# Compile the workflow
legal_agent = workflow.compile().with_config({"tags": ["legal-agent-v0"]})


if __name__ == "__main__":
    response = legal_agent.invoke(
        {
            "question": "I was caught speeding 20 km/h over the limit outside a built-up area. I received a fine and wonder if it makes sense to contest it."
        }
    )
    print(response)
