"""Aggregation node for validating and normalizing final results."""

from backend.agent_with_tools.schemas import AgentState, AgentOutput, CostBreakdown


def aggregate_node(state: AgentState) -> AgentState:
    """
    Validate and normalize all results into final JSON format.
    
    Args:
        state: Current agent state with all analysis results
        
    Returns:
        Updated state with validated final result
    """
    # Get category from state
    category = state.category.category if state.category else "Unknown"
    
    # Handle 'Andere' category - no estimations possible
    if category == "Andere":
        explanation = ""
        if state.explanation_parts:
            explanation = " | ".join(state.explanation_parts)
        else:
            explanation = "Category 'Andere' - analysis tools not applicable for this case type"
        
        state.result = AgentOutput(
            category=category,
            likelihood_win=None,
            estimated_time=None,
            estimated_cost=None,
            explanation=explanation,
            source_documents=state.source_documents or []
        )
        return state
    
    # Validate that we have all required components for other categories
    if not state.likelihood_win:
        raise ValueError("Missing likelihood_win score")
    
    if not state.time_estimate:
        raise ValueError("Missing time estimate")
    
    if not state.cost_estimate:
        raise ValueError("Missing cost estimate")
    
    # Normalize time estimate to readable string
    time_val = state.time_estimate.value
    time_unit = state.time_estimate.unit
    
    if time_unit == "days":
        if time_val == 1:
            time_str = "1 day"
        else:
            time_str = f"{time_val} days"
    elif time_unit == "weeks":
        if time_val == 1:
            time_str = "1 week" 
        else:
            time_str = f"{time_val} weeks"
    elif time_unit == "months":
        if time_val == 1:
            time_str = "1 month"
        else:
            time_str = f"{time_val} months"
    else:
        time_str = f"{time_val} {time_unit}"
    
    # Normalize cost estimate to string format
    if isinstance(state.cost_estimate, (int, float)):
        cost_output = f"{int(state.cost_estimate)} CHF"
    elif isinstance(state.cost_estimate, CostBreakdown):
        cost_output = f"{int(state.cost_estimate.total_chf)} CHF"
    else:
        # Handle dict format from fallback estimation
        if hasattr(state.cost_estimate, 'total_chf'):
            cost_output = f"{int(state.cost_estimate.total_chf)} CHF"
        else:
            cost_output = f"{int(float(state.cost_estimate))} CHF"
    
    # Ensure likelihood_win is within valid range and format as percentage string
    likelihood_num = max(1, min(100, state.likelihood_win))
    likelihood = f"{likelihood_num}%"
    
    # Compile explanation from all analysis parts
    explanation = ""
    if state.explanation_parts:
        explanation = " | ".join(state.explanation_parts)
    
    # Create final output with all fields
    state.result = AgentOutput(
        category=category,
        likelihood_win=likelihood,
        estimated_time=time_str,
        estimated_cost=cost_output,
        explanation=explanation,
        source_documents=state.source_documents or []
    )
    
    return state