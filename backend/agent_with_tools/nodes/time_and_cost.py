"""Time and cost estimation node."""

from langchain_core.messages import HumanMessage, SystemMessage
from backend.agent_with_tools.schemas import AgentState, TimeEstimate, CostBreakdown
from backend.agent_with_tools.tools.rag_swiss_law import rag_swiss_law
from backend.agent_with_tools.tools.historic_cases import historic_cases
from backend.agent_with_tools.tools.estimate_time import estimate_time
from backend.agent_with_tools.tools.estimate_cost import estimate_cost
from backend.agent_with_tools.policies import (
    TIME_COST_PROMPT, 
    DEFAULT_COMPLEXITY,
    DEFAULT_COURT_LEVEL,
    DEFAULT_HOURLY_RATE_LAWYER,
    DEFAULT_VAT_RATE
)


def time_and_cost_node(state: AgentState, llm) -> AgentState:
    """
    Estimate time and cost using ReAct with RAG and business logic tools.
    
    Args:
        state: Current agent state
        llm: Apertus LLM instance
        
    Returns:
        Updated state with time and cost estimates
    """
    category = state.category.category if state.category else "Andere"
    case_text = state.case_input.text
    
    # Build case facts from available information
    enhanced_case_facts = dict(state.case_facts) if state.case_facts else {}
    enhanced_case_facts.update({
        "category": category,
        "complexity": DEFAULT_COMPLEXITY,
        "court_level": enhanced_case_facts.get("court_level", DEFAULT_COURT_LEVEL),
    })
    
    # Try to enhance case facts with RAG and historic data
    context_parts = [f"Case: {case_text}"]
    
    try:
        # Get procedural information from Swiss law
        procedural_query = f"{category} court procedure timeline Switzerland"
        law_docs = rag_swiss_law(procedural_query, top_k=2)
        state.tool_call_count += 1
        
        if law_docs:
            law_info = " ".join([doc.snippet for doc in law_docs])
            context_parts.append(f"Procedural Law: {law_info[:200]}...")
            
    except NotImplementedError:
        context_parts.append("Procedural law: Not available")
    
    try:
        # Get timing information from historic cases  
        timing_query = f"{category} case duration time Switzerland"
        similar_cases = historic_cases(timing_query, top_k=2)
        state.tool_call_count += 1
        
        if similar_cases:
            cases_info = " ".join([case.summary for case in similar_cases])
            context_parts.append(f"Similar Cases: {cases_info[:200]}...")
            
    except NotImplementedError:
        context_parts.append("Historic timing data: Not available")
    
    # Use LLM to analyze complexity and enhance case facts
    analysis_context = "\n".join(context_parts)
    messages = [
        SystemMessage(content=TIME_COST_PROMPT),
        HumanMessage(content=f"""
        Analyze this case to determine complexity and key factors:
        
        {analysis_context}
        
        Based on the case description and legal context, assess:
        1. Complexity level (low/medium/high)
        2. Likely court level if not specified
        3. Whether appeals are expected
        4. Any procedural complications
        
        Respond with a brief analysis mentioning these factors.
        """)
    ]
    
    response = llm.invoke(messages)
    analysis = response.content.strip()
    
    # Extract complexity from LLM response
    if "high" in analysis.lower():
        enhanced_case_facts["complexity"] = "high"
    elif "low" in analysis.lower():
        enhanced_case_facts["complexity"] = "low"
    else:
        enhanced_case_facts["complexity"] = "medium"
    
    # Check for appeal mentions
    if "appeal" in analysis.lower():
        enhanced_case_facts["appeal_expected"] = True
    
    # Get time estimate
    try:
        time_estimate = estimate_time(enhanced_case_facts)
        state.tool_call_count += 1
        state.time_estimate = time_estimate
    except NotImplementedError:
        # Fallback time estimation based on category and complexity
        complexity = enhanced_case_facts.get("complexity", "medium")
        
        # Simple heuristic for time estimation
        if category == "Arbeitsrecht":
            base_months = {"low": 3, "medium": 6, "high": 12}[complexity]
        elif category == "Immobilienrecht": 
            base_months = {"low": 4, "medium": 8, "high": 15}[complexity]
        elif category == "Strafverkehrsrecht":
            base_months = {"low": 2, "medium": 4, "high": 8}[complexity]
        else:  # Andere
            base_months = {"low": 3, "medium": 6, "high": 12}[complexity]
        
        state.time_estimate = TimeEstimate(value=base_months, unit="months")
    
    # Prepare cost inputs
    cost_inputs = {
        "time_estimate": state.time_estimate.dict(),
        "hourly_rates": {
            "lawyer": DEFAULT_HOURLY_RATE_LAWYER,
        },
        "vat_rate": DEFAULT_VAT_RATE
    }
    
    # Add metadata if available
    if enhanced_case_facts.get("judges_count"):
        cost_inputs["judges_count"] = enhanced_case_facts["judges_count"]
    
    # Get cost estimate
    try:
        cost_estimate = estimate_cost(cost_inputs)
        state.tool_call_count += 1
        state.cost_estimate = cost_estimate
    except NotImplementedError:
        # Fallback cost estimation
        time_val = state.time_estimate.value
        time_unit = state.time_estimate.unit
        
        # Convert to hours
        hours_map = {"days": 24, "weeks": 168, "months": 720}  # rough estimates
        total_hours = time_val * hours_map.get(time_unit, 720) / 30  # work hours
        
        # Estimate lawyer hours (fraction of total time)
        lawyer_hours = total_hours * 0.3  # 30% of time with lawyer
        lawyer_cost = lawyer_hours * DEFAULT_HOURLY_RATE_LAWYER
        
        # Add court fees and VAT
        court_fees = 2000  # CHF estimate
        subtotal = lawyer_cost + court_fees
        vat = subtotal * DEFAULT_VAT_RATE
        total = subtotal + vat
        
        state.cost_estimate = CostBreakdown(
            total_chf=total,
            breakdown={
                "lawyer_fees": lawyer_cost,
                "court_fees": court_fees,
                "vat": vat
            }
        )
    
    return state