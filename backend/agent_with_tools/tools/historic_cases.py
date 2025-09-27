"""Historic cases tool - retrieves similar past legal cases for comparison."""

import sys
import os
from typing import List
from backend.agent_with_tools.schemas import Case

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
similar_cases_path = os.path.join(project_root, "experts", "tools", "similar_cases")
sys.path.insert(0, similar_cases_path)

try:
    from retriever import OptimizedChromaRetriever  # type: ignore
    
    # Initialize the retriever with the correct path
    _retriever = None
    
    def _get_retriever():
        global _retriever
        if _retriever is None:
            chroma_db_path = os.path.join(similar_cases_path, "chroma_db")
            _retriever = OptimizedChromaRetriever(
                chroma_db_path=chroma_db_path,
                collection_name="similar_vectors_gemini"
            )
        return _retriever
        
except ImportError as e:
    print(f"❌ Failed to import OptimizedChromaRetriever: {e}")
    _retriever = None


def historic_cases(query: str, top_k: int = 5) -> List[Case]:
    """
    Retrieve similar historic cases.
    
    Args:
        query: Search query for similar cases
        top_k: Maximum number of cases to return
        
    Returns:
        List of relevant historic cases
    """
    try:
        if _retriever is None:
            retriever = _get_retriever()
        else:
            retriever = _retriever
            
        if retriever is None:
            print("❌ Retriever not available, returning empty list")
            return []
        
        # Retrieve similar cases using the optimized retriever
        response = retriever.retrieve(
            query_text=query,
            n_results=top_k
        )
        
        # Convert RetrievalResults to Case objects
        cases = []
        for result in response.results:
            # Extract case information from metadata and document content
            metadata = result.metadata
            document_text = result.document
            
            # Try to parse structured information from the document content and metadata
            case_summary = document_text[:500] + "..." if len(document_text) > 500 else document_text
            
            # Extract relevant fields from metadata if available
            case_id = result.id
            
            # Extract court information - try different metadata fields and document parsing
            court = metadata.get("court", metadata.get("Court", ""))
            if not court or court == "Unknown Court":
                # Try to extract court from citation or document content
                citation_text = metadata.get("citation", metadata.get("Citation", metadata.get("docref", "")))
                if citation_text and isinstance(citation_text, str):
                    # Swiss court citations often start with numbers like "4A_", "8C_", etc.
                    if citation_text.startswith(("4A_", "4C_", "4P_")):
                        court = "Bundesgericht (Federal Supreme Court)"
                    elif citation_text.startswith(("8C_", "8G_")):
                        court = "Kantonsgericht (Cantonal Court)"
                    elif citation_text.startswith(("5A_", "5C_")):
                        court = "Zivilgericht (Civil Court)"
                    else:
                        court = "Swiss Court"
                else:
                    court = "Swiss Court"  # Better default than "Unknown Court"
            
            # Extract year - try different metadata fields and citation parsing
            year = metadata.get("year", metadata.get("Year", None))
            if not year:
                # Try to extract year from citation (format like "4A_401/2016")
                citation_text = metadata.get("citation", metadata.get("Citation", metadata.get("docref", "")))
                if citation_text and isinstance(citation_text, str):
                    import re
                    year_match = re.search(r'/(\d{4})$', citation_text)
                    if year_match:
                        year = int(year_match.group(1))
                    else:
                        # Try to find 4-digit year in the citation
                        year_match = re.search(r'\b(20\d{2})\b', citation_text)
                        if year_match:
                            year = int(year_match.group(1))
                        else:
                            year = 2020  # More reasonable default for recent cases
                else:
                    year = 2020
            
            # Ensure year is an integer
            if isinstance(year, str):
                try:
                    year = int(year)
                except (ValueError, TypeError):
                    year = 2020
            
            # Extract citation
            citation = metadata.get("citation", metadata.get("Citation", metadata.get("docref", "")))
            if not citation:
                # Generate a basic citation from the case ID if available
                if "email" in case_id:
                    citation = f"Legal Assistance Case {case_id}"
                else:
                    citation = None
            print(metadata.get("outcome", metadata.get("Outcome", "")))
            # Create Case object
            case = Case(
                id=case_id,
                court=str(court),
                year=year,
                summary=case_summary,
                outcome=metadata.get("outcome", metadata.get("Outcome", "")), #normalized_outcome,
                citation=str(citation) if citation else None
            )
            
            cases.append(case)
        
        return cases
        
    except Exception as e:
        print(f"❌ Historic cases retrieval failed: {e}")
        # Return empty list on error to allow the agent to continue
        return []