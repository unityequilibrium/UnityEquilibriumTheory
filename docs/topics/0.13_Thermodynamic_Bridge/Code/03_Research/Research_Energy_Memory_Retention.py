"""Bounded homogeneous retention/probe controls of the unchanged C/Phi/Pi RHS.

No file writes, physical data, parameter search or new evolution law.  --check
prints one compact JSON record; the analytic argument is in docs/meta section 11.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import scipy
from scipy.integrate import solve_ivp

model = importlib.import_module("docs.core.02_equations.matter_space.uet_matter_space")
CONFIG = model.MatterSpaceConfig(matter_dynamics="nonconserved", coupling_g=1.0)
DX = 0.25
SAMPLES = (0.0, 2.0, 5.0, 10.0, 20.0, 40.0, 80.0)
WAITS = (0.0, 5.0, 20.0, 80.0)
PROBE = 0.001
PROBE_DURATION = 1.0
LEVELS = ((1e-9, 1e-12), (1e-11, 1e-14))
COMPUTATIONAL_LIMIT = 1e-7  # method-control scale, NOT a physical error budget


def equilibrium_bracket(iterations: int = 60) -> tuple[Q, Q]:
    """Exact enclosure of the unique root of r^3+r/2-1/2 on [0,1]."""
    lo, hi = Q(0), Q(1)
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if mid**3 + mid / 2 - Q(1, 2) < 0:
            lo = mid
        else:
            hi = mid
    return lo, hi


def reference_state() -> np.ndarray:
    lo, hi = equilibrium_bracket()
    phi = float((lo + hi) / 2)
    return np.array([np.sqrt(1.0 + phi), phi, 0.0])


def fields(y: np.ndarray) -> object:
    return model.MatterSpaceState(*(np.full(4, float(v)) for v in y[:3]))


def energy(y: np.ndarray) -> float:
    return model.matter_space_extended_energy(fields(y), DX, CONFIG)


def evolution(_time: float, y: np.ndarray, drive: float = 0.0) -> np.ndarray:
    """Use canonical RHS, dissipation and source-power functions, without clipping."""
    state = fields(y)
    jc, jp = np.zeros(4), np.full(4, drive)
    dc, dphi, dpi, muc, _ = model.matter_space_rhs(state, DX, CONFIG, jc, jp)
    _, _, sigma = model.matter_space_dissipation(state, muc, DX, CONFIG)
    pc, pp = model._source_power(state, muc, jc, jp, DX, CONFIG)
    dissipation = model.integral_1d(sigma, DX)
    return np.array([dc[0], dphi[0], dpi[0], dissipation, pc + pp])


def integrate(initial: np.ndarray, times: tuple[float, ...], drive: float,
              level: tuple[float, float]) -> np.ndarray:
    """Integrate [C,Phi,Pi,int(D),int(P)] over one explicitly fixed interval."""
    state = np.r_[initial[:3], 0.0, 0.0]
    solution = solve_ivp(lambda t, y: evolution(t, y, drive), (0.0, times[-1]),
                         state, method="DOP853", t_eval=times,
                         rtol=level[0], atol=level[1])
    if not solution.success or not np.isfinite(solution.y).all():
        raise AssertionError("declared integration failed; no fallback solver")
    return solution.y.T


def balance_residual(initial: np.ndarray, rows: np.ndarray) -> float:
    return max(abs(energy(row) - energy(initial) + row[3] - row[4]) for row in rows)


def paired_probe(initials: list[np.ndarray], level: tuple[float, float]) -> dict:
    increments, square_increments = [], []
    worst_balance = 0.0
    for initial in initials:
        on = integrate(initial, (PROBE_DURATION,), PROBE, level)
        off = integrate(initial, (PROBE_DURATION,), 0.0, level)
        increments.append(float(on[-1, 0] - off[-1, 0]))
        square_increments.append(float(on[-1, 0]**2 - off[-1, 0]**2))
        worst_balance = max(worst_balance, balance_residual(initial, on),
                            balance_residual(initial, off))
    return {"signed_C_increments": increments,
            "signed_C_contrast": increments[0] - increments[1],
            "C_squared_contrast": square_increments[0] - square_increments[1],
            "max_balance_residual": worst_balance}


def one_level(level: tuple[float, float]) -> dict:
    initial = [np.array([1.0, 0.0, sign]) for sign in (1.0, -1.0)]
    trajectories = [integrate(x, SAMPLES, 0.0, level) for x in initial]
    target = reference_state()
    if min(float(np.min(x[:, 0])) for x in trajectories) <= 0.0:
        raise AssertionError("positive-C sign invariant violated numerically")
    distances = [float(np.max(np.abs(x[-1, :3] - target))) for x in trajectories]
    balances = [balance_residual(x, rows) for x, rows in zip(initial, trajectories)]
    probes = {str(t): paired_probe([rows[SAMPLES.index(t), :3] for rows in trajectories], level)
              for t in WAITS}
    plus, minus = target.copy(), target.copy()
    minus[0] *= -1.0
    stable = [integrate(x, (80.0,), 0.0, level) for x in (plus, minus)]
    basin_probe = paired_probe([x[-1, :3] for x in stable], level)
    sample_differences = [float(np.max(np.abs(trajectories[0][i, :3] -
                                               trajectories[1][i, :3])))
                          for i in range(len(SAMPLES))]
    result = {"rtol": level[0], "atol": level[1],
              "relaxed_state": target.tolist(),
              "waits": list(SAMPLES), "original_pair_state_differences": sample_differences,
              "original_pair_distance_to_positive_minimum_at_80": distances,
              "original_pair_max_sampled_energy_balance_residual": max(balances),
              "original_pair_probes": probes,
              "stable_basin_states_at_80": [x[-1, :3].tolist() for x in stable],
              "stable_basin_probe": basin_probe}
    observed_balances = balances + [p["max_balance_residual"] for p in probes.values()]
    observed_balances.append(basin_probe["max_balance_residual"])
    assert max(distances) < COMPUTATIONAL_LIMIT
    assert max(observed_balances) < COMPUTATIONAL_LIMIT
    assert abs(probes["80.0"]["signed_C_contrast"]) < COMPUTATIONAL_LIMIT
    assert abs(basin_probe["signed_C_contrast"]) > 10 * COMPUTATIONAL_LIMIT
    assert abs(basin_probe["C_squared_contrast"]) < COMPUTATIONAL_LIMIT
    return result


def run_checks() -> dict:
    coarse, fine = (one_level(level) for level in LEVELS)
    # Compare all reported state-difference and probe contrasts, not a solver
    # success flag alone. This is observed convergence, not a certified enclosure.
    differences = [abs(a-b) for a, b in zip(coarse["original_pair_state_differences"],
                                           fine["original_pair_state_differences"])]
    for t in WAITS:
        for key in ("signed_C_contrast", "C_squared_contrast"):
            differences.append(abs(coarse["original_pair_probes"][str(t)][key] -
                                   fine["original_pair_probes"][str(t)][key]))
    for key in ("signed_C_contrast", "C_squared_contrast"):
        differences.append(abs(coarse["stable_basin_probe"][key] - fine["stable_basin_probe"][key]))
    refinement = max(differences)
    assert refinement < COMPUTATIONAL_LIMIT
    return {"scope": "FORMAL homogeneous fixture plus bounded numerical controls",
            "scipy_version": scipy.__version__, "physical_acceptance": False,
            "computational_limit": COMPUTATIONAL_LIMIT,
            "max_reported_contrast_refinement_difference": refinement,
            "levels": [coarse, fine],
            "limitations": ["No PDE/global parameter claim", "No finite-wait exact erasure",
                            "No noise-robust physical retention time", "No learned-rule update",
                            "Signed C must be admissible and distinguishable for basin readout"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(run_checks(), sort_keys=True), file=sys.stderr, flush=True)
