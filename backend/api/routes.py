"""
API routes for the legal assistance application.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.agent_with_tools.graph import create_legal_agent
from backend.agent_with_tools.schemas import CaseInput, AgentOutput
from core.config import settings


router = APIRouter()

@router.post("/agent_with_tools", response_model=AgentOutput)
async def run_agent(case_input: CaseInput) -> AgentOutput:
    """
    Run the legal analysis agent on a given case.
    """
    try:
        # Create the agent, passing the API key from settings
        agent = create_legal_agent(api_key=settings.APERTUS_API_KEY)

        # Prepare the initial state for the agent
        initial_state = {"case_input": case_input}

        # Invoke the agent
        final_state = agent.invoke(initial_state)

        # The agent's final output is stored in the 'result' field of the state
        analysis_result = final_state.get("result")

        if not analysis_result:
            raise HTTPException(status_code=500, detail="Agent failed to produce a result.")
        print(analysis_result)
        return analysis_result
    except Exception as e:
        # Catch potential errors during agent execution
        raise HTTPException(status_code=500, detail=f"An error occurred during agent execution: {str(e)}")


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