"""Time estimation tool."""

import re
from typing import Dict, Any
from backend.agent_with_tools.schemas import TimeEstimate
from backend.agent_with_tools.tools.estimator_constants import CATEGORY_MAPPING
from backend.agent_with_tools.tools.estimator_utils import extract_subcategory, get_case_text_from_inputs


def _parse_time_string(time_str: str, preferred_unit: str = "months") -> TimeEstimate:
    """Parse time string from estimator and convert to TimeEstimate."""
    if not time_str or time_str == "unknown":
        # Fallback estimate
        return TimeEstimate(value=6, unit="months")
    
    # Handle complex strings like "Paid: 30 days; Contested: 3–6 months+"
    if ";" in time_str:
        # Use contested version if available (more accurate for legal proceedings)
        parts = time_str.split(";")
        for part in parts:
            if "contested" in part.lower() or "months" in part.lower():
                time_str = part.strip()
                break
        else:
            time_str = parts[0].strip()  # Use first part as fallback
    
    # Remove prefixes like "Paid:" or "Contested:"
    time_str = re.sub(r'^[^:]*:', '', time_str).strip()
    
    # Extract numbers and units
    # Handle ranges like "3–6 months" or "1-6 months"
    range_match = re.search(r'(\d+)[–\-](\d+)\s*(months?|weeks?|days?)', time_str.lower())
    if range_match:
        min_val, max_val, unit = range_match.groups()
        # Use average of range
        avg_val = (int(min_val) + int(max_val)) / 2
        unit = unit.rstrip('s') + 's'  # Normalize to plural
        return TimeEstimate(value=int(avg_val), unit=unit)
    
    # Handle single values like "6 months+" or "3 Months"
    single_match = re.search(r'(\d+)\s*(months?|weeks?|days?)', time_str.lower())
    if single_match:
        val, unit = single_match.groups()
        unit = unit.rstrip('s') + 's'  # Normalize to plural
        return TimeEstimate(value=int(val), unit=unit)
    
    # Handle special cases
    if "0" in time_str:
        return TimeEstimate(value=0, unit="months")
    
    # Fallback
    return TimeEstimate(value=6, unit="months")


def estimate_time(case_facts: Dict[str, Any]) -> TimeEstimate:
    """
    Estimate time to completion for a legal case.
    
    Args:
        case_facts: Dictionary containing case facts including category,
                   complexity, court_level, etc.
        
    Returns:
        Time estimate with value and unit
    """
    # Import the actual estimator functions
    from experts.tools.estimators.estimator import estimate_time as estimator_time_func
    
    # Get category and map to English
    german_category = case_facts.get("category", "Andere")
    english_category = CATEGORY_MAPPING.get(german_category, "other")
    
    # For categories not supported by estimator, use fallbacks
    if english_category in ["real_estate_law", "other"]:
        complexity = case_facts.get("complexity", "medium")
        if german_category == "Immobilienrecht":
            base_months = {"low": 4, "medium": 8, "high": 15}[complexity] 
        else:  # Andere
            base_months = {"low": 3, "medium": 6, "high": 12}[complexity]
        return TimeEstimate(value=base_months, unit="months")
    
    # Extract subcategory from case text
    case_text = get_case_text_from_inputs(case_facts)
    subcategory = extract_subcategory(case_text, english_category)
    
    # Call the actual estimator function
    try:
        time_str = estimator_time_func(english_category, subcategory)
        
        # Parse the result and convert to TimeEstimate
        preferred_unit = case_facts.get("preferred_units", "months")
        return _parse_time_string(time_str, preferred_unit)
        
    except Exception as e:
        # Fallback in case of any errors
        complexity = case_facts.get("complexity", "medium")
        if english_category == "employment_law":
            base_months = {"low": 3, "medium": 6, "high": 12}[complexity]
        elif english_category == "traffic_criminal_law":
            base_months = {"low": 2, "medium": 4, "high": 8}[complexity]
        else:
            base_months = {"low": 3, "medium": 6, "high": 12}[complexity]
        
        return TimeEstimate(value=base_months, unit="months")