"""Time estimation tool."""

import re
from typing import Dict, Any
from backend.agent_with_tools.schemas import TimeEstimate


# Category mapping from German agent categories to English estimator categories  
CATEGORY_MAPPING = {
    "Arbeitsrecht": "employment_law",
    "Strafverkehrsrecht": "traffic_criminal_law",
    "Immobilienrecht": "real_estate_law",  # Not in estimator yet, will use fallback
    "Andere": "other"  # Not in estimator yet, will use fallback
}

# Employment law subcategories mapping (inferred from case facts or complexity)
EMPLOYMENT_SUBCATEGORIES = {
    "termination": "termination_poor_performance",
    "dismissal": "fristlose_kuendigung", 
    "salary": "lohn_ausstehend",
    "illness": "kuendigung_waehrend_krankheit_unfall",
    "workload": "increase_in_workload",
    "default": "termination_poor_performance"
}

# Traffic law subcategories mapping
TRAFFIC_SUBCATEGORIES = {
    "speeding": "moderate_speeding",
    "alcohol": "driving_under_influence_alcohol_license_withdrawal",
    "parking": "parking_lot_accident_chf_2500_no_witnesses", 
    "fine": "parking_fine_expired_few_minutes",
    "penalty": "alcohol_06_penalty_order",
    "default": "moderate_speeding"
}


def _extract_subcategory(case_text: str, category: str) -> str:
    """Extract subcategory from case text based on keywords."""
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
    case_text = case_facts.get("case_text", "")
    if not case_text and "text" in case_facts:
        case_text = case_facts["text"]
    subcategory = _extract_subcategory(case_text, english_category)
    
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