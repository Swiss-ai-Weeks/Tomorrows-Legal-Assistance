"""User interaction tool for missing information."""

from typing import List


def ask_user(prompt: str, missing_fields: List[str]) -> str:
    """
    Ask user for additional information when case details are insufficient.
    
    Args:
        prompt: Clear question to ask the user
        missing_fields: List of specific fields that are missing
        
    Returns:
        Additional details provided by user
        
    Note:
        This is a stub implementation. Real implementation will be
        a UI callback handled by the frontend/server.
    """
    raise NotImplementedError("User interaction not yet implemented")