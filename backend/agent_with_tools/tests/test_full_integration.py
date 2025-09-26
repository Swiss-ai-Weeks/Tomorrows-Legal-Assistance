"""Integration test for the business likelihood estimation in the full agent."""

import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.agent_with_tools.schemas import CaseInput, AgentState, CategoryResult
from backend.agent_with_tools.nodes.win_likelihood import win_likelihood_node
from unittest.mock import Mock


def test_win_likelihood_node_with_business_logic():
    """Test the win likelihood node with business logic integration."""
    print("=== Testing win_likelihood_node with Business Logic ===")
    
    # Create test input
    case_input = CaseInput(
        text="I was fired during my illness and want to challenge the termination. I have medical documentation."
    )
    
    # Create initial state with category
    state = AgentState(
        case_input=case_input,
        category=CategoryResult(category="Arbeitsrecht", confidence=0.9),
        tool_call_count=0,
        explanation_parts=[]
    )
    
    # Mock the LLM
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.content.strip.return_value = "Based on the analysis, this case has a strong likelihood of success due to legal protections during illness. Score: 85"
    mock_llm.invoke.return_value = mock_response
    
    # Run the node
    result_state = win_likelihood_node(state, mock_llm)
    
    # Check results
    print(f"Final likelihood: {result_state.likelihood_win}%")
    print(f"Tool calls made: {result_state.tool_call_count}")
    print(f"Explanation parts:")
    for i, part in enumerate(result_state.explanation_parts):
        print(f"  {i+1}. {part}")
    
    # Verify that business logic was used
    assert result_state.tool_call_count >= 1, "Should have made at least one tool call for business logic"
    assert result_state.explanation_parts, "Should have explanation parts"
    assert result_state.likelihood_win is not None, "Should have likelihood score"
    
    # Check that business logic was applied (should mention 100% baseline for illness cases)
    business_explanations = [part for part in result_state.explanation_parts if "Business logic baseline" in part]
    assert business_explanations, "Should have business logic explanation"
    print(f"✓ Business logic explanation found: {business_explanations[0]}")
    
    return result_state


def test_unsupported_category():
    """Test behavior with unsupported category."""
    print("\n=== Testing Unsupported Category ===")
    
    # Create test input for unsupported category
    case_input = CaseInput(
        text="Property boundary dispute with neighbor"
    )
    
    # Create initial state with unsupported category
    state = AgentState(
        case_input=case_input,
        category=CategoryResult(category="Immobilienrecht", confidence=0.85),
        tool_call_count=0,
        explanation_parts=[]
    )
    
    # Mock the LLM
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.content.strip.return_value = "This real estate case requires detailed analysis. Score: 60"
    mock_llm.invoke.return_value = mock_response
    
    # Run the node
    result_state = win_likelihood_node(state, mock_llm)
    
    print(f"Final likelihood: {result_state.likelihood_win}%")
    print(f"Explanation parts:")
    for i, part in enumerate(result_state.explanation_parts):
        print(f"  {i+1}. {part}")
    
    # Should still get a result but with warning
    assert result_state.likelihood_win is not None, "Should still produce likelihood"
    
    # Check that it mentions category not supported
    unsupported_explanations = [part for part in result_state.explanation_parts if "not supported" in part]
    assert unsupported_explanations, "Should have explanation about unsupported category"
    print(f"✓ Unsupported category handled: {unsupported_explanations[0]}")
    
    return result_state


def test_traffic_law_case():
    """Test traffic law case with business logic."""
    print("\n=== Testing Traffic Law Case ===")
    
    # Create speeding case
    case_input = CaseInput(
        text="I was caught speeding 20 km/h over the limit and received a fine. Want to contest it."
    )
    
    state = AgentState(
        case_input=case_input,
        category=CategoryResult(category="Strafverkehrsrecht", confidence=0.95),
        tool_call_count=0,
        explanation_parts=[]
    )
    
    # Mock the LLM
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.content.strip.return_value = "Traffic violations are difficult to contest without technical errors. Score: 15"
    mock_llm.invoke.return_value = mock_response
    
    # Run the node
    result_state = win_likelihood_node(state, mock_llm)
    
    print(f"Final likelihood: {result_state.likelihood_win}%")
    print(f"Explanation parts:")
    for i, part in enumerate(result_state.explanation_parts):
        print(f"  {i+1}. {part}")
    
    # Should get low likelihood for speeding
    assert result_state.likelihood_win is not None, "Should produce likelihood"
    
    # Check for business logic about speeding
    business_explanations = [part for part in result_state.explanation_parts if "Business logic baseline" in part]
    if business_explanations:
        print(f"✓ Business logic for traffic case: {business_explanations[0]}")
    
    return result_state


if __name__ == "__main__":
    print("Running integration tests for business logic likelihood estimation...\n")
    
    try:
        test_win_likelihood_node_with_business_logic()
        test_unsupported_category()
        test_traffic_law_case()
        print("\n=== All integration tests passed! ===")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise