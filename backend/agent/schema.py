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
