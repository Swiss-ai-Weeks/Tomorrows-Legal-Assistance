"""
API routes for the legal assistance application.
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/")
async def api_root() -> Dict[str, str]:
    """API root endpoint."""
    return {"message": "Legal Assistance API", "status": "running"}

@router.get("/legal-advice")
async def get_legal_advice() -> Dict[str, Any]:
    """
    Minimal endpoint for legal advice.
    In a real implementation, this would process legal queries.
    """
    return {
        "advice": "This is a placeholder for legal advice functionality",
        "disclaimer": "This is not actual legal advice. Consult a qualified attorney.",
        "categories": ["contract", "employment", "property", "family"]
    }

@router.post("/legal-advice")
async def create_legal_query(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal endpoint to submit a legal query.
    In a real implementation, this would process the query and return advice.
    """
    return {
        "status": "received",
        "query_id": "placeholder-id-123",
        "message": "Your legal query has been received and will be processed",
        "submitted_query": query
    }