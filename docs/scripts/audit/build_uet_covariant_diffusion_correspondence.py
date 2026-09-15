"""Generate the canonical correspondence addendum for the diffusion bridge.

This is a traceability generator.  It does not promote the constitutive bridge
to a microscopic transport law or remove any of its blocked gates.
"""

from __future__ import annotations

import hashlib
import json
import argparse
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs" / "core" / "artifacts"
OUTPUT = ARTIFACTS / (
    "uet_equation_correspondence_registry_covariant_diffusion_addendum.json"
)
CENTRAL = ARTIFACTS / "uet_equation_correspondence_registry.json"
FORMULA_AUDIT = ARTIFACTS / "covariant_diffusion_formula_audit.json"
VERIFICATION = ARTIFACTS / "covariant_diffusive_current_verification.json"
CONTRACT = ARTIFACTS / "covariant_diffusion_contract.json"
SOURCE = ROOT / "docs" / "core" / "uet_covariant_diffusion.py"
SPEC = ROOT / "docs" / "core" / "UET_GR_NONCLOSED_RESEARCH_SPEC.md"

FORMULA_IDS = [
    "uet.covariant_diffusion.frame_decomposition",
    "uet.covariant_diffusion.finite_relaxation_current",
    "uet.covariant_diffusion.energy_identity",
    "uet.covariant_diffusion.adiabatic_model_b_limit",
]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry(
    equation_id: str,
    relation: str,
    variables: dict[str, str],
    role: str,
    counterpart: str,
    implementation_paths: list[str],
    proof_status: str,
    dependencies: list[str],
    claim_boundary: str,
    failure_mode: str,
    next_step: str,
    *,
    assumptions: list[str],
    conservation: str,
    limits: list[str],
    classification: str = "constitutive_lane_specific_equation",
) -> dict[str, Any]:
    return {
        "equation_id": equation_id,
        "version": "covariant-diffusion-v1",
        "classification": classification,
        "relation_or_code_path": relation,
        "variables": variables,
        "mathematical_role": role,
        "standard_physics_counterpart": counterpart,
        "observable_mapping": {
            "status": "PARTIAL",
            "observable": "normalized frame density/current and relaxation diagnostics",
            "reason": "material-specific SI units, detector response, and external physical validation are open",
        },
        "unit_lane": "natural_to_normalized",
        "parameter_dimensions": "density_scale, length_scale, time_scale, mobility, and relaxation are declared; SI transport dimensions remain open",
        "source_or_origin": "existing covariant O(2) current bridge and its declared constitutive reduction",
        "assumptions": assumptions,
        "symmetry_and_conservation": conservation,
        "limiting_cases": limits,
        "implementation_paths": [
            path.split("::", 1)[0] for path in implementation_paths
        ],
        "implementation_symbols": implementation_paths,
        "verifier_paths": [
            "docs/scripts/audit/audit_uet_gr_covariant_diffusion.py",
            "docs/core/test/test_covariant_diffusion.py",
            "docs/core/test/test_gr_covariant_diffusion_alignment.py",
            "docs/core/07_artifacts/verification/covariant_diffusive_current_verification.json",
        ],
        "evidence_class": "INTERNAL_CONSTITUTIVE_NUMERICAL",
        "proof_status": proof_status,
        "downstream_dependencies": dependencies,
        "claim_boundary": claim_boundary,
        "failure_mode": failure_mode,
        "next_hardening_step": next_step,
    }


def build() -> dict[str, Any]:
    formula_audit = load(FORMULA_AUDIT)
    verification = load(VERIFICATION)
    contract = load(CONTRACT)
    local_ids = {
        str(item["id"])
        for item in formula_audit.get("formula_registry", [])
        if isinstance(item, dict) and item.get("id")
    }
    expected_local_ids = {
        "current_frame_decomposition",
        "finite_relaxation_current",
        "semi_discrete_energy_identity",
        "model_b_adiabatic_limit",
    }
    if local_ids != expected_local_ids:
        raise ValueError(
            "diffusion formula audit registry drift: "
            f"expected {sorted(expected_local_ids)}, got {sorted(local_ids)}"
        )
    if verification.get("audit_status") != "PASS":
        raise ValueError("diffusion verification is not PASS; do not create a linked package")
    if contract.get("full_gradient_phase_field_causality") != "BLOCKED_FOURTH_ORDER_UV":
        raise ValueError("diffusion causal blocker wording changed; review before linking")

    module_path = "docs/core/uet_covariant_diffusion.py"
    entries = [
        entry(
            FORMULA_IDS[0],
            "N^mu = n u^mu + j^mu; u_mu j^mu = 0",
            {
                "N_mu": "on-shell O(2) Noether current",
                "u_mu": "normalized timelike frame velocity",
                "n": "frame-projected charge density",
                "j_mu": "spatial current orthogonal to u_mu",
            },
            "frame decomposition and reconstruction of a covariant current",
            "relativistic current decomposition in a chosen timelike frame",
            [f"{module_path}::decompose_noether_current"],
            "current reconstruction and orthogonality pass local numerical checks; microscopic density matching is not established",
            ["uet.o2.finite_density_eos", "uet.main_theory.coarse_graining"],
            "frame decomposition and normalized mapping only; not a microscopic transport derivation",
            "identifying the projected charge density or normalized C with mass density without a lane contract",
            "close the coarse-graining and dimensional observable map",
            assumptions=[
                "metric signature (-,+,+,+)",
                "u_mu u^mu = -1",
                "the current is supplied by the declared on-shell O(2) pilot",
            ],
            conservation="the decomposition is kinematic and reconstructs N^mu exactly; it does not add a source or alter current conservation",
            limits=[
                "zero spatial current gives a comoving current",
                "changing the frame changes n and j without changing N^mu",
            ],
            classification="kinematic_mapping",
        ),
        entry(
            FORMULA_IDS[1],
            "partial_t C + partial_x J = 0; tau_J partial_t J + J = -M_C partial_x mu_C",
            {
                "C": "normalized coarse-grained charge/current coordinate",
                "J": "finite-volume face current",
                "mu_C": "conditioned matter chemical potential",
                "tau_J": "current relaxation time",
            },
            "finite-relaxation constitutive bridge coupled to exact one-dimensional continuity",
            "Maxwell-Cattaneo-type current relaxation with a conservative continuity equation",
            [f"{module_path}::causal_current_rhs"],
            "local constitutive and conservation checks pass; transport coefficients and full gradient-phase closure remain open",
            [FORMULA_IDS[0], "uet.matter_space_flux.conservation"],
            "candidate normalized constitutive current bridge; not a relativistic microscopic transport law",
            "calling finite current relaxation a complete causal Cahn-Hilliard or covariant transport derivation",
            "close coefficient provenance, KMS/Kubo matching, and the UV phase-field branch",
            assumptions=[
                "one-dimensional periodic or zero-flux finite-volume lane",
                "declared natural-to-normalized scales",
                "C changes only through the face-current divergence",
            ],
            conservation="continuity is conservative under the declared closed boundaries; current relaxation is a constitutive input",
            limits=[
                "tau_J tending to zero gives the formal Model-B current",
                "epsilon_nc = 0 removes the nested response coupling",
            ],
        ),
        entry(
            FORMULA_IDS[2],
            "d_t [F_C + tau_J integral(J^2)/(2 M_C)] = - integral(J^2/M_C)",
            {
                "F_C": "conditioned normalized matter free energy",
                "J": "face current",
                "M_C": "positive mobility coefficient",
                "tau_J": "current relaxation time",
            },
            "semi-discrete closed-system energy ledger for the current bridge",
            "dissipative energy balance for a finite-relaxation constitutive current",
            [f"{module_path}::current_energy_balance"],
            "the declared semi-discrete identity closes to numerical precision in periodic and zero-flux tests",
            [FORMULA_IDS[1]],
            "normalized numerical ledger only; it is not a dimensional thermodynamic energy proof",
            "reporting the normalized ledger as SI energy or treating the trace as an energy source",
            "define dimensional work/heat observables and independently validate the ledger scale",
            assumptions=[
                "periodic or zero-flux boundaries",
                "positive mobility and relaxation time",
                "the current-storage term is included in the extended energy",
            ],
            conservation="current dissipation is non-negative and the ledger exposes, rather than hides, the residual",
            limits=[
                "J = 0 removes current dissipation",
                "the energy identity is conditional on the declared constitutive update",
            ],
            classification="numerical_energy_ledger",
        ),
        entry(
            FORMULA_IDS[3],
            "J -> -M_C partial_x mu_C; partial_t C -> M_C partial_x^2 mu_C",
            {
                "J": "equilibrium face current",
                "C": "conserved normalized coordinate",
                "mu_C": "conditioned matter chemical potential",
                "M_C": "mobility coefficient",
            },
            "exact discrete adiabatic limit from the finite-relaxation bridge to Model B",
            "overdamped conserved gradient-flow comparator",
            [f"{module_path}::compare_adiabatic_limit"],
            "the bridge continuity update and Model-B RHS agree within the generated artifact tolerance",
            [FORMULA_IDS[1], "uet.matter_space_flux.conservation"],
            "limiting comparator only; it does not establish finite-cone causality for the original fourth-order gradient system",
            "using the overdamped limit as proof of a relativistic causal Cahn-Hilliard theory",
            "keep the Model-B limit as a comparator while resolving the first-order hyperbolic UV closure",
            assumptions=[
                "adiabatic current relaxation",
                "the same declared chemical potential is used on both sides",
                "one-dimensional finite-volume boundary rules are shared",
            ],
            conservation="the limiting continuity equation remains conservative under the declared boundaries",
            limits=[
                "finite tau_J retains current memory",
                "kappa_matter greater than zero retains the fourth-order high-k blocker",
            ],
            classification="limiting_relation",
        ),
    ]
    return {
        "schema_version": "1.0",
        "artifact": "uet_equation_correspondence_registry_covariant_diffusion_addendum",
        "generated_at": date.today().isoformat(),
        "generator": "docs/scripts/audit/build_uet_covariant_diffusion_correspondence.py",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
        "status": "CANDIDATE_ENTRY_MERGED_INTO_CENTRAL_REGISTRY",
        "equation_entries": entries,
        "open_gates": sorted(set(formula_audit.get("open_formula_gates", []))),
        "source_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (SOURCE, SPEC, FORMULA_AUDIT, VERIFICATION, CONTRACT)
        },
        "merge_metadata": {
            "merged_into": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
            "merged_on": date.today().isoformat(),
            "equation_ids": FORMULA_IDS,
            "claim_promotion": False,
        },
    }


def merge_into_central(payload: dict[str, Any]) -> None:
    """Merge the generated entries while preserving the canonical file layout."""

    raw = CENTRAL.read_text(encoding="utf-8")
    central = json.loads(raw)
    existing_ids = {
        str(item.get("equation_id"))
        for item in central.get("entries", [])
        if isinstance(item, dict) and item.get("equation_id")
    }
    equation_ids = list(payload["merge_metadata"]["equation_ids"])
    if existing_ids.intersection(equation_ids):
        raise ValueError("one or more diffusion equation IDs are already in the central registry")

    marker = '\n  ],\n  "merge_history": {'
    if raw.count(marker) != 1:
        raise ValueError("unexpected central registry layout; refusing an unsafe merge")
    serialized = json.dumps(
        payload["equation_entries"], ensure_ascii=False, indent=4
    )[1:-1].strip("\n")
    raw = raw.replace(
        marker,
        ",\n" + serialized + marker,
        1,
    )

    addendum_path = str(OUTPUT.relative_to(ROOT)).replace("\\", "/")
    addenda_marker = (
        '      "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_matter_space_flux_addendum.json"\n'
    )
    if addendum_path in raw:
        raise ValueError("diffusion addendum is already listed in the central registry")
    if raw.count(addenda_marker) != 1:
        raise ValueError("matter-space flux addendum marker is missing or ambiguous")
    raw = raw.replace(
        addenda_marker,
        addenda_marker.rstrip("\n")
        + ",\n"
        + f'      "{addendum_path}"\n',
        1,
    )

    merge_marker = '      "uet.matter_space_flux.shared_energy_ledger"\n    ],'
    if raw.count(merge_marker) != 1:
        raise ValueError("merge-history marker is missing or ambiguous")
    merge_lines = ",\n".join(f'      "{item}"' for item in equation_ids)
    raw = raw.replace(
        merge_marker,
        '      "uet.matter_space_flux.shared_energy_ledger",\n'
        + merge_lines
        + "\n    ],",
        1,
    )
    json.loads(raw)
    CENTRAL.write_text(raw, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--merge",
        action="store_true",
        help="also merge the generated entries into the canonical registry",
    )
    args = parser.parse_args()
    payload = build()
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if args.merge:
        merge_into_central(payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "equation_count": len(payload["equation_entries"]),
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "central_merged": args.merge,
                "claim_promotion": payload["merge_metadata"]["claim_promotion"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
