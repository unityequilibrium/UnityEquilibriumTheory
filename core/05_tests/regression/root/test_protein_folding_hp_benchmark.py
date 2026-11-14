"""Unit checks for the finite 2-D HP benchmark contract."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
from pathlib import Path


SCRIPT_PATH = (
    (repo_root() / "docs")
    / "topics"
    / "0.22_Biophysics_Origin_of_Life"
    / "Code"
    / "03_Research"
    / "Research_Protein_Folding_HP_Benchmark.py"
)
SPEC = importlib.util.spec_from_file_location("protein_folding_hp_benchmark", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load benchmark module from {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_non_bonded_contact_rule_is_explicit() -> None:
    assert MODULE.hp_energy(((0, 0), (1, 0), (1, 1), (0, 1)), "HHHH") == -1
    assert MODULE.hp_energy(((0, 0), (1, 0), (2, 0), (3, 0)), "HHHH") == 0


def test_exact_reference_and_stochastic_replay_are_deterministic() -> None:
    config = MODULE.load_config()
    exact = MODULE.exact_reference(config["sequence"])
    assert exact["configuration_count"] == 11025
    assert exact["optimum_energy"] == -4
    assert exact["optimum_fold_count"] == 34

    first = MODULE.run_stochastic_method(
        config["sequence"],
        config["search"]["seeds"],
        config["search"]["attempts_per_seed"],
        "centroid_biased",
        exact["optimum_energy"],
        config["search"]["centroid_bias_probability"],
    )
    second = MODULE.run_stochastic_method(
        config["sequence"],
        config["search"]["seeds"],
        config["search"]["attempts_per_seed"],
        "centroid_biased",
        exact["optimum_energy"],
        config["search"]["centroid_bias_probability"],
    )
    assert first == second
    assert first["aggregate"]["optimum_gap"] >= 0
