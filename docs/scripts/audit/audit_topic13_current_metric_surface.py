"""Finite-cutoff integration-by-parts identities for the coupled current metric."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_topic13_coupled_gain_loss_operator import MixtureInputs, mass, bose, vector_factors


def witness(cutoff, mu=.2, order=192, T=.25):
    cfg=MixtureInputs()
    x,w=np.polynomial.legendre.leggauss(order)
    p=cutoff*(x+1)/2; w=cutoff*w/2
    metric=np.zeros((2,2)); n=h=b_n=b_h=0.
    for q in (-1,0,1):
        m=mass(q,cfg); E=np.sqrt(p*p+m*m); f=bose(E-q*mu,T)
        F,_=vector_factors(E,np.full_like(p,q),T)
        metric+=np.einsum('n,ni,nj->ij',w*p**4*f*(1+f)/(6*np.pi**2),F[:,:2],F[:,:2])
        n+=float(np.sum(w*p*p*q*f/(2*np.pi**2)))
        h+=float(np.sum(w*p*p*(E+p*p/(3*E))*f/(2*np.pi**2)))
        ep=np.sqrt(cutoff**2+m*m); fp=float(bose(ep-q*mu,T))
        b_n+=cutoff**3*q*fp/(6*np.pi**2)
        b_h+=cutoff**3*ep*fp/(6*np.pi**2)
    return dict(cutoff=cutoff,mu=mu,order=order,T=T,metric=metric.tolist(),charge_density=n,enthalpy_density=h,
                charge_surface=b_n,enthalpy_surface=b_h,
                corrected_charge_residual=abs(metric[0,1]-(n-b_n))/max(abs(n),h/T),
                corrected_enthalpy_residual=abs(T*metric[0,0]-(h-b_h))/h,
                omitted_enthalpy_surface_fraction=b_h/h,
                momentum_projection_ratio=float(metric[0,1]/metric[0,0]),
                thermodynamic_projection_ratio=T*n/h,
                boundary="Finite-cutoff metric identities, not transport or material calibration")


def main():
    rows=[witness(c) for c in (2.,4.,8.,12.,24.)]
    paths=["docs/scripts/audit/audit_topic13_current_metric_surface.py",
           "docs/core/test/test_topic13_current_metric_surface.py",
           "docs/scripts/audit/audit_topic13_coupled_gain_loss_operator.py"]
    result=dict(major_result_id="T13_CURRENT_METRIC_FINITE_CUTOFF_IDENTITY",topic="0.13",closure_level="PARTIAL",
        equation_or_mapping="T*G00=w-Bw; G01=n-Bn; Bw=P^3 sum E(P)f(P)/(6*pi^2); Bn=P^3 sum q f(P)/(6*pi^2)",
        units="G00 energy^2; G01 energy^3; w,Bw energy^4; n,Bn energy^3",
        derivation_class="Integration by parts of the existing Bose metric",observable="Projection coefficient consistency",
        data_role="SYNTHETIC_DIAGNOSTIC_NO_FIT",rows=rows,
        what_is_closed="Finite-cutoff surface terms explicitly compared with current metric and thermodynamic densities",
        verification_status="MEASURED_IDENTITY_NOT_FULL_CURRENT_MATCH",dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["basis_completeness","physical_collision_current_matching","material_calibration"],
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
        claim_boundary="No modification to projection or rates; no external data/holdout. This is not a remedy for missing material normalization.")
    (ROOT/"docs/core/07_artifacts/topic13/t13_current_metric_surface_audit.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    for r in rows: print(r["cutoff"],r["omitted_enthalpy_surface_fraction"],r["corrected_enthalpy_residual"],r["corrected_charge_residual"])


if __name__=="__main__": main()
