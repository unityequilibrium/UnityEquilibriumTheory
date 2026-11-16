"""Profile software regression only; untested engine/research paths remain open."""

from pathlib import Path
import pytest

from topics.tests.profile_contract_cases import CASES, exercise_profile_case


@pytest.mark.parametrize("case", CASES)
def test_profile_threshold_contract(case, tmp_path):
    exercise_profile_case(
        Path(__file__).resolve().parents[1],
        "Code/05_Simulation/Sim_Quantum_Solar.py",
        "empirical_solar_profile.json",
        case,
        tmp_path,
    )
