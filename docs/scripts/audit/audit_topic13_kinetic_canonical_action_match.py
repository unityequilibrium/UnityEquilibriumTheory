"""Canonical kinetic repair and independent quartic-potential mismatch audit.

A passing comparator covariance check is not an action-to-transport match.
The polynomial finite differences below evaluate the production potential,
not the legacy vertex helper.
"""
from __future__ import annotations

import hashlib
import json
from math import sqrt
from pathlib import Path

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig, matter_potential
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import FiniteTemperatureO2QuasiparticleConfig
from docs.core.uet_o2_kinetic_collision_kubo import (
    _normal_state_inputs, kinetic_collision_contract, kinetic_collision_state,
)
from docs.core.uet_o2_one_loop_vertex_uv_boundary import _tree_vertex_tensor

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_kinetic_canonical_action_match_audit.json"


def config(z=1., coupling=.5):
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(matter=CovariantMatterConfig(
            matter_kinetic=z, matter_mass_sq=z,
            matter_quartic=coupling*z*z, response_coupling=0.,
        )),
    )


def kinetic_witnesses():
    covariance, conjugation = [], []
    for quantum in (False, True):
        states = {}
        for z in (.25, 1., 4.):
            for mu in (-.2, .2):
                states[z, mu] = kinetic_collision_state(
                    .25, mu, 0., config(z), quadrature_order=32, angular_order=24,
                    cutoff_factor=20., include_final_state_bose_enhancement=quantum,
                )
        for z in (.25, 1., 4.):
            for mu in (-.2, .2):
                actual, reference = states[z, mu], states[1., mu]
                names = ("effective_mass", "quartic_coupling", "momentum_cutoff",
                         "reference_momentum", "drude_weight_by_species",
                         "collision_width_by_species", "kinetic_coefficient_by_species")
                covariance.append({
                    "Z": z, "mu": mu, "outgoing_bose": quantum,
                    "canonical_inputs": list(_normal_state_inputs(.25, mu, 0., config(z))),
                    "widths": list(actual.collision_width_by_species),
                    "kinetic_comparator": actual.kinetic_coefficient,
                    "pass": all(bool(np.allclose(
                        getattr(actual, name), getattr(reference, name), rtol=1e-12, atol=0.
                    )) for name in names),
                })
            positive, negative = states[z, .2], states[z, -.2]
            conjugation.append({
                "Z": z, "outgoing_bose": quantum,
                "positive_mu_drude": list(positive.drude_weight_by_species),
                "negative_mu_drude": list(negative.drude_weight_by_species),
                "pass": all(bool(np.allclose(
                    getattr(positive, name), getattr(negative, name)[::-1], rtol=1e-12, atol=0.
                )) for name in ("drude_weight_by_species", "collision_width_by_species",
                                "kinetic_coefficient_by_species")),
            })
    return {
        "canonical_covariance_pass": all(row["pass"] for row in covariance),
        "charge_conjugation_pass": all(row["pass"] for row in conjugation),
        "covariance_rows": covariance, "conjugation_rows": conjugation,
    }


def potential_vertex_witnesses():
    """Fourth derivatives are exact stencil identities for this quartic."""
    rows = []
    for z in (.25, 1., 4.):
        cfg = config(z).eos.matter
        canonical_coupling = cfg.matter_quartic / z**2

        def potential(x, y):
            return matter_potential((x/sqrt(z), y/sqrt(z)), cfg)

        for h in (.125, .25, .5):
            pure = sum(weight*potential(offset*h, 0.)
                       for offset, weight in zip((-2, -1, 0, 1, 2), (1, -4, 6, -4, 1))) / h**4
            mixed = sum(wx*wy*potential(x*h, y*h)
                        for x, wx in zip((-1, 0, 1), (1, -2, 1))
                        for y, wy in zip((-1, 0, 1), (1, -2, 1))) / h**4
            legacy = _tree_vertex_tensor(canonical_coupling)
            # O(2) symmetry fixes all remaining entries from these derivatives.
            delta = np.eye(2)
            action_tensor = mixed*(
                np.einsum("ab,cd->abcd", delta, delta)
                + np.einsum("ac,bd->abcd", delta, delta)
                + np.einsum("ad,bc->abcd", delta, delta)
            )
            plus = np.array([1., 1.j])/sqrt(2.)
            minus = plus.conj()
            charged = np.einsum("abcd,a,b,c,d", action_tensor, plus, plus, minus, minus)
            rows.append({
                "Z": z, "step": h, "lambda_c": canonical_coupling,
                "potential_d1111": pure, "potential_d1122": mixed,
                "legacy_tensor_1111": float(legacy[0, 0, 0, 0]),
                "legacy_tensor_1122": float(legacy[0, 0, 1, 1]),
                "charged_all_incoming_contact_magnitude": float(abs(charged)),
                "unit_channel_comparator_amplitude": canonical_coupling,
                "polynomial_derivative_pass": bool(
                    np.isclose(pure, 6*canonical_coupling, rtol=1e-10, atol=1e-12)
                    and np.isclose(mixed, 2*canonical_coupling, rtol=1e-10, atol=1e-12)
                    and np.isclose(charged, 4*canonical_coupling, rtol=1e-10, atol=1e-12)
                ),
                "legacy_tensor_matches_potential": bool(
                    np.isclose(legacy[0, 0, 0, 0], pure, rtol=1e-10, atol=1e-12)
                    and np.isclose(legacy[0, 0, 1, 1], mixed, rtol=1e-10, atol=1e-12)
                ),
            })
    return {
        "derivative_verification_pass": all(row["polynomial_derivative_pass"] for row in rows),
        "legacy_tensor_matches_potential": all(row["legacy_tensor_matches_potential"] for row in rows),
        "rows": rows,
        "derivation": "V_c=m_c^2*(x^2+y^2)/2+lambda_c*(x^2+y^2)^2/4; V_abcd=2*lambda_c*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc).",
        "boundary": "Contact polynomial only. Exchange channels, LSZ/phase-space convention, species symmetry factors and complete retarded collision operator are not matched.",
    }


def main():
    kinetic, vertex = kinetic_witnesses(), potential_vertex_witnesses()
    verified = (kinetic["canonical_covariance_pass"] and kinetic["charge_conjugation_pass"]
                and vertex["derivative_verification_pass"])
    contract = kinetic_collision_contract()
    paths = (
        "docs/core/uet_o2_kinetic_collision_kubo.py",
        "docs/core/uet_covariant_matter.py",
        "docs/core/uet_o2_one_loop_vertex_uv_boundary.py",
        "docs/core/uet_o2_contact_sk_transition_vertex_match.py",
        "docs/core/uet_o2_tree_level_bs_sk_match.py",
        "docs/scripts/audit/audit_topic13_kinetic_canonical_action_match.py",
        "docs/core/test/test_topic13_kinetic_canonical_normalization.py",
    )
    sha = lambda path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    blockers = [
        "full_action_tensor_channel_and_symmetry_normalization_not_matched",
        "mixed_normalization_in_remaining_charged_SK_and_vertex_consumers",
        "downstream_artifact_refresh",
        "complete_current_condensate_material_transport_mapping",
    ]
    artifact = {
        "schema_version": "t13-kinetic-canonical-action-match-v1",
        "major_result_id": "T13_KINETIC_CANONICAL_REPAIR_AND_ACTION_MATCH_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "PARTIAL",
        "verification_status": "PASS_REPAIR_WITH_OPEN_ACTION_MATCH" if verified else "BLOCKED_REPAIR",
        "what_is_closed": [
            "Canonical normal kinetic input normalization and fixed charge labels.",
            "Field-redefinition covariance of the declared dilute/Bose-enhanced comparator.",
            "Independent fourth derivative of the production quartic potential.",
        ] if verified else [],
        "equation_or_mapping": {**contract["equations"], "quartic_tensor": vertex["derivation"]},
        "units": contract["unit_contract"],
        "derivation_class": "IMPLEMENTATION_REPAIR_AND_PRODUCTION_POTENTIAL_DERIVATIVE",
        "observable": "natural-unit labeled collision rates and a diagnostic quartic tensor",
        "data_role": "SYNTHETIC_INTERNAL_NO_CALIBRATION",
        "source_hashes": {path: sha(path) for path in paths},
        "evidence_artifacts": [{"path": path, "sha256": sha(path)} for path in paths],
        "kinetic_witnesses": kinetic,
        "action_vertex_witnesses": vertex,
        "action_matching_status": "OPEN_CHANNEL_MATCH" if vertex["legacy_tensor_matches_potential"] else "BLOCKED_LEGACY_TENSOR_NOT_POTENTIAL_DERIVATIVE",
        "open_blockers": blockers,
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_promotion": False,
        "parameter_fitting_performed": False,
        "xie_2026_accessed": False,
        "previous_baseline": {
            "git_revision": "bd55dc487",
            "regression_before_repair": "11 failed, 6 passed in the new 17-case suite",
            "changed_domains": "general Z and negative chemical potential; old Z=1, mu>=0 comparator normalization unchanged",
        },
        "supersedes": "The known copied kinetic-input normalization finding in t13_fixed_phi_spectrum_repair_audit.json is repaired here; its broader transport blockers remain.",
        "controlling_blocker": blockers[0],
        "next_action": "Derive a named action-normalized species/channel collision operator and reconcile charged SK/vertex consumers before transporting the new normalization into physical claims.",
        "claim_boundary": "Comparator covariance is repaired, not full microscopic transport. Do not multiply all historical rates by a single guessed factor or reuse formal action-match PASS as proof.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": artifact["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN": blockers,
        "DEPENDENCY_UNLOCKED": [],
        "STATUS": artifact["verification_status"],
        "WHAT_CHANGED": "Canonical m and lambda; signed mu; independent quartic derivative exposes unresolved action matching.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"],
        "VERIFICATION": {"kinetic_covariance": kinetic["canonical_covariance_pass"],
                         "charge_labels": kinetic["charge_conjugation_pass"],
                         "potential_derivative": vertex["derivative_verification_pass"],
                         "legacy_action_match": vertex["legacy_tensor_matches_potential"]},
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": artifact["next_action"],
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["verification_status"],
        "canonical_covariance": kinetic["canonical_covariance_pass"],
        "charge_conjugation": kinetic["charge_conjugation_pass"],
        "potential_derivative": vertex["derivative_verification_pass"],
        "legacy_tensor_match": vertex["legacy_tensor_matches_potential"],
        "action_matching_status": artifact["action_matching_status"],
        "sample_vertex": vertex["rows"][0],
        "full_core_unlock": False,
    }, indent=2))
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
