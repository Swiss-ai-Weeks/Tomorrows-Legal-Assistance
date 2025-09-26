"""Simple test for RAG Swiss law retrieval only."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables from .env
def load_env_vars():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
        print(f"✅ Environment variables loaded from {env_path}")
    else:
        print(f"⚠️  .env file not found at {env_path}")

def test_simple_rag():
    """Test just the RAG Swiss law retrieval."""
    print("🧪 Testing RAG Swiss Law Integration (Simple)")
    print("=" * 40)
    
    try:
        from backend.agent_with_tools.tools.rag_swiss_law import rag_swiss_law
        
        # Test query
        query = "employment termination rights Switzerland"
        print(f"📝 Test Query: {query}")
        print("🔍 Retrieving Swiss law documents...")
        
        # Get results
        docs = rag_swiss_law(query, top_k=3)
        
        if docs and len(docs) > 0:
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
            print("Docs result:", docs)
            return False
            
    except Exception as e:
        print(f"❌ RAG integration failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure ChromaDB is set up with Swiss law documents")
        print("2. Check GOOGLE_API_KEY environment variable is set")
        print("3. Verify ChromaDB path exists: ./chroma_db")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    load_env_vars()
    test_simple_rag()