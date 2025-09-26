"""Graph nodes for the legal analysis agent."""

from .ingest import ingest_node
from .categorize import categorize_node
from .win_likelihood import win_likelihood_node
from .time_and_cost import time_and_cost_node
from .aggregate import aggregate_node

__all__ = [
    "ingest_node",
    "categorize_node", 
    "win_likelihood_node",
    "time_and_cost_node",
    "aggregate_node"
]