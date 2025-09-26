from typing import Literal
from pydantic import BaseModel


class LegalFieldClassification(BaseModel):
    legal_field: Literal["traffic_law", "employment_law"] | None = None


class CaseCategoryClassification(BaseModel):
    case_category: (
        Literal[
            "speeding_20_outside_areas",
            "driving_alcohol_18",
            "parking_accident_2500_no_witnesses",
        ]
        | None
    ) = None
