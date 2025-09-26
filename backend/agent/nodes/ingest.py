"""Ingest node for normalizing input and creating working memory."""

from backend.agent.schemas import AgentState


def ingest_node(state: AgentState) -> AgentState:
    """
    Normalize input and create working memory.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with normalized input and initialized working memory
    """
    # Initialize case_facts with basic information
    case_facts = {
        "text": state.case_input.text,
        "jurisdiction": "CH"
    }
    
    # Add metadata if available
    if state.case_input.metadata:
        if state.case_input.metadata.court_level:
            case_facts["court_level"] = state.case_input.metadata.court_level
        if state.case_input.metadata.judges_count:
            case_facts["judges_count"] = state.case_input.metadata.judges_count
        if state.case_input.metadata.language:
            case_facts["language"] = state.case_input.metadata.language
        if state.case_input.metadata.preferred_units:
            case_facts["preferred_units"] = state.case_input.metadata.preferred_units
    
    # Update state
    state.case_facts = case_facts
    state.tool_call_count = 0
    
    return state