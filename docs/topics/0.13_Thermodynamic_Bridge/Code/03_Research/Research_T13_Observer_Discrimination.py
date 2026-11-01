"""Exact bounded W1/W2 controls and pinned W3 feasibility, not a material fit.

Run --check to reproduce without writing; --emit writes three compact records
only after contract/source identities validate. No dataset or network access.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import (  # noqa: E402
    artifact_metadata, identity_bytes, load_json,
)

CONTRACT = "docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/observer_discrimination.json"
OUT = "docs/core/07_artifacts/topic13"
OWNER = "0f17012ffd6ad456c150b10e048efd868ce95588"
SOURCE = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/graphite_nonlinear_response_source_fit.json"


def pole(z, a0, residue, location):
    if z == location:
        raise ValueError("sample on pole")
    return a0 - residue / (location - z)


def joint_parameters(lam, strength, location, gain, offset, clock_scale):
    """x=clock_scale*z, not an additive offset of angular frequency."""
    if clock_scale <= 0 or location <= 0 or strength < 0:
        raise ValueError("need positive squared-frequency scale/pole and nonnegative inherited strength")
    return gain * lam + offset, gain * strength / clock_scale, location / clock_scale


def contrast(z, y, errors):
    """Exact second divided-difference contrast; errors are JOINT box bounds.

    This enclosure needs no probabilistic independence. It is only a necessary
    condition for affine compatibility, not a full pole-feasibility solver.
    """
    if len(z) != 3 or len(y) != 3 or len(errors) != 3:
        raise ValueError("exactly three samples required")
    if not z[0] < z[1] < z[2] or any(e < 0 for e in errors):
        raise ValueError("ordered exact coordinates and nonnegative bounds required")
    left, right = z[1] - z[0], z[2] - z[1]
    weights = (1 / left, -1 / left - 1 / right, 1 / right)
    value = sum(w * v for w, v in zip(weights, y))
    radius = sum(abs(w) * e for w, e in zip(weights, errors))
    return value, radius


def drift_error(gain_error, kernel_bound, offset_error, residual_error):
    """Bound relative to a COMMON constant-gain/background baseline."""
    if min(gain_error, kernel_bound, offset_error, residual_error) < 0:
        raise ValueError("negative bound")
    return gain_error * kernel_bound + offset_error + residual_error


def uniform_affine_witness(z, tolerance):
    """Nonzero pole with residual below tolerance at every supplied coordinate."""
    if not z or tolerance <= 0:
        raise ValueError("finite nonempty design and positive tolerance required")
    location = max(max(z), Q(0)) + 1
    distance = min(abs(location - x) for x in z)
    residue = tolerance * distance / 2
    return location, residue


def w1():
    # Fixed exact fixtures: not inferred coefficients or experimental precision.
    z = tuple(map(Q, (0, 1, 2)))
    params = tuple(map(Q, (2, 3, 8, 4, 5, 2)))
    a0, residue, location = joint_parameters(*params)
    assert all(params[3] * pole(params[5] * x, *params[:3]) + params[4]
               == pole(x, a0, residue, location) for x in z)
    # Change clock scale and all dimensional pole parameters together.
    changed = tuple(map(Q, (2, 9, 24, 4, 5, 6)))
    assert joint_parameters(*changed) == (a0, residue, location)
    # Change gain, L, B, offset while preserving the SAME whole function.
    gain_changed = tuple(map(Q, (1, 6, 8, 2, 11, 2)))
    assert joint_parameters(*gain_changed) == (a0, residue, location)
    return {
        "status": "PASS_EXACT_CONDITIONAL_JOINT_EQUIVALENCE",
        "reused": "Owner constant affine-output invariance and inverse; not rederived as new evidence",
        "joint_formula": "A=g*L+c; D=g*B/a; P=p/a for x=a*z, a>0",
        "global_witness": {"parameters_L_B_p_g_c_a": [str(v) for v in params],
                           "same_output_different_clock": [str(v) for v in changed],
                           "same_output_different_gain": [str(v) for v in gain_changed]},
        "recoverable": "A,D,P only for exact nonconstant finite-pole response; use inherited inverse",
        "unrecoverable": "p without independent a; L,B without g,c; sign(B) without sign(g)",
        "unconstrained_transfer": "Any y_i can be matched by c_i=y_i-g_i*F_i; negative control only",
        "degenerate_cases": ["g=0", "B=0", "on-pole exclusion", "unresolved curvature", "frequency-dependent nuisance"],
        "physical_operator_admitted": False,
    }


def design_grid(denominator):
    """Fixed endpoints [0,2], conditional P=4,D=3, joint error=1/100.

    Grids denominator=4,8,16 have 7+15+31=53 exact candidates. This is a
    synthetic conditional design example, not a material protocol optimization.
    """
    best = None
    for i in range(1, 2 * denominator):
        z = (Q(0), Q(i, denominator), Q(2))
        y = tuple(pole(x, Q(5), Q(3), Q(4)) for x in z)
        value, radius = contrast(z, y, (Q(1, 100),) * 3)
        score = abs(value) / radius
        row = (score, z[1], value, radius)
        if best is None or score > best[0]:
            best = row
    return {"grid_denominator": denominator, "candidates": 2 * denominator - 1,
            "best_midpoint": str(best[1]), "separation_ratio": str(best[0]),
            "contrast": str(best[2]), "error_bound": str(best[3])}


def w2():
    z = (Q(0), Q(1), Q(2))
    y = tuple(pole(x, Q(5), Q(3), Q(4)) for x in z)
    value, radius = contrast(z, y, (Q(1, 100),) * 3)
    assert value == -Q(1, 4) and radius == Q(1, 25)
    assert abs(value) > radius
    p, d = uniform_affine_witness(z, Q(1, 100))
    assert d > 0 and all(abs(pole(x, Q(5), d, p) - 5) < Q(1, 100) for x in z)
    designs = [design_grid(n) for n in (4, 8, 16)]
    assert sum(r["candidates"] for r in designs) == 53
    assert all(Q(b["separation_ratio"]) >= Q(a["separation_ratio"])
               for a, b in zip(designs, designs[1:]))
    return {
        "status": "CONDITIONAL_DESIGN_NO_UNIFORM_DISCRIMINATION",
        "observable": "T=(y3-y2)/(z3-z2)-(y2-y1)/(z2-z1)",
        "error_bound": "E=sum_i |w_i| delta_i; delta_i>=eta_g_i*M_i+eta_c_i+eta_e_i",
        "rule": "|T_observed|>E rejects affine-only output under declared operator/error bounds; otherwise inconclusive",
        "pole_contrast": "T=-D*(z3-z1)/product_i(P-z_i)",
        "coordinates": "Exact declared instrument z; uncertain z needs joint propagation, not this fixed-weight shortcut",
        "conditional_control": {"z": [str(x) for x in z], "T": str(value), "E": str(radius)},
        "no_uniform_proof": "For any finite z and eps>0 choose P>max(z), D=eps*min|P-z|/2>0; all |y-A|<=eps/2",
        "ordinary_pole_competitor": "Identical A,D,P gives identical response on the whole declared domain; no frequency design separates mechanism labels",
        "design_search": designs,
        "search_scope": "53 exact rational candidates, fixed synthetic P,D,error; grid maxima only, not a physical/global optimum",
        "required_for_uniform_design": "Independent nonzero residue/gain lower bound and admissible pole/location/transfer/error constraints; none inferred here",
        "physical_acceptance": False,
    }


def w3(contract):
    item = next(i for i in contract["identities"] if i["path"] == SOURCE)
    source = json.loads(identity_bytes(ROOT, item))
    decision = source["bounded_search_decision"]
    admitted = decision["admitted_discriminator_records"]
    if admitted:
        raise ValueError("Source admission changed: review before scoring; do not auto-run a comparison")
    return {
        "status": "FEASIBILITY_COMPLETE_PHYSICAL_TEST_NOT_RUN",
        "source_commit": item["commit"], "existing_routes_reviewed": len(source["sources"]),
        "admitted_records": admitted, "source_decision": decision["status"],
        "source_reason": decision["reason"],
        "route_dispositions": [{"id": s["id"], "disposition": s["disposition"],
                                "missing": s.get("missing"),
                                "missing_field_recorded": "missing" in s}
                               for s in source["sources"]],
        "missing_input_card": {
            "owner": "Topic13 source/readout owner; Core reviewer for material correspondence",
            "quantity": "Same-state signed phase-resolved Q1,Q2,Q3 and independent linear propagator, or already admitted equivalent mechanical kernel",
            "state": "Independently identified weak-response material mode, finite-stack profile and stationary conditions",
            "protocol": "Distinct controlled drives in same state; direct harmonic forcing absent or bounded",
            "calibration": "Independent clock, amplitude sign/gain, full temporal/nonlinear readout and source transfer; no target-curve fit",
            "processing": "Forward intensity convolution before inversion; provenance/product level and correction history",
            "errors": "Joint bounds including mode/transfer/frequency/background and weak-response truncation; covariance or conservative enclosures",
            "reopen": decision["reopen_only_with"],
        },
        "next_action": "Admit an exact eligible record/operator package; no repeat source search or inherited algebra fixtures",
        "holdout_accessed": False, "new_contact": False, "physical_test_run": False,
        "claim_boundary": "Not a global absence theorem, UET falsification or physical validation",
    }


def records():
    contract = load_json(ROOT / CONTRACT)
    metadata = artifact_metadata(contract, ROOT)  # verifies pinned/local identities
    return {wave: {**payload, **metadata, "wave": wave,
                   "generator_path": Path(__file__).relative_to(ROOT).as_posix(),
                   "evidence_class": "FORMAL_CONDITIONAL_NOT_PHYSICAL_VALIDATION"}
            for wave, payload in (("w1", w1()), ("w2", w2()), ("w3", w3(contract)))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    if args.emit and shutil.disk_usage(ROOT).free < 100 * 1024 * 1024:
        raise SystemExit("Insufficient free space for safe evidence writing")
    result = records()
    for wave, record in result.items():
        target = ROOT / OUT / f"t13_observer_discrimination_{wave}.json"
        content = json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.emit:
            target.write_text(content, encoding="utf-8", newline="\n")
        elif not target.exists() or target.read_text(encoding="utf-8") != content:
            raise SystemExit(f"Missing/drifted generated evidence: {target.relative_to(ROOT)}")
        print(f"{wave}: {record['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
