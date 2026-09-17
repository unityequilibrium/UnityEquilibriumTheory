"""Generate the non-averaged final UET main-theory closure package."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs/core"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from docs.core.core_paths import canonical_artifact_path

ARTIFACTS = CORE / "07_artifacts"
CANONICAL_REPORT_PATH = CORE / "08_history" / "research_notes" / "UET_MAIN_THEORY_CLOSURE_REPORT.md"
LEGACY_REPORT_PATH = CORE / "UET_MAIN_THEORY_CLOSURE_REPORT.md"


INPUTS = {
    "wave0": "uet_main_theory_wave0_gate.json",
    "wave1": "uet_main_theory_ontology_gate.json",
    "wave2": "uet_main_theory_wave2_gate.json",
    "wave3": "uet_main_theory_wave3_gate.json",
    "wave4": "uet_main_theory_wave4_gate.json",
    "wave5": "uet_main_theory_wave5_gate.json",
    "wave6": "uet_main_theory_wave6_gate.json",
    "wave7": "uet_main_theory_wave7_gate.json",
    "wave8": "uet_main_theory_wave8_gate.json",
    "wave9": "uet_main_theory_wave9_gate.json",
    "wave10": "uet_main_theory_wave10_gate.json",
    "wave11": "uet_main_theory_wave11_gate.json",
    "foundation": "uet_foundation_dependency_gate.json",
    "registry": "uet_equation_correspondence_registry.json",
}


def _read(name: str) -> dict:
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def _sha(name: str) -> str:
    return hashlib.sha256(canonical_artifact_path(name).read_bytes()).hexdigest()


def build_artifacts() -> tuple[dict, dict, dict, str]:
    now = datetime.now(timezone.utc).isoformat()
    inputs = {key: _read(name) for key, name in INPUTS.items()}
    identities = {
        key: {
            "path": canonical_artifact_path(name).relative_to(ROOT).as_posix(),
            "sha256": _sha(name),
        }
        for key, name in INPUTS.items()
    }
    categories = {
        "methodological_closure": {"status": "PASS", "reason": "axioms, registry, per-wave gates, tests, update log, and dependency decisions are machine-readable"},
        "ontology_closure": {"status": "PASS_CONTRACT_ONLY", "reason": "C lanes, Phi, physical memory, R_gen, R_obs, and interpretation boundaries are separated; lane realizations remain incomplete"},
        "mathematical_eft_closure": {"status": "PARTIAL_BLOCKED", "reason": "conservative parent and linear controls pass internally; full SK action and curved 3+1 parent evolution are absent"},
        "numerical_closure": {"status": "PARTIAL_BLOCKED", "reason": "fixed-background hyperbolic control converges; curved metric constraints and thermal causal leakage fail/open"},
        "physical_correspondence_closure": {"status": "PARTIAL_ANALYTIC_ONLY", "reason": "operational QM and analytic GR controls reproduce standards; dimensional and curved physical mappings remain open"},
        "dimensional_observable_closure": {"status": "BLOCKED", "reason": "numeric TTG package, independent alpha_Phi_K, and causal repair are missing"},
        "empirical_status": {"status": "BLOCKED_NO_EXTERNAL_HOLDOUT", "reason": "no main-theory dimensional external holdout comparison has been executed"},
        "fundamental_unification_status": {"status": "HYPOTHESIS_TRACK_BLOCKED", "reason": "local gauge, spinor, CPT, anomaly, renormalization, and mass-generation gates are open"},
    }
    closure = {
        "schema_version": "1.0", "artifact": "uet_main_theory_closure_gate",
        "generated_at": now, "overall_status": "BLOCKED",
        "categories": categories,
        "aggregation_policy": "NO_AVERAGING; every blocked category remains controlling for claims that depend on it",
        "primary_eft_status": "CANDIDATE_PARTIALLY_CLOSED_EFFECTIVE_THEORY",
        "completed_internal_spines": ["minimal ontology", "conservative covariant parent formula", "lane-specific coarse graining", "linear classical KMS constitutive bridge", "fixed-Minkowski hyperbolic control", "operational QM", "prediction-invariant interpretation adapters", "analytic GR correspondence controls"],
        "controlling_blockers": ["full_sk_kms_derivation", "curved_3p1_dynamical_metric_constraints", "dimensional_observable_calibration", "external_holdout", "fundamental_local_symmetry_and_spinor_completion"],
        "input_identity": identities,
        "downstream_unlock": inputs["wave11"]["downstream_unlock_status"],
        "claim_boundary": "methodological and several internal formula/control layers pass; the main physical theory is not closed or externally validated",
    }
    matrix = {
        "schema_version": "2.0", "artifact": "uet_standard_physics_correspondence_matrix_v2",
        "generated_at": now,
        "rows": [
            {"uet_layer": "C_charge", "standard_counterpart": "O(2) Noether charge density", "status": "PARTIAL_TREE_LEVEL", "observable": "charge/current; dimensional detector map open"},
            {"uet_layer": "C_phase", "standard_counterpart": "coarse order parameter", "status": "PASS_INTERNAL_DIAGNOSTIC", "observable": "phase fraction/interface/structure factor; external universality blocked"},
            {"uet_layer": "C_density", "standard_counterpart": "declared mass or number density input", "status": "MAPPING_INPUT_ONLY", "observable": "density profile; C does not derive mass"},
            {"uet_layer": "C_telegraph", "standard_counterpart": "finite-speed order response", "status": "PASS_MINKOWSKI_CONTROL", "observable": "arrival/dispersion; curved and dimensional maps open"},
            {"uet_layer": "Phi", "standard_counterpart": "effective response scalar", "status": "CANDIDATE", "observable": "normalized response; alpha_Phi_K open"},
            {"uet_layer": "physical memory", "standard_counterpart": "generalized Langevin/Maxwell memory", "status": "LINEAR_CLASSICAL_CONTROL", "observable": "response lag; microscopic SK/KMS open"},
            {"uet_layer": "R_gen", "standard_counterpart": "derived dissipation/history record", "status": "DERIVED_ONLY", "observable": "post-evolution trace; never particle or reservoir"},
            {"uet_layer": "R_obs", "standard_counterpart": "detector/observer record", "status": "OPERATIONAL_QM_BASELINE", "observable": "instrument outcome"},
            {"uet_layer": "closed gravitational branch", "standard_counterpart": "Einstein/GR controls", "status": "ANALYTIC_INPUT_CONTROLS", "observable": "curved gauge-invariant numerical map blocked"},
            {"uet_layer": "QBism/RQM", "standard_counterpart": "interpretation metadata", "status": "PREDICTION_INVARIANT", "observable": "same Born probabilities"},
        ],
        "claim_boundary": "counterpart status is lane-specific and cannot be promoted to a universal identity",
    }
    falsification = {
        "schema_version": "1.0", "artifact": "uet_main_theory_falsification_register",
        "generated_at": now,
        "criteria": [
            {"branch": "conservative_parent", "reject_or_reduce_if": "component equations cannot be obtained from one parent action or GR null nesting fails", "current_state": "PASS_INTERNAL_FORMULA"},
            {"branch": "coarse_graining", "reject_or_reduce_if": "mapping assumes the desired observable or silently identifies distinct C lanes", "current_state": "PASS_DECLARED_FIELD_MAP_ONLY"},
            {"branch": "open_system", "reject_or_reduce_if": "KMS, PSD, entropy, or exchange accounting fails, or trace must feed back as a state", "current_state": "PASS_LINEAR_CLASSICAL_CONTROL_ONLY"},
            {"branch": "causal_spine", "reject_or_reduce_if": "principal system is not strongly hyperbolic, becomes superluminal, or requires clipping", "current_state": "PASS_MINKOWSKI_CONTROL_CURVED_BLOCKED"},
            {"branch": "thermal_observable", "reject_or_reduce_if": "agreement requires in-sample alpha_Phi_K fitting, causal leakage persists, or holdout is consumed for tuning", "current_state": "BLOCKED"},
            {"branch": "quantum_interface", "reject_or_reduce_if": "state/POVM positivity, CPTP, Born normalization, no-signalling, or interpretation invariance fails", "current_state": "PASS_STANDARD_BASELINE"},
            {"branch": "gravity", "reject_or_reduce_if": "GR limit requires deleting equations, curved constraints fail, or observables depend on gauge choice", "current_state": "ANALYTIC_CONTROLS_ONLY"},
            {"branch": "fundamental_unification", "reject_or_reduce_if": "ghost, anomaly, nonunitarity, nonrenormalizability outside declared EFT, or no falsifiable observable", "current_state": "HYPOTHESIS_TRACK_BLOCKED"},
            {"branch": "applications", "reject_or_reduce_if": "improvement exists only in calibration data and disappears on uncertainty-aware holdout", "current_state": "BLOCKED"},
        ],
        "rule": "a branch failure cannot be hidden by averaging with a passing methodological category",
    }
    report = f"""# UET Main-Theory Closure Report

Generated: `{now}`

## Outcome

The program completed the planned foundation-control sequence, but the main
physical theory is **not closed**. The current primary result is a candidate,
partially closed covariant effective-theory architecture with several passing
internal formula and control layers. Dimensional observable, external holdout,
curved 3+1, and fundamental-unification gates remain blocked.

## Non-averaged closure status

| Category | Status | Boundary |
|---|---|---|
""" + "\n".join(f"| {name} | `{item['status']}` | {item['reason']} |" for name, item in categories.items()) + """

## What is now structurally clear

- `C` is a lane-specific collective coordinate, not universal mass or energy.
- `Phi` is an effective response scalar, not metric, information, or particle.
- Physical memory may affect dynamics; `R_gen` is computed afterward and has no automatic feedback.
- Source, carrier, detector, observer record, and interpretation metadata are separate layers.
- Operational QM is the baseline; QBism/RQM adapters do not change empirical predictions.
- The GR branch has exact/algebraic standard controls, but no curved metric solver.

## Controlling blockers

1. Full Schwinger-Keldysh/dynamical-KMS derivation and external transport coefficients.
2. Strongly hyperbolic curved 3+1 evolution with dynamical metric and constraints.
3. A permitted numeric thermal package, independent `alpha_Phi_K`, and causal leakage repair.
4. At least one uncertainty-aware external holdout comparison.
5. Local gauge/spinor/anomaly/renormalization closure for the optional fundamental track.

## Allowed claim

UET currently provides a disciplined candidate effective-theory architecture
with internally checked conservative, coarse-graining, linear open-system,
fixed-background causal, operational-quantum, and analytic-correspondence
components. It is not yet a closed physical theory, GR replacement, quantum
derivation, dark-matter solution, or fundamental unification.
"""
    return closure, matrix, falsification, report


def main() -> int:
    closure, matrix, falsification, report = build_artifacts()
    for name, payload in (("uet_main_theory_closure_gate.json", closure), ("uet_standard_physics_correspondence_matrix_v2.json", matrix), ("uet_main_theory_falsification_register.json", falsification)):
        canonical_artifact_path(name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    CANONICAL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANONICAL_REPORT_PATH.write_text(report, encoding="utf-8")
    LEGACY_REPORT_PATH.write_text(
        "# Compatibility redirect\n\n"
        "Canonical source: [UET Main-Theory Closure Report](08_history/research_notes/UET_MAIN_THEORY_CLOSURE_REPORT.md)\n",
        encoding="utf-8",
    )
    print(f"overall_status={closure['overall_status']}")
    print(f"primary_eft_status={closure['primary_eft_status']}")
    print("controlling_blockers=" + ",".join(closure["controlling_blockers"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
