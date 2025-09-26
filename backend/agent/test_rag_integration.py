#!/usr/bin/env python3
"""Test the integrated RAG Swiss law retriever."""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_rag_integration():
    """Test that the RAG Swiss law tool works with the real retriever."""
    
    print("🧪 Testing RAG Swiss Law Integration")
    print("=" * 40)
    
    try:
        from backend.agent.tools.rag_swiss_law import rag_swiss_law
        
        # Test query
        query = "employment termination rights Switzerland"
        print(f"📝 Test Query: {query}")
        print("🔍 Retrieving Swiss law documents...")
        
        # Get results
        docs = rag_swiss_law(query, top_k=3)
        
        if docs:
            print(f"✅ Retrieved {len(docs)} documents:")
            for i, doc in enumerate(docs, 1):
                print(f"\n📄 Document {i}:")
                print(f"   ID: {doc.id}")
                print(f"   Title: {doc.title}")
                print(f"   Citation: {doc.citation}")
                print(f"   Snippet: {doc.snippet[:100]}...")
            
            print(f"\n🎉 RAG integration successful!")
            return True
        else:
            print("⚠️  No documents retrieved - check ChromaDB connection")
            return False
            
    except Exception as e:
        print(f"❌ RAG integration failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure ChromaDB is set up with Swiss law documents")
        print("2. Check GOOGLE_API_KEY environment variable is set")
        print("3. Verify ChromaDB path exists: ./chroma_db")
        return False


def test_full_agent_with_rag():
    """Test the complete agent with real RAG integration."""
    
    print("\n🤖 Testing Full Agent with RAG")
    print("=" * 40)
    
    try:
        from backend.agent.graph_with_tools import create_legal_agent
        from backend.agent.schemas import CaseInput
        
        # Load API key
        api_key = os.getenv("APERTUS_API_KEY")
        if not api_key:
            # Try loading from .env
            env_path = os.path.join(project_root, ".env")
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('APERTUS_API_KEY='):
                            api_key = line.split('=', 1)[1].strip().strip('"\'')
                            break
        
        if not api_key:
            print("❌ No APERTUS_API_KEY found")
            return False
            
        print(f"🔑 Using API key: {api_key[:8]}...")
        
        # Create agent
        agent = create_legal_agent(api_key=api_key)
        
        # Test case
        case = CaseInput(
            text="My employer terminated my employment contract without proper notice period"
        )
        
        print(f"📝 Test Case: {case.text}")
        print("🔍 Running full analysis with RAG...")
        
        # Run analysis
        result = agent.invoke({"case_input": case})
        
        if result.get("result"):
            output = result["result"]
            print(f"\n✅ Analysis Complete:")
            print(f"   Category: {output.category}")
            print(f"   Win Likelihood: {output.likelihood_win}")
            print(f"   Time Estimate: {output.estimated_time}")
            print(f"   Cost Estimate: {output.estimated_cost}")
            
            return True
        else:
            print("❌ No result generated")
            return False
            
    except Exception as e:
        print(f"❌ Full agent test failed: {e}")
        return False


if __name__ == "__main__":
    print("🇨🇭 Swiss Legal Agent - RAG Integration Test")
    print("=" * 50)
    
    # Test RAG integration
    rag_success = test_rag_integration()
    
    # Test full agent (optional, requires API key)
    if rag_success:
        full_success = test_full_agent_with_rag()
    else:
        full_success = False
        
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   RAG Integration: {'✅ PASSED' if rag_success else '❌ FAILED'}")
    print(f"   Full Agent Test: {'✅ PASSED' if full_success else '❌ FAILED'}")
    
    if rag_success and full_success:
        print("\n🎉 All tests passed! RAG integration is working.")
    elif rag_success:
        print("\n⚠️  RAG works but full agent needs setup (API key, etc.)")
    else:
        print("\n❌ RAG integration needs setup (ChromaDB, GOOGLE_API_KEY)")
        
    print("\n💡 Setup Requirements:")
    print("   • ChromaDB with Swiss law documents")
    print("   • GOOGLE_API_KEY for Gemini embeddings")
    print("   • APERTUS_API_KEY for LLM reasoning")