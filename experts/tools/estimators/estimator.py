def estimate_chance_of_winning(claims_type: str, claims_category: str):
    """
    Estimate the chance of winning based on claims type and category.
    """
    if claims_type == "traffic_criminal_law":
        if claims_category == "Speeding 20 km/h outside built-up areas":
            chance_of_winning = "10–15% (usually hopeless unless technical errors)"
        elif claims_category == "Driving under influence – 1.8 ‰ alcohol, license withdrawal":
            chance_of_winning = "<10% (almost hopeless, mandatory withdrawal)"
        elif claims_category == "Parking lot accident CHF 2,500, no witnesses":
            chance_of_winning = "50–60% (good if insurance involved; depends on proof)"
        elif claims_category == "Parking fine expired by 5 minutes":
            chance_of_winning = "<10% (hopeless)"
        elif claims_category == "Alcohol 0.6 ‰ (penalty order)":
            chance_of_winning = "20–30% (low, slightly better if strong evidence)"
        else:
            chance_of_winning = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "Termination (poor performance)":
            chance_of_winning = "20%"
        elif claims_category == "Increase in workload":
            chance_of_winning = "0%"
        elif claims_category == "Lohn Monate ausstehend":
            chance_of_winning = "100%"
        elif claims_category == "Fristlose Kündigung":
            chance_of_winning = "80%"
        elif claims_category == "Kündigung während Krankheit/Unfall":
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
        if claims_category == "Speeding 20 km/h outside built-up areas":
            time = "Paid: 30 days; Contested: 3–6 months+"
        elif claims_category == "Driving under influence – 1.8 ‰ alcohol, license withdrawal":
            time = "6–12 months+"
        elif claims_category == "Parking lot accident CHF 2,500, no witnesses":
            time = "1–6 months"
        elif claims_category == "Parking fine expired by 5 minutes":
            time = "Paid: 30 days; Contested: 3–6 months"
        elif claims_category == "Alcohol 0.6 ‰ (penalty order)":
            time = "3–6 months"
        else:
            time = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "Termination (poor performance)":
            time = "3 Months"
        elif claims_category == "Increase in workload":
            time = "0 Months"
        elif claims_category == "Lohn Monate ausstehend":
            time = "5 Months"
        elif claims_category == "Fristlose Kündigung":
            time = "6 Months"
        elif claims_category == "Kündigung während Krankheit/Unfall":
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
        if claims_category == "Speeding 20 km/h outside built-up areas":
            costs = "Fine: CHF 240; Admin fees: CHF 0–600; Lawyer: CHF 1,000–5,000; Court: CHF 300–3,000"
        elif claims_category == "Driving under influence – 1.8 ‰ alcohol, license withdrawal":
            costs = "Fine: CHF 500–10,000; Road Traffic fees: CHF 400–1,000; Assessment: CHF 1,500–3,000; Lawyer: CHF 2,000–8,000"
        elif claims_category == "Parking lot accident CHF 2,500, no witnesses":
            costs = "Deductible CHF 200–1,000; Lawyer usually unnecessary (insurance covers); private lawyer CHF 1,000–4,000"
        elif claims_category == "Parking fine expired by 5 minutes":
            costs = "Fine: CHF 40–80; Lawyer: CHF 500–2,000; Court: CHF 300–1,000"
        elif claims_category == "Alcohol 0.6 ‰ (penalty order)":
            costs = "Fine: CHF 500–1,000; Road Traffic fees: CHF 200–1,000; Lawyer: CHF 1,000–3,000; Court: CHF 500–3,000"
        else:
            costs = "unknown"
    elif claims_type == "employment_law":
        if claims_category == "Termination (poor performance)":
            costs = "3500"
        elif claims_category == "Increase in workload":
            costs = "0"
        elif claims_category == "Lohn Monate ausstehend":
            costs = "5000"
        elif claims_category == "Fristlose Kündigung":
            costs = "2500"
        elif claims_category == "Kündigung während Krankheit/Unfall":
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
