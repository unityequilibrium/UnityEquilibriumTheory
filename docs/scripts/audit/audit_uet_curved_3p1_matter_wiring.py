"""Audit the prescribed Topic 13 stress-energy wiring into the Core GH parent."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_curved_3p1_matter_wiring import (
    RelativisticFluidState,
    compute_nonlinear_prescribed_matter_gh_rhs,
    curved_3p1_matter_wiring_contract,
    project_stress_energy_3p1,
    relativistic_fluid_stress_energy,
    trace_reversed_stress_energy,
)


ARTIFACTS = ROOT / "docs/core/artifacts"
SOURCE_3P1 = ROOT / "docs/data/external/gr_3p1/gourgoulhon_2007/source_record.json"
SOURCE_GH = ROOT / "docs/data/external/gr_3p1/lindblom_et_al_2006_gh/source_record.json"
T13_COMPOSITION = ARTIFACTS / "t13_he4_core_thermodynamic_bridge_composition_audit.json"
T13_EOS = ARTIFACTS / "t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json"
T13_SI = ARTIFACTS / "t13_he4_o2_si_beta_mapping_audit.json"
MODULE = ROOT / "docs/core/uet_curved_3p1_matter_wiring.py"
VERIFY = ARTIFACTS / "curved_3p1_topic13_matter_wiring_verification.json"
FORMULA = ARTIFACTS / "curved_3p1_topic13_matter_wiring_formula_audit.json"
GATE = ARTIFACTS / "curved_3p1_topic13_matter_wiring_gate.json"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _minkowski(shape: tuple[int, ...] = ()) -> np.ndarray:
    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    return np.broadcast_to(metric, shape + (4, 4)).copy()


def _velocity(shape: tuple[int, ...], speed: float = 0.0) -> np.ndarray:
    gamma = 1.0 / np.sqrt(1.0 - speed**2)
    velocity = np.zeros(shape + (4,), dtype=float)
    velocity[..., 0] = gamma
    velocity[..., 1] = gamma * speed
    return velocity


def build_artifacts() -> tuple[dict, dict, dict]:
    generated_at = datetime.now(timezone.utc).isoformat()
    source_3p1 = _read(SOURCE_3P1)
    source_gh = _read(SOURCE_GH)
    composition = _read(T13_COMPOSITION)
    eos = _read(T13_EOS)
    si_mapping = _read(T13_SI)
    contract = curved_3p1_matter_wiring_contract()

    energy = float(eos["state"]["energy_density"])
    pressure = float(eos["state"]["pressure"])
    e0 = float(si_mapping["record"]["energy_density_scale_J_m3"])
    metric = _minkowski()

    rest_stress = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(energy, pressure, _velocity(())),
    )
    rest_projection = project_stress_energy_3p1(
        metric, rest_stress, unit_lane="natural"
    )

    speed = 0.2
    gamma = 1.0 / np.sqrt(1.0 - speed**2)
    boost_stress = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(energy, pressure, _velocity((), speed)),
    )
    boost_projection = project_stress_energy_3p1(
        metric, boost_stress, unit_lane="natural"
    )
    expected_boost_rho = (energy + pressure) * gamma**2 - pressure
    expected_boost_momentum = (energy + pressure) * gamma**2 * speed

    shifted_metric = _minkowski()
    shifted_metric[0, 0] = -0.96
    shifted_metric[0, 1] = shifted_metric[1, 0] = 0.2
    shifted_normal = np.array([1.0, -0.2, 0.0, 0.0])
    shifted_stress = relativistic_fluid_stress_energy(
        shifted_metric,
        RelativisticFluidState(energy, pressure, shifted_normal),
    )
    shifted_projection = project_stress_energy_3p1(
        shifted_metric, shifted_stress, unit_lane="natural"
    )

    si_stress = relativistic_fluid_stress_energy(
        metric,
        RelativisticFluidState(
            e0 * energy,
            e0 * pressure,
            _velocity(()),
            unit_lane="SI",
        ),
    )
    scaling_residual = float(np.max(np.abs(si_stress - e0 * rest_stress)))

    grid_shape = (5, 5, 5)
    grid_metric = _minkowski(grid_shape)
    grid_stress = np.broadcast_to(
        rest_stress, grid_shape + (4, 4)
    ).copy()
    zeros_pi = np.zeros(grid_shape + (4, 4))
    zeros_phi = np.zeros(grid_shape + (3, 4, 4))
    zeros_source = np.zeros(grid_shape + (4,))
    zeros_source_derivative = np.zeros(grid_shape + (4, 4))
    coupling_witness = 0.25
    gh_result = compute_nonlinear_prescribed_matter_gh_rhs(
        grid_metric,
        zeros_pi,
        zeros_phi,
        zeros_source,
        zeros_source_derivative,
        (0.2, 0.2, 0.2),
        grid_stress,
        einstein_coupling=coupling_witness,
        matter_unit_lane="natural_witness",
    )
    expected_source = -2.0 * coupling_witness * trace_reversed_stress_energy(
        grid_metric, grid_stress
    )
    source_residual = float(
        np.max(np.abs(gh_result.matter_source_term - expected_source))
    )
    vacuum_result = compute_nonlinear_prescribed_matter_gh_rhs(
        grid_metric,
        zeros_pi,
        zeros_phi,
        zeros_source,
        zeros_source_derivative,
        (0.2, 0.2, 0.2),
        np.zeros_like(grid_stress),
        einstein_coupling=coupling_witness,
        matter_unit_lane="natural_witness",
    )
    vacuum_residual = float(
        np.max(
            np.abs(
                vacuum_result.normal_derivative_rhs
                - vacuum_result.vacuum_rhs.normal_derivative_rhs
            )
        )
    )

    tolerance = 1.0e-12
    checks = {
        "gourgoulhon_source_locked": source_3p1.get("arxiv_id")
        == "gr-qc/0703035",
        "lindblom_source_locked": source_gh.get("arxiv_id")
        == "gr-qc/0512093",
        "topic13_core_handoff_closed": composition.get("status")
        == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY",
        "topic13_claim_promotion_false": composition.get("claim_promotion")
        is False,
        "rest_energy_projection_exact": abs(
            float(rest_projection.energy_density) - energy
        )
        <= tolerance,
        "rest_pressure_projection_exact": np.max(
            np.abs(rest_projection.spatial_stress - pressure * np.eye(3))
        )
        <= tolerance,
        "rest_reconstruction_exact": rest_projection.reconstruction_residual
        <= tolerance,
        "boost_energy_projection_exact": abs(
            float(boost_projection.energy_density) - expected_boost_rho
        )
        <= tolerance,
        "boost_momentum_projection_exact": abs(
            float(boost_projection.momentum_density[0])
            - expected_boost_momentum
        )
        <= tolerance,
        "boost_reconstruction_exact": boost_projection.reconstruction_residual
        <= tolerance,
        "nonzero_shift_energy_projection_exact": abs(
            float(shifted_projection.energy_density) - energy
        )
        <= tolerance,
        "nonzero_shift_momentum_projection_exact": np.max(
            np.abs(shifted_projection.momentum_density)
        )
        <= tolerance,
        "nonzero_shift_reconstruction_exact": shifted_projection.reconstruction_residual
        <= tolerance,
        "natural_to_si_scale_multiplicative": scaling_residual <= tolerance,
        "gh_trace_reversed_source_exact": source_residual <= tolerance,
        "vacuum_source_is_null": vacuum_residual <= tolerance,
        "matter_state_not_evolved": gh_result.diagnostics[
            "matter_state_evolution"
        ]
        is False,
        "stress_conservation_not_claimed": gh_result.diagnostics[
            "stress_energy_conservation_evolved"
        ]
        is False,
        "no_clipping": gh_result.diagnostics["field_clipping"] is False,
        "no_fitting": gh_result.diagnostics["parameter_fitting"] is False,
        "phi_excluded_from_stress_state": contract["ontology"]["Phi"].startswith(
            "excluded"
        ),
        "r_gen_excluded_from_stress_state": contract["ontology"][
            "R_gen"
        ].startswith("excluded"),
        "numeric_einstein_coupling_is_witness_only": "numerical SI Einstein coupling provenance"
        in contract["not_implemented"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    passed = all(checks.values())
    status = (
        "PASS_CURVED_3P1_TOPIC13_PRESCRIBED_MATTER_WIRING"
        if passed
        else "FAIL_CURVED_3P1_TOPIC13_PRESCRIBED_MATTER_WIRING"
    )
    evidence = [
        SOURCE_3P1,
        SOURCE_GH,
        T13_COMPOSITION,
        T13_EOS,
        T13_SI,
        MODULE,
    ]
    evidence_artifacts = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": _sha256(path),
        }
        for path in evidence
    ]
    metrics = {
        "topic13_natural_energy_density": energy,
        "topic13_natural_pressure": pressure,
        "he4_e0_J_m3": e0,
        "rest_reconstruction_max_abs": rest_projection.reconstruction_residual,
        "boost_reconstruction_max_abs": boost_projection.reconstruction_residual,
        "nonzero_shift_reconstruction_max_abs": shifted_projection.reconstruction_residual,
        "nonzero_shift_momentum_max_abs": float(
            np.max(np.abs(shifted_projection.momentum_density))
        ),
        "natural_to_si_scaling_max_abs": scaling_residual,
        "gh_matter_source_max_abs_residual": source_residual,
        "vacuum_null_source_max_abs_residual": vacuum_residual,
    }

    verification = {
        "schema_version": "curved-3p1-topic13-matter-wiring-v1",
        "artifact": "curved_3p1_topic13_matter_wiring_verification",
        "generated_at": generated_at,
        "status": status,
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_TOPIC13_PRESCRIBED_MATTER_WIRING_READY",
            "topic": "core",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "lane-bounded relativistic-fluid stress-energy construction",
                "Eulerian rho, S_i, and S_ij projection and reconstruction",
                "trace-reversed prescribed GH matter source",
                "vacuum null-source and natural-to-SI scaling controls",
            ]
            if passed
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_lanes"],
            "derivation_class": "STANDARD_PHYSICS_TRANSCRIPTION_WITH_TOPIC13_EXTERNAL_INPUT_COMPOSITION",
            "observable": "prescribed He-4/O(2) stress-energy source; no detector observable",
            "data_role": "CORE_INTEGRATION_INPUT_NOT_EXTERNAL_VALIDATION",
            "evidence_artifacts": evidence_artifacts,
            "verification_status": status,
            "open_blockers": contract["not_implemented"],
            "dependency_unlocked": "constraint-preserving boundary and dimensional-observable waves only",
            "claim_boundary": contract["claim_boundary"],
        },
        "input_identity": {
            "topic13_result": T13_COMPOSITION.relative_to(ROOT).as_posix(),
            "natural_eos": T13_EOS.relative_to(ROOT).as_posix(),
            "si_scale": T13_SI.relative_to(ROOT).as_posix(),
            "einstein_coupling_witness": coupling_witness,
            "einstein_coupling_role": "dimensionless internal operator witness; not a physical SI calibration",
        },
        "thresholds": {"algebraic_max_abs": tolerance},
        "metrics": metrics,
        "checks": checks,
        "contract": contract,
        "claim_promotion": False,
        "controlling_blocker": None if passed else "matter_wiring_verification_failed",
        "next_action": "Integrate the passed prescribed source into the curved 3+1 parent; retain self-consistent matter evolution and boundaries as open.",
    }

    formula = {
        "schema_version": "curved-3p1-topic13-matter-formula-audit-v1",
        "artifact": "curved_3p1_topic13_matter_wiring_formula_audit",
        "generated_at": generated_at,
        "status": "PASS_SOURCE_LOCKED_TOPIC13_MATTER_FORMULAS"
        if passed
        else "FAIL",
        "relations": [
            {
                "formula_id": "UET-CURVED3P1-MATTER-TAB-021",
                "relation": contract["equations"]["fluid_stress_energy"],
                "unit_contract": "epsilon, p, q_a, and pi_ab share one declared energy-density lane",
                "derivation_status": "standard relativistic dissipative-fluid decomposition",
            },
            {
                "formula_id": "UET-CURVED3P1-MATTER-ADM-022",
                "relation": "; ".join(
                    [
                        contract["equations"]["adm_energy"],
                        contract["equations"]["adm_momentum"],
                        contract["equations"]["adm_stress"],
                    ]
                ),
                "unit_contract": "rho, S_i, and S_ij inherit the T_ab energy-density lane",
                "derivation_status": "standard 3+1 projection",
            },
            {
                "formula_id": "UET-CURVED3P1-MATTER-GH-023",
                "relation": contract["equations"]["gh_matter_source"],
                "unit_contract": "kappa_E*T_ab has inverse-coordinate-length squared units",
                "derivation_status": "standard trace-reversed Einstein source transcription",
            },
        ],
        "sources": evidence_artifacts[:2],
        "ontology": contract["ontology"],
        "open_items": contract["not_implemented"],
        "claim_boundary": contract["claim_boundary"],
    }

    gate = {
        "schema_version": "curved-3p1-topic13-matter-gate-v1",
        "artifact": "curved_3p1_topic13_matter_wiring_gate",
        "generated_at": generated_at,
        "status": "PARTIAL_CURVED_3P1_PRESCRIBED_MATTER_SOURCE_READY"
        if passed
        else "BLOCKED",
        "requirements": {
            "topic13_core_handoff": "PASS" if checks["topic13_core_handoff_closed"] else "FAIL",
            "stress_energy_construction": "PASS" if checks["rest_reconstruction_exact"] else "FAIL",
            "adm_projection": "PASS" if checks["boost_reconstruction_exact"] else "FAIL",
            "gh_trace_reversed_source": "PASS" if checks["gh_trace_reversed_source_exact"] else "FAIL",
            "natural_si_scale_compatibility": "PASS" if checks["natural_to_si_scale_multiplicative"] else "FAIL",
            "self_consistent_matter_evolution": "OPEN",
            "stress_energy_conservation_propagation": "OPEN",
            "physical_si_einstein_coupling": "OPEN",
            "constraint_preserving_boundaries": "OPEN",
            "detector_observable_mapping": "OPEN",
        },
        "evidence_artifacts": evidence_artifacts,
        "verification_artifact": VERIFY.relative_to(ROOT).as_posix(),
        "formula_artifact": FORMULA.relative_to(ROOT).as_posix(),
        "controlling_blocker": "curved_3p1_self_consistent_matter_evolution_and_constraint_preserving_boundaries_open",
        "claim_promotion": False,
        "claim_boundary": contract["claim_boundary"],
    }
    return verification, formula, gate


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    verification, formula, gate = build_artifacts()
    VERIFY.write_text(
        json.dumps(verification, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    FORMULA.write_text(
        json.dumps(formula, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    gate["verification_sha256"] = _sha256(VERIFY)
    gate["formula_sha256"] = _sha256(FORMULA)
    GATE.write_text(
        json.dumps(gate, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": verification["status"],
                "gate_status": gate["status"],
                "checks_passed": sum(verification["checks"].values()),
                "checks_total": len(verification["checks"]),
            },
            indent=2,
        )
    )
    return 0 if verification["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
