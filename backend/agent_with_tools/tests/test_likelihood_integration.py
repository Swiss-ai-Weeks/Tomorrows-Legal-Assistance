"""Test business logic likelihood estimation integration."""

import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.agent_with_tools.tools.estimate_likelihood import (
    estimate_business_likelihood, 
    _parse_likelihood_percentage,
    get_likelihood_explanation_context
)


def test_parse_likelihood_percentage():
    """Test the percentage parsing function."""
    print("\n=== Testing _parse_likelihood_percentage ===")
    
    test_cases = [
        ("20%", 20),
        ("80%", 80),
        ("10–15% (usually hopeless unless technical errors)", 12),  # midpoint of range
        ("100%", 95),  # capped at 95
        ("<10% (almost hopeless, mandatory withdrawal)", 5),  # special case
        ("50–60% (good if insurance involved; depends on proof)", 55),  # midpoint
        ("unknown", None),
        ("", None),
        (None, None),
    ]
    
    for input_str, expected in test_cases:
        result = _parse_likelihood_percentage(input_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_str}' -> {result} (expected {expected})")


def test_estimate_business_likelihood():
    """Test the main business likelihood estimation function."""
    print("\n=== Testing estimate_business_likelihood ===")
    
    test_cases = [
        # Employment law cases
        ("I was terminated from my job without proper notice", "Arbeitsrecht"),
        ("My employer hasn't paid my salary for 3 months", "Arbeitsrecht"),
        ("I was fired during illness", "Arbeitsrecht"),
        
        # Traffic law cases
        ("I was caught speeding at 80 in a 60 zone", "Strafverkehrsrecht"),
        ("I was driving under the influence", "Strafverkehrsrecht"),
        ("I got a parking fine", "Strafverkehrsrecht"),
        
        # Unsupported categories
        ("Real estate dispute", "Immobilienrecht"),
        ("Some other legal issue", "Andere"),
    ]
    
    for case_text, category in test_cases:
        print(f"\n--- Testing: {category} ---")
        print(f"Case: {case_text}")
        
        result = estimate_business_likelihood(case_text, category)
        
        print(f"Result:")
        print(f"  Likelihood: {result['likelihood']}")
        print(f"  Raw estimate: {result['raw_estimate']}")
        print(f"  Category mapped: {result['category_mapped']}")
        print(f"  Subcategory: {result['subcategory']}")
        print(f"  Explanation: {result['explanation']}")
        
        # Test the context generation
        context = get_likelihood_explanation_context(result)
        print(f"Context for LLM:\n{context}")


def test_integration_with_sample_case():
    """Test with the sample case from the main graph."""
    print("\n=== Testing with Sample Employment Case ===")
    
    case_text = """I was employed as a software developer at TechCorp AG in Zurich for 3 years. 
    Last month, my manager terminated my contract with only 2 weeks notice, claiming 
    'restructuring'. However, I believe this was actually because I reported safety 
    violations to HR. I have email evidence of the safety complaints and witness 
    statements from colleagues. My contract specified 3 months notice period during 
    probation, which ended 2.5 years ago. I want to challenge this termination and 
    seek reinstatement or compensation."""
    
    category = "Arbeitsrecht"
    
    result = estimate_business_likelihood(case_text, category)
    
    print(f"Case category: {category}")
    print(f"Likelihood: {result['likelihood']}%")
    print(f"Raw business estimate: {result['raw_estimate']}")
    print(f"Explanation: {result['explanation']}")
    
    context = get_likelihood_explanation_context(result)
    print(f"\nContext for LLM integration:\n{context}")


if __name__ == "__main__":
    test_parse_likelihood_percentage()
    test_estimate_business_likelihood()
    test_integration_with_sample_case()
    print("\n=== All tests completed ===")