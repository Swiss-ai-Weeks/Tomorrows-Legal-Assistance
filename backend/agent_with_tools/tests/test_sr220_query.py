#!/usr/bin/env python3
"""Test specific queries to find the Code of Obligations."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add experts directory to path
project_root = os.path.dirname(os.path.abspath(__file__))
experts_path = os.path.join(project_root, "experts", "tools", "swiss_law_retriever")
sys.path.insert(0, experts_path)

def test_code_of_obligations_queries():
    """Test different ways to find the Code of Obligations (SR-220)."""
    try:
        from retriever import LegalRetriever
        
        retriever = LegalRetriever()
        
        # Test different queries to find SR-220
        test_queries = [
            "Code of Obligations",
            "Obligationenrecht", 
            "SR-220",
            "article 319 320 321 322 employment",
            "article 336 termination",
            "contract law obligations",
            "Swiss civil law contracts",
            "employment contract Swiss law",
            "termination notice Switzerland",
            "Arbeitsvertrag Schweiz",
            "Kündigung Kündigungsfrist",
        ]
        
        print("🔍 Testing Queries to Find Code of Obligations (SR-220)")
        print("=" * 60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 TEST {i}: '{query}'")
            print("-" * 30)
            
            results = retriever.retrieve(query, n_results=5)
            
            if results and results.get("documents") and results["documents"][0]:
                documents = results["documents"][0]
                metadatas = results.get("metadatas", [[{}] * len(documents)])[0]
                distances = results.get("distances", [[0] * len(documents)])[0]
                
                sr220_found = False
                
                for j, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    filename = metadata.get('filename', 'Unknown')
                    
                    if "SR-220" in filename:
                        sr220_found = True
                        print(f"  🎉 FOUND SR-220: {filename} (distance: {distance:.3f})")
                        print(f"     Content: {doc[:200]}...")
                    else:
                        print(f"  ❌ {filename} (distance: {distance:.3f})")
                
                if sr220_found:
                    print(f"  ✅ SUCCESS: Query '{query}' found Code of Obligations!")
                else:
                    print(f"  ⚠️  Query '{query}' did not find Code of Obligations")
            else:
                print(f"  ❌ No results for '{query}'")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def test_employment_content_in_sr220():
    """Check if SR-220 actually contains employment-related content."""
    try:
        from retriever import LegalRetriever
        
        retriever = LegalRetriever()
        
        print("\n🔎 Checking Content of SR-220 for Employment Terms")
        print("=" * 60)
        
        # Search specifically for SR-220 document
        results = retriever.retrieve("SR-220", n_results=10)
        
        if results and results.get("documents") and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results.get("metadatas", [[{}] * len(documents)])[0]
            
            sr220_chunks = []
            
            for doc, metadata in zip(documents, metadatas):
                filename = metadata.get('filename', '')
                if "SR-220" in filename:
                    sr220_chunks.append(doc)
            
            if sr220_chunks:
                print(f"📄 Found {len(sr220_chunks)} chunks from SR-220")
                
                employment_terms = [
                    "employment", "arbeitsvertrag", "termination", "kündigung", 
                    "article 319", "article 320", "article 321", "article 336",
                    "employee", "employer", "arbeitnehmer", "arbeitgeber",
                    "notice period", "kündigungsfrist", "salary", "lohn"
                ]
                
                for i, chunk in enumerate(sr220_chunks[:3]):  # Check first 3 chunks
                    print(f"\n📋 Chunk {i+1}:")
                    print(f"Content: {chunk[:300]}...")
                    
                    # Check for employment terms
                    found_terms = [term for term in employment_terms if term.lower() in chunk.lower()]
                    if found_terms:
                        print(f"✅ Employment terms found: {', '.join(found_terms)}")
                    else:
                        print("❌ No employment terms found in this chunk")
            else:
                print("❌ No SR-220 chunks found in database")
        else:
            print("❌ Could not retrieve SR-220 document")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_code_of_obligations_queries()
    test_employment_content_in_sr220()