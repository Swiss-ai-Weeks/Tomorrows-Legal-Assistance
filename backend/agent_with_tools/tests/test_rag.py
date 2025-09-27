#!/usr/bin/env python3
"""Test script to check RAG retrieval for employment law."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add experts directory to path
project_root = os.path.dirname(os.path.abspath(__file__))
experts_path = os.path.join(project_root, "experts", "tools", "swiss_law_retriever")
sys.path.insert(0, experts_path)

def test_rag_queries():
    """Test different RAG queries for employment law."""
    try:
        from retriever import LegalRetriever
        
        retriever = LegalRetriever()
        
        # Test queries
        queries = [
            "employment termination dismissal notice period article 336 337 338 339 fristlose kündigung Arbeitsvertrag",
            "Swiss employment law termination Code of Obligations",
            "article 336 termination dismissal",
            "Arbeitsrecht Kündigung",
            "Code of Obligations employment contract"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'='*60}")
            print(f"QUERY {i}: {query}")
            print('='*60)
            
            results = retriever.retrieve(query, n_results=3)
            
            if results and results.get("documents") and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results.get("metadatas", [[{}] * len(documents)])[0]
                distances = results.get("distances", [[0] * len(documents)])[0]
                
                for j, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    filename = metadata.get('filename', 'Unknown')
                    print(f"\n📄 Result {j+1}: {filename} (distance: {distance:.3f})")
                    print(f"Content preview: {doc[:300]}...")
            else:
                print("❌ No results found")
                
    except ImportError as e:
        print(f"❌ Could not import retriever: {e}")
    except Exception as e:
        print(f"❌ Error during retrieval: {e}")

if __name__ == "__main__":
    print("🔍 Testing RAG Retrieval for Employment Law")
    test_rag_queries()