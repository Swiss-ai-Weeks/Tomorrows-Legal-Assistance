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
    
    # Try to gather Swiss law context with focused queries
    rag_calls = 0
    try:
        if rag_calls < MAX_RAG_CALLS:
            # Create specific query based on case category and key terms from case
            case_lower = case_text.lower()
            
            if "Arbeitsrecht" in category:
                if "terminated" in case_lower or "dismissal" in case_lower or "notice" in case_lower:
                    law_query = "Swiss employment termination notice period OR 336 Code of Obligations dismissal protection"
                elif "wage" in case_lower or "salary" in case_lower:
                    law_query = "Swiss employment law wage payment obligations OR 322 Code of Obligations"
                else:
                    law_query = "Swiss employment law employee rights protection OR Code of Obligations employment"
            elif "Immobilienrecht" in category:
                if "defect" in case_lower or "damage" in case_lower:
                    law_query = "Swiss property law hidden defects warranty OR 197 Code of Obligations"
                else:
                    law_query = "Swiss real estate law property disputes contracts"
            elif "Strafverkehrsrecht" in category:
                if "license" in case_lower or "driving" in case_lower:
                    law_query = "Swiss traffic law license suspension OR Road Traffic Act penalties"
                else:
                    law_query = "Swiss traffic criminal law violations fines"
            else:
                law_query = f"Swiss law {category} legal regulations"
            
            law_docs = rag_swiss_law(law_query, top_k=2)  # Reduced for performance
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
            similar_cases = historic_cases(cases_query, top_k=2)  # Reduced for performance
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
        Analyze this Swiss legal case and provide a win likelihood score:
        
        {full_context}{baseline_guidance}
        
        Format your response as:
        SCORE: [number from 1-100]
        REASONING: [1-2 clear sentences explaining why this score, focusing on key legal strengths or weaknesses]
        
        Guidelines:
        - Use business logic baseline as starting point if provided
        - Adjust based on Swiss legal requirements and case facts
        - Be concise and user-friendly
        - Ignore any "stub" or "not available" data
        """)
    ]
    
    response = llm.invoke(messages)
    content = response.content.strip()
    
    # Extract numerical score and reasoning
    likelihood = 50  # default moderate score
    reasoning = content
    
    try:
        import re
        # Look for SCORE: pattern first
        score_match = re.search(r'SCORE:\s*(\d{1,3})', content, re.IGNORECASE)
        if score_match:
            likelihood = int(score_match.group(1))
            likelihood = max(1, min(100, likelihood))  # Clamp to 1-100
        else:
            # Fallback: look for any number in valid range
            numbers = re.findall(r'\b(\d{1,3})\b', content)
            for num_str in numbers:
                num = int(num_str)
                if 1 <= num <= 100:
                    likelihood = num
                    break
        
        # Extract reasoning if available
        reasoning_match = re.search(r'REASONING:\s*(.+)', content, re.IGNORECASE | re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        
    except (ValueError, AttributeError):
        pass  # Keep defaults
    
    state.likelihood_win = likelihood
    
    # Add clean reasoning to explanation
    state.explanation_parts.append(f"Win likelihood analysis: {reasoning}")
    
    return state