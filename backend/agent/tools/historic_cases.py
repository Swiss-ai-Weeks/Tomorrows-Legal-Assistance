"""Historic cases retrieval tool."""

from typing import List
from backend.agent.schemas import Case


def historic_cases(query: str, top_k: int = 5) -> List[Case]:
    """
    Retrieve similar historic cases.
    
    Args:
        query: Search query for similar cases
        top_k: Maximum number of cases to return
        
    Returns:
        List of relevant historic cases
        
    Note:
        This is a stub implementation. Real implementation will query
        the historic cases database.
    """
    raise NotImplementedError("Historic cases retrieval not yet implemented")