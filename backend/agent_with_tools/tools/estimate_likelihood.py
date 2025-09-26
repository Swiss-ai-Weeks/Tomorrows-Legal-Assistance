"""Business logic likelihood estimation tool.

This tool uses the estimator functions from experts/tools/estimators/estimator.py
to provide baseline likelihood estimates based on business logic and experience.
"""

import re
from typing import Dict, Any, Optional, Tuple
from backend.agent_with_tools.tools.estimator_constants import CATEGORY_MAPPING
from backend.agent_with_tools.tools.estimator_utils import extract_subcategory
from experts.tools.estimators.estimator import estimate_chance_of_winning


def estimate_business_likelihood(case_text: str, category: str) -> Dict[str, Any]:
    """
    Get baseline likelihood estimate using business logic.
    
    Args:
        case_text: The case description text
        category: Legal category (German format: "Arbeitsrecht", "Strafverkehrsrecht", etc.)
        
    Returns:
        Dictionary containing:
        - likelihood: Numerical likelihood (1-100) or None if not supported
        - raw_estimate: Original string from estimator function
        - explanation: Reasoning and warnings
        - category_mapped: English category used for estimation
        - subcategory: Subcategory used for estimation
    """
    result = {
        "likelihood": None,
        "raw_estimate": None,
        "explanation": "",
        "category_mapped": None,
        "subcategory": None
    }
    
    # Map German category to English
    english_category = CATEGORY_MAPPING.get(category)
    result["category_mapped"] = english_category
    
    if not english_category or english_category in ["other", "real_estate_law"]:
        result["explanation"] = f"Category '{category}' not supported by business logic estimator. Using fallback analysis."
        return result
    
    # Extract subcategory from case text
    try:
        subcategory = extract_subcategory(case_text, english_category)
        result["subcategory"] = subcategory
        
        if not subcategory or subcategory == "default":
            result["explanation"] = f"Could not determine specific subcategory for {category}. Using general analysis."
            return result
        
        # Get business logic estimate
        raw_estimate = estimate_chance_of_winning(english_category, subcategory)
        result["raw_estimate"] = raw_estimate
        
        if raw_estimate == "unknown":
            result["explanation"] = f"Business logic estimator returned 'unknown' for {category}/{subcategory}. Using fallback analysis."
            return result
        
        # Parse numerical likelihood from string estimate
        likelihood = _parse_likelihood_percentage(raw_estimate)
        result["likelihood"] = likelihood
        
        if likelihood is not None:
            result["explanation"] = f"Business logic baseline: {raw_estimate}. This provides initial guidance but will be adjusted based on case-specific factors."
        else:
            result["explanation"] = f"Could not parse numerical likelihood from: {raw_estimate}. Using as qualitative guidance only."
            
    except Exception as e:
        result["explanation"] = f"Error in business logic estimation: {str(e)}. Using fallback analysis."
    
    return result


def _parse_likelihood_percentage(estimate_string: str) -> Optional[int]:
    """
    Parse numerical percentage from estimator string.
    
    Args:
        estimate_string: String like "20%", "80%", "10–15% (usually hopeless)", etc.
        
    Returns:
        Integer percentage (1-100) or None if cannot parse
    """
    if not estimate_string or estimate_string == "unknown":
        return None
    
    # Look for percentage patterns
    # Handle ranges like "10–15%" - take midpoint
    range_pattern = r'(\d+)[-–](\d+)%'
    range_match = re.search(range_pattern, estimate_string)
    if range_match:
        low = int(range_match.group(1))
        high = int(range_match.group(2))
        return (low + high) // 2
    
    # Handle single percentages like "20%", "80%"
    single_pattern = r'(\d+)%'
    single_match = re.search(single_pattern, estimate_string)
    if single_match:
        percentage = int(single_match.group(1))
        # Cap 100% at 95% for more realistic modeling
        if percentage == 100:
            return 95
        # Ensure it's in valid range
        return max(1, min(100, percentage))
    
    # Handle special cases with qualitative descriptions
    estimate_lower = estimate_string.lower()
    
    if "<10%" in estimate_string:
        return 5  # Very low chance for <10%
    elif any(word in estimate_lower for word in ["hopeless", "almost hopeless"]):
        return 5  # Very low chance
    elif "100%" in estimate_string:
        return 95  # Very high but not absolute certainty
    elif any(word in estimate_lower for word in ["low", "poor", "weak"]):
        return 25  # Low chance
    elif any(word in estimate_lower for word in ["good", "strong"]):
        return 65  # Good chance
    elif any(word in estimate_lower for word in ["moderate", "medium"]):
        return 50  # Medium chance
    
    return None


def get_likelihood_explanation_context(business_result: Dict[str, Any]) -> str:
    """
    Generate context string for LLM explaining business logic result.
    
    Args:
        business_result: Result dictionary from estimate_business_likelihood
        
    Returns:
        Formatted context string for LLM
    """
    if not business_result["likelihood"]:
        return f"Business Logic Analysis: {business_result['explanation']}"
    
    context_parts = [
        f"Business Logic Baseline: {business_result['likelihood']}% likelihood",
        f"Category: {business_result['category_mapped']}/{business_result['subcategory']}",
        f"Raw Estimate: {business_result['raw_estimate']}",
        f"Note: {business_result['explanation']}"
    ]
    
    return "\n".join([f"- {part}" for part in context_parts if part])