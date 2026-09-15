"""Conditional polynomial symmetry, not a measured lattice anisotropy."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_shear_symmetry import e2_group,rotation


def monomials(points,degree):
    x,y=points.T
    return np.column_stack([x**(degree-k)*y**k for k in range(degree+1)])


def invariant_dimension(degree,group):
    angles=2*np.pi*np.arange(32)/32
    points=np.column_stack([np.cos(angles),np.sin(angles)])
    base=monomials(points,degree)
    matrix=np.vstack([monomials(points@g.T,degree)-base for g in group])
    return degree+1-int(np.sum(np.linalg.svd(matrix,compute_uv=False)>1e-10))


def cubic(points):
    x,y=np.asarray(points).T
    return x**3-3*x*y*y


def main():
    points=np.array([[1.,0.],[.3,.8],[-.4,.2]])
    rows=[dict(degree=d,e2_dimension=invariant_dimension(d,e2_group()),
               continuous_rotation_dimension=invariant_dimension(d,[rotation(np.sqrt(2.))])) for d in range(1,7)]
    files=["docs/scripts/audit/audit_topic13_e2g_nonlinear_symmetry.py",
           "docs/core/test/test_topic13_e2g_nonlinear_symmetry.py","docs/core/uet_shear_symmetry.py"]
    r=dict(major_result_id="T13_E2G_NONLINEAR_O2_MATCH_BOUNDARY",topic="0.13",closure_level="PARTIAL",
        what_is_closed="Conditional E2 representation permits a cubic invariant absent from continuous O(2)",
        equation_or_mapping="I3=s1^3-3*s1*s2^2=r^3*cos(3theta); internal torque=-partial_theta(c3*I3)",
        units="I3 displacement^3; c3 fixed by chosen energy density units, not supplied",
        derivation_class="Conditional polynomial group algebra",observable="Allowed anisotropic term, not a measured coefficient",
        data_role="NO_MATERIAL_CALIBRATION",rows=rows,
        cubic_group_residual=max(float(np.max(abs(cubic(points@g.T)-cubic(points)))) for g in e2_group()),
        arbitrary_rotation_difference=float(np.max(abs(cubic(points@rotation(np.pi/6).T)-cubic(points)))),
        verification_status="POLYNOMIAL_SYMMETRY_CONTROL",dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["material_representation_and_extra_symmetries","anisotropy_coefficient_or_suppression_bound","dispersion_and_kinetic_residue"],
        claim_boundary="Allowed does not mean nonzero. Harmonic/emergent O(2) remains possible in a declared approximation; two components alone do not establish exact O(2) charge.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in files])
    (ROOT/"docs/core/07_artifacts/topic13/t13_e2g_nonlinear_symmetry_audit.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(rows=rows,residual=r["cubic_group_residual"],rotation_difference=r["arbitrary_rotation_difference"])))


if __name__=="__main__":main()
