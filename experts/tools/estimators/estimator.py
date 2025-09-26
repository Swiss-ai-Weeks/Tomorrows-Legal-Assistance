def estimate_chance_of_winning(claims_type: str, claims_category: str):
    """
    Estimate the chance of winning based on claims type and category.
    """
    if claims_type == "traffic_criminal_law":
        if claims_category == "moderate_speeding":
            chance_of_winning = "10–15% (usually hopeless unless technical errors)"
        elif claims_category == "driving_under_influence_alcohol_license_withdrawal":
            chance_of_winning = "<10% (almost hopeless, mandatory withdrawal)"
        elif claims_category == "parking_lot_accident_chf_2500_no_witnesses":
            chance_of_winning = "50–60% (good if insurance involved; depends on proof)"
        elif claims_category == "parking_fine_expired_few_minutes":
            chance_of_winning = "<10% (hopeless)"
        elif claims_category == "alcohol_06_penalty_order":
            chance_of_winning = "20–30% (low, slightly better if strong evidence)"
        else:
            chance_of_winning = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "termination_poor_performance":
            chance_of_winning = "20%"
        elif claims_category == "increase_in_workload":
            chance_of_winning = "0%"
        elif claims_category == "lohn_ausstehend":
            chance_of_winning = "100%"
        elif claims_category == "fristlose_kuendigung":
            chance_of_winning = "80%"
        elif claims_category == "kuendigung_waehrend_krankheit_unfall":
            chance_of_winning = "100%"
        else:
            chance_of_winning = "unknown"
    else:
        chance_of_winning = "unknown"
    return chance_of_winning

def estimate_time(claims_type: str, claims_category: str):
    """
    Estimate the time required based on claims type and category.
    """
    if claims_type == "traffic_criminal_law":
        if claims_category == "moderate_speeding":
            time = "Paid: 30 days; Contested: 3–6 months+"
        elif claims_category == "driving_under_influence_alcohol_license_withdrawal":
            time = "6–12 months+"
        elif claims_category == "parking_lot_accident_chf_2500_no_witnesses":
            time = "1–6 months"
        elif claims_category == "parking_fine_expired_few_minutes":
            time = "Paid: 30 days; Contested: 3–6 months"
        elif claims_category == "alcohol_06_penalty_order":
            time = "3–6 months"
        else:
            time = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "termination_poor_performance":
            time = "3 Months"
        elif claims_category == "increase_in_workload":
            time = "0 Months"
        elif claims_category == "lohn_ausstehend":
            time = "5 Months"
        elif claims_category == "fristlose_kuendigung":
            time = "6 Months"
        elif claims_category == "kuendigung_waehrend_krankheit_unfall":
            time = "3 Months"
        else:
            time = "unknown"
    else:
        time = "unknown"
    return time

def estimate_costs(claims_type: str, claims_category: str):
    """
    Estimate the costs involved based on claims type and category.
    """
    if claims_type == "traffic_criminal_law":
        if claims_category == "moderate_speeding":
            costs = "Fine: CHF 240; Admin fees: CHF 0–600; Lawyer: CHF 1,000–5,000; Court: CHF 300–3,000"
        elif claims_category == "driving_under_influence_alcohol_license_withdrawal":
            costs = "Fine: CHF 500–10,000; Road Traffic fees: CHF 400–1,000; Assessment: CHF 1,500–3,000; Lawyer: CHF 2,000–8,000"
        elif claims_category == "parking_lot_accident_chf_2500_no_witnesses":
            costs = "Deductible CHF 200–1,000; Lawyer usually unnecessary (insurance covers); private lawyer CHF 1,000–4,000"
        elif claims_category == "parking_fine_expired_few_minutes":
            costs = "Fine: CHF 40–80; Lawyer: CHF 500–2,000; Court: CHF 300–1,000"
        elif claims_category == "alcohol_06_penalty_order":
            costs = "Fine: CHF 500–1,000; Road Traffic fees: CHF 200–1,000; Lawyer: CHF 1,000–3,000; Court: CHF 500–3,000"
        else:
            costs = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "termination_poor_performance":
            costs = "3500"
        elif claims_category == "increase_in_workload":
            costs = "0"
        elif claims_category == "lohn_ausstehend":
            costs = "5000"
        elif claims_category == "fristlose_kuendigung":
            costs = "2500"
        elif claims_category == "kuendigung_waehrend_krankheit_unfall":
            costs = "1500"
        else:
            costs = "unknown"
    else:
        costs = "unknown"
    return costs

# Update the known_actions dictionary to use these functions
known_actions = {
    "estimate_chance_of_winning": estimate_chance_of_winning,
    "estimate_time": estimate_time,
    "estimate_costs": estimate_costs,
}
#print(estimate_chance_of_winning("employment_law","kuendigung_waehrend_krankheit_unfall"))
