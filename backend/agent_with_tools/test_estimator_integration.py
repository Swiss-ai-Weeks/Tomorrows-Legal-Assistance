#!/usr/bin/env python3
"""Test script for estimator function integration."""

import sys
import os
from typing import Dict, Any

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.agent_with_tools.tools.estimate_time import estimate_time
from backend.agent_with_tools.tools.estimate_cost import estimate_cost
from backend.agent_with_tools.schemas import TimeEstimate, CostBreakdown


def test_employment_case():
    """Test estimator functions with an employment law case."""
    print("🧪 Testing Employment Law Case")
    print("-" * 40)
    
    # Employment case - salary dispute
    case_facts = {
        "category": "Arbeitsrecht",
        "complexity": "medium",
        "court_level": "district",
        "case_text": "My employer has not paid my salary for the last 3 months. I have evidence of my employment contract and worked hours.",
        "preferred_units": "months"
    }
    
    print(f"📋 Case Facts: {case_facts}")
    
    # Test time estimation
    try:
        time_result = estimate_time(case_facts)
        print(f"⏱️  Time Estimate: {time_result.value} {time_result.unit}")
        print(f"   Type: {type(time_result)}")
        assert isinstance(time_result, TimeEstimate)
        assert time_result.value > 0
    except Exception as e:
        print(f"❌ Time estimation failed: {e}")
        return False
    
    # Test cost estimation
    try:
        cost_inputs = {
            "time_estimate": time_result.model_dump(),
            "category": case_facts["category"],
            "case_text": case_facts["case_text"],
            "hourly_rates": {"lawyer": 400},
            "vat_rate": 0.077
        }
        
        cost_result = estimate_cost(cost_inputs)
        print(f"💰 Cost Estimate: CHF {cost_result.total_chf:,.2f}")
        print(f"   Type: {type(cost_result)}")
        if hasattr(cost_result, 'breakdown') and cost_result.breakdown:
            print(f"   Breakdown: {cost_result.breakdown}")
        
        assert isinstance(cost_result, (CostBreakdown, float))
        if isinstance(cost_result, CostBreakdown):
            assert cost_result.total_chf > 0
    except Exception as e:
        print(f"❌ Cost estimation failed: {e}")
        return False
    
    print("✅ Employment case test passed!")
    return True


def test_traffic_case():
    """Test estimator functions with a traffic law case."""
    print("\n🧪 Testing Traffic Criminal Law Case")
    print("-" * 40)
    
    # Traffic case - speeding
    case_facts = {
        "category": "Strafverkehrsrecht", 
        "complexity": "low",
        "court_level": "district",
        "case_text": "I received a speeding ticket for driving 15 km/h over the limit in a 50 km/h zone. I want to contest this fine.",
        "preferred_units": "months"
    }
    
    print(f"📋 Case Facts: {case_facts}")
    
    # Test time estimation
    try:
        time_result = estimate_time(case_facts)
        print(f"⏱️  Time Estimate: {time_result.value} {time_result.unit}")
        assert isinstance(time_result, TimeEstimate)
        assert time_result.value >= 0  # Traffic cases might be 0 months
    except Exception as e:
        print(f"❌ Time estimation failed: {e}")
        return False
    
    # Test cost estimation
    try:
        cost_inputs = {
            "time_estimate": time_result.model_dump(),
            "category": case_facts["category"],
            "case_text": case_facts["case_text"],
            "hourly_rates": {"lawyer": 400},
            "vat_rate": 0.077
        }
        
        cost_result = estimate_cost(cost_inputs)
        print(f"💰 Cost Estimate: CHF {cost_result.total_chf:,.2f}")
        if hasattr(cost_result, 'breakdown') and cost_result.breakdown:
            print(f"   Breakdown: {cost_result.breakdown}")
        
        assert isinstance(cost_result, (CostBreakdown, float))
        if isinstance(cost_result, CostBreakdown):
            assert cost_result.total_chf >= 0
    except Exception as e:
        print(f"❌ Cost estimation failed: {e}")
        return False
    
    print("✅ Traffic case test passed!")
    return True


def test_unsupported_case():
    """Test estimator functions with an unsupported category."""
    print("\n🧪 Testing Unsupported Category (Immobilienrecht)")
    print("-" * 40)
    
    # Real estate case - not supported by estimator, should use fallback
    case_facts = {
        "category": "Immobilienrecht",
        "complexity": "high", 
        "court_level": "cantonal",
        "case_text": "Property boundary dispute with neighbor over 2 meter strip of land.",
        "preferred_units": "months"
    }
    
    print(f"📋 Case Facts: {case_facts}")
    
    # Test time estimation (should use fallback)
    try:
        time_result = estimate_time(case_facts)
        print(f"⏱️  Time Estimate (Fallback): {time_result.value} {time_result.unit}")
        assert isinstance(time_result, TimeEstimate)
        assert time_result.value > 0
    except Exception as e:
        print(f"❌ Time estimation failed: {e}")
        return False
    
    # Test cost estimation (should use fallback)
    try:
        cost_inputs = {
            "time_estimate": time_result.model_dump(),
            "category": case_facts["category"],
            "case_text": case_facts["case_text"],
            "hourly_rates": {"lawyer": 450},  # Higher rate for complex real estate
            "vat_rate": 0.077
        }
        
        cost_result = estimate_cost(cost_inputs)
        print(f"💰 Cost Estimate (Fallback): CHF {cost_result.total_chf:,.2f}")
        if hasattr(cost_result, 'breakdown') and cost_result.breakdown:
            print(f"   Breakdown: {cost_result.breakdown}")
        
        assert isinstance(cost_result, (CostBreakdown, float))
        if isinstance(cost_result, CostBreakdown):
            assert cost_result.total_chf > 0
    except Exception as e:
        print(f"❌ Cost estimation failed: {e}")
        return False
    
    print("✅ Unsupported category test passed!")
    return True


def run_all_tests():
    """Run all estimator integration tests."""
    print("🧪 Estimator Function Integration Tests")
    print("=" * 50)
    
    tests = [
        test_employment_case,
        test_traffic_case, 
        test_unsupported_case
    ]
    
    passed = 0
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Estimator functions are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the implementations.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)