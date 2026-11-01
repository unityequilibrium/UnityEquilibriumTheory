"""Exact conditional two-channel calibration controls, not a physical fit."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

CONTRACT = "docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/dual_channel_identifiability.json"
OUTPUT = "docs/core/07_artifacts/topic13/t13_dual_channel_identifiability.json"


def observed_coefficients(kappa, mq, mr, gq, gr, lam):
    if mq <= 0 or mr <= 0 or gq == 0 or gr == 0:
        raise ValueError("positive masses and nonzero real gains required")
    alpha, beta = 2*kappa/mq, kappa/mr
    return lam/gq**2, alpha/gr, beta*gr/gq**2


def equilibrium(y, wr2, ell, a, b):
    if wr2 <= 0:
        raise ValueError("stable auxiliary stiffness required")
    z = -b*y*y/wr2
    return z, ell*y**3 + a*y*z


def identify(row1, row2):
    """Rows (y,z,Rq), with independently calibrated Rq, not fitted forcing."""
    y1, z1, r1 = row1
    y2, z2, r2 = row2
    u1, v1, u2, v2 = y1**3, y1*z1, y2**3, y2*z2
    det = u1*v2-u2*v1
    if det == 0:
        raise ValueError("collinear controls: ell and a cannot be separated")
    return (r1*v2-r2*v1)/det, (u1*r2-u2*r1)/det


def auxiliary_coefficient(y, rr):
    if y == 0:
        raise ValueError("nonzero primary coordinate required")
    return rr/y**2


def reciprocity_residual(a, b, mq, mr, gain_ratio):
    """gain_ratio=gr/gq must be independently calibrated, not solved from a/b."""
    if mq <= 0 or mr <= 0 or gain_ratio == 0:
        raise ValueError("invalid mass or relative gain")
    return mq*a*gain_ratio**2-2*mr*b


def calculation():
    # One exact rational fixture, two calibration controls and one reserved control.
    # These are arbitrary method controls, not material parameters/measurements.
    ell, a, b = observed_coefficients(Q(2), Q(2), Q(4), Q(3), Q(5), Q(3))
    wr2 = Q(4)
    for y in (Q(1), Q(2), Q(3)):
        self_output = equilibrium(y, wr2, ell, a, b)
        shifted = equilibrium(y, wr2, ell+Q(7)*b/wr2, a+Q(7), b)
        assert self_output == shifted
    # Independent auxiliary forcing is needed to set these off-equilibrium z.
    controls = ((Q(1), Q(1)), (Q(1), Q(2)))
    rows = tuple((y,z,ell*y**3+a*y*z) for y,z in controls)
    fitted_ell, fitted_a = identify(*rows)
    fitted_b = auxiliary_coefficient(Q(1), b)
    assert (fitted_ell, fitted_a, fitted_b) == (ell, a, b)
    y3, z3 = Q(2), Q(3)
    predicted = fitted_ell*y3**3+fitted_a*y3*z3
    reserved = ell*y3**3+a*y3*z3
    assert predicted == reserved
    assert reciprocity_residual(a,b,Q(2),Q(4),Q(5,3)) == 0
    return {
        "status": "PASS_EXACT_CONDITIONAL_DUAL_CHANNEL_DESIGN",
        "scope": "Generic conservative two-coordinate interaction; material/UET correspondence not admitted",
        "interaction": "V_int=kappa*q^2*r; alpha=2*kappa/mq; beta=kappa/mr",
        "observed": "ell=lambda/Gq^2; a=alpha/Gr; b=beta*Gr/Gq^2, offsets/phase already calibrated",
        "passive_no_go": "sr=0 static: z=-b*y^2/wr2; Rq=(ell-a*b/wr2)*y^3; a->a+t,ell->ell+t*b/wr2 preserves both channels",
        "active_design": "two independent rows (y^3,y*z), nonzero determinant, calibrated sources; b from Rr/y^2",
        "reciprocity_rule": "mq*a*(Gr/Gq)^2-2*mr*b=0; known positive modal masses, independent relative gains and error budget required",
        "unknown_gain_boundary": "Any nonzero same-sign a,b can satisfy reciprocity by choosing a relative gain; opposite signs cannot under this real constant-gain positive-mass model",
        "synthetic_controls": {"ell":str(ell),"a":str(a),"b":str(b),
                               "calibration_rows":[[str(v) for v in row] for row in rows],
                               "reserved_y_z":[str(y3),str(z3)],"predicted_Rq":str(predicted)},
        "limits": ["unknown or freely fitted forcing destroys the inference",
                   "singular/near-collinear controls are not identified by adding samples on same line",
                   "finite-noise uncertainty and damping/omitted terms need a physical contract",
                   "same interaction in ordinary mechanics gives same predictions; no UET-specific mechanism discrimination"],
        "next_action": "No physical scoring: need admitted material operator and independently calibrated two-channel sources/gain ratio/masses, or an independently constrained distinguishing relation",
        "physical_acceptance":False,"holdout_accessed":False,"new_source_search":False,
    }


def record():
    metadata = artifact_metadata(load_json(ROOT/CONTRACT), ROOT)
    return {**calculation(), **metadata,
            "generator_path":Path(__file__).relative_to(ROOT).as_posix(),
            "evidence_class":"FORMAL_CONDITIONAL_NOT_PHYSICAL_VALIDATION"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit",action="store_true")
    mode.add_argument("--check",action="store_true")
    args=p.parse_args()
    content=json.dumps(record(),indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    path=ROOT/OUTPUT
    if args.emit:
        if shutil.disk_usage(ROOT).free < 100*1024*1024:
            raise SystemExit("Insufficient disk space")
        path.write_text(content,encoding="utf-8",newline="\n")
    elif not path.exists() or path.read_text(encoding="utf-8") != content:
        raise SystemExit("Missing/drifted evidence; --check does not write")
    print("PASS_EXACT_CONDITIONAL_DUAL_CHANNEL_DESIGN; physical acceptance remains false")


if __name__=="__main__":
    main()
