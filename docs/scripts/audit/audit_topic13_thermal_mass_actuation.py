"""Conditional static mass-source response with thermal Phi backreaction.

The reference tadpole is subtracted explicitly to hold the declared background.
This is not a fitted counterterm or a newly accepted material action.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_matter_strain_susceptibility import thermal_moments


def response(T=.8,x=2.25,eta=.35,curvature=.8):
    m=thermal_moments(T,x)
    effective=curvature+eta**2*m["mass_second_derivative"]
    if curvature<=0 or effective<=0:
        raise ValueError("positive bare and effective static curvature required")
    return dict(effective_curvature=effective,
                mass_gain=eta*m["mass_second_derivative"]/effective,
                temperature_gain=eta*m["mass_temperature_derivative"]/effective,
                frozen_phi_mass_gain=eta*m["mass_second_derivative"]/curvature,
                amplification=curvature/effective)


def equilibrium(u,dT=0.,T=.8,x=2.25,eta=.35,curvature=.8):
    response(T,x,eta,curvature)
    fx0=thermal_moments(T,x)["mass_derivative"]
    def residual(phi):
        return curvature*phi-eta*(thermal_moments(T+dT,x+u-eta*phi)["mass_derivative"]-fx0)
    # Fixed local bracket, not adaptive selection of a remote unstable branch.
    phi=brentq(residual,-.1,.1,xtol=1e-14)
    effective=curvature+eta**2*thermal_moments(T+dT,x+u-eta*phi)["mass_second_derivative"]
    if effective<=0: raise ValueError("root is not a stable local response")
    return phi


def main():
    rows=[]
    for T in (.4,.8,1.2):
        analytic=response(T=T)
        derivatives=[]
        for step in (.01,.005,.0025):
            dm=(equilibrium(step,T=T)-equilibrium(-step,T=T))/(2*step)
            dt=(equilibrium(0.,step,T=T)-equilibrium(0.,-step,T=T))/(2*step)
            derivatives.append(dict(step=step,mass_derivative=dm,temperature_derivative=dt,
                mass_relative_error=abs(dm/analytic["mass_gain"]-1),
                temperature_relative_error=abs(dt/analytic["temperature_gain"]-1)))
        rows.append(dict(T=T,**analytic,derivatives=derivatives))
    paths=["docs/scripts/audit/audit_topic13_thermal_mass_actuation.py",
           "docs/core/test/test_topic13_thermal_mass_actuation.py","docs/core/uet_matter_strain_susceptibility.py"]
    artifact=dict(major_result_id="T13_THERMAL_MASS_SOURCE_STATIC_RESPONSE",topic="0.13",closure_level="PARTIAL",
        equation_or_mapping="A*phi-eta*(F_x(T+dT,x+u-eta*phi)-F_x(T,x))=0; A_eff=A+eta^2*F_xx; dphi/du=eta*F_xx/A_eff; dphi/dT=eta*F_xT/A_eff",
        units="u,x energy^2; phi,T,eta energy; A,A_eff energy^2; F energy^4",
        derivation_class="Implicit derivative of declared local Gaussian thermal free energy",
        observable="Static Phi susceptibility to mass-source or temperature, not a measured material coefficient",
        data_role="SYNTHETIC_CONDITIONAL_SOURCE_RESPONSE",config=dict(x=2.25,eta=.35,curvature=.8,reference_tadpole_subtracted=True),
        what_is_closed="A thermal variance route can drive Phi at linear order without nonzero coherent mean chi; local feedback explicitly retained",
        rows=rows,verification_status="IMPLICIT_ROOT_DERIVATIVE_CHECK",dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["physical_mass_source_gain","bare_coefficient_and_reference_provenance","finite_frequency_and_source_energy_ledger","material_SI_calibration"],
        claim_boundary="Fixed synthetic bare curvature and tadpole convention; do not add this correction again to measured total coefficients. Temperature-driven Phi is not an independent alpha calibration.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths])
    (ROOT/"docs/core/07_artifacts/topic13/t13_thermal_mass_actuation_audit.json").write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    for r in rows: print(r)


if __name__=="__main__":main()
