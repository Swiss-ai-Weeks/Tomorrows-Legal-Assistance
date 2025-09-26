"""Win likelihood analysis node."""

from langchain_core.messages import HumanMessage, SystemMessage
from backend.agent_with_tools.schemas import AgentState
from backend.agent_with_tools.tools.rag_swiss_law import rag_swiss_law
from backend.agent_with_tools.tools.historic_cases import historic_cases
from backend.agent_with_tools.policies import WIN_LIKELIHOOD_PROMPT, MAX_RAG_CALLS, MAX_HISTORIC_CALLS


def win_likelihood_node(state: AgentState, llm) -> AgentState:
    """
    Analyze likelihood of winning using ReAct with RAG and historic cases.
    
    Args:
        state: Current agent state
        llm: Apertus LLM instance
        
    Returns:
        Updated state with likelihood_win score
    """
    category = state.category.category if state.category else "Unknown"
    case_text = state.case_input.text
    
    # Prepare context for analysis
    context_parts = [f"Case Category: {category}", f"Case Description: {case_text}"]
    
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
    
    # Use LLM for ReAct analysis
    full_context = "\n\n".join(context_parts)
    
    messages = [
        SystemMessage(content=WIN_LIKELIHOOD_PROMPT),
        HumanMessage(content=f"""
        Analyze the likelihood of winning this case based on the available evidence:
        
        {full_context}
        
        Provide a numerical score from 1-100 representing the likelihood of winning.
        Consider:
        1. Strength of legal position based on statutes
        2. Historical outcomes in similar cases
        3. Quality of evidence and case facts
        4. Potential procedural challenges
        
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
    
    return state