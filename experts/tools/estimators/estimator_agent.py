from enum import Enum

class ClaimsType(Enum):
    TRAFFIC_CRIMINAL_LAW = "traffic_criminal_law"
    EMPLOYMENT_LAW = "employment_law"

class TrafficCriminalLawCategory(Enum):
    MODERATE_SPEEDING = "moderate_speeding"
    DRIVING_UNDER_INFLUENCE = "driving_under_influence_alcohol_license withdrawal"
    PARKING_LOT_ACCIDENT = "parking_lot_accident_chf_2500_no_witnesses"
    PARKING_FINE_EXPIRED = "parking_fine_expired_few_minutes"
    ALCOHOL_PENALTY_ORDER = "alcohol_06_penalty_order"

class EmploymentLawCategory(Enum):
    TERMINATION_POOR_PERFORMANCE = "termination_poor_performance"
    INCREASE_IN_WORKLOAD = "increase_in_workload"
    LOHN_AUSSTEHEND = "lohn_ausstehend"
    FRISTLOSE_KUENDIGUNG = "fristlose_kuendigung"
    KUENDIGUNG_WAEHREND_KRANKHEIT = "kuendigung_waehrend_krankheit_unfall"

def estimate_chance_of_winning(claims_type: ClaimsType, claims_category: Enum):
    """
    Estimate the chance of winning based on claims type and category.
    """
    if claims_type == ClaimsType.TRAFFIC_CRIMINAL_LAW:
        if claims_category == TrafficCriminalLawCategory.MODERATE_SPEEDING:
            return "10–15% (usually hopeless unless technical errors)"
        elif claims_category == TrafficCriminalLawCategory.DRIVING_UNDER_INFLUENCE:
            return "<10% (almost hopeless, mandatory withdrawal)"
        elif claims_category == TrafficCriminalLawCategory.PARKING_LOT_ACCIDENT:
            return "50–60% (good if insurance involved; depends on proof)"
        elif claims_category == TrafficCriminalLawCategory.PARKING_FINE_EXPIRED:
            return "<10% (hopeless)"
        elif claims_category == TrafficCriminalLawCategory.ALCOHOL_PENALTY_ORDER:
            return "20–30% (low, slightly better if strong evidence)"
        else:
            return "unknown"
    elif claims_type == ClaimsType.EMPLOYMENT_LAW:
        if claims_category == EmploymentLawCategory.TERMINATION_POOR_PERFORMANCE:
            return "20%"
        elif claims_category == EmploymentLawCategory.INCREASE_IN_WORKLOAD:
            return "0%"
        elif claims_category == EmploymentLawCategory.LOHN_AUSSTEHEND:
            return "100%"
        elif claims_category == EmploymentLawCategory.FRISTLOSE_KUENDIGUNG:
            return "80%"
        elif claims_category == EmploymentLawCategory.KUENDIGUNG_WAEHREND_KRANKHEIT:
            return "100%"
        else:
            return "unknown"
    else:
        return "unknown"

def estimate_time(claims_type: ClaimsType, claims_category: Enum):
    """
    Estimate the time required based on claims type and category.
    """
    if claims_type == ClaimsType.TRAFFIC_CRIMINAL_LAW:
        if claims_category == TrafficCriminalLawCategory.MODERATE_SPEEDING:
            return "Paid: 30 days; Contested: 3–6 months+"
        elif claims_category == TrafficCriminalLawCategory.DRIVING_UNDER_INFLUENCE:
            return "6–12 months+"
        elif claims_category == TrafficCriminalLawCategory.PARKING_LOT_ACCIDENT:
            return "1–6 months"
        elif claims_category == TrafficCriminalLawCategory.PARKING_FINE_EXPIRED:
            return "Paid: 30 days; Contested: 3–6 months"
        elif claims_category == TrafficCriminalLawCategory.ALCOHOL_PENALTY_ORDER:
            return "3–6 months"
        else:
            return "unknown"
    elif claims_type == ClaimsType.EMPLOYMENT_LAW:
        if claims_category == EmploymentLawCategory.TERMINATION_POOR_PERFORMANCE:
            return "3 Months"
        elif claims_category == EmploymentLawCategory.INCREASE_IN_WORKLOAD:
            return "0 Months"
        elif claims_category == EmploymentLawCategory.LOHN_AUSSTEHEND:
            return "5 Months"
        elif claims_category == EmploymentLawCategory.FRISTLOSE_KUENDIGUNG:
            return "6 Months"
        elif claims_category == EmploymentLawCategory.KUENDIGUNG_WAEHREND_KRANKHEIT:
            return "3 Months"
        else:
            return "unknown"
    else:
        return "unknown"

def estimate_costs(claims_type: ClaimsType, claims_category: Enum):
    """
    Estimate the costs involved based on claims type and category.
    """
    if claims_type == ClaimsType.TRAFFIC_CRIMINAL_LAW:
        if claims_category == TrafficCriminalLawCategory.MODERATE_SPEEDING:
            return "Fine: CHF 240; Admin fees: CHF 0–600; Lawyer: CHF 1,000–5,000; Court: CHF 300–3,000"
        elif claims_category == TrafficCriminalLawCategory.DRIVING_UNDER_INFLUENCE:
            return "Fine: CHF 500–10,000; Road Traffic fees: CHF 400–1,000; Assessment: CHF 1,500–3,000; Lawyer: CHF 2,000–8,000"
        elif claims_category == TrafficCriminalLawCategory.PARKING_LOT_ACCIDENT:
            return "Deductible CHF 200–1,000; Lawyer usually unnecessary (insurance covers); private lawyer CHF 1,000–4,000"
        elif claims_category == TrafficCriminalLawCategory.PARKING_FINE_EXPIRED:
            return "Fine: CHF 40–80; Lawyer: CHF 500–2,000; Court: CHF 300–1,000"
        elif claims_category == TrafficCriminalLawCategory.ALCOHOL_PENALTY_ORDER:
            return "Fine: CHF 500–1,000; Road Traffic fees: CHF 200–1,000; Lawyer: CHF 1,000–3,000; Court: CHF 500–3,000"
        else:
            return "unknown"
    elif claims_type == ClaimsType.EMPLOYMENT_LAW:
        if claims_category == EmploymentLawCategory.TERMINATION_POOR_PERFORMANCE:
            return "3500"
        elif claims_category == EmploymentLawCategory.INCREASE_IN_WORKLOAD:
            return "0"
        elif claims_category == EmploymentLawCategory.LOHN_AUSSTEHEND:
            return "5000"
        elif claims_category == EmploymentLawCategory.FRISTLOSE_KUENDIGUNG:
            return "2500"
        elif claims_category == EmploymentLawCategory.KUENDIGUNG_WAEHREND_KRANKHEIT:
            return "1500"
        else:
            return "unknown"
    else:
        return "unknown"

# Update the known_actions dictionary to use these functions
known_actions = {
    "estimate_chance_of_winning": estimate_chance_of_winning,
    "estimate_time": estimate_time,
    "estimate_costs": estimate_costs,
}


#print(estimate_chance_of_winning(ClaimsType.TRAFFIC_CRIMINAL_LAW, TrafficCriminalLawCategory.MODERATE_SPEEDING))