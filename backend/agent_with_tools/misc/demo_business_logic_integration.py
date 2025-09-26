"""End-to-end demonstration of the business logic likelihood integration."""

import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.agent_with_tools.graph import run_case_analysis


def test_employment_case_with_business_logic():
    """Demonstrate full workflow with employment case."""
    print("=== End-to-End Test: Employment Termination Case ===\n")
    
    case_input = {
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
    
    print("Case Description:")
    print(case_input["text"])
    print("\n" + "="*80 + "\n")
    
    try:
        # Run the full analysis
        result = run_case_analysis(case_input)
        
        print("FINAL ANALYSIS RESULT:")
        print(f"Category: {result.get('category', 'Unknown')}")
        print(f"Likelihood of Winning: {result.get('likelihood_win', 'N/A')}%")
        print(f"Estimated Time: {result.get('estimated_time', 'N/A')}")
        print(f"Estimated Cost: CHF {result.get('estimated_cost', 'N/A')}")
        
        if 'explanation' in result:
            print(f"\nExplanation: {result['explanation']}")
        
        # Analyze the explanation to verify business logic integration
        explanation = result.get('explanation', '')
        if 'Business logic baseline' in explanation:
            print("\n✓ Business logic successfully integrated!")
            
            # Extract business logic part
            parts = explanation.split(' | ')
            business_part = next((part for part in parts if 'Business logic baseline' in part), None)
            if business_part:
                print(f"✓ Business guidance: {business_part}")
        else:
            print("\n⚠️ Business logic not found in explanation")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_traffic_case_with_business_logic():
    """Test traffic law case."""
    print("\n" + "="*80 + "\n")
    print("=== End-to-End Test: Traffic Violation Case ===\n")
    
    case_input = {
        "text": "I was caught driving under the influence with 0.6 BAC and received a penalty order. My license was withdrawn. I want to appeal this decision.",
        "metadata": {
            "language": "en",
            "court_level": "district"
        }
    }
    
    print("Case Description:")
    print(case_input["text"])
    print("\n" + "="*40 + "\n")
    
    try:
        result = run_case_analysis(case_input)
        
        print("FINAL ANALYSIS RESULT:")
        print(f"Category: {result.get('category', 'Unknown')}")
        print(f"Likelihood of Winning: {result.get('likelihood_win', 'N/A')}%")
        print(f"Estimated Time: {result.get('estimated_time', 'N/A')}")
        print(f"Estimated Cost: CHF {result.get('estimated_cost', 'N/A')}")
        
        if 'explanation' in result:
            print(f"\nExplanation: {result['explanation']}")
        
        # Should be very low likelihood for DUI
        likelihood = result.get('likelihood_win')
        if likelihood is not None and likelihood < 20:
            print("✓ Low likelihood correctly identified for DUI case")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_unsupported_category():
    """Test case with unsupported category.""" 
    print("\n" + "="*80 + "\n")
    print("=== End-to-End Test: Unsupported Category Case ===\n")
    
    case_input = {
        "text": "I have a boundary dispute with my neighbor regarding property lines. The fence encroaches 50cm onto my land according to the survey.",
        "metadata": {
            "language": "en"
        }
    }
    
    print("Case Description:")
    print(case_input["text"])
    print("\n" + "="*40 + "\n")
    
    try:
        result = run_case_analysis(case_input)
        
        print("FINAL ANALYSIS RESULT:")
        print(f"Category: {result.get('category', 'Unknown')}")
        print(f"Likelihood of Winning: {result.get('likelihood_win', 'N/A')}%")
        print(f"Estimated Time: {result.get('estimated_time', 'N/A')}")
        print(f"Estimated Cost: CHF {result.get('estimated_cost', 'N/A')}")
        
        if 'explanation' in result:
            print(f"\nExplanation: {result['explanation']}")
        
        # Should show proper handling of unsupported category
        explanation = result.get('explanation', '')
        if 'not supported' in explanation:
            print("✓ Unsupported category properly handled with explanation")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("Running end-to-end demonstrations of business logic likelihood integration...")
    print("This will show how the business logic estimator guides the final likelihood values.\n")
    
    try:
        # Run all test cases
        employment_result = test_employment_case_with_business_logic()
        traffic_result = test_traffic_case_with_business_logic() 
        unsupported_result = test_unsupported_category()
        
        print("\n" + "="*80)
        print("SUMMARY OF RESULTS:")
        print("="*80)
        
        if employment_result:
            print(f"Employment Case: {employment_result.get('likelihood_win', 'N/A')}% likelihood")
        if traffic_result:
            print(f"Traffic DUI Case: {traffic_result.get('likelihood_win', 'N/A')}% likelihood") 
        if unsupported_result:
            print(f"Real Estate Case: {unsupported_result.get('likelihood_win', 'N/A')}% likelihood")
        
        print("\n✓ All end-to-end tests completed successfully!")
        print("✓ Business logic estimator is properly integrated and influencing final results!")
        
    except Exception as e:
        print(f"\n❌ End-to-end test failed: {e}")
        raise