"""RAG tool for Swiss law retrieval."""

import sys
import os
from typing import List
from backend.agent_with_tools.schemas import Doc

# Ensure environment variables are set from settings
try:
    from core.config import settings
    # Set environment variables if not already set
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    if not os.environ.get("APERTUS_API_KEY"):
        os.environ["APERTUS_API_KEY"] = settings.APERTUS_API_KEY
except ImportError:
    # Fallback if settings not available
    pass

# Add experts directory to path to import the retriever
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
experts_path = os.path.join(project_root, "experts", "tools", "swiss_law_retriever")
sys.path.insert(0, experts_path)

from retriever_v2 import LegalRetriever

# Initialize the retriever
retriever = LegalRetriever()

def rag_swiss_law(query: str, top_k: int = 5) -> List[Doc]:
    """
    Retrieve relevant Swiss law documents using RAG.
    
    Args:
        query: Search query for relevant law documents
        top_k: Maximum number of documents to return
        
    Returns:
        List of relevant Swiss law documents
    """
    try:
        
        # Get search results with improved query
        search_results = retriever.retrieve(query, n_results=top_k)
        
        if not search_results or not search_results.get("documents") or not search_results["documents"][0]:
            return []
        
        # Convert to Doc objects with relevance filtering
        docs = []
        documents = search_results["documents"][0]
        metadatas = search_results.get("metadatas", [[{}] * len(documents)])[0]
        
        # Define relevant document patterns for different legal areas
        employment_docs = ["SR-220", "SR-221"]  # Code of Obligations
        real_estate_docs = ["SR-210", "SR-211"]  # Civil Code
        traffic_docs = ["SR-741", "SR-742"]  # Road Traffic Act
        
        # Prioritize relevant documents based on query content
        query_lower = query.lower()
        relevant_patterns = []
        if any(term in query_lower for term in ["employment", "arbeitsrecht", "termination", "dismissal", "wage", "salary", "arbeitsvertrag"]):
            relevant_patterns.extend(employment_docs)
        elif any(term in query_lower for term in ["property", "real estate", "immobilien", "building", "contract"]):
            relevant_patterns.extend(real_estate_docs)
        elif any(term in query_lower for term in ["traffic", "driving", "license", "verkehr", "fahren"]):
            relevant_patterns.extend(traffic_docs)
        
        # First, add documents that match relevant patterns
        for i, doc_text in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {}
            filename = metadata.get('filename', f'Document {i+1}')
            
            # Check if document matches relevant patterns
            is_relevant = not relevant_patterns or any(pattern in filename for pattern in relevant_patterns)
            
            doc = Doc(
                id=metadata.get('id', f'doc_{i}'),
                title=filename,
                snippet=doc_text[:500] + "..." if len(doc_text) > 500 else doc_text,
                citation=metadata.get('citation', filename)
            )
            
            # Add relevant documents first, others if we have space
            if is_relevant or len(docs) < top_k:
                docs.append(doc)
                
        # Limit to requested number
        docs = docs[:top_k]
        
        return docs
        
    except ImportError as e:
        print(f"❌ Failed to import LegalRetriever: {e}")
        # Fallback to stub behavior
        return []
        
    except Exception as e:
        print(f"❌ RAG retrieval failed: {e}")
        # Return empty list on error
        return []