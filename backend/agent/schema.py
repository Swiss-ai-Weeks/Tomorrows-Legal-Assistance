from typing import Literal
from pydantic import BaseModel
from experts.tools.estimators.estimator_agent import (
    TrafficCriminalLawCategory,
    EmploymentLawCategory,
)

traffic_values = [cat.value for cat in TrafficCriminalLawCategory]
employment_values = [cat.value for cat in EmploymentLawCategory]


class LegalFieldClassification(BaseModel):
    legal_field: Literal["traffic_law", "employment_law"] | None = None


class CaseCategoryClassification(BaseModel):
    case_category: Literal[*traffic_values, *employment_values] | None = None

classes = {
    "traffic_law": """
* MODERATE_SPEEDING: Exceeding the statutory maximum speed limit. Slight excess, handled as an Ordnungsbusse. 
* DRIVING_UNDER_INFLUENCE: Operating a motor vehicle with BAC above the legal threshold. Administrative consequences: licence withdrawal, traffic medical assessment. Criminal consequences: fine or custodial sentence. Insurance consequences: possible reduction or refusal of benefits.
* PARKING_LOT_ACCIDENT: Damage to a parked car without witnesses.
* PARKING_FINE_EXPIRED: Fine for parking a vehicle longer than allowed of paid for. Even for small excesses.
* ALCOHOL_PENALTY_ORDER: Operating a motor vehicle with BAC above the legal threshold. Administrative consequences: licence withdrawal, traffic medical assessment. Criminal consequences: fine or custodial sentence. Insurance consequences: possible reduction or refusal of benefits.
    """,
    "employment_law": """
* TERMINATION_POOR_PERFORMANCE: Termination for poop performance.
* INCREASE_IN_WORKLOAD: Request to employer for increased workload/pensum.
* LOHN_AUSSTEHEND: SAlary payment outstanding.
* FRISTLOSE_KUENDIGUNG: Termination without notice period. Active immediately.
* KUENDIGUNG_WAEHREND_KRANKHEIT: Termination due to illness.
    """
}
