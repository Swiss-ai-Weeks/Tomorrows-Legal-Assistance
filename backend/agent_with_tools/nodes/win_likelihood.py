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
    print("In Win likelihood")
    category = state.category.category if state.category else "Unknown"
    case_text = state.case_input.text
    
    # Initialize explanation parts and source documents if not already done
    if state.explanation_parts is None:
        state.explanation_parts = []
    if state.source_documents is None:
        state.source_documents = []
    
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
                if "terminated" in case_lower or "dismissal" in case_lower or "kündigung" in case_lower or "notice" in case_lower:
                    law_query = "employment termination dismissal notice period article 336 337 338 339 fristlose kündigung Arbeitsvertrag"
                elif "wage" in case_lower or "salary" in case_lower or "lohn" in case_lower:
                    law_query = "employment wage salary payment article 322 323 324 Lohn Arbeitslohn"
                elif "mobbing" in case_lower or "harassment" in case_lower or "discrimination" in case_lower:
                    law_query = "employment protection harassment discrimination article 328 328a Fürsorgepflicht"
                else:
                    law_query = "employment contract work Arbeitsvertrag article 319 320 321 employee rights obligations"
            elif "Immobilienrecht" in category:
                if "defect" in case_lower or "damage" in case_lower or "mängel" in case_lower:
                    law_query = "property defects warranty article 197 208 Civil Code real estate purchase"
                elif "rent" in case_lower or "miete" in case_lower or "lease" in case_lower:
                    law_query = "rental law lease agreement tenant landlord article 253 Civil Code"
                else:
                    law_query = "real estate property law Civil Code article 641 ownership purchase contract"
            elif "Strafverkehrsrecht" in category:
                if "license" in case_lower or "driving" in case_lower:
                    law_query = "Swiss traffic law license suspension OR Road Traffic Act penalties"
                else:
                    law_query = "Swiss traffic criminal law violations fines"
            else:
                law_query = f"Swiss law {category} legal regulations"
            
            law_docs = rag_swiss_law(law_query, top_k=3)  # Increased for better matching
            state.tool_call_count += 1
            rag_calls += 1
            
            # Check if relevant documents were found and provide fallback if needed
            if law_docs and "Arbeitsrecht" in category:
                # Check if retrieved documents are employment-related
                employment_related = any("SR-220" in doc.title for doc in law_docs)
                if not employment_related:
                    print("⚠️ RAG did not return employment law documents, using fallback knowledge")
                    # Create fallback employment law context from known Swiss law
                    from backend.agent_with_tools.schemas import Doc
                    fallback_docs = [
                        Doc(
                            id="sr220_fallback",
                            title="SR-220 Code of Obligations (Employment Law - Articles 319-362)",
                            snippet="""Swiss employment law is governed by Articles 319-362 of the Code of Obligations (SR-220). 
                            Key provisions include: Article 319 (employment contract formation), Articles 320-330 (employee duties and rights), 
                            Articles 331-333 (employer duties including wage payment and protection), Articles 334-339 (termination including notice periods), 
                            Article 336 (wrongful termination protection), Article 336a (protection against retaliation), 
                            Article 337 (immediate termination for cause). Notice periods: 1 month during probation, 
                            1-3 months based on service length thereafter. Immediate termination requires serious cause.""",
                            citation="Swiss Code of Obligations SR-220"
                        )
                    ]
                    law_docs = fallback_docs
                    # Store fallback documents for frontend display
                    if state.source_documents is None:
                        state.source_documents = []
                    state.source_documents.extend(fallback_docs)
                    
            elif law_docs and "Immobilienrecht" in category:
                # Check if retrieved documents are real estate-related
                real_estate_related = any(any(pattern in doc.title for pattern in ["SR-210", "SR-220"]) for doc in law_docs)
                if not real_estate_related:
                    print("⚠️ RAG did not return real estate law documents, using fallback knowledge")
                    # Create fallback real estate law context from known Swiss law
                    from backend.agent_with_tools.schemas import Doc
                    fallback_docs = [
                        Doc(
                            id="sr210_fallback",
                            title="Swiss Civil Code & Code of Obligations (Real Estate Law)",
                            snippet="""Swiss real estate law is governed by the Civil Code (SR-210) and Code of Obligations (SR-220). 
                            Key provisions include: Articles 641-729 Civil Code (property ownership), Articles 197-210 Code of Obligations (warranty for defects), 
                            Articles 253-304 Code of Obligations (rental law). Hidden defects: Seller liable for defects not disclosed (Art. 197-210). 
                            Notice periods for defects: 2 years for real estate. Rental law: Tenant protection, deposit rules, termination notice periods. 
                            Property transfer requires notarization and land register entry.""",
                            citation="Swiss Civil Code SR-210 & Code of Obligations SR-220"
                        )
                    ]
                    law_docs = fallback_docs
                    # Store fallback documents for frontend display
                    if state.source_documents is None:
                        state.source_documents = []
                    state.source_documents.extend(fallback_docs)
                    
            elif law_docs and "Strafverkehrsrecht" in category:
                # Check if retrieved documents are traffic law-related  
                traffic_related = any(any(pattern in doc.title for pattern in ["SR-741", "SR-742"]) for doc in law_docs)
                if not traffic_related:
                    print("⚠️ RAG did not return traffic law documents, using fallback knowledge")
                    # Create fallback traffic law context from known Swiss law
                    from backend.agent_with_tools.schemas import Doc
                    fallback_docs = [
                        Doc(
                            id="sr741_fallback",
                            title="Swiss Road Traffic Act (SR-741) & Road Traffic Ordinance (SR-742)",
                            snippet="""Swiss traffic law is governed by the Road Traffic Act (SR-741) and Road Traffic Ordinance (SR-742). 
                            Key provisions: Speed limits are strictly enforced. Appeals require proof of technical errors or improper signage. 
                            Administrative fines: 1st class (minor violations), 2nd class (moderate speeding), 3rd class (serious violations). 
                            License suspension: automatic for certain speeds over limit. Defense options: measurement errors, 
                            improper signage, emergency situations. Success rate for appeals is generally low unless technical violations proven.""",
                            citation="Swiss Road Traffic Act SR-741 & Road Traffic Ordinance SR-742"
                        )
                    ]
                    law_docs = fallback_docs
                    # Store fallback documents for frontend display
                    if state.source_documents is None:
                        state.source_documents = []
                    state.source_documents.extend(fallback_docs)
            
            if law_docs:
                law_context = "\n".join([
                    f"- {doc.title}: {doc.snippet}" for doc in law_docs[:2]
                ])
                context_parts.append(f"Relevant Swiss Law:\n{law_context}")
                
                # Store source documents for frontend display (only if not already added by fallback)
                if not any("fallback" in doc.id for doc in (state.source_documents or [])):
                    if state.source_documents is None:
                        state.source_documents = []
                    state.source_documents.extend(law_docs[:2])
                
    except NotImplementedError:
        context_parts.append("Swiss law documents: Not available (stub implementation)")
    
    # Try to gather historic cases
    historic_calls = 0
    print("START HISTORICAL")
    try:
        if historic_calls < MAX_HISTORIC_CALLS:
            # Create specific query based on case content and category for better matching
            case_keywords = case_text.lower()
            if "Arbeitsrecht" in category:
                if any(term in case_keywords for term in ["kündigung", "termination", "dismissed", "fired"]):
                    cases_query = f"employment termination dismissal wrongful firing {category}"
                elif any(term in case_keywords for term in ["wage", "salary", "lohn", "payment"]):
                    cases_query = f"employment wage salary payment dispute {category}"
                elif any(term in case_keywords for term in ["mobbing", "harassment", "discrimination"]):
                    cases_query = f"employment harassment mobbing workplace discrimination {category}"
                else:
                    cases_query = f"employment law workplace dispute {category}"
            else:
                cases_query = f"{category} similar case outcomes"
                
            similar_cases = historic_cases(cases_query, top_k=3)  # Get more cases for better context
            state.tool_call_count += 1
            historic_calls += 1

            print(similar_cases)
            
            if similar_cases:
                cases_context = "\n".join([
                    f"- **Case {case.year}** ({case.court}): {case.summary[:200]}... → **Outcome: {case.outcome.upper()}**"
                    for case in similar_cases[:2]
                ])
                context_parts.append(f"Historic Precedent Cases (CRITICAL for assessment):\n{cases_context}")
                
                # Add to explanation parts for transparency
                cases_summary = f"Found {len(similar_cases)} similar cases: " + ", ".join([
                    f"{case.year} ({case.outcome})" for case in similar_cases[:3]
                ])
                state.explanation_parts.append(f"Historic cases analysis: {cases_summary}")
                
    except NotImplementedError:
        context_parts.append("Historic cases: Not available (stub implementation)")
    
    # Use LLM for synthesis and analysis
    full_context = "\n\n".join(context_parts)
    
    # Prepare enhanced prompt with baseline guidance
    baseline_guidance = ""
    adjustment_range = ""
    if baseline_likelihood is not None:
        # Calculate allowed adjustment range (±20% max, but not below 1 or above 100)
        min_score = max(1, baseline_likelihood - 20)
        max_score = min(100, baseline_likelihood + 20)
        
        baseline_guidance = f"""
        
        CRITICAL BASELINE: Business logic analysis indicates {baseline_likelihood}% likelihood for this case type.
        This is based on extensive legal experience and case outcomes.
        """
        
        adjustment_range = f"""
        SCORING CONSTRAINTS:
        - Your score MUST be between {min_score}% and {max_score}% (±20% from baseline)
        - Only deviate from {baseline_likelihood}% if you have STRONG legal evidence
        - Small case improvements cannot overcome fundamental legal category limitations
        - Swiss courts are generally predictable - respect the baseline guidance
        """
    
    messages = [
        SystemMessage(content=WIN_LIKELIHOOD_PROMPT),
        HumanMessage(content=f"""
        Analyze this Swiss legal case and provide a win likelihood score:
        
        {full_context}{baseline_guidance}
        
        {adjustment_range}
        
        Format your response as:
        SCORE: [number from 1-100]
        REASONING: [Provide detailed analysis citing SPECIFIC sources - mention Swiss law articles, historic case outcomes, and business logic baseline. Explain how similar cases inform your assessment.]
        
        Guidelines:
        - RESPECT the baseline percentage - it's based on real case outcomes
        - EXPLICITLY reference historic precedent cases in your reasoning if provided
        - Mention specific Swiss law provisions that apply
        - Only adjust within the specified range unless extraordinary circumstances
        - Swiss legal system is predictable - don't overestimate chances
        - Focus on realistic legal assessment informed by precedents and law
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
        
        # Apply baseline constraint validation if business logic baseline exists
        if baseline_likelihood is not None:
            # Calculate allowed range (±20% but not below 1 or above 100)
            min_allowed = max(1, baseline_likelihood - 20)
            max_allowed = min(100, baseline_likelihood + 20)
            
            # If LLM score is outside allowed range, constrain it
            if likelihood < min_allowed or likelihood > max_allowed:
                original_likelihood = likelihood
                likelihood = max(min_allowed, min(max_allowed, likelihood))
                print(f"⚠️ LLM score {original_likelihood}% outside baseline range [{min_allowed}-{max_allowed}%], constrained to {likelihood}%")
                
                # Update reasoning to reflect constraint
                reasoning += f" Note: Score adjusted from {original_likelihood}% to respect business logic baseline of {baseline_likelihood}% (±20% range)."
        
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