#!/usr/bin/env python3
"""Test script to check if the RAG system retrieves appropriate documents."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend tools to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_rag_tool_directly():
    """Test the RAG tool directly to see what it retrieves."""
    try:
        from backend.agent_with_tools.tools.rag_swiss_law import rag_swiss_law
        
        print("🔍 Testing RAG Tool Directly")
        print("=" * 50)
        
        # Test cases for different legal areas
        test_cases = [
            {
                "name": "Employment Termination",
                "query": "employment termination dismissal notice period article 336 337 338 339 fristlose kündigung Arbeitsvertrag",
                "expected_docs": ["SR-220"],
                "category": "Arbeitsrecht"
            },
            {
                "name": "Employment Harassment", 
                "query": "employment protection harassment discrimination article 328 328a Fürsorgepflicht",
                "expected_docs": ["SR-220"],
                "category": "Arbeitsrecht"
            },
            {
                "name": "Employment Wage",
                "query": "employment wage salary payment article 322 323 324 Lohn Arbeitslohn",
                "expected_docs": ["SR-220"],
                "category": "Arbeitsrecht"
            },
            {
                "name": "Generic Employment",
                "query": "employment contract work Arbeitsvertrag article 319 320 321 employee rights obligations",
                "expected_docs": ["SR-220"],
                "category": "Arbeitsrecht"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 TEST {i}: {test_case['name']}")
            print(f"📝 Query: {test_case['query']}")
            print(f"🎯 Expected documents containing: {', '.join(test_case['expected_docs'])}")
            print("-" * 40)
            
            # Call the RAG tool
            docs = rag_swiss_law(test_case['query'], top_k=3)
            
            if docs:
                print(f"✅ Retrieved {len(docs)} documents:")
                relevant_found = False
                
                for j, doc in enumerate(docs, 1):
                    title = doc.title
                    snippet = doc.snippet[:150] + "..." if len(doc.snippet) > 150 else doc.snippet
                    
                    # Check if document is relevant
                    is_relevant = any(expected in title for expected in test_case['expected_docs'])
                    if is_relevant:
                        relevant_found = True
                        print(f"  {j}. ✅ {title} (RELEVANT)")
                    else:
                        print(f"  {j}. ❌ {title} (NOT RELEVANT)")
                    
                    print(f"     Content: {snippet}")
                
                if relevant_found:
                    print(f"🎉 SUCCESS: Found relevant documents for {test_case['category']}")
                else:
                    print(f"⚠️  WARNING: No relevant documents found for {test_case['category']}")
                    
            else:
                print("❌ No documents retrieved")
            
            print()
        
    except ImportError as e:
        print(f"❌ Could not import RAG tool: {e}")
        print("This might be due to missing dependencies like chromadb")
        return False
    except Exception as e:
        print(f"❌ Error testing RAG tool: {e}")
        return False
    
    return True

def test_backend_api_retrieval():
    """Test the backend API to see what documents it retrieves."""
    try:
        import requests
        
        print("\n🌐 Testing Backend API Retrieval")
        print("=" * 50)
        
        # Employment test case (German, like the user's example)
        employment_case = {
            "text": """Ich bin 45 Jahre alt und arbeite seit 8 Jahren als Projektmanager bei einer Schweizer IT-Firma in Zürich. 
            Letzte Woche wurde mir vom Geschäftsführer mitgeteilt, dass mein Arbeitsvertrag mit sofortiger Wirkung gekündigt wird, 
            angeblich wegen 'mangelnder Leistung'. Ich erhielt keine schriftliche Kündigung und keine Kündigungsfrist wurde eingehalten. 
            Mein Arbeitsvertrag sieht eine 3-monatige Kündigungsfrist vor. Kann ich gegen diese fristlose Kündigung rechtlich vorgehen?""",
            "metadata": {
                "language": "de",
                "court_level": "cantonal",
                "preferred_units": "months"
            }
        }
        
        print("📝 Testing with employment termination case (German)...")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/agent_with_tools",
                json=employment_case,
                timeout=60  # Longer timeout for full analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Backend API responded successfully!")
                
                print("\n📊 Analysis Results:")
                print(f"  Category: {result.get('category', 'N/A')}")
                print(f"  Likelihood: {result.get('likelihood_win', 'N/A')}")
                print(f"  Time: {result.get('estimated_time', 'N/A')}")
                print(f"  Cost: {result.get('estimated_cost', 'N/A')}")
                
                # Check source documents
                source_docs = result.get('source_documents', [])
                if source_docs:
                    print(f"\n📚 Source Documents ({len(source_docs)} found):")
                    employment_related = 0
                    
                    for i, doc in enumerate(source_docs, 1):
                        title = doc.get('title', 'Unknown')
                        snippet = doc.get('snippet', 'No content')[:200] + "..."
                        
                        # Check relevance for employment law
                        is_employment = any(pattern in title for pattern in ['SR-220', 'SR-221'])
                        if is_employment:
                            employment_related += 1
                            print(f"  {i}. ✅ {title} (EMPLOYMENT LAW - Code of Obligations)")
                        else:
                            print(f"  {i}. ❌ {title} (NOT EMPLOYMENT RELATED)")
                        
                        print(f"     Content: {snippet}")
                    
                    print(f"\n📈 Relevance Score: {employment_related}/{len(source_docs)} documents are employment-related")
                    
                    if employment_related == 0:
                        print("⚠️  WARNING: No employment-related documents retrieved!")
                        print("   Expected: SR-220 (Code of Obligations) which contains employment law")
                    elif employment_related < len(source_docs):
                        print("⚠️  PARTIAL SUCCESS: Some irrelevant documents mixed in")
                    else:
                        print("🎉 PERFECT: All documents are employment-related!")
                        
                else:
                    print("❌ No source documents returned by backend")
                    
            else:
                print(f"❌ Backend API error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to backend API")
            print("   Make sure backend is running: uvicorn backend.main:app --reload")
            return False
        except requests.exceptions.Timeout:
            print("⏰ Backend request timed out (analysis takes time)")
            return False
            
    except ImportError:
        print("❌ Requests library not available")
        return False
    except Exception as e:
        print(f"❌ Error testing backend API: {e}")
        return False
    
    return True

def check_available_laws():
    """Check what law documents are actually available."""
    print("\n📚 Checking Available Swiss Law Documents")
    print("=" * 50)
    
    swiss_law_dir = os.path.join(os.path.dirname(__file__), "data", "swiss_law")
    
    if not os.path.exists(swiss_law_dir):
        print(f"❌ Swiss law directory not found: {swiss_law_dir}")
        return
    
    # Look for key legal documents
    key_laws = {
        "SR-220": "Code of Obligations (includes employment law Articles 319-362)",
        "SR-221": "Code of Obligations - Additional provisions", 
        "SR-210": "Civil Code",
        "SR-741": "Road Traffic Act",
        "SR-742": "Road Traffic Ordinance"
    }
    
    available_files = os.listdir(swiss_law_dir)
    
    print("🔍 Key Legal Documents Status:")
    for law_code, description in key_laws.items():
        matching_files = [f for f in available_files if f.startswith(law_code)]
        if matching_files:
            print(f"  ✅ {law_code}: {matching_files[0]} - {description}")
        else:
            print(f"  ❌ {law_code}: NOT FOUND - {description}")
    
    print(f"\n📊 Total documents available: {len(available_files)}")

def main():
    """Run all RAG retrieval tests."""
    print("🧪 RAG Retrieval Testing Suite")
    print("=" * 60)
    
    # Check available documents first
    check_available_laws()
    
    # Test RAG tool directly
    rag_success = test_rag_tool_directly()
    
    # Test backend API
    api_success = test_backend_api_retrieval()
    
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"RAG Tool Direct Test: {'✅ PASSED' if rag_success else '❌ FAILED'}")
    print(f"Backend API Test: {'✅ PASSED' if api_success else '❌ FAILED'}")
    
    if not rag_success and not api_success:
        print("\n💡 RECOMMENDATIONS:")
        print("1. Check if chromadb and dependencies are installed")
        print("2. Verify GOOGLE_API_KEY is set for embeddings")
        print("3. Ensure backend server is running")
        print("4. Check if vector database is properly populated")

if __name__ == "__main__":
    main()