"""LangGraph implementation for Swiss legal case analysis agent.

This module creates a deterministic pipeline agent that:
1. Ingests case descriptions and classifies them into legal categories
2. Analyzes likelihood of winning using RAG and historic cases
3. Estimates time and cost in structured workflow
4. Produces validated JSON results

Example usage:
    >>> from backend.agent_with_tools.graph import create_legal_agent
    >>> from backend.agent_with_tools.schemas import CaseInput
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

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from backend.agent_with_tools.schemas import AgentState
from backend.agent_with_tools.nodes.ingest import ingest_node
from backend.agent_with_tools.nodes.categorize import categorize_node
from backend.agent_with_tools.nodes.win_likelihood import win_likelihood_node
from backend.agent_with_tools.nodes.time_and_cost import time_and_cost_node
from backend.agent_with_tools.nodes.aggregate import aggregate_node
from backend.agent_with_tools.nodes.prepare_final_answer import (
    prepare_final_answer_node,
)
from backend.apertus.model import get_apertus_model


def should_skip_analysis(state: AgentState) -> Literal["aggregate", "win_likelihood"]:
    """
    Conditional edge function to determine if analysis should be skipped.

    Args:
        state: Current agent state

    Returns:
        "aggregate" if category is 'Andere', "win_likelihood" otherwise
    """
    category = state.category.category if state.category else "Unknown"
    if category == "Andere":
        return "aggregate"
    return "win_likelihood"


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

    def prepare_final_answer(state: AgentState) -> AgentState:
        return prepare_final_answer_node(state)

    # Add nodes to workflow
    workflow.add_node("ingest", ingest_wrapper)
    workflow.add_node("categorize", categorize_wrapper)
    workflow.add_node("win_likelihood", win_likelihood_wrapper)
    workflow.add_node("time_and_cost", time_cost_wrapper)
    workflow.add_node("aggregate", aggregate_wrapper)
    workflow.add_node("prepare_final_answer", prepare_final_answer)

    # Define the flow with conditional branching for 'Andere' category
    workflow.set_entry_point("ingest")

    # Flow: ingest → categorize → conditional branch
    workflow.add_edge("ingest", "categorize")

    # Conditional edge: if 'Andere', skip to aggregate; otherwise continue with analysis
    workflow.add_conditional_edges(
        "categorize",
        should_skip_analysis,
        {
            "aggregate": "aggregate",  # Skip analysis for 'Andere'
            "win_likelihood": "win_likelihood",  # Continue with analysis
        },
    )

    # Continue analysis flow: win_likelihood → time_and_cost → aggregate
    workflow.add_edge("win_likelihood", "time_and_cost")
    workflow.add_edge("time_and_cost", "aggregate")

    # Aggregate the information we have
    workflow.add_edge("aggregate", "prepare_final_answer")

    # Prepare the final answer + end the workflow
    workflow.add_edge("prepare_final_answer", END)

    # Compile and return
    return workflow.compile()


def run_case_analysis(
    case_input_dict: Dict[str, Any], api_key: str = None
) -> Dict[str, Any]:
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
    from backend.agent_with_tools.schemas import CaseInput

    # Convert dict to CaseInput
    case_input = CaseInput(**case_input_dict)

    # Create initial state
    initial_state = AgentState(case_input=case_input)

    # Create and run agent
    agent = create_legal_agent(api_key=api_key)
    result = agent.invoke(initial_state)

    # Return the final result
    if result.result:
        return result.result.model_dump()
    else:
        raise RuntimeError("Agent failed to produce result")


def generate_mermaid_diagram() -> str:
    """
    Generate a Mermaid flowchart diagram of the legal agent graph.

    Returns:
        String containing Mermaid diagram code
    """
    mermaid_code = """
graph TD
    Start([Start]) --> Ingest[🔧 Ingest Node<br/>Normalize Input & Initialize Memory]
    Ingest --> Categorize[🏷️ Categorize Node<br/>Classify Case into Legal Category]
    
    %% Conditional branching based on category
    Categorize --> Decision{Category = 'Andere'?}
    Decision -->|Yes| AggregateSkip[📊 Aggregate Node<br/>Return Category Only<br/>No Estimations]
    Decision -->|No| WinLikelihood[🎯 Win Likelihood Node<br/>Multi-Source Analysis with RAG & Historic Cases]
    
    %% Main analysis flow
    WinLikelihood --> TimeCost[⏱️💰 Time & Cost Node<br/>Business Logic Estimation]
    TimeCost --> AggregateFull[📊 Aggregate Node<br/>Validate & Format Full Results]
    
    %% Both paths end
    AggregateSkip --> End([End])
    AggregateFull --> End
    
    %% Styling
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef aggregate fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class Start,End startEnd
    class Ingest,Categorize,WinLikelihood,TimeCost process
    class Decision decision
    class AggregateSkip,AggregateFull aggregate
    
    %% Add notes
    Categorize -.->|"Categories:<br/>• Arbeitsrecht<br/>• Immobilienrecht<br/>• Strafverkehrsrecht<br/>• Andere"| Categorize
    WinLikelihood -.->|"Uses:<br/>• rag_swiss_law()<br/>• historic_cases()<br/>• Apertus LLM"| WinLikelihood
    TimeCost -.->|"Uses:<br/>• estimate_time()<br/>• estimate_cost()<br/>• Business Logic"| TimeCost
"""

    return mermaid_code.strip()


def save_mermaid_diagram_png(agent: CompiledStateGraph, filepath: str = None) -> bytes:
    """
    Generate and save Mermaid diagram as PNG using LangGraph's built-in method.

    Args:
        agent: Compiled LangGraph agent
        filepath: Optional path to save the PNG. If None, saves to current directory.

    Returns:
        PNG bytes data
    """
    import os

    if filepath is None:
        # Save in the agent directory
        current_dir = os.path.dirname(__file__)
        filepath = os.path.join(current_dir, "agent_workflow_diagram.png")

    try:
        # Generate PNG using LangGraph's built-in method
        png_data = agent.get_graph().draw_mermaid_png()

        # Save to file
        with open(filepath, "wb") as f:
            f.write(png_data)
        print(f"✓ Mermaid diagram PNG saved to: {filepath}")

        return png_data

    except Exception as e:
        print(f"❌ Failed to generate PNG diagram: {e}")
        print("Note: This requires graphviz and additional dependencies")
        return b""


def display_mermaid_png(agent: CompiledStateGraph) -> None:
    """
    Display Mermaid diagram as PNG in Jupyter notebook or save to file.

    Args:
        agent: Compiled LangGraph agent
    """
    try:
        # Try to use IPython display if available (Jupyter environment)
        from IPython.display import display, Image

        png_data = agent.get_graph().draw_mermaid_png()
        display(Image(png_data))
        print("✓ Mermaid diagram displayed in notebook")

    except ImportError:
        # Fallback to saving PNG file
        print("📊 Not in Jupyter environment, saving PNG to file...")
        save_mermaid_diagram_png(agent)

    except Exception as e:
        print(f"❌ Failed to display diagram: {e}")
        print("Falling back to text-based Mermaid diagram...")
        # Fallback to text diagram
        save_mermaid_text_diagram()


def save_mermaid_text_diagram(filepath: str = None) -> str:
    """
    Save text-based Mermaid diagram to file (fallback method).

    Args:
        filepath: Optional path to save the diagram. If None, saves to current directory.

    Returns:
        The Mermaid diagram code
    """
    import os

    if filepath is None:
        # Save in the agent directory
        current_dir = os.path.dirname(__file__)
        filepath = os.path.join(current_dir, "agent_workflow_diagram.mmd")

    diagram_code = generate_mermaid_diagram()

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(diagram_code)
        print(f"✓ Mermaid text diagram saved to: {filepath}")
    except Exception as e:
        print(f"❌ Failed to save diagram: {e}")

    return diagram_code


def print_mermaid_info():
    """Print information about viewing the Mermaid diagram."""
    print("\n📊 Graph Workflow Diagram")
    print("=" * 40)
    print("The agent workflow diagram has been generated.")
    print("\nViewing options:")
    print("1. 📱 PNG Image: Check the saved .png file")
    print("2. 🌐 Online: Copy .mmd code to https://mermaid.live/")
    print("3. 🔧 VS Code: Install 'Mermaid Preview' extension")
    print("4. 📖 Documentation: Embed in Markdown with ```mermaid blocks")

    print("\n🏛️ Workflow Summary:")
    print("• Start → Ingest → Categorize")
    print("• If 'Andere': → Aggregate (category only) → End")
    print("• If Other: → Win Likelihood → Time & Cost → Aggregate → End")
    print("• Total nodes: 5 | Conditional branching: 1")


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
        "preferred_units": "months",
    },
}


if __name__ == "__main__":
    # Generate and save Mermaid diagram
    print("🇨🇭 Swiss Legal Analysis Agent - Graph Generator")
    print("=" * 50)

    # Basic functionality test and diagram generation
    try:
        agent = create_legal_agent()
        print("✓ Agent created successfully")

        # Generate PNG diagram using LangGraph's built-in method
        print("\n📊 Generating workflow diagram...")
        display_mermaid_png(agent)

        # Test with sample input
        from backend.agent_with_tools.schemas import CaseInput

        sample_case = CaseInput(**SAMPLE_INPUT)
        initial_state = AgentState(case_input=sample_case)

        print("✓ Sample input prepared")
        print("Note: Full execution requires API key and will call tool stubs")

    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        print("This is expected without proper API key setup")

        # Fallback to text diagram
        print("\n📊 Generating text-based Mermaid diagram as fallback...")
        diagram_code = save_mermaid_text_diagram()

        print("\n📊 Mermaid Diagram Preview:")
        print("```mermaid")
        print(diagram_code)
        print("```")

    print_mermaid_info()
