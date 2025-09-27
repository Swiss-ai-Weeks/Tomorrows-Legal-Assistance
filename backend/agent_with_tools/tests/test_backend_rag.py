#!/usr/bin/env python3
"""Quick test of the backend API changes."""

import requests

def test_backend_with_employment_case():
    """Test the backend with an employment law case."""
    
    # Employment case about termination
    case_input = {
        "text": "I was terminated from my job without proper notice after filing a harassment complaint",
        "metadata": {
            "language": "en",
            "court_level": "district",
            "preferred_units": "months"
        }
    }
    
    try:
        print("🧪 Testing backend with employment case...")
        print(f"📝 Case: {case_input['text']}")
        
        # Make request to backend
        response = requests.post(
            "http://localhost:8000/api/agent_with_tools",
            json=case_input,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend responded successfully!")
            print(f"📊 Category: {result.get('category', 'N/A')}")
            print(f"🎯 Likelihood: {result.get('likelihood_win', 'N/A')}")
            print(f"📄 Source Documents: {len(result.get('source_documents', []))}")
            
            # Print source document titles
            if result.get('source_documents'):
                print("\n📚 Retrieved Documents:")
                for doc in result['source_documents']:
                    title = doc.get('title', 'Unknown')
                    print(f"  - {title}")
                    # Check if employment-related
                    if "SR-220" in title:
                        print("    ✅ Employment-related (Code of Obligations)")
                    elif any(pattern in title for pattern in ["SR-232", "SR-451", "SR-814"]):
                        print("    ❌ Unrelated document")
                    else:
                        print("    ❓ Unknown relevance")
            else:
                print("❌ No source documents returned")
                
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backend_with_employment_case()