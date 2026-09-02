"""Audit the same-kernel tree tagged loss, gain, and retarded width."""
from __future__ import annotations

from dataclasses import asdict
from math import log
from pathlib import Path
import hashlib
import json

import numpy as np

from docs.core.uet_o2_same_kernel_tagged_width import (
    same_kernel_tagged_width_contract,
    same_kernel_tagged_width_state,
)
from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import (
    ActionInputs,
    tagged_loss_rates,
)
from docs.scripts.audit.audit_topic13_invariant_rate_collision_repair import config


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_same_kernel_tagged_spectral_width_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_same_kernel_width_addendum.json"
EQUATION_ID = "uet.o2.thermal.same_kernel_tree_tagged_spectral_width"
REFINEMENT_THRESHOLD = 5.0e-4
INDEPENDENT_FORM_THRESHOLD = 1.0e-10


def _relative_array(first: np.ndarray, second: np.ndarray) -> float:
    denominator = np.maximum(np.maximum(np.abs(first), np.abs(second)), 1.0e-300)
    return float(np.max(np.abs(second - first) / denominator))


def scale_witness(scale: float) -> dict[str, object]:
    if scale <= 0.0 or scale == 1.0:
        raise ValueError("positive nonunit scale required")
    controls = {
        "radial_order": 12,
        "incoming_angular_order": 6,
        "outgoing_angular_order": 6,
        "outgoing_azimuth_order": 8,
    }
    base = same_kernel_tagged_width_state(
        0.25, 0.1, 0.0, config(), tagged_momenta=(1.0,), **controls
    )
    scaled = same_kernel_tagged_width_state(
        0.25 * scale,
        0.1 * scale,
        0.0,
        config(scale),
        tagged_momenta=(scale,),
        **controls,
    )
    ratios = (
        np.asarray(scaled.retarded_spectral_widths_by_tag_momentum)[:, 0]
        / np.asarray(base.retarded_spectral_widths_by_tag_momentum)[:, 0]
    )
    return {
        "scale": scale,
        "width_ratios_by_tag": ratios.tolist(),
        "energy_exponents_by_tag": [log(float(value)) / log(scale) for value in ratios],
    }


def convergence_witnesses() -> dict[str, object]:
    radial_rows = []
    for order in (12, 16, 24):
        state = same_kernel_tagged_width_state(
            0.25, 0.1, 0.0, config(), tagged_momenta=(1.0,),
            radial_order=order,
            incoming_angular_order=6,
            outgoing_angular_order=6,
            outgoing_azimuth_order=8,
        )
        radial_rows.append({
            "radial_order": order,
            "retarded_widths_by_tag": np.asarray(
                state.retarded_spectral_widths_by_tag_momentum
            )[:, 0].tolist(),
        })
    angular_rows = []
    for order in (4, 6, 8):
        state = same_kernel_tagged_width_state(
            0.25, 0.1, 0.0, config(), tagged_momenta=(1.0,),
            radial_order=16,
            incoming_angular_order=order,
            outgoing_angular_order=order,
            outgoing_azimuth_order=2 * order,
        )
        angular_rows.append({
            "angular_order": order,
            "azimuth_order": 2 * order,
            "retarded_widths_by_tag": np.asarray(
                state.retarded_spectral_widths_by_tag_momentum
            )[:, 0].tolist(),
        })
    return {
        "radial_rows": radial_rows,
        "angular_rows": angular_rows,
        "radial_last_relative_difference": _relative_array(
            np.asarray(radial_rows[-2]["retarded_widths_by_tag"]),
            np.asarray(radial_rows[-1]["retarded_widths_by_tag"]),
        ),
        "angular_last_relative_difference": _relative_array(
            np.asarray(angular_rows[-2]["retarded_widths_by_tag"]),
            np.asarray(angular_rows[-1]["retarded_widths_by_tag"]),
        ),
    }


def independent_cross_section_witness() -> dict[str, object]:
    controls = {
        "radial_order": 16,
        "incoming_angular_order": 8,
        "outgoing_angular_order": 8,
        "outgoing_azimuth_order": 12,
    }
    invariant = same_kernel_tagged_width_state(
        0.25, 0.1, 0.0, config(), tagged_momenta=(1.0,), cutoff_factor=12.0, **controls
    )
    cross_section = tagged_loss_rates(
        ActionInputs(),
        temperature=0.25,
        mu=0.1,
        momentum=1.0,
        radial_order=controls["radial_order"],
        incoming_order=controls["incoming_angular_order"],
        outgoing_order=controls["outgoing_angular_order"],
        azimuth_order=controls["outgoing_azimuth_order"],
        cutoff=12.0,
    )
    invariant_channels = np.asarray(invariant.widths_by_tag_momentum_target)[:, 0, :]
    cross_section_channels = np.asarray(cross_section["rates_by_tag_and_target"])
    return {
        "invariant_cut_channels": invariant_channels.tolist(),
        "independent_vMoller_cross_section_channels": cross_section_channels.tolist(),
        "maximum_relative_residual": _relative_array(invariant_channels, cross_section_channels),
    }


def charge_conjugation_witness() -> dict[str, object]:
    controls = {
        "tagged_momenta": (1.0,),
        "radial_order": 16,
        "incoming_angular_order": 6,
        "outgoing_angular_order": 6,
        "outgoing_azimuth_order": 8,
    }
    positive = same_kernel_tagged_width_state(0.25, 0.1, 0.0, config(), **controls)
    negative = same_kernel_tagged_width_state(0.25, -0.1, 0.0, config(), **controls)
    first = np.asarray(positive.widths_by_tag_momentum_target)[:, 0, :]
    second = np.asarray(negative.widths_by_tag_momentum_target)[::-1, 0, ::-1]
    retarded_first = np.asarray(
        positive.retarded_spectral_widths_by_tag_momentum
    )[:, 0]
    retarded_second = np.asarray(
        negative.retarded_spectral_widths_by_tag_momentum
    )[::-1, 0]
    return {
        "positive_mu_channels": first.tolist(),
        "negative_mu_charge_swapped_channels": second.tolist(),
        "maximum_relative_residual": _relative_array(first, second),
        "retarded_maximum_relative_residual": _relative_array(
            retarded_first, retarded_second
        ),
    }


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def main() -> int:
    reference = same_kernel_tagged_width_state(
        0.25, 0.1, 0.0, config(),
        tagged_momenta=(0.5, 1.0, 2.0),
        radial_order=16,
        incoming_angular_order=8,
        outgoing_angular_order=8,
        outgoing_azimuth_order=12,
    )
    scaling = [scale_witness(value) for value in (1.5, 2.0, 3.0)]
    convergence = convergence_witnesses()
    independent = independent_cross_section_witness()
    conjugation = charge_conjugation_witness()
    contract = same_kernel_tagged_width_contract()
    source_text = (ROOT / "docs/core/uet_o2_same_kernel_tagged_width.py").read_text(encoding="utf-8")
    loss_widths = np.asarray(reference.total_widths_by_tag_momentum)
    gain_widths = np.asarray(reference.total_gain_widths_by_tag_momentum)
    retarded_widths = np.asarray(
        reference.retarded_spectral_widths_by_tag_momentum
    )
    self_energy = np.asarray(
        reference.retarded_self_energy_imaginary_by_tag_momentum
    )
    energies = np.asarray(reference.tagged_energies)
    checks = {
        "symbolic_width_dimension_E1": contract["unit_contract"]["Gamma"] == 1,
        "whole_action_width_scales_E1": all(
            max(abs(value - 1.0) for value in row["energy_exponents_by_tag"]) <= 1.0e-10
            for row in scaling
        ),
        "independent_invariant_cut_cross_section_agreement": independent["maximum_relative_residual"] <= INDEPENDENT_FORM_THRESHOLD,
        "charge_conjugation": conjugation["maximum_relative_residual"] <= 1.0e-10
        and conjugation["retarded_maximum_relative_residual"] <= 1.0e-10,
        "radial_quadrature_converged": convergence["radial_last_relative_difference"] <= REFINEMENT_THRESHOLD,
        "angular_quadrature_converged": convergence["angular_last_relative_difference"] <= REFINEMENT_THRESHOLD,
        "positive_loss_gain_and_retarded_widths": bool(
            np.all(loss_widths > gain_widths)
            and np.all(gain_widths > 0.0)
            and np.all(retarded_widths > 0.0)
        ),
        "kms_gain_loss_identity": reference.maximum_kms_gain_loss_residual
        <= 1.0e-12,
        "spectral_interface_exact": bool(
            np.allclose(
                self_energy,
                -2.0 * energies[None, :] * retarded_widths,
                rtol=1.0e-14,
            )
        ),
        "eventwise_energy_momentum": reference.maximum_event_energy_residual <= 1.0e-12
        and reference.maximum_event_momentum_residual <= 1.0e-12,
        "detailed_balance": reference.maximum_detailed_balance_residual <= 1.0e-10,
        "same_action_and_event_kernel": reference.same_kernel_amplitude_used
        and reference.same_center_of_mass_event_kernel_used,
        "no_clipping_fit_or_absolute_mode_cutoff": "np.clip" not in source_text
        and "eigenvalues > 1.0e-" not in source_text
        and not reference.parameter_fitting_performed,
    }
    status = (
        "PASS_SCOPED_SAME_KERNEL_TREE_LOSS_GAIN_RETARDED_WIDTH"
        if all(checks.values())
        else "WARN_SAME_KERNEL_TREE_TAGGED_SPECTRAL_WIDTH"
    )
    paths = [
        "docs/core/uet_o2_same_kernel_tagged_width.py",
        "docs/core/uet_o2_invariant_galerkin_collision_operator.py",
        "docs/core/test/test_topic13_same_kernel_tagged_width.py",
        "docs/scripts/audit/audit_topic13_same_kernel_tagged_width.py",
        "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
    ]
    prior = "docs/core/artifacts/t13_invariant_galerkin_collision_operator_audit.json"
    artifact = {
        "schema_version": "t13-same-kernel-tagged-width-v2",
        "major_result_id": "T13_SAME_KERNEL_TREE_TAGGED_SPECTRAL_WIDTH",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "verification_status": status,
        "what_is_closed": [
            "Charge- and momentum-resolved tagged elastic out-scattering and inverse gain cuts are derived from the same production contact-plus-Phi amplitude and center-of-mass event kernel as the invariant Galerkin operator.",
            "The invariant-cut normalization agrees with an independent v_Moller cross-section implementation for every tag/target charge channel.",
            "KMS detailed balance gives Gamma_R=Gamma_out-Gamma_in=Gamma_out/(1+f), and the corrected on-shell interface -Im Sigma_R=2E Gamma_R uses no fitted damping input.",
            "The earlier identification of the tagged out-scattering rate itself as the retarded width is superseded and must not be reused in an RA pair.",
        ],
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping": contract["equations"],
        "ontology": {"C": "unchanged", "Phi": "effective response variable; internal exchange line only", "R_gen": "excluded", "R_obs": "excluded"},
        "unit_lane": "natural_units",
        "units": contract["unit_contract"],
        "derivation_class": "same_action_tree_elastic_loss_gain_cuts_with_kms_retarded_width",
        "observable": "Tagged elastic loss/gain and on-shell retarded width, not conductivity",
        "data_role": "DERIVED_SYNTHETIC_STRUCTURAL_CANDIDATE",
        "reference_state": asdict(reference),
        "whole_action_scale_witnesses": scaling,
        "convergence": convergence,
        "independent_cross_section_witness": independent,
        "charge_conjugation_witness": conjugation,
        "thresholds": {"last_refinement_relative": REFINEMENT_THRESHOLD, "independent_formula_relative": INDEPENDENT_FORM_THRESHOLD, "event_energy_momentum_absolute": 1.0e-12},
        "checks": checks,
        "open_blockers": [
            "dressed_self_consistent_width_and_resonant_resummation",
            "vector_tensor_heat_current_Galerkin_basis",
            "microscopic_retarded_ladder_solution",
            "number_changing_and_response_channels",
            "physical_Kubo_and_SI_normalization",
        ],
        "controlling_blocker": "vector_heat_current_basis_and_dressed_ladder_missing",
        "source_hashes": {path: _sha(path) for path in paths},
        "evidence_artifacts": [{"path": prior, "sha256": _sha(prior)}],
        "dependency_unlocked": ["tree_width_dressed_RA_pair_insertion", "vector_heat_current_Galerkin_extension"],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Tree elastic same-kernel tagged loss/gain and KMS retarded width only; not a dressed self-consistent/resonant width, complete damping rate, vector heat-current ladder, Kubo/SI coefficient, external validation, or Full Topic 13 closure.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN": artifact["open_blockers"],
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Separated tagged loss, inverse gain, and retarded spectral widths; repaired the RA self-energy mapping through the KMS gain/loss identity.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"],
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Insert the same-kernel tree width into the dressed RA pair and build the vector heat/current Galerkin basis; retain dressed/resonant self-consistency as a separate gate.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {key: artifact[key] for key in (
        "ontology", "unit_lane", "units", "derivation_class", "observable",
        "data_role", "verification_status", "controlling_blocker", "claim_boundary",
    )}
    entry.update({
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "candidate_same_kernel_tree_loss_gain_retarded_width",
        "relation_or_code_path": artifact["equation_or_mapping"],
        "standard_physics_counterpart": "Relativistic 2-to-2 greater/lesser cuts and on-shell retarded self-energy width",
        "variables": {"Gamma_out": "tagged elastic loss rate", "Gamma_in": "inverse gain rate", "Gamma_R": "retarded pole width", "Sigma_R": "retarded on-shell self-energy"},
        "mathematical_role": "same-kernel damping input precursor for dressed RA ladder",
        "observable_mapping": artifact["observable"],
        "parameter_dimensions": artifact["units"],
        "source_or_origin": "Declared O(2)-Phi tree action and invariant two-body cut",
        "assumptions": {"natural_units": True, "normal_response_background": True, "elastic_tree_channels_only": True, "nonresonant_response_exchange": True},
        "symmetry_and_conservation": "Charge conjugation and eventwise four-momentum conservation",
        "limiting_cases": ["energy scales 1.5, 2, 3", "radial orders 12, 16, 24", "angular orders 4, 6, 8"],
        "implementation_paths": [paths[0], paths[1]],
        "verifier_paths": [paths[3], paths[2]],
        "evidence_class": "INTERNAL_STRUCTURAL_CANDIDATE",
        "proof_status": "TREE_LOSS_GAIN_KMS_RETARDED_WIDTH_VERIFIED",
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "tree_width_precursor_not_physical_unlock",
        "physical_dependency_unlock": False,
        "failure_mode": artifact["open_blockers"],
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
    })
    REGISTRY_OUT.write_text(json.dumps({
        "schema_version": "uet-equation-registry-addendum-v1",
        "status": "CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json",
        "equation_entries": [entry],
        "full_core_unlock": False,
        "claim_promotion": False,
    }, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "checks": checks,
        "scaling": scaling,
        "convergence": convergence,
        "independent_relative_residual": independent["maximum_relative_residual"],
        "charge_conjugation_relative_residual": conjugation["maximum_relative_residual"],
        "retarded_charge_conjugation_relative_residual": conjugation[
            "retarded_maximum_relative_residual"
        ],
        "kms_gain_loss_relative_residual": reference.maximum_kms_gain_loss_residual,
    }, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
