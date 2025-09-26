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
        from retriever import LegalRetriever
        
        # Initialize the retriever
        retriever = LegalRetriever()
        
        # Get search results
        search_results = retriever.retrieve(query, n_results=top_k)
        
        if not search_results or not search_results.get("documents") or not search_results["documents"][0]:
            return []
        
        # Convert to Doc objects
        docs = []
        documents = search_results["documents"][0]
        metadatas = search_results.get("metadatas", [[{}] * len(documents)])[0]
        
        for i, doc_text in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {}
            
            docs.append(Doc(
                id=metadata.get('id', f'doc_{i}'),
                title=metadata.get('filename', f'Document {i+1}'),
                snippet=doc_text[:500] + "..." if len(doc_text) > 500 else doc_text,
                citation=metadata.get('citation', metadata.get('filename', 'Unknown'))
            ))
        
        return docs
        
    except ImportError as e:
        print(f"❌ Failed to import LegalRetriever: {e}")
        # Fallback to stub behavior
        return []
        
    except Exception as e:
        print(f"❌ RAG retrieval failed: {e}")
        # Return empty list on error
        return []