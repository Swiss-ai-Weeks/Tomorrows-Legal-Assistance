"""Smoke tests for the legal analysis agent."""

import pytest
from unittest.mock import Mock, patch
from backend.agent_with_tools.schemas import CaseInput, CaseMetadata, AgentState
from backend.agent_with_tools.nodes.ingest import ingest_node
from backend.agent_with_tools.nodes.aggregate import aggregate_node


def test_case_input_validation():
    """Test that CaseInput validates correctly."""
    # Valid input
    case = CaseInput(
        text="Employment termination case",
        metadata=CaseMetadata(language="en", court_level="district")
    )
    assert case.text == "Employment termination case"
    assert case.metadata.language == "en"
    
    # Minimal input
    minimal_case = CaseInput(text="Simple case")
    assert minimal_case.text == "Simple case"
    assert minimal_case.metadata is None


def test_ingest_node():
    """Test the ingest node processes input correctly."""
    case_input = CaseInput(
        text="Test case description",
        metadata=CaseMetadata(language="de", court_level="cantonal", judges_count=3)
    )
    
    initial_state = AgentState(case_input=case_input)
    result_state = ingest_node(initial_state)
    
    # Check that case facts were initialized
    assert result_state.case_facts is not None
    assert result_state.case_facts["text"] == "Test case description"
    assert result_state.case_facts["jurisdiction"] == "CH"
    assert result_state.case_facts["court_level"] == "cantonal"
    assert result_state.case_facts["judges_count"] == 3
    assert result_state.case_facts["language"] == "de"
    assert result_state.tool_call_count == 0


def test_aggregate_node():
    """Test the aggregate node produces valid output."""
    from backend.agent_with_tools.schemas import TimeEstimate, CostBreakdown
    
    # Create state with all required components
    state = AgentState(
        case_input=CaseInput(text="Test case"),
        likelihood_win=75,
        time_estimate=TimeEstimate(value=6, unit="months"),
        cost_estimate=CostBreakdown(total_chf=15000.0, breakdown={"lawyer": 12000.0, "court": 3000.0})
    )
    
    result_state = aggregate_node(state)
    
    # Check final output
    assert result_state.result is not None
    assert result_state.result.likelihood_win == 75
    assert result_state.result.estimated_time == "6 months"
    assert isinstance(result_state.result.estimated_cost, CostBreakdown)
    assert result_state.result.estimated_cost.total_chf == 15000.0


def test_aggregate_node_missing_data():
    """Test aggregate node fails gracefully with missing data."""
    state = AgentState(case_input=CaseInput(text="Test case"))
    
    with pytest.raises(ValueError, match="Missing likelihood_win score"):
        aggregate_node(state)


def test_agent_creation():
    """Test that the agent can be created without errors."""
    from backend.agent_with_tools.graph import create_legal_agent
    
    # Mock the Apertus model to avoid needing API key
    with patch('backend.agent_with_tools.graph.get_apertus_model') as mock_get_model:
        mock_llm = Mock()
        mock_get_model.return_value = mock_llm
        
        agent = create_legal_agent()
        assert agent is not None
        
        # Verify the model was requested
        mock_get_model.assert_called_once_with(api_key=None)


def test_schema_validation():
    """Test output schema validation."""
    from backend.agent_with_tools.schemas import AgentOutput
    
    # Valid output
    output = AgentOutput(
        likelihood_win=85,
        estimated_time="4 months",
        estimated_cost=12500.0
    )
    assert output.likelihood_win == 85
    
    # Invalid likelihood (too high)
    with pytest.raises(ValueError):
        AgentOutput(
            likelihood_win=150,  # Invalid: > 100
            estimated_time="4 months", 
            estimated_cost=12500.0
        )
    
    # Invalid likelihood (too low)
    with pytest.raises(ValueError):
        AgentOutput(
            likelihood_win=0,  # Invalid: < 1
            estimated_time="4 months",
            estimated_cost=12500.0
        )


def test_categories():
    """Test that categorization covers expected legal areas."""
    from backend.agent_with_tools.schemas import CategoryResult
    
    categories = ["Arbeitsrecht", "Immobilienrecht", "Strafverkehrsrecht", "Andere"]
    
    for category in categories:
        result = CategoryResult(category=category, confidence=0.9)
        assert result.category == category
        assert 0.0 <= result.confidence <= 1.0


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running smoke tests...")
    
    test_case_input_validation()
    print("✓ Case input validation")
    
    test_ingest_node()  
    print("✓ Ingest node")
    
    test_aggregate_node()
    print("✓ Aggregate node")
    
    test_agent_creation()
    print("✓ Agent creation")
    
    test_schema_validation()
    print("✓ Schema validation")
    
    test_categories()
    print("✓ Category validation")
    
    print("\nAll smoke tests passed! 🎉")
    print("\nNote: Full integration tests require:")
    print("- Valid API_KEY environment variable")
    print("- LangGraph and dependencies installed")
    print("- Tool implementations (currently stubs)")