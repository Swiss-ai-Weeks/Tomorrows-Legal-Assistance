"""Test the aggregate node with explanation field."""

import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.agent_with_tools.schemas import CaseInput, AgentState, CategoryResult, TimeEstimate
from backend.agent_with_tools.nodes.aggregate import aggregate_node


def test_aggregate_with_explanation():
    """Test that aggregate node properly includes explanation."""
    print("=== Testing Aggregate Node with Explanation ===")
    
    # Create state with all components including explanation
    case_input = CaseInput(text="Employment termination case")
    
    state = AgentState(
        case_input=case_input,
        category=CategoryResult(category="Arbeitsrecht", confidence=0.9),
        likelihood_win=75,
        time_estimate=TimeEstimate(value=6, unit="months"),
        cost_estimate=15000.0,
        explanation_parts=[
            "Business logic baseline: 20%. This provides initial guidance but will be adjusted based on case-specific factors.",
            "Swiss law documents: Not available (stub implementation)",
            "Historic cases: Not available (stub implementation)",
            "Final likelihood analysis: Strong case with good legal foundation. Score: 75"
        ]
    )
    
    # Run aggregate node
    result_state = aggregate_node(state)
    
    # Check result
    result = result_state.result
    print(f"Category: {result.category}")
    print(f"Likelihood: {result.likelihood_win}%")
    print(f"Time: {result.estimated_time}")
    print(f"Cost: CHF {result.estimated_cost}")
    print(f"Explanation: {result.explanation}")
    
    # Verify explanation is properly compiled
    assert result.explanation is not None, "Should have explanation"
    assert "Business logic baseline" in result.explanation, "Should include business logic"
    assert "Final likelihood analysis" in result.explanation, "Should include final analysis"
    print("✓ Explanation properly compiled")
    
    return result


def test_aggregate_andere_category():
    """Test aggregate with 'Andere' category includes explanation."""
    print("\n=== Testing Aggregate Node with 'Andere' Category ===")
    
    case_input = CaseInput(text="Some unusual legal matter")
    
    state = AgentState(
        case_input=case_input,
        category=CategoryResult(category="Andere", confidence=0.7),
        explanation_parts=[
            "Category 'Andere' not supported by business logic estimator. Using fallback analysis.",
            "Analysis tools not applicable for this case type."
        ]
    )
    
    # Run aggregate node
    result_state = aggregate_node(state)
    
    # Check result
    result = result_state.result
    print(f"Category: {result.category}")
    print(f"Likelihood: {result.likelihood_win}")
    print(f"Time: {result.estimated_time}")
    print(f"Cost: {result.estimated_cost}")
    print(f"Explanation: {result.explanation}")
    
    # Verify 'Andere' handling
    assert result.category == "Andere", "Should be 'Andere' category"
    assert result.likelihood_win is None, "Should have no likelihood for 'Andere'"
    assert result.explanation is not None, "Should have explanation even for 'Andere'"
    assert "not supported" in result.explanation, "Should explain why no estimates available"
    print("✓ 'Andere' category properly handled with explanation")
    
    return result


if __name__ == "__main__":
    print("Testing aggregate node with explanation support...\n")
    
    try:
        test_aggregate_with_explanation()
        test_aggregate_andere_category()
        print("\n=== All aggregate tests passed! ===")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise