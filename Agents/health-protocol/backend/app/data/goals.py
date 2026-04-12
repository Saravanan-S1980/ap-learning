"""Goal definitions and marker associations.

Each Goal maps a user health objective to the biomarkers that most
directly influence it. This drives Step 3 (cross-reference) which
tells the protocol generator which flagged markers to prioritize.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Goal:
    id: str
    display_name: str
    emoji: str
    description: str
    relevant_markers: list[str] = field(default_factory=list)


GOALS: dict[str, Goal] = {
    "cardiovascular_health": Goal(
        id="cardiovascular_health",
        display_name="Heart Health",
        emoji="❤️",
        description="Optimize lipid profile and reduce cardiovascular risk",
        relevant_markers=[
            "Total Cholesterol", "LDL", "HDL", "Triglycerides", "VLDL",
            "Non-HDL Cholesterol", "Atherogenic Index", "Chol/HDL Ratio",
            "CRP", "Homocysteine", "Fasting Glucose", "HbA1c",
            "Lipoprotein(a)", "ApoB", "Blood Pressure",
        ],
    ),
    "energy_vitality": Goal(
        id="energy_vitality",
        display_name="Energy & Vitality",
        emoji="⚡",
        description="Improve cellular energy production and combat fatigue",
        relevant_markers=[
            "Hemoglobin", "Ferritin", "Iron", "TIBC", "Vitamin B12",
            "Vitamin D", "Fasting Glucose", "HbA1c", "TSH", "Free T3",
            "Free T4", "Testosterone", "Magnesium", "Cortisol",
        ],
    ),
    "fat_loss": Goal(
        id="fat_loss",
        display_name="Fat Loss",
        emoji="🏃",
        description="Support metabolic health for sustainable weight management",
        relevant_markers=[
            "Fasting Glucose", "HbA1c", "Fasting Insulin", "HOMA-IR",
            "Triglycerides", "HDL", "LDL", "Total Cholesterol",
            "TSH", "Free T3", "Free T4", "Cortisol", "Testosterone",
            "CRP", "Vitamin D",
        ],
    ),
    "hormonal_balance": Goal(
        id="hormonal_balance",
        display_name="Hormonal Balance",
        emoji="🧬",
        description="Optimize hormone levels for overall wellbeing",
        relevant_markers=[
            "Testosterone", "Free Testosterone", "SHBG", "LH", "FSH",
            "Estradiol", "Progesterone", "Cortisol", "DHEA-S",
            "TSH", "Free T3", "Free T4", "Prolactin",
            "Vitamin D", "Zinc", "Magnesium",
        ],
    ),
    "longevity": Goal(
        id="longevity",
        display_name="Longevity",
        emoji="🕐",
        description="Optimize markers associated with healthy aging and disease prevention",
        relevant_markers=[
            "CRP", "Homocysteine", "HbA1c", "Fasting Glucose",
            "Vitamin D", "Vitamin B12", "Total Cholesterol", "LDL",
            "HDL", "Triglycerides", "Ferritin", "Testosterone",
            "Free T3", "TSH", "Uric Acid", "Atherogenic Index",
        ],
    ),
    "immune_function": Goal(
        id="immune_function",
        display_name="Immune Function",
        emoji="🛡️",
        description="Strengthen immune defenses and reduce chronic inflammation",
        relevant_markers=[
            "Vitamin D", "Vitamin B12", "Iron", "Ferritin", "Zinc",
            "CRP", "WBC", "Neutrophils", "Lymphocytes",
            "Hemoglobin", "Fasting Glucose",
        ],
    ),
    "cognitive_performance": Goal(
        id="cognitive_performance",
        display_name="Brain Power",
        emoji="🧠",
        description="Support cognitive function, memory, and mental clarity",
        relevant_markers=[
            "Vitamin B12", "Vitamin D", "Homocysteine", "TSH", "Free T3",
            "Fasting Glucose", "HbA1c", "Total Cholesterol", "Triglycerides",
            "CRP", "Ferritin", "Testosterone", "Cortisol", "Omega-3 Index",
        ],
    ),
    "athletic_performance": Goal(
        id="athletic_performance",
        display_name="Athletic Performance",
        emoji="💪",
        description="Maximize physical performance, recovery, and muscle building",
        relevant_markers=[
            "Testosterone", "Free Testosterone", "Hemoglobin", "Ferritin",
            "Vitamin D", "Magnesium", "Creatinine", "Uric Acid",
            "CRP", "Fasting Glucose", "HbA1c", "Cortisol", "SHBG",
        ],
    ),
    "gut_health": Goal(
        id="gut_health",
        display_name="Gut Health",
        emoji="🌿",
        description="Improve digestive health and nutrient absorption",
        relevant_markers=[
            "CRP", "Ferritin", "Vitamin B12", "Vitamin D", "Calcium",
            "Magnesium", "Albumin", "Total Protein", "ALT", "AST",
            "Alkaline Phosphatase",
        ],
    ),
    "stress_resilience": Goal(
        id="stress_resilience",
        display_name="Stress Resilience",
        emoji="🧘",
        description="Reduce stress response and improve HPA axis balance",
        relevant_markers=[
            "Cortisol", "DHEA-S", "Vitamin D", "Magnesium",
            "Vitamin B12", "TSH", "Free T3", "Fasting Glucose",
            "CRP", "Testosterone",
        ],
    ),
}


def get_goal(goal_id: str) -> Goal | None:
    """Return Goal for the given ID, or None if not found."""
    return GOALS.get(goal_id)


# Flat list for frontend (id, display_name, emoji, description)
GOALS_LIST: list[dict] = [
    {
        "id": g.id,
        "display_name": g.display_name,
        "emoji": g.emoji,
        "description": g.description,
    }
    for g in GOALS.values()
]
