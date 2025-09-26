"""Tool interfaces for the legal agent."""

from .rag_swiss_law import rag_swiss_law
from .historic_cases import historic_cases
from .estimate_time import estimate_time
from .estimate_cost import estimate_cost
from .categorize_case import categorize_case
from .ask_user import ask_user

__all__ = [
    "rag_swiss_law",
    "historic_cases", 
    "estimate_time",
    "estimate_cost",
    "categorize_case",
    "ask_user"
]