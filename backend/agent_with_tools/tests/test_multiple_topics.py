#!/usr/bin/env python3
"""Test different legal topics to verify RAG retrieval accuracy."""

import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend tools to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_real_estate_case():
    """Test a real estate/property law case."""
    case_input = {
        "text": """Ich habe vor 6 Monaten ein Einfamilienhaus in Basel gekauft. Beim Kauf wurden keine 
        Mängel erwähnt, aber jetzt habe ich entdeckt, dass das Dach undicht ist und Wasser in den 
        Dachboden eindringt. Die Reparaturkosten werden auf 25.000 CHF geschätzt. Der Verkäufer 
        behauptet, er wusste nichts von dem Problem. Kann ich Schadenersatz fordern oder vom Kaufvertrag zurücktreten?""",
        "metadata": {
            "language": "de",
            "court_level": "cantonal",
            "preferred_units": "months"
        }
    }
    
    return test_backend_case("Real Estate - Hidden Defects", case_input, expected_category="Immobilienrecht", expected_docs=["SR-210", "SR-220"])

def test_traffic_case():
    """Test a traffic law case.""" 
    case_input = {
        "text": """I was driving on the highway near Zurich and was caught speeding at 135 km/h in a 100 km/h zone. 
        This is my first traffic violation. I received a fine of 800 CHF and my license might be suspended. 
        Can I appeal this fine or request a reduced penalty? What are my options?""",
        "metadata": {
            "language": "en",
            "court_level": "district", 
            "preferred_units": "weeks"
        }
    }
    
    return test_backend_case("Traffic - Speeding Violation", case_input, expected_category="Strafverkehrsrecht", expected_docs=["SR-741", "SR-742"])

def test_other_category_case():
    """Test a case that should be categorized as 'Andere'."""
    case_input = {
        "text": """I want to start a cryptocurrency business in Switzerland and need to understand the regulatory 
        requirements. What licenses do I need and what are the compliance obligations for crypto exchanges?""",
        "metadata": {
            "language": "en",
            "court_level": "federal",
            "preferred_units": "months"  
        }
    }
    
    return test_backend_case("Crypto Regulation", case_input, expected_category="Andere", expected_docs=None)

def test_contract_law_case():
    """Test a general contract law case."""
    case_input = {
        "text": """Ich habe einen Vertrag mit einem Bauunternehmen für Renovierungsarbeiten abgeschlossen. 
        Das Unternehmen hat die Arbeit nicht termingerecht fertiggestellt und die Qualität ist mangelhaft. 
        Ich habe bereits 50% der vereinbarten Summe (15.000 CHF) bezahlt. Kann ich den Vertrag kündigen 
        und Schadenersatz fordern?""",
        "metadata": {
            "language": "de", 
            "court_level": "cantonal",
            "preferred_units": "months"
        }
    }
    
    return test_backend_case("Contract Law - Construction", case_input, expected_category="Andere", expected_docs=["SR-220"])

def test_backend_case(case_name, case_input, expected_category, expected_docs):
    """Test a case against the backend and analyze the results."""
    print(f"\n🧪 TESTING: {case_name}")
    print("=" * 60)
    print(f"📝 Case Description: {case_input['text'][:100]}...")
    print(f"🎯 Expected Category: {expected_category}")
    print(f"📚 Expected Documents: {expected_docs or 'None (fallback expected)'}")
    print("-" * 40)
    
    try:
        # Make request to backend
        response = requests.post(
            "http://localhost:8000/api/agent_with_tools",
            json=case_input,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Analyze results
            actual_category = result.get('category', 'Unknown')
            likelihood = result.get('likelihood_win', 'N/A')
            time_est = result.get('estimated_time', 'N/A')
            cost_est = result.get('estimated_cost', 'N/A')
            source_docs = result.get('source_documents', [])
            
            print("✅ Backend Response Successful")
            print("📊 Results:")
            print(f"  Category: {actual_category}")
            print(f"  Likelihood: {likelihood}")
            print(f"  Time: {time_est}")
            print(f"  Cost: {cost_est}")
            
            # Check category accuracy
            category_correct = actual_category == expected_category
            if category_correct:
                print(f"✅ Category Classification: CORRECT ({actual_category})")
            else:
                print(f"❌ Category Classification: INCORRECT (expected {expected_category}, got {actual_category})")
            
            # Analyze source documents
            if source_docs:
                print(f"\n📚 Source Documents ({len(source_docs)} found):")
                relevant_count = 0
                
                for i, doc in enumerate(source_docs, 1):
                    doc_id = doc.get('id', '')
                    title = doc.get('title', 'Unknown')
                    snippet = doc.get('snippet', '')[:150] + "..."
                    
                    # Check document relevance
                    is_fallback = 'fallback' in doc_id
                    is_relevant = False
                    
                    if expected_docs:
                        is_relevant = any(expected_doc in title for expected_doc in expected_docs)
                        if is_relevant:
                            relevant_count += 1
                            print(f"  {i}. ✅ {title} (RELEVANT)")
                        elif is_fallback:
                            print(f"  {i}. 📚 {title} (FALLBACK - Legal Knowledge)")
                        else:
                            print(f"  {i}. ❌ {title} (NOT RELEVANT)")
                    else:
                        # For 'Andere' category, we expect either no docs or fallback
                        if is_fallback or not source_docs:
                            print(f"  {i}. ✅ {title} (EXPECTED - No specific analysis)")
                        else:
                            print(f"  {i}. ❓ {title} (UNEXPECTED)")
                    
                    print(f"     Content: {snippet}")
                
                # Document relevance assessment
                if expected_docs:
                    if relevant_count > 0:
                        print(f"📈 Document Relevance: {relevant_count}/{len(source_docs)} documents are relevant")
                        doc_success = True
                    elif any('fallback' in doc.get('id', '') for doc in source_docs):
                        print("📚 Document Relevance: Fallback knowledge provided (RAG system didn't find relevant docs)")
                        doc_success = True
                    else:
                        print("⚠️ Document Relevance: No relevant documents found")
                        doc_success = False
                else:
                    print("📊 Document Relevance: N/A (Andere category)")
                    doc_success = True
                    
            else:
                if expected_category == "Andere":
                    print(f"✅ No source documents (expected for {expected_category} category)")
                    doc_success = True
                else:
                    print("❌ No source documents found (unexpected)")
                    doc_success = False
            
            # Overall assessment
            overall_success = category_correct and doc_success
            if overall_success:
                print(f"\n🎉 OVERALL: SUCCESS - System working correctly for {case_name}")
            else:
                print(f"\n⚠️ OVERALL: ISSUES DETECTED for {case_name}")
                if not category_correct:
                    print("  - Category classification incorrect")
                if not doc_success:
                    print("  - Document retrieval issues")
            
            return overall_success
            
        else:
            print(f"❌ Backend Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend API")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Backend request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run comprehensive tests across different legal topics."""
    print("🧪 COMPREHENSIVE LEGAL TOPIC TESTING")
    print("=" * 70)
    print("Testing RAG retrieval and fallback systems across different legal areas...")
    
    test_results = {}
    
    # Test different legal areas
    test_cases = [
        ("Real Estate Law", test_real_estate_case),
        ("Traffic Law", test_traffic_case), 
        ("Other Category", test_other_category_case),
        ("Contract Law", test_contract_law_case)
    ]
    
    for test_name, test_func in test_cases:
        try:
            success = test_func()
            test_results[test_name] = success
        except Exception as e:
            print(f"❌ Test {test_name} failed with error: {e}")
            test_results[test_name] = False
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 40)
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, success in test_results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is working correctly across all legal areas!")
    elif passed >= total * 0.8:
        print("✅ MOSTLY SUCCESSFUL - Minor issues detected")
    else:
        print("⚠️ SIGNIFICANT ISSUES - Multiple areas need attention")

if __name__ == "__main__":
    main()