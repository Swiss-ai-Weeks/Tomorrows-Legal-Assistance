"""Swiss Legal Case Analysis Agent.

A LangGraph-based ReAct agent for analyzing Swiss legal cases.
Provides case classification, win likelihood estimation, and time/cost analysis.
"""

from .graph_with_tools import create_legal_agent, run_case_analysis
from .schemas import CaseInput, AgentOutput, CaseMetadata

__version__ = "0.1.0"

__all__ = [
    "create_legal_agent",
    "run_case_analysis", 
    "CaseInput",
    "AgentOutput",
    "CaseMetadata"
]