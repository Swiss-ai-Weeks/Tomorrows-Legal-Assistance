"""Shared utilities for estimator tools.

This module contains common utility functions used by both estimate_time.py and 
estimate_cost.py to avoid code duplication. It includes functions for extracting
subcategories from case text, normalizing time estimates, and handling input formats.
"""

from typing import Union, Dict, Any
from backend.agent_with_tools.schemas import TimeEstimate


def extract_subcategory(case_text: str, category: str) -> str:
    """
    Extract subcategory from case text based on keywords.
    
    Args:
        case_text: The case description text
        category: The main legal category (employment_law, traffic_criminal_law, etc.)
        
    Returns:
        Subcategory string matching the estimator function expectations
    """
    if not case_text:
        return "default"
    
    case_lower = case_text.lower()
    
    if category == "employment_law":
        if any(word in case_lower for word in ["salary", "wage", "pay", "lohn"]):
            return "lohn_ausstehend"
        elif any(word in case_lower for word in ["illness", "sick", "krankheit", "unfall"]):
            return "kuendigung_waehrend_krankheit_unfall"
        elif any(word in case_lower for word in ["dismissal", "fired", "fristlos"]):
            return "fristlose_kuendigung"
        elif any(word in case_lower for word in ["workload", "overtime", "work hours"]):
            return "increase_in_workload" 
        else:
            return "termination_poor_performance"
    
    elif category == "traffic_criminal_law":
        if any(word in case_lower for word in ["alcohol", "drunk", "dui"]):
            return "driving_under_influence_alcohol_license_withdrawal"
        elif any(word in case_lower for word in ["parking", "parked"]):
            if "accident" in case_lower:
                return "parking_lot_accident_chf_2500_no_witnesses"
            else:
                return "parking_fine_expired_few_minutes"
        elif any(word in case_lower for word in ["speeding", "speed", "fast"]):
            return "moderate_speeding"
        elif any(word in case_lower for word in ["penalty", "fine"]):
            return "alcohol_06_penalty_order"
        else:
            return "moderate_speeding"
    
    return "default"


def normalize_time_estimate(time_estimate: Union[TimeEstimate, Dict[str, Any]]) -> tuple[int, str]:
    """
    Normalize time estimate input to a consistent format.
    
    Args:
        time_estimate: Either a TimeEstimate object or a dictionary with value/unit keys
        
    Returns:
        Tuple of (value, unit) as (int, str)
    """
    if isinstance(time_estimate, TimeEstimate):
        return time_estimate.value, time_estimate.unit
    elif isinstance(time_estimate, dict):
        return time_estimate.get("value", 6), time_estimate.get("unit", "months")
    else:
        # Fallback for unexpected input types
        return 6, "months"


def get_case_text_from_inputs(inputs: Dict[str, Any]) -> str:
    """
    Extract case text from various possible input formats.
    
    Args:
        inputs: Dictionary that might contain case text under different keys
        
    Returns:
        Case text string, or empty string if not found
    """
    # Try different possible keys for case text
    for key in ["case_text", "text", "description"]:
        if key in inputs and inputs[key]:
            return str(inputs[key])
    
    return ""