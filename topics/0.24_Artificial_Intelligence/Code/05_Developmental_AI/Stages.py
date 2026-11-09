"""
Module: Developmental Stages Curriculum
Topic: 0.24 Artificial Intelligence
Folder: 05_Developmental_AI

Defines the curriculum and passing criteria for each stage of life.
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


from docs.core.uet_parameters import UETParameters


class LifeStage:
    def __init__(self, name, age_range, focus, passing_criteria, params=None):
        self.name = name
        self.age_range = age_range
        self.focus = focus
        self.passing_criteria = passing_criteria
        self.params = params if params else UETParameters()

    def __repr__(self):
        return f"<{self.name} Stage ({self.age_range[0]}-{self.age_range[1]} Years) | Beta={self.params.beta}>"


# Define the Curriculum with Thermodynamic Parameters
# Infant: High Temperature, Low Beta (High Plasticity, Easy to Change)
# Adult: Low Temperature, High Beta (Low Plasticity, Hard to Change, Efficient)
STAGES = {
    "Infant": LifeStage(
        name="Infant",
        age_range=(0, 5),
        focus="Pattern Recognition, Noise Filter, Basic Motor Control",
        passing_criteria={"entropy_stability": 2.0, "vocab_size": 50},  # Higher entropy allowed
        params=UETParameters(
            scale="macroscopic",
            beta=0.1,  # Low coupling (fluid mind)
            kappa=0.01,  # Low stiffness (short-term memory only)
            temperature=500.0,  # Hot brain (active learning)
        ),
    ),
    "Child": LifeStage(
        name="Child",
        age_range=(6, 12),
        focus="Vocabulary (HF/Kaggle), Basic Facts, Social Rules",
        passing_criteria={"entropy_stability": 1.5, "vocab_size": 1000, "exam_score": 70},
        params=UETParameters(
            scale="macroscopic",
            beta=0.5,  # Moderate coupling
            kappa=0.05,  # Moderate stiffness
            temperature=310.0,  # Normal body temp
        ),
    ),
    "Adolescent": LifeStage(
        name="Adolescent",
        age_range=(13, 18),
        focus="Logic, Conflict Resolution, Ethics (Nash Eq)",
        passing_criteria={"entropy_stability": 1.0, "vocab_size": 5000, "logic_test": 85},
        params=UETParameters(scale="macroscopic", beta=0.8, kappa=0.08, temperature=300.0),
    ),
    "Adult": LifeStage(
        name="Adult",
        age_range=(19, 100),
        focus="Specialization, Mastery, Complex Optimization",
        passing_criteria={"mastery_level": "Expert", "entropy_stability": 0.5},
        params=UETParameters(
            scale="macroscopic",
            beta=1.0,  # Strong coupling (crystalized intelligence)
            kappa=0.1,  # High stiffness (long-term stability)
            temperature=293.15,  # Room temp (Cool/Efficient)
        ),
    ),
}


def get_stage_by_age(age):
    for stage_name, stage_data in STAGES.items():
        min_age, max_age = stage_data.age_range
        if min_age <= age <= max_age:
            return stage_data
    return STAGES["Adult"]  # Default to Adult if older
