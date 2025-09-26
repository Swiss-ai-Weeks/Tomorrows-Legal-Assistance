"""Integration example for the Swiss Legal Analysis Agent.

This example demonstrates how to use the agent with mock implementations
of the tools, showing the complete workflow from case input to final analysis.
"""

import os
import sys
from typing import List, Dict, Any, Union

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.agent_with_tools.schemas import (
    Doc, Case, TimeEstimate, CostBreakdown, CategoryResult
)
from backend.agent_with_tools import create_legal_agent, run_case_analysis
from backend.agent_with_tools.schemas import CaseInput, CaseMetadata


def load_env_vars():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value


# Mock tool implementations for demonstration
class MockTools:
    """Mock implementations of tools for demonstration purposes."""
    
    @staticmethod
    def mock_rag_swiss_law(query: str, top_k: int = 5) -> List[Doc]:
        """Mock Swiss law RAG retrieval."""
        return [
            Doc(
                id="OR-328",
                title="Swiss Code of Obligations Art. 328",
                snippet="The employer may terminate the employment relationship at any time by giving notice...",
                citation="OR Art. 328"
            ),
            Doc(
                id="OR-336",
                title="Swiss Code of Obligations Art. 336", 
                snippet="The employer may not give notice at inopportune times...",
                citation="OR Art. 336"
            )
        ]
    
    @staticmethod
    def mock_historic_cases(query: str, top_k: int = 5) -> List[Case]:
        """Mock historic cases retrieval."""
        return [
            Case(
                id="BGer-4A.123/2022",
                court="Swiss Federal Court",
                year=2022,
                summary="Employment termination during sick leave ruled invalid",
                outcome="win",
                citation="BGer 4A_123/2022"
            ),
            Case(
                id="KGer-ZH-LA180045/2021",
                court="Zurich Labor Court",
                year=2021,
                summary="Wrongful dismissal claim partially successful",
                outcome="win", 
                citation="KGer ZH LA180045/2021"
            )
        ]
    
    @staticmethod
    def mock_categorize_case(text: str) -> CategoryResult:
        """Mock case categorization."""
        # Simple keyword-based classification for demo
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["employment", "employer", "work", "job", "termination", "dismissal"]):
            return CategoryResult(category="Arbeitsrecht", confidence=0.92)
        elif any(word in text_lower for word in ["property", "real estate", "rental", "lease", "building"]):
            return CategoryResult(category="Immobilienrecht", confidence=0.88) 
        elif any(word in text_lower for word in ["traffic", "driving", "license", "speed", "vehicle"]):
            return CategoryResult(category="Strafverkehrsrecht", confidence=0.85)
        else:
            return CategoryResult(category="Andere", confidence=0.70)
    
    @staticmethod
    def mock_estimate_time(case_facts: Dict[str, Any]) -> TimeEstimate:
        """Mock time estimation."""
        category = case_facts.get("category", "Andere")
        complexity = case_facts.get("complexity", "medium")
        
        # Base time estimates by category (in months)
        base_times = {
            "Arbeitsrecht": {"low": 4, "medium": 8, "high": 14},
            "Immobilienrecht": {"low": 6, "medium": 12, "high": 20}, 
            "Strafverkehrsrecht": {"low": 2, "medium": 5, "high": 10},
            "Andere": {"low": 3, "medium": 7, "high": 15}
        }
        
        months = base_times.get(category, base_times["Andere"])[complexity]
        return TimeEstimate(value=months, unit="months")
    
    @staticmethod
    def mock_estimate_cost(inputs: Dict[str, Any]) -> Union[float, CostBreakdown]:
        """Mock cost estimation."""
        time_est = inputs.get("time_estimate", {})
        months = time_est.get("value", 6)
        
        # Calculate costs (Swiss rates)
        lawyer_hours = months * 20  # 20 hours per month average
        lawyer_rate = inputs.get("hourly_rates", {}).get("lawyer", 400)
        lawyer_fees = lawyer_hours * lawyer_rate
        
        court_fees = 2500  # Base court fees
        expert_fees = 1500 if months > 8 else 0  # Expert witness for complex cases
        
        subtotal = lawyer_fees + court_fees + expert_fees
        vat = subtotal * inputs.get("vat_rate", 0.077)
        total = subtotal + vat
        
        return CostBreakdown(
            total_chf=round(total, 2),
            breakdown={
                "lawyer_fees": round(lawyer_fees, 2),
                "court_fees": court_fees,
                "expert_witness": expert_fees,
                "vat": round(vat, 2)
            }
        )
    
    @staticmethod
    def mock_ask_user(prompt: str, missing_fields: List[str]) -> str:
        """Mock user interaction."""
        # Simulate user providing clarification
        if "employment" in prompt.lower() or "work" in prompt.lower():
            return "This is about wrongful termination from employment. I was fired without proper notice."
        elif "property" in prompt.lower():
            return "This concerns a rental dispute with my landlord."
        else:
            return "This is a contract dispute that doesn't fit the other categories."


def patch_tools_for_demo():
    """Patch the tool modules with mock implementations for demonstration."""
    from backend.agent_with_tools.tools import (
        historic_cases, categorize_case, 
        estimate_time, estimate_cost, ask_user
    )
    
    # Replace the NotImplementedError functions with mocks
    # Note: rag_swiss_law is no longer patched since it has real implementation
    historic_cases.__code__ = MockTools.mock_historic_cases.__code__  
    categorize_case.__code__ = MockTools.mock_categorize_case.__code__
    estimate_time.__code__ = MockTools.mock_estimate_time.__code__
    estimate_cost.__code__ = MockTools.mock_estimate_cost.__code__
    ask_user.__code__ = MockTools.mock_ask_user.__code__


def demo_employment_case():
    """Demonstrate analysis of an employment law case."""
    print("🏛️ Swiss Legal Analysis Agent - Employment Case Demo\n")
    
    # Load environment variables
    load_env_vars()
    
    case_input = CaseInput(
        text="""I worked as a software developer at TechCorp AG in Zurich for 3 years. 
        Last month, my manager terminated my contract with only 2 weeks notice, claiming 
        'restructuring'. However, I believe this was actually because I reported safety 
        violations to HR. I have email evidence of the safety complaints and witness 
        statements from colleagues. My contract specified 3 months notice during 
        probation, which ended 2.5 years ago. I want to challenge this termination.""",
        
        metadata=CaseMetadata(
            language="en",
            court_level="district", 
            preferred_units="months",
            judges_count=1
        )
    )
    
    print("📝 Case Description:")
    print(f"   {case_input.text[:100]}...")
    print(f"📋 Metadata: {case_input.metadata}")
    print()
    
    # Check for API key
    api_key = os.environ.get("APERTUS_API_KEY")
    if api_key:
        print(f"🔑 API Key found: {api_key[:8]}...")
        print("⚠️  Note: Using mock tools for demonstration")
    else:
        print("⚠️  No API key found, using fallback behavior")
    
    try:
        # Patch tools with mocks for demo
        patch_tools_for_demo()
        
        print("🤖 Creating agent...")
        agent = create_legal_agent(api_key=api_key)
        print("✓ Agent created successfully")
        
        print("🔍 Running analysis...")
        result = agent.invoke({"case_input": case_input})
        
        print("📊 Analysis Results:")
        # LangGraph returns the full state as a dict
        if "category" in result and result["category"]:
            print(f"   Category: {result['category'].category}")
            print(f"   Confidence: {result['category'].confidence:.1%}")
        
        if "likelihood_win" in result and result["likelihood_win"]:
            print(f"   Win Likelihood: {result['likelihood_win']}%")
            
        if "time_estimate" in result and result["time_estimate"]:
            time_est = result["time_estimate"]
            print(f"   Estimated Time: {time_est.value} {time_est.unit}")
            
        if "cost_estimate" in result and result["cost_estimate"]:
            cost_est = result["cost_estimate"]
            if hasattr(cost_est, 'total_chf'):
                print(f"   Estimated Cost: CHF {cost_est.total_chf:,.2f}")
            else:
                print(f"   Estimated Cost: CHF {cost_est:,.2f}")
        
        if "result" in result and result["result"]:
            print("\n🎯 Final Output:")
            output = result["result"].model_dump()
            for key, value in output.items():
                if value is not None:
                    print(f"   {key}: {value}")
                else:
                    print(f"   {key}: null (not available for this category)")
        
        print(f"\n🔧 Tool Calls Used: {result.get('tool_call_count', 0)}")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Install with: pip install langgraph langchain-openai")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        print("   This might be expected if tools are not fully implemented")
    
    print("\n✅ Demo completed!")
    print("\n📋 Next Steps:")
    print("   1. ✓ LangGraph and dependencies installed")
    print("   2. ✓ API_KEY environment variable set") 
    print("   3. Implement real tool backends (RAG, database)")
    print("   4. Integrate with FastAPI endpoints")


def demo_mock_analysis():
    """Show mock analysis results without running the full agent."""
    print("🧪 Mock Analysis Demo (No Dependencies Required)\n")
    
    # Demo case - employment
    case_text = "Employment termination dispute with insufficient notice period"
    print(f"📝 Case 1: {case_text}")
    print()
    
    # Mock categorization
    category = MockTools.mock_categorize_case(case_text)
    print(f"🏷️  Category: {category.category} (confidence: {category.confidence:.1%})")
    
    if category.category != "Andere":
        # Mock case facts
        case_facts = {
            "category": category.category,
            "complexity": "medium", 
            "court_level": "district"
        }
        
        # Mock time estimate
        time_est = MockTools.mock_estimate_time(case_facts)
        print(f"⏱️  Time Estimate: {time_est.value} {time_est.unit}")
        
        # Mock cost estimate
        cost_inputs = {
            "time_estimate": {"value": time_est.value, "unit": time_est.unit},
            "hourly_rates": {"lawyer": 400},
            "vat_rate": 0.077
        }
        cost_est = MockTools.mock_estimate_cost(cost_inputs)
        
        print(f"💰 Cost Estimate: CHF {cost_est.total_chf:,.2f}")
        if cost_est.breakdown:
            print("   Breakdown:")
            for item, amount in cost_est.breakdown.items():
                print(f"     {item}: CHF {amount:,.2f}")
        
        # Mock win likelihood (simplified)
        win_likelihood = 72  # Would be calculated by LLM + RAG
        
        print(f"🎯 Win Likelihood: {win_likelihood}%")
        
        print("\n📊 Final Analysis Result:")
        final_result = {
            "category": category.category,
            "likelihood_win": win_likelihood,
            "estimated_time": f"{time_est.value} {time_est.unit}",
            "estimated_cost": cost_est.total_chf
        }
        
        for key, value in final_result.items():
            print(f"   {key}: {value}")
    else:
        print("ℹ️  No estimations available for 'Andere' category")
        print("\n📊 Final Analysis Result:")
        final_result = {
            "category": category.category,
            "likelihood_win": None,
            "estimated_time": None,
            "estimated_cost": None
        }
        for key, value in final_result.items():
            print(f"   {key}: {value}")
    
    # Demo 'Andere' case
    print("\n" + "-" * 40)
    print("📝 Case 2: Complex constitutional law question about digital privacy")
    andere_category = CategoryResult(category="Andere", confidence=0.85)
    print(f"🏷️  Category: {andere_category.category} (confidence: {andere_category.confidence:.1%})")
    print("ℹ️  Analysis skipped - 'Andere' category has no estimations available")
    print("\n📊 Final Analysis Result:")
    andere_result = {
        "category": andere_category.category,
        "likelihood_win": None,
        "estimated_time": None,
        "estimated_cost": None
    }
    for key, value in andere_result.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    print("🇨🇭 Swiss Legal Analysis Agent - Integration Demo")
    print("=" * 50)
    
    # Load environment variables first
    load_env_vars()
    
    # Run mock demo (no dependencies required)
    demo_mock_analysis()
    
    print("\n" + "=" * 50)
    
    # Try full demo (with real API)
    demo_employment_case()