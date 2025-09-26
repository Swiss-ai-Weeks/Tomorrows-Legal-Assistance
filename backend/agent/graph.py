"""LangGraph implementation for Swiss legal case analysis agent.

This module creates a ReAct-style agent that:
1. Ingests case descriptions and classifies them into legal categories
2. Analyzes likelihood of winning using RAG and historic cases  
3. Estimates time and cost in parallel
4. Produces validated JSON results

Example usage:
    >>> from backend.agent.graph import create_legal_agent
    >>> from backend.agent.schemas import CaseInput
    >>> 
    >>> agent = create_legal_agent()
    >>> case = CaseInput(text="My employer terminated me without cause...")
    >>> result = agent.invoke({"case_input": case})
    >>> print(result["result"])
    {
        "likelihood_win": 75,
        "estimated_time": "6 months", 
        "estimated_cost": 15000.0
    }
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from backend.agent.schemas import AgentState
from backend.agent.nodes.ingest import ingest_node
from backend.agent.nodes.categorize import categorize_node
from backend.agent.nodes.win_likelihood import win_likelihood_node
from backend.agent.nodes.time_and_cost import time_and_cost_node
from backend.agent.nodes.aggregate import aggregate_node
from backend.apertus.model import get_apertus_model
# Note: MAX_TOOL_CALLS can be imported from policies for guard logic if needed


def create_legal_agent(api_key: str = None) -> CompiledStateGraph:
    """
    Create and compile the legal analysis LangGraph agent.
    
    Args:
        api_key: API key for Apertus model. If None, reads from environment.
        
    Returns:
        Compiled LangGraph agent ready for execution
    """
    # Initialize the LLM
    llm = get_apertus_model(api_key=api_key)
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Define nodes
    def ingest_wrapper(state: AgentState) -> AgentState:
        return ingest_node(state)
    
    def categorize_wrapper(state: AgentState) -> AgentState:
        return categorize_node(state, llm)
    
    def win_likelihood_wrapper(state: AgentState) -> AgentState:
        return win_likelihood_node(state, llm)
    
    def time_cost_wrapper(state: AgentState) -> AgentState:
        return time_and_cost_node(state, llm)
    
    def aggregate_wrapper(state: AgentState) -> AgentState:
        return aggregate_node(state)
    
    # Add nodes to workflow
    workflow.add_node("ingest", ingest_wrapper)
    workflow.add_node("categorize", categorize_wrapper) 
    workflow.add_node("win_likelihood", win_likelihood_wrapper)
    workflow.add_node("time_and_cost", time_cost_wrapper)
    workflow.add_node("aggregate", aggregate_wrapper)
    
    # Define the flow - sequential for now to avoid concurrency issues
    workflow.set_entry_point("ingest")
    
    # Sequential flow: ingest → categorize → win_likelihood → time_and_cost → aggregate
    workflow.add_edge("ingest", "categorize")
    workflow.add_edge("categorize", "win_likelihood")
    workflow.add_edge("win_likelihood", "time_and_cost")
    workflow.add_edge("time_and_cost", "aggregate")
    
    # End after aggregation
    workflow.add_edge("aggregate", END)
    
    # Compile and return
    return workflow.compile()


def run_case_analysis(case_input_dict: Dict[str, Any], api_key: str = None) -> Dict[str, Any]:
    """
    Convenience function to run case analysis with dictionary input.
    
    Args:
        case_input_dict: Dictionary containing case input data
        api_key: API key for Apertus model
        
    Returns:
        Dictionary containing the analysis results
        
    Example:
        >>> result = run_case_analysis({
        ...     "text": "Employment termination dispute...",
        ...     "metadata": {"language": "en", "court_level": "district"}
        ... })
        >>> print(result["likelihood_win"])
        75
    """
    from backend.agent.schemas import CaseInput
    
    # Convert dict to CaseInput
    case_input = CaseInput(**case_input_dict)
    
    # Create initial state
    initial_state = AgentState(case_input=case_input)
    
    # Create and run agent
    agent = create_legal_agent(api_key=api_key)
    result = agent.invoke(initial_state)
    
    # Return the final result
    if result.result:
        return result.result.dict()
    else:
        raise RuntimeError("Agent failed to produce result")


# Smoke test case for development
SAMPLE_INPUT = {
    "text": """I was employed as a software developer at TechCorp AG in Zurich for 3 years. 
    Last month, my manager terminated my contract with only 2 weeks notice, claiming 
    'restructuring'. However, I believe this was actually because I reported safety 
    violations to HR. I have email evidence of the safety complaints and witness 
    statements from colleagues. My contract specified 3 months notice period during 
    probation, which ended 2.5 years ago. I want to challenge this termination and 
    seek reinstatement or compensation.""",
    "metadata": {
        "language": "en",
        "court_level": "district",
        "preferred_units": "months"
    }
}


if __name__ == "__main__":
    # Basic functionality test
    try:
        agent = create_legal_agent()
        print("✓ Agent created successfully")
        
        # Test with sample input
        from backend.agent.schemas import CaseInput
        sample_case = CaseInput(**SAMPLE_INPUT)
        initial_state = AgentState(case_input=sample_case)
        
        print("✓ Sample input prepared")
        print("Note: Full execution requires API key and will call tool stubs")
        
    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        raise