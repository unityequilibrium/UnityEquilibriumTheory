"""Generate the canonical correspondence addendum for the Noether map.

This generator records the already-audited O(2) current and hydrodynamic
coordinate relations.  It deliberately preserves the many-to-one boundary of
coarse graining and does not promote the map to a universal definition of C,
mass, or a microscopic equation of state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)

ARTIFACTS = CANONICAL_ARTIFACT_ROOT
OUTPUT = canonical_artifact_path(
    "uet_equation_correspondence_registry_noether_mapping_addendum.json",
    "correspondence",
)
CENTRAL = canonical_artifact_path(
    "uet_equation_correspondence_registry.json", "correspondence"
)
FORMULA_AUDIT = canonical_artifact_path("noether_phase_field_map_formula_audit.json")
VERIFICATION = canonical_artifact_path(
    "noether_phase_field_state_map_verification.json", "verification"
)
DEPENDENCY = canonical_artifact_path("noether_phase_field_dependency_gate.json", "gates")
SOURCE_NOETHER = canonical_existing_path(ROOT / "docs" / "core" / "uet_noether.py")
SOURCE_MAP = canonical_existing_path(ROOT / "docs" / "core" / "uet_noether_phase_field_map.py")
SOURCE_MATTER = canonical_existing_path(ROOT / "docs" / "core" / "uet_covariant_matter.py")
SOURCE_DIFFUSION = canonical_existing_path(ROOT / "docs" / "core" / "uet_covariant_diffusion.py")
SPEC = canonical_existing_path(ROOT / "docs" / "core" / "UET_GR_NONCLOSED_RESEARCH_SPEC.md")

FORMULA_IDS = [
    "uet.noether_mapping.frame_projected_charge_density",
    "uet.noether_mapping.affine_phase_coordinate",
    "uet.noether_mapping.normalized_current_coordinate",
    "uet.noether_mapping.continuity_residual_scaling",
    "uet.noether_mapping.o2_polar_current",
    "uet.noether_mapping.symmetric_double_well_conjugacy",
    "uet.noether_mapping.normalized_constitutive_scales",
]

LOCAL_FORMULA_IDS = {
    "frame_projected_charge_density",
    "affine_phase_coordinate",
    "normalized_current_coordinate",
    "continuity_residual_scaling",
    "O2_polar_current",
    "symmetric_double_well_conjugacy",
    "normalized_constitutive_scales",
}

VERIFIER_PATHS = [
    "docs/scripts/audit/audit_uet_noether_phase_field_map.py",
    "docs/core/test/test_noether_phase_field_map.py",
    "docs/core/test/test_gr_noether_phase_field_map_alignment.py",
    "docs/core/test/test_noether_phase_field_topic_0_11_dependency.py",
    "docs/core/07_artifacts/verification/noether_phase_field_state_map_verification.json",
]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_entry(
    equation_id: str,
    relation: str,
    variables: dict[str, str],
    role: str,
    counterpart: str,
    implementation_paths: list[str],
    implementation_symbols: list[str],
    proof_status: str,
    dependencies: list[str],
    claim_boundary: str,
    failure_mode: str,
    next_step: str,
    *,
    assumptions: list[str],
    conservation: str,
    limits: list[str],
    classification: str,
    evidence_class: str = "INTERNAL_MAPPING_DIAGNOSTIC",
) -> dict[str, Any]:
    return {
        "equation_id": equation_id,
        "version": "noether-mapping-v1",
        "classification": classification,
        "relation_or_code_path": relation,
        "variables": variables,
        "mathematical_role": role,
        "standard_physics_counterpart": counterpart,
        "observable_mapping": {
            "status": "PARTIAL",
            "observable": (
                "coarse signed O(2) charge/current coordinates and phase-field "
                "diagnostics"
            ),
            "reason": (
                "the fixed-scale coordinate layer is checked, while a covariant "
                "coarse-graining kernel, material units, detector response, and "
                "external validation remain open"
            ),
        },
        "unit_lane": "natural_to_normalized",
        "parameter_dimensions": (
            "natural charge/current scales and declared density, length, time, "
            "and chemical-potential scales; material SI mapping remains open"
        ),
        "source_or_origin": (
            "existing O(2) Noether-current identity plus a declared fixed-scale "
            "hydrodynamic coordinate map"
        ),
        "assumptions": assumptions,
        "symmetry_and_conservation": conservation,
        "limiting_cases": limits,
        "implementation_paths": implementation_paths,
        "implementation_symbols": implementation_symbols,
        "verifier_paths": VERIFIER_PATHS,
        "evidence_class": evidence_class,
        "proof_status": proof_status,
        "downstream_dependencies": dependencies,
        "claim_boundary": claim_boundary,
        "failure_mode": failure_mode,
        "next_hardening_step": next_step,
    }


def build() -> dict[str, Any]:
    formula_audit = load(FORMULA_AUDIT)
    verification = load(VERIFICATION)
    dependency = load(DEPENDENCY)
    local_ids = {
        str(item["id"])
        for item in formula_audit.get("formula_registry", [])
        if isinstance(item, dict) and item.get("id")
    }
    if local_ids != LOCAL_FORMULA_IDS:
        raise ValueError(
            "Noether formula audit registry drift: "
            f"expected {sorted(LOCAL_FORMULA_IDS)}, got {sorted(local_ids)}"
        )
    if formula_audit.get("status") != "WARN":
        raise ValueError(
            "Noether formula audit status changed; review the family boundary "
            "before creating a correspondence package"
        )
    if verification.get("audit_status") != "PASS":
        raise ValueError(
            "Noether state-map verification is not PASS; do not create a linked package"
        )
    if dependency.get("status") != "BLOCKED":
        raise ValueError(
            "Noether dependency status changed; review the controlling gate before linking"
        )

    shared_assumptions = [
        "metric signature (-,+,+,+) for the covariant current identity",
        "signed global-O2 Noether charge convention",
        "declared local cell-average coarse graining precedes the affine map",
        "positive fixed reference and scale parameters",
    ]
    shared_conservation = (
        "the O(2) current and continuity scaling are used as declared; the "
        "coordinate map introduces no source and does not prove microscopic "
        "Cahn-Hilliard conservation"
    )
    shared_next = (
        "complete covariant coarse-graining, equation-of-state, transport, and "
        "observable matching before physical interpretation"
    )
    entries = [
        make_entry(
            FORMULA_IDS[0],
            "n = -u_mu N^mu",
            {
                "N^mu": "covariant O(2) Noether current",
                "u_mu": "declared unit timelike frame covector",
                "n": "frame-projected signed charge density",
            },
            "frame projection of a covariant current to a hydrodynamic density",
            "relativistic decomposition of a conserved current in a chosen frame",
            [
                "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py",
                "docs/core/02_equations/covariant/uet_covariant_diffusion.py",
            ],
            [
                "docs/core/02_equations/covariant/uet_covariant_diffusion.py::decompose_noether_current",
                "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py::normalize_noether_hydrodynamic_state",
            ],
            "kinematic projection is covered by existing local current/map checks; microscopic inversion is not established",
            ["uet.o2.finite_density_eos", "uet.main_theory.coarse_graining"],
            "frame-projected signed O(2) charge only; not mass density and not universal C",
            "a frame-projected charge density is silently renamed mass, energy, or universal C",
            shared_next,
            assumptions=shared_assumptions,
            conservation=shared_conservation,
            limits=[
                "changing u_mu changes the projected density and spatial current without changing N^mu",
                "zero spatial current gives a comoving current",
            ],
            classification="kinematic_mapping",
        ),
        make_entry(
            FORMULA_IDS[1],
            "C = (n_bar - n_ref) / n_scale",
            {
                "n_bar": "already coarse-grained signed charge density",
                "n_ref": "declared density reference",
                "n_scale": "positive density scale",
                "C": "normalized hydrodynamic coordinate",
            },
            "exact affine coordinate change after the declared coarse-graining layer",
            "dimensionless nondimensionalization of a lane-specific hydrodynamic variable",
            ["docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py"],
            [
                "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py::normalize_noether_hydrodynamic_state",
                "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py::denormalize_phase_field_coordinates",
            ],
            "fixed-scale round-trip and negative controls pass; the upstream microscopic map remains many-to-one",
            ["uet.main_theory.coarse_graining", "uet.matter_space_flux.conservation"],
            "candidate C_charge coordinate on a declared O(2) lane; no universal C ontology",
            "the affine coordinate change is presented as a microscopic reconstruction or mass definition",
            "derive a covariant coarse-graining kernel and an independent physical observable map",
            assumptions=shared_assumptions,
            conservation="the affine change preserves a declared continuity residual under constant scales",
            limits=[
                "fixed positive scales give exact coordinate round-trip",
                "changing the reference shifts C without changing the underlying coarse density",
            ],
            classification="coordinate_definition",
        ),
        make_entry(
            FORMULA_IDS[2],
            "J = j / (n_scale L/T)",
            {
                "j": "coarse spatial charge current",
                "L": "declared length scale",
                "T": "declared time scale",
                "J": "normalized current coordinate",
            },
            "fixed-scale normalization of the spatial current paired with C",
            "dimensionless current coordinate in a declared natural-to-normalized lane",
            ["docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py"],
            [
                "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py::normalize_noether_hydrodynamic_state",
                "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py::denormalize_phase_field_coordinates",
            ],
            "current round-trip and legacy bridge compatibility pass for the declared scales",
            [FORMULA_IDS[1], "uet.matter_space_flux.relaxation"],
            "normalized current-coordinate map only; transport coefficients and SI meaning remain open",
            "the normalized current is treated as an independently derived microscopic transport law",
            shared_next,
            assumptions=shared_assumptions,
            conservation=shared_conservation,
            limits=[
                "the current scale is n_scale L/T",
                "zero current maps to zero normalized current",
            ],
            classification="coordinate_definition",
        ),
        make_entry(
            FORMULA_IDS[3],
            "R_hat = (T/n_scale) R_natural",
            {
                "R_natural": "natural continuity residual",
                "R_hat": "normalized continuity residual",
                "n_scale": "density scale",
                "T": "time scale",
            },
            "exact residual scaling under constant space-time and density scales",
            "nondimensional continuity-equation rescaling",
            ["docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py"],
            ["docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py::map_continuity_terms"],
            "analytic scaling identity passes deterministic numerical checks",
            [FORMULA_IDS[1], FORMULA_IDS[2]],
            "coordinate-level continuity scaling; it does not close dynamics or prove a physical conservation law by itself",
            "a zero normalized residual is used as evidence of microscopic conservation without the declared current dynamics",
            "connect the scaled residual to a covariant current law and dimensional measurement operator",
            assumptions=shared_assumptions,
            conservation="the residual vanishes together with the declared natural continuity residual",
            limits=[
                "constant scales preserve exact proportionality",
                "non-constant scales would require extra derivative terms and are outside v1",
            ],
            classification="conservation_scaling",
        ),
        make_entry(
            FORMULA_IDS[4],
            "N^mu = Z A^2 partial^mu(theta)",
            {
                "A": "O(2) polar amplitude",
                "theta": "O(2) phase",
                "Z": "declared kinetic coefficient",
                "N^mu": "Noether current",
            },
            "polar-coordinate identity for the implemented global O(2) current",
            "global O(2)/U(1) Noether current in a complex-scalar realization",
            ["docs/core/02_equations/covariant/uet_covariant_matter.py", "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py"],
            [
                "docs/core/02_equations/covariant/uet_covariant_matter.py::matter_noether_current",
                "docs/core/test/test_noether_phase_field_map.py::test_polar_O2_identity_matches_matter_noether_current",
            ],
            "polar-current identity passes the local analytic/numerical comparison in the declared metric convention",
            ["uet.o2.finite_density_eos", "uet.main_theory.covariant_parent"],
            "O(2) realization identity only; it does not identify the scalar amplitude, current, or charge with universal C or mass",
            "the O(2) current identity is used to infer a unique microscopic state from N^mu",
            "derive the covariant projected current law and match its hydrodynamic coefficients",
            assumptions=[
                "global O(2) scalar doublet written in polar variables",
                "declared inverse metric and kinetic coefficient",
                "away from any singular amplitude-coordinate patch",
            ],
            conservation="the identity is associated with the declared global O(2) current; conservation still depends on the matter equations and boundary conditions",
            limits=[
                "constant phase gives vanishing derivative current",
                "changing amplitude and phase gradient can preserve the same current, demonstrating non-invertibility",
            ],
            classification="action_level_identity",
            evidence_class="INTERNAL_ACTION_IDENTITY",
        ),
        make_entry(
            FORMULA_IDS[5],
            "f = n_scale*mu_scale*(C^2 - 1)^2/4; df/dn = mu_scale*(C^3 - C)",
            {
                "C": "normalized lane coordinate",
                "n": "coarse charge-coordinate realization",
                "f": "declared natural free-energy density comparator",
                "mu_scale": "chemical-potential scale",
            },
            "local conjugacy check for the symmetric double-well constitutive comparator",
            "Landau/Cahn-Hilliard-style constitutive free-energy coordinate",
            ["docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py"],
            [
                "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py::symmetric_double_well_thermodynamic_map",
                "docs/core/test/test_noether_phase_field_map.py::test_physical_free_energy_derivative_matches_mapped_chemical_potential",
            ],
            "local derivative and coefficient checks pass; the double well is explicitly not derived from the O(2) action",
            [FORMULA_IDS[1], "uet.o2.finite_density_eos"],
            "constitutive comparator in a declared coordinate; not the O(2) equation of state and not universal C physics",
            "local conjugacy is called a microscopic EOS derivation or used to identify C with mass",
            "compare against the exact finite-density O(2) EOS in a preregistered domain without fitting the comparator to holdout data",
            assumptions=shared_assumptions,
            conservation="free-energy conjugacy does not itself impose charge conservation",
            limits=[
                "C = plus or minus 1 gives the declared coexistence minima",
                "the curvature changes sign near the comparator spinodal region",
            ],
            classification="constitutive_comparator",
            evidence_class="INTERNAL_CONSTITUTIVE_COMPARATOR",
        ),
        make_entry(
            FORMULA_IDS[6],
            "tau_nat = T*tau_hat; M_nat = n_scale*L^2/(T*mu_scale)",
            {
                "tau_hat": "normalized relaxation parameter",
                "M_hat": "normalized mobility parameter",
                "tau_nat": "mapped relaxation scale",
                "M_nat": "mapped mobility scale",
            },
            "dimensional coordinate conversion for declared constitutive parameters",
            "unit conversion/nondimensionalization of relaxation and mobility coefficients",
            ["docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py"],
            ["docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py::map_normalized_constitutive_scales"],
            "fixed-scale conversion identity passes; no microscopic coefficient origin is supplied",
            ["uet.foundation.units", "uet.covariant_diffusion.finite_relaxation_current"],
            "declared natural-to-normalized scale map only; no SI transport prediction",
            "a coordinate conversion is presented as a measured or action-derived transport coefficient",
            "supply provenance, Kubo matching, and a material-specific observable/unit contract",
            assumptions=shared_assumptions,
            conservation="parameter rescaling does not alter the underlying continuity law",
            limits=[
                "positive density, length, time, and chemical-potential scales are required",
                "nonnegative normalized gradient coefficient is enforced by the map contract",
            ],
            classification="unit_coordinate_map",
            evidence_class="INTERNAL_DEFINITIONAL_MAP",
        ),
    ]
    source_paths = (
        SOURCE_NOETHER,
        SOURCE_MAP,
        SOURCE_MATTER,
        SOURCE_DIFFUSION,
        SPEC,
        FORMULA_AUDIT,
        VERIFICATION,
        DEPENDENCY,
    )
    return {
        "schema_version": "1.0",
        "artifact": "uet_equation_correspondence_registry_noether_mapping_addendum",
        "generated_at": date.today().isoformat(),
        "generator": "docs/scripts/audit/build_uet_noether_mapping_correspondence.py",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
        "status": "CANDIDATE_ENTRY_MERGED_INTO_CENTRAL_REGISTRY",
        "equation_entries": entries,
        "open_gates": sorted(
            set(formula_audit.get("open_formula_gates", []))
            | set(dependency.get("blocked_layers", {}).keys())
        ),
        "source_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in source_paths
        },
        "merge_metadata": {
            "merged_into": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
            "merged_on": date.today().isoformat(),
            "equation_ids": FORMULA_IDS,
            "claim_promotion": False,
            "controlling_blocker": dependency.get("controlling_blocker"),
            "verification_status": verification.get("evidence_status"),
        },
    }


def merge_into_central(payload: dict[str, Any]) -> None:
    """Merge generated entries while preserving the canonical registry layout."""

    raw = CENTRAL.read_text(encoding="utf-8")
    central = json.loads(raw)
    existing_ids = {
        str(item.get("equation_id"))
        for item in central.get("entries", [])
        if isinstance(item, dict) and item.get("equation_id")
    }
    equation_ids = list(payload["merge_metadata"]["equation_ids"])
    if existing_ids.intersection(equation_ids):
        raise ValueError(
            "one or more Noether mapping equation IDs are already in the central registry"
        )

    marker = '\n  ],\n  "merge_history": {'
    if raw.count(marker) != 1:
        raise ValueError("unexpected central registry layout; refusing an unsafe merge")
    serialized = json.dumps(
        payload["equation_entries"], ensure_ascii=False, indent=4
    )[1:-1].strip("\n")
    raw = raw.replace(marker, ",\n" + serialized + marker, 1)

    addendum_path = str(OUTPUT.relative_to(ROOT)).replace("\\", "/")
    if addendum_path in raw:
        raise ValueError("Noether addendum is already listed in the central registry")
    diffusion_marker = (
        '      "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_covariant_diffusion_addendum.json"\n'
    )
    if raw.count(diffusion_marker) != 1:
        raise ValueError("covariant-diffusion addendum marker is missing or ambiguous")
    raw = raw.replace(
        diffusion_marker,
        diffusion_marker.rstrip("\n") + ",\n" + f'      "{addendum_path}"\n',
        1,
    )

    merge_marker = '      "uet.covariant_diffusion.adiabatic_model_b_limit"\n    ],'
    if raw.count(merge_marker) != 1:
        raise ValueError("merge-history marker is missing or ambiguous")
    merge_lines = ",\n".join(f'      "{item}"' for item in equation_ids)
    raw = raw.replace(
        merge_marker,
        '      "uet.covariant_diffusion.adiabatic_model_b_limit",\n'
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
                "controlling_blocker": payload["merge_metadata"]["controlling_blocker"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
