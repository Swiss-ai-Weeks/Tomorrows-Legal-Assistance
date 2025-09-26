"""Jupyter notebook utilities for the Swiss Legal Analysis Agent.

This module provides functions specifically designed for Jupyter notebook environments,
including interactive diagram display and analysis demonstrations.
"""

from typing import Optional
from IPython.display import display, Image
from backend.agent_with_tools.graph import create_legal_agent
# Schema imports available but not needed for this module


def display_agent_graph(api_key: Optional[str] = None) -> None:
    """
    Display the legal agent workflow graph as a PNG in Jupyter notebook.
    
    Args:
        api_key: Optional API key for Apertus. If None, tries environment variables.
        
    Example:
        >>> from backend.agent_with_tools.jupyter_utils import display_agent_graph
        >>> display_agent_graph()
    """
    try:
        # Create the agent
        agent = create_legal_agent(api_key=api_key)
        
        # Generate and display PNG
        png_data = agent.get_graph().draw_mermaid_png()
        display(Image(png_data))
        
        print("🏛️ Swiss Legal Analysis Agent Workflow")
        print("=" * 45)
        print("📊 Graph Structure:")
        print("• Nodes: 5 (Ingest → Categorize → Win Likelihood → Time & Cost → Aggregate)")
        print("• Conditional: 'Andere' category skips analysis and goes directly to output")
        print("• Tools: 6 plug-and-play interfaces for RAG, estimation, and user interaction")
        
    except ImportError:
        print("❌ This function requires IPython/Jupyter environment")
        print("💡 Use create_legal_agent() and agent.get_graph().draw_mermaid_png() instead")
        
    except Exception as e:
        print(f"❌ Failed to display graph: {e}")
        print("💡 Make sure you have graphviz installed: pip install graphviz")


def run_interactive_demo(api_key: Optional[str] = None) -> dict:
    """
    Run an interactive demo of the legal agent in Jupyter notebook.
    
    Args:
        api_key: Optional API key for Apertus
        
    Returns:
        Dictionary containing analysis results
        
    Example:
        >>> from backend.agent_with_tools.jupyter_utils import run_interactive_demo
        >>> result = run_interactive_demo()
        >>> print(result)
    """
    from backend.agent_with_tools.graph import run_case_analysis
    
    # Sample employment case
    sample_case = {
        "text": """I was employed as a software developer at TechCorp AG in Zurich for 3 years. 
        Last month, my manager terminated my contract with only 2 weeks notice, claiming 
        'restructuring'. However, I believe this was actually because I reported safety 
        violations to HR. I have email evidence and witness statements.""",
        "metadata": {
            "language": "en",
            "court_level": "district",
            "preferred_units": "months"
        }
    }
    
    print("🇨🇭 Swiss Legal Analysis Agent - Interactive Demo")
    print("=" * 50)
    print("📝 Analyzing employment termination case...")
    print()
    
    try:
        # Run analysis
        result = run_case_analysis(sample_case, api_key=api_key)
        
        # Display results nicely
        print("📊 Analysis Results:")
        print(f"   🏷️  Category: {result.get('category', 'Unknown')}")
        
        if result.get('likelihood_win'):
            print(f"   🎯 Win Likelihood: {result['likelihood_win']}%")
        else:
            print("   🎯 Win Likelihood: Not available for this category")
            
        if result.get('estimated_time'):
            print(f"   ⏱️  Estimated Time: {result['estimated_time']}")
        else:
            print("   ⏱️  Estimated Time: Not available for this category")
            
        if result.get('estimated_cost'):
            cost = result['estimated_cost']
            if isinstance(cost, dict):
                print(f"   💰 Estimated Cost: CHF {cost.get('total_chf', 0):,.2f}")
                if cost.get('breakdown'):
                    print("      Breakdown:")
                    for item, amount in cost['breakdown'].items():
                        print(f"        • {item}: CHF {amount:,.2f}")
            else:
                print(f"   💰 Estimated Cost: CHF {cost:,.2f}")
        else:
            print("   💰 Estimated Cost: Not available for this category")
        
        return result
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure API key is set and dependencies are installed")
        return {}


def show_category_examples() -> None:
    """
    Display examples of different legal categories handled by the agent.
    """
    print("🏛️ Swiss Legal Categories - Examples")
    print("=" * 40)
    
    categories = {
        "Arbeitsrecht": [
            "Employment termination without proper notice",
            "Workplace discrimination or harassment",
            "Wage disputes and overtime claims",
            "Contract violations by employer"
        ],
        "Immobilienrecht": [
            "Property purchase disputes",
            "Rental agreement conflicts", 
            "Construction defects and warranties",
            "Zoning and planning permission issues"
        ],
        "Strafverkehrsrecht": [
            "Traffic violations and fines",
            "License suspension cases",
            "Criminal traffic offenses",
            "Insurance disputes after accidents"
        ],
        "Andere": [
            "Constitutional law questions",
            "Complex commercial disputes",
            "International law matters",
            "Administrative law cases"
        ]
    }
    
    for category, examples in categories.items():
        print(f"\n📋 {category}:")
        for example in examples:
            print(f"   • {example}")
    
    print("\n💡 Note: 'Andere' category receives classification only")
    print("   (No time/cost estimates available for complex cases)")


if __name__ == "__main__":
    print("🚀 Jupyter Utilities for Swiss Legal Analysis Agent")
    print("\nAvailable functions:")
    print("• display_agent_graph() - Show workflow diagram")
    print("• run_interactive_demo() - Run analysis demo")
    print("• show_category_examples() - View legal categories")
    
    # Show examples
    show_category_examples()