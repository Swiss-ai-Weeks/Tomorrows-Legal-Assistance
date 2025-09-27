"""Pydantic models for I/O contracts in the legal agent."""

from typing import Literal, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class CaseMetadata(BaseModel):
    """Optional metadata for case input."""
    language: Optional[Literal["de", "fr", "it", "en"]] = None
    preferred_units: Optional[Literal["days", "weeks", "months"]] = None
    court_level: Optional[str] = None
    judges_count: Optional[int] = None


class CaseInput(BaseModel):
    """Input schema for case analysis."""
    text: str = Field(..., description="User-provided case description")
    metadata: Optional[CaseMetadata] = None


class CategoryResult(BaseModel):
    """Result of case categorization."""
    category: Literal["Arbeitsrecht", "Immobilienrecht", "Strafverkehrsrecht", "Andere"]
    confidence: float = Field(..., ge=0.0, le=1.0)


class Doc(BaseModel):
    """Swiss law document from RAG."""
    id: str
    title: str
    snippet: str
    citation: Optional[str] = None


class Case(BaseModel):
    """Historic case result."""
    id: str
    court: str
    year: int
    summary: str
    outcome: Literal["win", "loss", "settled"]
    citation: Optional[str] = None


class TimeEstimate(BaseModel):
    """Time estimation result."""
    value: int = Field(..., gt=0)
    unit: Literal["days", "weeks", "months"]


class CostBreakdown(BaseModel):
    """Cost estimation with breakdown."""
    total_chf: float = Field(..., ge=0)
    breakdown: Optional[Dict[str, float]] = None


class AgentOutput(BaseModel):
    """Final output schema for the agent."""
    category: str = Field(..., description="Legal case category")
    likelihood_win: Optional[str] = Field(None, description="Likelihood of winning as percentage string (e.g., '60%')")
    estimated_time: Optional[str] = Field(None, description="Time estimate (ISO 8601 duration or human string)")
    estimated_cost: Optional[str] = Field(None, description="Cost estimate as string (e.g., '3500 CHF')")
    explanation: Optional[str] = Field(None, description="Reasoning and explanation for the analysis")
    source_documents: Optional[list[Doc]] = Field(None, description="Source documents used in the analysis")


class AgentState(BaseModel):
    """Internal state managed by the LangGraph agent."""
    # Input
    case_input: CaseInput
    
    # Intermediate results
    category: Optional[CategoryResult] = None
    likelihood_win: Optional[int] = None
    time_estimate: Optional[TimeEstimate] = None
    cost_estimate: Optional[Union[float, CostBreakdown]] = None
    
    # Working memory
    case_facts: Optional[Dict[str, Any]] = None
    tool_call_count: int = 0
    explanation_parts: Optional[list[str]] = None  # Collect explanation parts during analysis
    source_documents: Optional[list[Doc]] = None  # Collect source documents used during analysis
    
    # Final output
    result: Optional[AgentOutput] = None
    
    class Config:
        arbitrary_types_allowed = True


# Tool input/output schemas
class CaseFacts(BaseModel):
    """Facts about a case for time estimation."""
    category: str
    complexity: Optional[Literal["low", "medium", "high"]] = None
    court_level: Optional[str] = None
    jurisdiction: str = "CH"
    prior_motions: Optional[int] = None
    appeal_expected: Optional[bool] = None
    # Additional facts can be added as needed


class CostInputs(BaseModel):
    """Inputs for cost estimation."""
    time_estimate: TimeEstimate
    judges_count: Optional[int] = None
    hourly_rates: Optional[Dict[str, float]] = None  # e.g., {"lawyer": 400, "paralegal": 150}
    filing_fees: Optional[float] = None
    expert_witness_fees: Optional[float] = None
    vat_rate: Optional[float] = 0.077  # Swiss VAT rate