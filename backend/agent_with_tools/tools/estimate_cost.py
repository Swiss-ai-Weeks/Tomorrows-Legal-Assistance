"""Cost estimation tool."""

import re
from typing import Dict, Any, Union
from backend.agent_with_tools.schemas import CostBreakdown, TimeEstimate
from backend.agent_with_tools.tools.estimator_constants import CATEGORY_MAPPING
from backend.agent_with_tools.tools.estimator_utils import (
    extract_subcategory, 
    normalize_time_estimate, 
    get_case_text_from_inputs
)


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
    time_val, time_unit = normalize_time_estimate(time_estimate)
    
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
    case_text = get_case_text_from_inputs(inputs)
    
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
    subcategory = extract_subcategory(case_text, english_category)
    
    # Call the actual estimator function
    try:
        cost_str = estimator_cost_func(english_category, subcategory)
        
        # Parse the result and convert to CostBreakdown
        time_estimate = inputs.get("time_estimate")
        return _parse_cost_string(cost_str, time_estimate)
        
    except Exception as e:
        # Fallback in case of any errors
        return _calculate_fallback_cost(inputs)