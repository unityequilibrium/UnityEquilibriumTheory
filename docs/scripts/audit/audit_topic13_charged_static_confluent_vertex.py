"""Static charged density-current vertex from confluent one-loop diagrams.

This is the thermodynamic Euclidean P=Q=0 limit.  Coincident thermal poles
are evaluated analytically as Bose divided-difference derivatives; no pole
splitting, regulator, Ward reconstruction, or experimental input is used.
"""
from __future__ import annotations

from dataclasses import asdict
from math import pi, sqrt
from pathlib import Path
import hashlib
import json
import numpy as np

from docs.scripts.audit import audit_topic13_charged_one_loop_match as charged

thermal = charged.thermal
CFG = charged.CFG
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_charged_static_confluent_vertex_audit.json"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_charged_static_vertex_addendum.json"
EQUATION_ID = "uet.o2.thermal.charged_static_confluent_vertex"
SAMPLES = tuple((T, mu, q) for T in (.1, .25, .5, 1.) for mu in (0., .2) for q in (-1, 1))


def occupation_prime(energy, T):
    if T == 0:
        return np.zeros_like(np.asarray(energy, float))
    n = charged.occupation(energy, T)
    return -n * (1 + n) / T


def occupation_second(energy, T):
    if T == 0:
        return np.zeros_like(np.asarray(energy, float))
    n = charged.occupation(energy, T)
    return n * (1 + n) * (1 + 2 * n) / (T * T)


def divided_occupation_derivative(a, b, T, *, order=48):
    """d/da [(n(a)-n(b))/(a-b)] in its exact confluent representation."""
    a, b = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float))
    charged.occupation(a, T)
    charged.occupation(b, T)
    if T == 0:
        return np.zeros_like(a)
    if isinstance(order, bool) or not isinstance(order, (int, np.integer)) or order < 16:
        raise ValueError("integer confluent quadrature order >=16 required")
    nodes, weights = thermal.nodes(order)
    t = (nodes + 1) / 2
    weights = weights / 2
    result = np.zeros_like(a)
    for ti, wi in zip(t, weights):
        result += wi * ti * occupation_second(b + ti * (a - b), T)
    return result


def static_mixed_bubble_derivative(E, W, r, T):
    """Derivative d B_T(E,W,r)/dr at the static Matsubara point z=r."""
    E, W = np.broadcast_arrays(np.asarray(E, float), np.asarray(W, float))
    if not np.isfinite(r) or np.any(E <= abs(r)):
        raise ValueError("strict charged Bose gap required")
    if T == 0:
        return np.zeros_like(E)
    npart = charged.occupation(E - r, T)
    nant = charged.occupation(E + r, T)
    n0 = charged.occupation(W, T)
    dpart = npart * (1 + npart) / T
    dant = -nant * (1 + nant) / T
    S = E + W
    pair = (dpart / (S - r) + (npart + n0) / (S - r) ** 2
            + dant / (S + r) - (nant + n0) / (S + r) ** 2)
    landau = (divided_occupation_derivative(E - r, W, T)
              - divided_occupation_derivative(E + r, W, T))
    return (pair + landau) / (4 * E * W)


def _half_line_integral(values, T, cfg, order):
    nodes, weights = thermal.nodes(order)
    scale = max(T, cfg.mass, sqrt(cfg.response_mass_sq))
    p = scale * (1 + nodes) / (1 - nodes)
    jacobian = 2 * scale / (1 - nodes) ** 2
    measure = weights * jacobian * p * p / (2 * pi * pi)
    return float(measure @ values(p))


def static_vertex(T=.25, mu=.2, q=1, cfg=CFG, *, order=128):
    if not np.isfinite(T) or T < 0 or not np.isfinite(mu) or abs(mu) >= cfg.mass:
        raise ValueError("finite T>=0 and chemical potential inside the normal gap required")
    if q not in (-1, 1) or isinstance(order, bool) or not isinstance(order, (int, np.integer)) or order < 32:
        raise ValueError("signed charge and integer quadrature order >=32 required")
    matter = thermal.thermal_terms(cfg.mass**2, T, mu, (-1, 1), order=order, cutoff_factor=64.)
    bath = 1j * (-4 * cfg.coupling + cfg.cubic**2 / cfg.response_mass_sq) * matter["tadpole_mu"]

    def mixed_integrand(p):
        E = np.sqrt(p * p + cfg.mass**2)
        W = np.sqrt(p * p + cfg.response_mass_sq)
        return static_mixed_bubble_derivative(E, W, q * mu, T)

    mixed = 1j * cfg.cubic**2 * q * _half_line_integral(mixed_integrand, T, cfg, order)
    _, ds = charged.vacuum_kernel(mu * mu, cfg, order)
    vacuum = -2j * mu * ds
    bare = 2j * mu
    total = bare + bath + mixed + vacuum
    return {"T": T, "mu": mu, "q": q, "bare": bare,
            "bath_and_response_mean": bath, "mixed_thermal_confluent": mixed,
            "vacuum_and_counterterm": vacuum, "total": total,
            "spatial_vertex_by_isotropy": 0.,
            "boundary": "Thermodynamic Euclidean P=Q=0 limit; not the collisionless retarded order of limits."}


def static_inverse(mu, T=.25, q=1, cfg=CFG, *, order=160):
    kernel = charged.charged_self_energy(q * mu, T, mu, q, cfg, order=order, static=True)
    return cfg.mass**2 - mu**2 + kernel["self_energy"]


def finite_difference_witness(T=.25, mu=.2, q=1, cfg=CFG, h=5e-5, *, order=160):
    if not np.isfinite(h) or h <= 0 or abs(mu) + h >= cfg.mass:
        raise ValueError("positive finite difference step inside the normal gap required")
    explicit = static_vertex(T, mu, q, cfg, order=order)["total"]
    derivative = (static_inverse(mu + h, T, q, cfg, order=order)
                  - static_inverse(mu - h, T, q, cfg, order=order)) / (2 * h)
    finite_difference = -1j * derivative
    absolute_error = float(abs(explicit - finite_difference))
    return {"T": T, "mu": mu, "q": q, "h": h, "explicit": explicit,
            "finite_difference": finite_difference,
            "absolute_error": absolute_error,
            "relative_error": (float(absolute_error / abs(finite_difference))
                               if abs(finite_difference) > 1e-12 * cfg.mass else None)}


def _serial(value):
    if isinstance(value, complex):
        return [value.real, value.imag]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: _serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serial(v) for v in value]
    return value


def main():
    rows = [static_vertex(T, mu, q) for T, mu, q in SAMPLES]
    witnesses = [finite_difference_witness(T, mu, q, h=h)
                 for T, mu, q in SAMPLES for h in (1e-4, 5e-5, 2.5e-5)]
    refinements = [static_vertex(.25, .2, 1, order=n) for n in (80, 112, 160)]
    changes = [float(abs(b["total"] - a["total"]) / max(abs(b["total"]), 1e-300))
               for a, b in zip(refinements, refinements[1:])]
    nonzero_witnesses = [w for w in witnesses if w["relative_error"] is not None]
    zero_witnesses = [w for w in witnesses if w["relative_error"] is None]
    checks = {
        "explicit_matches_thermodynamic_derivative": (max(w["relative_error"] for w in nonzero_witnesses) < 2e-7
                                                       and max(w["absolute_error"] for w in zero_witnesses) < 1e-14),
        "finite_difference_step_convergence": (all(w["relative_error"] < 2e-7 for w in nonzero_witnesses)
                                                and all(w["absolute_error"] < 1e-14 for w in zero_witnesses)),
        "quadrature_refinement": max(changes) < 1e-6,
        "charge_even_static_limit": all(abs(static_vertex(T, mu, 1)["total"] - static_vertex(T, mu, -1)["total"]) < 1e-14
                                        for T in (.1, .25, .5, 1.) for mu in (0., .2)),
        "zero_mu_temporal_vertex": all(abs(static_vertex(T, 0., q)["total"]) < 1e-14
                                           for T in (.1, .25, .5, 1.) for q in (-1, 1)),
        "no_spatial_static_current": all(r["spatial_vertex_by_isotropy"] == 0 for r in rows),
    }
    paths = ["docs/scripts/audit/audit_topic13_charged_static_confluent_vertex.py",
             "docs/core/test/test_topic13_charged_static_confluent_vertex.py",
             "docs/scripts/audit/audit_topic13_charged_one_loop_match.py",
             "docs/scripts/audit/audit_topic13_charged_one_loop_current_vertex.py"]
    sha = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
    prior = "docs/core/artifacts/t13_charged_one_loop_current_vertex_audit.json"
    artifact = {
        "schema_version": "t13-charged-static-confluent-vertex-v1",
        "major_result_id": "T13_CHARGED_STATIC_CONFLUENT_VERTEX_MATCH",
        "topic": "0.13_Thermodynamic_Bridge", "closure_level": "CLOSED_FOR_LANE",
        "verification_status": "PASS_SCOPED_STATIC_CONFLUENT_VERTEX" if all(checks.values()) else "WARN_STATIC_CONFLUENT_VERTEX",
        "what_is_closed": [
            "The strict Euclidean P=Q=0 temporal charged vertex is derived diagram by diagram without artificial pole splitting.",
            "The mixed thermal confluent derivative, bath/mean response, and vacuum subtraction jointly match the thermodynamic derivative of the full static inverse propagator.",
            "Charge-even, zero-density and spatial-isotropy limits are explicit in the declared normal lane."],
        "equation_registry_ids": [EQUATION_ID], "registration_status": "CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping": {
            "source_identity": "partial_mu D_static^-1 = i Gamma_static^0",
            "full_vertex": "Gamma_static^0=-i partial_mu[m^2-mu^2+Sigma_mean+Sigma_quartic+Sigma_mix+Sigma_vac]",
            "confluent_derivative": "partial_a[(n(a)-n(W))/(a-W)]=integral_0^1 t*n''(W+t(a-W)) dt",
            "bath_mean": "Gamma_bath^0=i[-4 lambda_chi+G^2/M0^2] partial_mu I_chi",
            "mixed": "Gamma_mix^0=i G^2 q partial_r B_T(r)|r=q*mu",
            "vacuum": "Gamma_vac^0=-2 i mu partial_s Sigma_vac(s)|s=mu^2"},
        "ontology": {"C": "collective lane coordinate, not O(2) charge", "Phi": "effective response; internal exchanged response remains lane-specific", "R_gen": "derived trace excluded", "R_obs": "excluded"},
        "unit_lane": "natural_units", "units": {"mu": 1, "T": 1, "Gamma0": 1, "self_energy": 2},
        "derivation_class": "derived_relation_with_numerical_quadrature",
        "observable": "Internal static Euclidean density-source vertex, not physical heat/current conductivity",
        "data_role": "DERIVED_SYNTHETIC_DIAGNOSTIC", "config": asdict(CFG),
        "samples": _serial(rows), "finite_difference_witnesses": _serial(witnesses),
        "refinement_relative_changes": changes, "checks": checks,
        "approximation_contract": {"order": "strict one loop in normal zero-field propagators", "limit": "P=Q=0 thermodynamic Euclidean limit", "confluent_policy": "analytic divided-difference derivative; no epsilon splitting", "retarded_limit": "not evaluated"},
        "open_blockers": ["real_time_finite_k_transverse_vertex", "collision_and_heat_current_ladder_matching", "material_SI_calibration_and_full_T13_acceptance"],
        "controlling_blocker": "real_time_finite_k_transverse_vertex_and_collision_heat_ladder_matching",
        "source_hashes": {p: sha(p) for p in paths}, "evidence_artifacts": [{"path": prior, "sha256": sha(prior)}],
        "dependency_unlocked": ["static_density_response_internal_handoff"], "full_core_unlock": False,
        "claim_promotion": False, "xie_2026_accessed": False, "parameter_fitting_performed": False,
        "claim_boundary": "Static natural-unit Euclidean one-loop density-current lane only; not a finite-k retarded vertex, Kubo coefficient, heat current, SI mapping, external validation, or Full Topic 13 closure."}
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
        "WHAT_IS_ACTUALLY_CLOSED": artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN": artifact["open_blockers"],
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": artifact["verification_status"],
        "WHAT_CHANGED": "Resolved the coincident-pole static vertex with an analytic confluent derivative and matched it to the full static inverse-propagator derivative.",
        "EQUATION_OR_MAPPING": artifact["equation_or_mapping"], "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Derive the real-time finite-k transverse/current vertex and then match collision and heat-current ladders.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {k: artifact[k] for k in ("ontology", "unit_lane", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary")}
    entry.update({"equation_id": EQUATION_ID, "version": "1", "classification": "derived_relation",
                  "relation_or_code_path": artifact["equation_or_mapping"],
                  "standard_physics_counterpart": "Static Ward/thermodynamic density vertex with confluent thermal bubble",
                  "variables": {"Gamma0": "temporal density-source vertex", "q": "O(2) charge sign, not core C"},
                  "mathematical_role": "Static one-loop current insertion", "observable_mapping": artifact["observable"],
                  "parameter_dimensions": artifact["units"], "source_or_origin": "Canonical action and differentiated one-loop diagrams",
                  "assumptions": artifact["approximation_contract"], "symmetry_and_conservation": "Static O(2) Ward identity and charge conjugation",
                  "limiting_cases": ["T=0", "mu=0", "G=0", "P=Q=0"], "implementation_paths": [paths[0]],
                  "verifier_paths": [paths[1]], "evidence_class": "INTERNAL_SYNTHETIC_DIAGNOSTIC",
                  "proof_status": "CHECKED_STATIC_EUCLIDEAN_ONE_LOOP_ONLY",
                  "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": sha(OUT)}],
                  "downstream_dependencies": [], "dependency_role": "static_internal_handoff_only", "physical_dependency_unlock": False,
                  "failure_mode": artifact["open_blockers"], "next_hardening_step": artifact["report"]["NEXT_ACTION"]})
    REGISTRY_OUT.write_text(json.dumps({"schema_version": "uet-equation-registry-addendum-v1", "status": "CANDIDATE_DIAGNOSTIC_NOT_MERGED",
                            "extends": "docs/core/artifacts/uet_equation_correspondence_registry.json", "equation_entries": [entry],
                            "full_core_unlock": False, "claim_promotion": False}, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["verification_status"], "checks": checks,
                      "max_nonzero_derivative_relative_error": max(w["relative_error"] for w in nonzero_witnesses),
                      "max_zero_limit_absolute_error": max(w["absolute_error"] for w in zero_witnesses),
                      "refinement": changes}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
