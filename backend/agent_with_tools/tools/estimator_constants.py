"""Shared constants for estimator tools.

This module contains all the shared constants used by both estimate_time.py and 
estimate_cost.py to avoid code duplication. It includes category mappings and
subcategory mappings for Swiss legal case analysis.
"""

from typing import Dict

# Category mapping from German agent categories to English estimator categories  
CATEGORY_MAPPING: Dict[str, str] = {
    "Arbeitsrecht": "employment_law",
    "Strafverkehrsrecht": "traffic_criminal_law",
    "Immobilienrecht": "real_estate_law",  # Not in estimator yet, will use fallback
    "Andere": "other"  # Not in estimator yet, will use fallback
}

# Employment law subcategories mapping (inferred from case facts or complexity)
EMPLOYMENT_SUBCATEGORIES: Dict[str, str] = {
    "termination": "termination_poor_performance",
    "dismissal": "fristlose_kuendigung", 
    "salary": "lohn_ausstehend",
    "illness": "kuendigung_waehrend_krankheit_unfall",
    "workload": "increase_in_workload",
    "default": "termination_poor_performance"
}

# Traffic law subcategories mapping
TRAFFIC_SUBCATEGORIES: Dict[str, str] = {
    "speeding": "moderate_speeding",
    "alcohol": "driving_under_influence_alcohol_license_withdrawal",
    "parking": "parking_lot_accident_chf_2500_no_witnesses", 
    "fine": "parking_fine_expired_few_minutes",
    "penalty": "alcohol_06_penalty_order",
    "default": "moderate_speeding"
}