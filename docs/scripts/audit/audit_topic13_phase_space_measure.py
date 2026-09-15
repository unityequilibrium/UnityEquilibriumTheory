"""Independent product-measure pilot, not a physical collision coefficient.

Radial variables x=p/P lie in [0,1]. Angular averages are normalized.
Fixing the incoming orientation is permitted only for rotational scalars;
tensor response needs a separate global orientation integration.
"""
from hashlib import sha256
import json
from math import exp, pi
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def rule(radial_order, cosine_order, azimuth_order):
    for n in (radial_order, cosine_order, azimuth_order):
        if isinstance(n, bool) or not isinstance(n, int) or n < 2:
            raise ValueError("integer orders >=2 required")
    z, w = np.polynomial.legendre.leggauss(radial_order)
    x = (z + 1) / 2
    radial = w / 2 * x**2
    cosine, angular = np.polynomial.legendre.leggauss(cosine_order)
    return x, radial, cosine, angular / 2, 2*pi*np.arange(azimuth_order)/azimuth_order


def audit_case(n, m, k):
    x, w, c, a, phi = rule(n, m, k)
    # Independent radial indices: all n*n pairs, each counted exactly once.
    radial_pair_weights = w[:, None] * w[None, :]
    moments = {
        "constant": (float(radial_pair_weights.sum()), 1/9),
        "x1_squared_x2_fourth": (float(np.sum(w*x**2)*np.sum(w*x**4)), 1/35),
        "incoming_cosine_squared": (float(np.sum(a*c**2)), 1/3),
        "outgoing_cosine_fourth": (float(np.sum(a*c**4)), 1/5),
        "outgoing_phi_cosine": (float(np.mean(np.cos(phi))), 0.),
        "outgoing_phi_cosine_squared": (float(np.mean(np.cos(phi)**2)), .5),
    }
    # A non-polynomial manufactured integrand, fixed before running.
    # Integral x^2 exp(-b*x) dx = [2-exp(-b)(b^2+2b+2)]/b^3.
    b = 12.
    one = (2-exp(-b)*(b*b+2*b+2))/b**3
    thermal = float(np.sum(w*np.exp(-b*x))**2)
    moments["manufactured_exponential"] = (thermal, one**2)
    errors = {name: abs(value-target) for name, (value, target) in moments.items()}
    return dict(radial_order=n, cosine_order=m, azimuth_order=k,
                independent_radial_pairs=n*n, product_node_count=n*n*m*m*k,
                weights_positive=bool(np.all(w>0) and np.all(a>0)),
                normalized_angular_weight=float(np.sum(a)**2),
                moments={name: dict(measured=value, reference=target, absolute_error=errors[name])
                         for name, (value, target) in moments.items()},
                exponential_relative_error=errors["manufactured_exponential"]/(one**2))


def main():
    rows = [audit_case(n, 6, 16) for n in (4, 8, 16, 32)]
    paths = ["docs/scripts/audit/audit_topic13_phase_space_measure.py",
             "docs/core/test/test_topic13_phase_space_measure.py",
             "docs/core/uet_o2_action_derived_transition_kernel.py"]
    result = dict(
        major_result_id="T13_INDEPENDENT_PHASE_SPACE_MEASURE_PILOT", topic="0.13",
        closure_level="PARTIAL", verification_status="MANUFACTURED_MEASURE_ONLY",
        what_is_closed="Independent radial pair and angular product integration checked against analytic moments",
        equation_or_mapping="x1^2 dx1 x2^2 dx2 dcos(theta12)/2 dcos(theta_star)/2 dphi_star/(2*pi)",
        units="Dimensionless x=p/P; physical radial prefactor P^6/(2*pi^2)^2 excluded",
        derivation_class="Gauss-Legendre product integration and periodic angular average",
        observable="Manufactured scalar integral, not Kubo or heat flux",
        data_role="ANALYTIC_MANUFACTURED_CONTROL_NOT_EXTERNAL_DATA",
        rows=rows, evidence_artifacts=[dict(path=p, sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
        open_blockers=["differential_cross_section_and_species_symmetry_contract", "boosted_Bose_weight_and_collision_integrand", "global_orientation_for_tensor_response", "material_calibration"],
        dependency_unlocked=[], full_core_unlock=False, global_claim_promotion=False,
        claim_boundary="No production replacement. Angular factors are normalized averages, not derived scattering rates. No external data or holdout is read by this runner.")
    out = ROOT/"docs/core/07_artifacts/topic13/t13_phase_space_measure_audit.json"
    out.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    for row in rows:
        print(row["radial_order"], row["independent_radial_pairs"], row["exponential_relative_error"])


if __name__ == "__main__":
    main()
