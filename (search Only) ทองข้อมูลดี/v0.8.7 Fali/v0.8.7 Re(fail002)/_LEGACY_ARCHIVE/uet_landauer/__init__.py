"""
UET Landauer Package
====================

New foundation based on Landauer principle, not Cahn-Hilliard.

Core equations:
- E_bit = k_B × T × ln(2)
- V = M × (C/I)^α

Vision:
"พฤติกรรม → เสื่อมพลังงาน → บันทึกเป็นข้อมูลลงใน Space"

Author: Santa (Original Vision)
Date: 2025-12-30
"""

from .core import (
    # Constants
    K_B,
    LN_2,
    # Functions
    energy_per_bit,
    value_function,
    information_energy,
    energy_rate,
    behavior_energy,
    # Classes
    LandauerParams,
    LandauerSystem,
)

from .thermodynamics import (
    ThermodynamicState,
    ThermodynamicSystem,
    law_0_equilibrium,
    law_1_conservation,
    law_2_entropy_increase,
    law_3_space_is_order,
    behavior_to_entropy,
    entropy_to_information,
)

from .space import (
    InformationRecord,
    SpaceRegion,
    UniverseSpace,
    HBAR,
    C_LIGHT,
)

from .simulator import (
    Agent,
    SimulationConfig,
    FullSimulator,
)

__version__ = "1.0.0"
__all__ = [
    # Core
    "K_B",
    "LN_2",
    "energy_per_bit",
    "value_function",
    "information_energy",
    "energy_rate",
    "behavior_energy",
    "LandauerParams",
    "LandauerSystem",
    # Thermodynamics
    "ThermodynamicState",
    "ThermodynamicSystem",
    "law_0_equilibrium",
    "law_1_conservation",
    "law_2_entropy_increase",
    "law_3_space_is_order",
    "behavior_to_entropy",
    "entropy_to_information",
    # Space
    "InformationRecord",
    "SpaceRegion",
    "UniverseSpace",
    "HBAR",
    "C_LIGHT",
    # Simulator
    "Agent",
    "SimulationConfig",
    "FullSimulator",
]
