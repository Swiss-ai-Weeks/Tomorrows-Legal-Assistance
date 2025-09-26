"""Cost estimation tool."""

import re
from typing import Dict, Any, Union
from backend.agent_with_tools.schemas import CostBreakdown, TimeEstimate


# Category mapping from German agent categories to English estimator categories  
CATEGORY_MAPPING = {
    "Arbeitsrecht": "employment_law",
    "Strafverkehrsrecht": "traffic_criminal_law",
    "Immobilienrecht": "real_estate_law",  # Not in estimator yet, will use fallback
    "Andere": "other"  # Not in estimator yet, will use fallback
}

# Employment law subcategories mapping (same as in estimate_time.py)
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


def _parse_cost_string(cost_str: str, time_estimate: TimeEstimate = None) -> CostBreakdown:
    """Parse cost string from estimator and convert to CostBreakdown."""
    if not cost_str or cost_str == "unknown":
        # Fallback cost estimate
        return CostBreakdown(total_chf=5000.0, breakdown={"estimated_total": 5000.0})
    
    # Handle simple numeric values (employment law cases)
    if cost_str.isdigit():
        total = float(cost_str)
        return CostBreakdown(
            total_chf=total,
            breakdown={"estimated_total": total}
        )
    
    # Handle complex cost breakdowns (traffic law cases)
    breakdown = {}
    total = 0.0
    
    # Extract different cost components using regex
    patterns = {
        'fine': r'Fine:\s*CHF\s*([\d,\-–]+)',
        'lawyer': r'Lawyer:\s*CHF\s*([\d,\-–]+)',
        'court': r'Court:\s*CHF\s*([\d,\-–]+)',
        'admin_fees': r'Admin fees:\s*CHF\s*([\d,\-–]+)',
        'road_traffic_fees': r'Road Traffic fees:\s*CHF\s*([\d,\-–]+)',
        'assessment': r'Assessment:\s*CHF\s*([\d,\-–]+)',
        'deductible': r'Deductible\s*CHF\s*([\d,\-–]+)',
    }
    
    for category, pattern in patterns.items():
        matches = re.findall(pattern, cost_str, re.IGNORECASE)
        if matches:
            cost_value = matches[0]
            # Handle ranges like "1,000–5,000" or "500–10,000"
            if '–' in cost_value or '-' in cost_value:
                range_parts = re.split('[–\\-]', cost_value)
                if len(range_parts) == 2:
                    try:
                        min_val = float(range_parts[0].replace(',', ''))
                        max_val = float(range_parts[1].replace(',', ''))
                        # Use average of range
                        avg_val = (min_val + max_val) / 2
                        breakdown[category] = avg_val
                        total += avg_val
                    except ValueError:
                        continue
            else:
                try:
                    val = float(cost_value.replace(',', ''))
                    breakdown[category] = val
                    total += val
                except ValueError:
                    continue
    
    # If we couldn't parse anything, fall back to a reasonable estimate
    if not breakdown:
        # Extract any numbers and use the largest as an estimate
        numbers = re.findall(r'[\d,]+', cost_str)
        if numbers:
            try:
                max_num = max(float(num.replace(',', '')) for num in numbers)
                breakdown['estimated_total'] = max_num
                total = max_num
            except ValueError:
                breakdown['estimated_total'] = 5000.0
                total = 5000.0
        else:
            breakdown['estimated_total'] = 5000.0
            total = 5000.0
    
    return CostBreakdown(total_chf=total, breakdown=breakdown)


def _calculate_fallback_cost(inputs: Dict[str, Any]) -> CostBreakdown:
    """Calculate fallback cost when estimator doesn't have data."""
    time_estimate = inputs.get("time_estimate", {})
    if isinstance(time_estimate, TimeEstimate):
        time_val = time_estimate.value
        time_unit = time_estimate.unit
    else:
        time_val = time_estimate.get("value", 6)
        time_unit = time_estimate.get("unit", "months")
    
    hourly_rates = inputs.get("hourly_rates", {})
    lawyer_rate = hourly_rates.get("lawyer", 400)  # CHF per hour
    vat_rate = inputs.get("vat_rate", 0.077)
    
    # Convert time to hours (rough estimates for legal work)
    hours_map = {"days": 8, "weeks": 40, "months": 160}  # work hours per period
    total_hours = time_val * hours_map.get(time_unit, 160)
    
    # Estimate different cost components
    lawyer_hours = total_hours * 0.3  # 30% of time with lawyer
    lawyer_cost = lawyer_hours * lawyer_rate
    
    # Court fees estimation based on case complexity
    court_fees = min(max(1000, lawyer_cost * 0.2), 5000)  # 20% of lawyer costs, capped
    
    # Expert witness fees (if needed for complex cases)
    expert_fees = 0
    if time_val > 6:  # Complex cases might need experts
        expert_fees = 2000
    
    subtotal = lawyer_cost + court_fees + expert_fees
    vat = subtotal * vat_rate
    total = subtotal + vat
    
    breakdown = {
        "lawyer_fees": lawyer_cost,
        "court_fees": court_fees,
        "vat": vat
    }
    
    if expert_fees > 0:
        breakdown["expert_fees"] = expert_fees
    
    return CostBreakdown(total_chf=total, breakdown=breakdown)


def estimate_cost(inputs: Dict[str, Any]) -> Union[float, CostBreakdown]:
    """
    Estimate cost to win a legal case.
    
    Args:
        inputs: Dictionary containing time_estimate and other cost factors
                like judges_count, hourly_rates, filing_fees, etc.
        
    Returns:
        Cost estimate as CostBreakdown object
    """
    # Import the actual estimator functions
    from experts.tools.estimators.estimator import estimate_costs as estimator_cost_func
    
    # Get category from the time estimate context (if available)
    # This is a bit tricky since the cost function doesn't directly get the category
    # We'll try to infer it or use the fallback
    
    # Try to get category from inputs or use fallback calculation
    category = inputs.get("category")
    case_text = inputs.get("case_text", "")
    
    if not category:
        # Use fallback cost calculation
        return _calculate_fallback_cost(inputs)
    
    # Map category to English
    german_category = category
    english_category = CATEGORY_MAPPING.get(german_category, "other")
    
    # For categories not supported by estimator, use fallbacks
    if english_category in ["real_estate_law", "other"]:
        return _calculate_fallback_cost(inputs)
    
    # Extract subcategory from case text
    subcategory = _extract_subcategory(case_text, english_category)
    
    # Call the actual estimator function
    try:
        cost_str = estimator_cost_func(english_category, subcategory)
        
        # Parse the result and convert to CostBreakdown
        time_estimate = inputs.get("time_estimate")
        return _parse_cost_string(cost_str, time_estimate)
        
    except Exception as e:
        # Fallback in case of any errors
        return _calculate_fallback_cost(inputs)