"""Categorization node for classifying legal cases."""

from langchain_core.messages import HumanMessage, SystemMessage
from backend.agent.schemas import AgentState
from backend.agent.tools.categorize_case import categorize_case
from backend.agent.tools.ask_user import ask_user
from backend.agent.policies import CATEGORIZE_PROMPT, MIN_CATEGORY_CONFIDENCE


def categorize_node(state: AgentState, llm) -> AgentState:
    """
    Categorize the case into one of four legal categories.
    
    Args:
        state: Current agent state
        llm: Apertus LLM instance
        
    Returns:
        Updated state with category classification
    """
    try:
        # First attempt at categorization
        category_result = categorize_case(state.case_input.text)
        state.tool_call_count += 1
        
        # Check if confidence is sufficient
        if category_result.confidence >= MIN_CATEGORY_CONFIDENCE:
            state.category = category_result
        else:
            # Use LLM to generate a precise question for the user
            messages = [
                SystemMessage(content=CATEGORIZE_PROMPT),
                HumanMessage(content=f"""
                Case text: {state.case_input.text}
                
                The initial categorization has low confidence ({category_result.confidence:.2f}).
                Generate a single, clear question to ask the user to clarify the case type.
                Focus on distinguishing between: Arbeitsrecht, Immobilienrecht, Strafverkehrsrecht, Andere.
                """)
            ]
            
            response = llm.invoke(messages)
            clarification_question = response.content.strip()
            
            # Ask user for clarification
            missing_fields = ["case_type_clarification"]
            additional_info = ask_user(clarification_question, missing_fields)
            state.tool_call_count += 1
            
            # Re-categorize with additional information
            augmented_text = f"{state.case_input.text}\n\nAdditional clarification: {additional_info}"
            category_result = categorize_case(augmented_text)
            state.tool_call_count += 1
            state.category = category_result
            
            # Update case facts with additional info
            if state.case_facts:
                state.case_facts["clarification"] = additional_info
            
    except NotImplementedError:
        # Fallback: Use LLM for categorization when tool is not implemented
        messages = [
            SystemMessage(content=CATEGORIZE_PROMPT),
            HumanMessage(content=f"Categorize this case: {state.case_input.text}")
        ]
        
        response = llm.invoke(messages)
        
        # Parse LLM response (simplified - assumes LLM returns category name)
        content = response.content.strip()
        categories = ["Arbeitsrecht", "Immobilienrecht", "Strafverkehrsrecht", "Andere"]
        
        # Find matching category
        category = "Andere"  # default
        for cat in categories:
            if cat.lower() in content.lower():
                category = cat
                break
        
        from backend.agent.schemas import CategoryResult
        state.category = CategoryResult(category=category, confidence=0.8)
    
    # Update case facts with category
    if state.case_facts:
        state.case_facts["category"] = state.category.category
    
    return state