# Protocol output models — placeholder
from pydantic import BaseModel


class SupplementRecommendation(BaseModel):
    name: str
    dose: str
    timing: str
    duration_weeks: int
    targets: list[str] = []


class DietChange(BaseModel):
    action: str
    phase: str  # "immediate" | "phase_in"


class LifestyleChange(BaseModel):
    action: str
    frequency: str


class RetestItem(BaseModel):
    marker: str
    weeks_from_now: int
    reason: str


class Protocol(BaseModel):
    extraction_id: str
    goals: list[str]
    diet_changes: list[DietChange] = []
    supplements: list[SupplementRecommendation] = []
    lifestyle_changes: list[LifestyleChange] = []
    retest_schedule: list[RetestItem] = []
    disclaimer: str = (
        "This protocol is for informational purposes only and does not "
        "constitute medical advice. Consult a qualified healthcare provider "
        "before making changes to your diet, supplements, or lifestyle."
    )
