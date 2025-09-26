"""Win likelihood analysis node."""

from langchain_core.messages import HumanMessage, SystemMessage
from backend.agent_with_tools.schemas import AgentState
from backend.agent_with_tools.tools.rag_swiss_law import rag_swiss_law
from backend.agent_with_tools.tools.historic_cases import historic_cases
from backend.agent_with_tools.tools.estimate_likelihood import estimate_business_likelihood, get_likelihood_explanation_context
from backend.agent_with_tools.policies import WIN_LIKELIHOOD_PROMPT, MAX_RAG_CALLS, MAX_HISTORIC_CALLS, MAX_BUSINESS_LIKELIHOOD_CALLS


def win_likelihood_node(state: AgentState, llm) -> AgentState:
    """
    Analyze likelihood of winning using multi-source analysis with RAG and historic cases.
    
    Args:
        state: Current agent state
        llm: Apertus LLM instance
        
    Returns:
        Updated state with likelihood_win score
    """
    category = state.category.category if state.category else "Unknown"
    case_text = state.case_input.text
    
    # Initialize explanation parts if not already done
    if state.explanation_parts is None:
        state.explanation_parts = []
    
    # Prepare context for analysis
    context_parts = [f"Case Category: {category}", f"Case Description: {case_text}"]
    
    # Get business logic baseline estimate first
    business_likelihood_calls = 0
    baseline_likelihood = None
    
    if business_likelihood_calls < MAX_BUSINESS_LIKELIHOOD_CALLS:
        business_result = estimate_business_likelihood(case_text, category)
        state.tool_call_count += 1
        business_likelihood_calls += 1
        
        baseline_likelihood = business_result["likelihood"]
        business_context = get_likelihood_explanation_context(business_result)
        context_parts.append(f"Business Logic Analysis:\n{business_context}")
        
        # Add explanation
        state.explanation_parts.append(business_result["explanation"])
    
    # Try to gather relevant Swiss law
    rag_calls = 0
    try:
        if rag_calls < MAX_RAG_CALLS:
            # Query relevant statutes
            law_query = f"{category} legal requirements case analysis"
            law_docs = rag_swiss_law(law_query, top_k=3)
            state.tool_call_count += 1
            rag_calls += 1
            
            if law_docs:
                law_context = "\n".join([
                    f"- {doc.title}: {doc.snippet}" for doc in law_docs[:2]
                ])
                context_parts.append(f"Relevant Swiss Law:\n{law_context}")
                
    except NotImplementedError:
        context_parts.append("Swiss law documents: Not available (stub implementation)")
    
    # Try to gather historic cases
    historic_calls = 0
    try:
        if historic_calls < MAX_HISTORIC_CALLS:
            # Query similar cases
            cases_query = f"{category} similar case outcomes"
            similar_cases = historic_cases(cases_query, top_k=3)
            state.tool_call_count += 1
            historic_calls += 1
            
            if similar_cases:
                cases_context = "\n".join([
                    f"- {case.year} {case.court}: {case.summary} → {case.outcome}" 
                    for case in similar_cases[:2]
                ])
                context_parts.append(f"Similar Historic Cases:\n{cases_context}")
                
    except NotImplementedError:
        context_parts.append("Historic cases: Not available (stub implementation)")
    
    # Use LLM for synthesis and analysis
    full_context = "\n\n".join(context_parts)
    
    # Prepare enhanced prompt with baseline guidance
    baseline_guidance = ""
    if baseline_likelihood is not None:
        baseline_guidance = f"""
        
        BASELINE GUIDANCE: Business logic suggests {baseline_likelihood}% likelihood based on case type and category.
        Use this as a starting point but adjust based on case-specific evidence below.
        """
    
    messages = [
        SystemMessage(content=WIN_LIKELIHOOD_PROMPT),
        HumanMessage(content=f"""
        Analyze the likelihood of winning this case based on the available evidence:
        
        {full_context}{baseline_guidance}
        
        Provide a numerical score from 1-100 representing the likelihood of winning.
        Consider:
        1. Business logic baseline (if available) as starting point
        2. Strength of legal position based on statutes
        3. Historical outcomes in similar cases (when available, not stub data)
        4. Quality of evidence and case facts
        5. Potential procedural challenges
        
        If historic cases are not available (stub implementation), do not factor them into your analysis.
        Focus on legal statutes, business logic baseline, and case facts.
        
        Respond with just the numerical score (1-100) and brief reasoning.
        """)
    ]
    
    response = llm.invoke(messages)
    content = response.content.strip()
    
    # Extract numerical score
    likelihood = 50  # default moderate score
    try:
        # Look for numbers in the response
        import re
        numbers = re.findall(r'\b(\d{1,3})\b', content)
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= 100:
                likelihood = num
                break
    except (ValueError, AttributeError):
        pass  # Keep default
    
    state.likelihood_win = likelihood
    
    # Add LLM reasoning to explanation
    state.explanation_parts.append(f"Final likelihood analysis: {content}")
    
    return state