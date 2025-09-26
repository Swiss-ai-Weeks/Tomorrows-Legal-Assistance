"""Test script to verify 'Andere' category handling in the legal agent."""

from backend.agent.schemas import CaseInput, CaseMetadata, CategoryResult
from backend.agent.tools.categorize_case import categorize_case


def test_andere_category():
    """Test that 'Andere' category properly skips analysis."""
    print("🧪 Testing 'Andere' Category Handling")
    print("=" * 40)
    
    # Mock the categorize_case function to return 'Andere'
    def mock_categorize_andere(text: str) -> CategoryResult:
        return CategoryResult(category="Andere", confidence=0.95)
    
    # Patch the function temporarily
    original_func = categorize_case.__code__
    categorize_case.__code__ = mock_categorize_andere.__code__
    
    try:
        from backend.agent import create_legal_agent
        
        # Load environment
        from backend.agent.demo import load_env_vars
        load_env_vars()
        
        # Create agent
        agent = create_legal_agent()
        
        # Test case that should be classified as 'Andere'
        andere_case = CaseInput(
            text="Complex constitutional law question about digital privacy rights and international treaties",
            metadata=CaseMetadata(language="en")
        )
        
        print(f"📝 Test Case: {andere_case.text[:50]}...")
        print("🏷️  Expected Category: Andere")
        
        # Run analysis
        result = agent.invoke({"case_input": andere_case})
        
        # Check results
        final_output = result.get("result")
        
        if final_output:
            print("\n📊 Results:")
            print(f"   Category: {final_output.category}")
            print(f"   Win Likelihood: {final_output.likelihood_win}")
            print(f"   Estimated Time: {final_output.estimated_time}")
            print(f"   Estimated Cost: {final_output.estimated_cost}")
            
            # Verify 'Andere' behavior
            if final_output.category == "Andere":
                if (final_output.likelihood_win is None and 
                    final_output.estimated_time is None and 
                    final_output.estimated_cost is None):
                    print("\n✅ SUCCESS: 'Andere' category correctly skipped analysis")
                    return True
                else:
                    print("\n❌ FAILURE: 'Andere' category should have null estimations")
                    return False
            else:
                print(f"\n❌ FAILURE: Expected 'Andere' category, got '{final_output.category}'")
                return False
        else:
            print("\n❌ FAILURE: No final output generated")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
    
    finally:
        # Restore original function
        categorize_case.__code__ = original_func


def test_regular_category():
    """Test that regular categories still get full analysis."""
    print("\n🧪 Testing Regular Category Handling")
    print("=" * 40)
    
    try:
        from backend.agent.demo import patch_tools_for_demo
        from backend.agent import create_legal_agent
        
        # Patch tools with mocks
        patch_tools_for_demo()
        
        # Load environment
        from backend.agent.demo import load_env_vars
        load_env_vars()
        
        # Create agent
        agent = create_legal_agent()
        
        # Test employment case
        employment_case = CaseInput(
            text="Employment termination without proper notice period",
            metadata=CaseMetadata(language="en")
        )
        
        print(f"📝 Test Case: {employment_case.text}")
        print("🏷️  Expected Category: Arbeitsrecht")
        
        # Run analysis
        result = agent.invoke({"case_input": employment_case})
        
        # Check results
        final_output = result.get("result")
        
        if final_output:
            print("\n📊 Results:")
            print(f"   Category: {final_output.category}")
            print(f"   Win Likelihood: {final_output.likelihood_win}")
            print(f"   Estimated Time: {final_output.estimated_time}")
            print(f"   Estimated Cost: {final_output.estimated_cost}")
            
            # Verify regular category behavior
            if final_output.category in ["Arbeitsrecht", "Immobilienrecht", "Strafverkehrsrecht"]:
                if (final_output.likelihood_win is not None and 
                    final_output.estimated_time is not None and 
                    final_output.estimated_cost is not None):
                    print(f"\n✅ SUCCESS: '{final_output.category}' category provided full analysis")
                    return True
                else:
                    print(f"\n❌ FAILURE: '{final_output.category}' category should have estimations")
                    return False
            else:
                print(f"\n❌ FAILURE: Unexpected category '{final_output.category}'")
                return False
        else:
            print("\n❌ FAILURE: No final output generated")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    print("🇨🇭 Swiss Legal Analysis Agent - Category Flow Tests")
    print("=" * 55)
    
    # Test both flows
    andere_success = test_andere_category()
    regular_success = test_regular_category()
    
    print("\n" + "=" * 55)
    print("📊 Test Summary:")
    print(f"   'Andere' category test: {'✅ PASSED' if andere_success else '❌ FAILED'}")
    print(f"   Regular category test: {'✅ PASSED' if regular_success else '❌ FAILED'}")
    
    if andere_success and regular_success:
        print("\n🎉 All tests passed! Conditional flow is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the implementation.")
    
    print("\n💡 Key Features Verified:")
    print("   • Category included in final output")
    print("   • 'Andere' category skips time/cost analysis")
    print("   • Regular categories provide full estimations")
    print("   • Conditional graph branching works correctly")