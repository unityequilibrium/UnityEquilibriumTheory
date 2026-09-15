"""Taylor control of Popov et al. arXiv:1205.0777 Eq.(1); model only."""
import json
from pathlib import Path
import numpy as np
K=2*np.pi/3
ROOT=Path(__file__).resolve().parents[3]


def potential(x,y):
    return 1.5+np.cos(2*K*x-2*np.pi/3)-2*np.cos(K*x-np.pi/3)*np.cos(np.sqrt(3)*K*y)


def gradient(x,y):
    return np.array([-2*K*np.sin(2*K*x-2*np.pi/3)+2*K*np.sin(K*x-np.pi/3)*np.cos(np.sqrt(3)*K*y),
        2*np.sqrt(3)*K*np.cos(K*x-np.pi/3)*np.sin(np.sqrt(3)*K*y)])


def scan(radius):
    angle=np.arange(360)*2*np.pi/360
    p=radius*np.array([np.cos(angle),np.sin(angle)])
    exact=gradient(*p); harmonic=3*K*K*p
    cubic=-np.sqrt(3)*K**3/2
    third=cubic*np.array([3*p[0]**2-3*p[1]**2,-6*p[0]*p[1]])
    denominator=3*K*K*radius
    return dict(radius_over_bond=radius,leading_force_ratio=np.pi/np.sqrt(3)*radius,
                sampled_full_force_ratio=float(np.max(np.linalg.norm(exact-harmonic,axis=0))/denominator),
                sampled_after_cubic_ratio=float(np.max(np.linalg.norm(exact-harmonic-third,axis=0))/denominator))


def main():
    r=dict(major_result_id="T13_FIRST_FOURIER_SHEAR_ANISOTROPY_ESTIMATE",topic="0.13",closure_level="PARTIAL",
        source=dict(url="https://arxiv.org/pdf/1205.0777",locator="Equation(1), PDF page4",role="PUBLISHED_MODEL_NOT_DIRECT_CUBIC_MEASUREMENT"),
        equation_or_mapping="U/U1=3*k^2*r^2/2-sqrt(3)*k^3*(x^3-3*x*y^2)/2+O(r^4); k=2*pi/3 for x,y in bond-length units",
        units="Normalized U/U1 and displacement/bond length; no UET coefficient",
        derivation_class="Taylor expansion of published first-spatial-harmonic approximation",
        rows=[scan(r) for r in (.001,.002,.005,.01,.02)],
        illustrative_leading_one_percent_radius_over_bond=.01*np.sqrt(3)/np.pi,
        illustrative_radius_angstrom_at_source_bond_1p42=.01*np.sqrt(3)/np.pi*1.42,
        what_is_closed="Model-dependent leading anisotropic force ratio is pi*r/(sqrt(3)*bond_length), independent of U1",
        verification_status="TAYLOR_NUMERICAL_CONTROL",dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["higher_spatial_harmonic_derivatives","same_state_mode_amplitude_and_normalization","anharmonic_thermal_dynamics"],
        claim_boundary="One-percent illustration is not a changed acceptance threshold or proven material bound. Small potential-fit error does not bound third derivatives. No physical c3, alpha, holdout or full-topic promotion.")
    from hashlib import sha256
    r["evidence_artifacts"]=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
        "docs/scripts/audit/audit_topic13_fourier_shear_anisotropy.py","docs/core/test/test_topic13_fourier_shear_anisotropy.py")]
    (ROOT/"docs/core/07_artifacts/topic13/t13_fourier_shear_anisotropy_audit.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(r["rows"]))


if __name__=="__main__":main()
