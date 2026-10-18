"""Audit existing action's coefficient image and conditional static falsifier.

No core model modification, measured-response fit or claim of unique UET physics.
The all-field proof is in the linked result note; finite controls test code only.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata,load_json

CONTRACT="docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/action_discrimination.json"
OUTPUT="docs/core/07_artifacts/topic13/t13_action_discrimination.json"


def canonical_coefficients(e,zp,zc,mp2,mc2,lp,lc,h,xi,rho,p,c):
    """Exact coefficients given certified p^2=e*Zp and c^2=Zc.

    The proof permits real square roots. Exact controls supply rational roots;
    no approximate root or singular epsilon chart is silently substituted.
    """
    if e<=0 or zp<=0 or zc<=0 or p<=0 or c<=0 or p*p!=e*zp or c*c!=zc:
        raise ValueError("need invertible canonical chart with certified roots")
    if mp2<0 or min(lp,lc)<=0 or h<0:
        raise ValueError("outside implemented parent coefficient domain")
    return {"M2":mp2/zp,"m2":mc2/zc,"ls":lp/(e*zp*zp),
            "lm":lc/(zc*zc),"g":e*h/(p*c*c),"X":xi/zp,"r0":e*rho}


def exact_action_coefficients(parent,p,c,kappa,cosmological_constant):
    """Coefficient dictionaries after field substitution, independent of fields.

    R*psi^2 and cosmological psi^2 terms are both retained. Equality of
    dictionaries establishes the polynomial identity for arbitrary local jets.
    """
    if kappa<=0:
        raise ValueError("positive gravitational normalization required")
    e,zp,zc,mp2,mc2,lp,lc,h,xi,rho=parent
    a=canonical_coefficients(*parent,p,c)
    before={"R":1/(2*kappa),"constant":-cosmological_constant/kappa-e*rho,
            "R_psi2":e*xi/(2*kappa*p*p),
            "psi2":-e*mp2/(2*p*p)-e*xi*cosmological_constant/(kappa*p*p),
            "psi4":-e*lp/(4*p**4),"eta2":-mc2/(2*c*c),"eta4":-lc/(4*c**4),
            "psi_eta2":e*h/(2*p*c*c),"Kpsi":-e*zp/(2*p*p),"Keta":-zc/(2*c*c)}
    after={"R":1/(2*kappa),"constant":-cosmological_constant/kappa-a["r0"],
           "R_psi2":a["X"]/(2*kappa),
           "psi2":-a["M2"]/2-a["X"]*cosmological_constant/kappa,
           "psi4":-a["ls"]/4,"eta2":-a["m2"]/2,"eta4":-a["lm"]/4,
           "psi_eta2":a["g"]/2,"Kpsi":Q(-1,2),"Keta":Q(-1,2)}
    return before,after


def exact_fixture():
    return tuple(map(Q,(4,1,9,5,7,11,13,3,Q(17,100),19)))


def production_action_control():
    """Pointwise bridge to actual current evaluator, not a PDE solution."""
    import numpy as np
    from docs.core.uet_covariant_response import CovariantResponseConfig,conservative_lagrangian_scalar
    from docs.core.uet_covariant_matter import CovariantMatterConfig,coupled_matter_lagrangian_scalar
    e,zp,zc,mp2,mc2,lp,lc,h,xi,rho=exact_fixture()
    p,c=Q(2),Q(3)
    a={k:float(v) for k,v in canonical_coefficients(*exact_fixture(),p,c).items()}
    rc=CovariantResponseConfig(epsilon_nc=float(e),response_kinetic=float(zp),response_mass_sq=float(mp2),
        response_quartic=float(lp),curvature_coupling=float(xi),equilibrium_density=float(rho),
        einstein_coupling=1.5,cosmological_constant=2,phi_equilibrium=0.25)
    mc=CovariantMatterConfig(matter_kinetic=float(zc),matter_mass_sq=float(mc2),
        matter_quartic=float(lc),response_coupling=float(h))
    inverse=np.diag([-1.,1.,1.,1.])
    chi=np.array([1/3,-2/5]); gradchi=np.array([[1/7,2/9,-1/11,3/13],[-2/7,1/9,3/11,-1/13]])
    gradphi=np.array([1/5,-2/7,1/11,-3/13]); d=2/7; curvature=5/7
    matter=coupled_matter_lagrangian_scalar(inverse,gradchi,chi,rc.phi_equilibrium+d,rc,mc)
    kp=float(gradphi@inverse@gradphi)
    original=conservative_lagrangian_scalar(curvature,kp,rc.phi_equilibrium+d,matter,rc)
    psi=float(p)*d; eta=float(c)*chi; esq=float(eta@eta)
    kinetic_eta=float(np.einsum('am,mn,an->',float(c)*gradchi,inverse,float(c)*gradchi))
    transformed=(1+a['X']*psi**2)*(curvature-2*rc.cosmological_constant)/(2*rc.einstein_coupling)
    transformed-=.5*float(p)**2*kp+.5*kinetic_eta+a['r0']+.5*a['M2']*psi**2
    transformed-=a['ls']*psi**4/4+.5*a['m2']*esq+a['lm']*esq**2/4
    transformed+=a['g']*psi*esq/2
    error=abs(original-transformed)
    if error>1e-12*max(1,abs(original),abs(transformed)):
        raise ValueError("current source action no longer matches audited transformation")
    return {"relative_scaled_residual":error/max(1,abs(original),abs(transformed)),
            "tolerance":1e-12,"scope":"pointwise evaluator consistency only; not physical uncertainty"}


def static_state_at_response(mass2,quartic,coupling,matter_quartic,psi):
    """Evaluate source and exact implicit-response derivatives at chosen psi.

    Choosing a synthetic psi and computing its source avoids an unverified
    cubic root. These are not calibrated experimental parameters.
    """
    if mass2<0 or quartic<=0 or coupling<=0 or matter_quartic<=0 or psi<0:
        raise ValueError("need nonnegative static branch and positive interaction")
    s=2*(mass2*psi+quartic*psi**3)/coupling
    d=mass2+3*quartic*psi**2
    if d==0:
        raise ValueError("massless origin has no finite implicit derivative")
    return {"s":s,"D":d,"dpsi_ds":coupling/(2*d),
            "effective_second":matter_quartic/2-coupling**2/(4*d),
            "effective_third":3*coupling**3*quartic*psi/(4*d**3)}


def identify_cubic_source(z1,u1,z2,u2):
    if z1<=0 or z2<=0 or z1==z2:
        raise ValueError("two distinct nonzero same-orientation response controls required")
    b=(u2/z2-u1/z1)/(z2*z2-z1*z1)
    a=u1/z1-b*z1*z1
    if a<0 or b<=0:
        raise ValueError("controls incompatible with declared monotone cubic class")
    return a,b


def cubic_root_bracket(a,b,u,upper,steps=40):
    if a<0 or b<=0 or u<0 or upper<=0 or not 1<=steps<=64:
        raise ValueError("invalid cubic source or numerical domain")
    if a*upper+b*upper**3<u:
        raise ValueError("root not bracketed; do not expand the job silently")
    lo,hi=Q(0),upper
    if u==0:
        return lo,lo
    for _ in range(steps):
        mid=(lo+hi)/2
        if a*mid+b*mid**3<u:
            lo=mid
        else:
            hi=mid
    return lo,hi


def rectangular_prediction_enclosure(a_interval,b_interval,u_interval,upper):
    """Conservative joint outer rectangle, never an independence assumption."""
    al,ah=a_interval; bl,bh=b_interval; ul,uh=u_interval
    if not (0<=al<=ah and 0<bl<=bh and 0<=ul<=uh):
        raise ValueError("joint enclosing intervals outside stated domain")
    lower=cubic_root_bracket(ah,bh,ul,upper)[0]
    higher=cubic_root_bracket(al,bl,uh,upper)[1]
    return lower,higher


def phase_field_operator_controls():
    """Independent named-order-parameter RHS, same declared discrete operators."""
    import numpy as np
    from docs.core.uet_matter_space import MatterSpaceConfig,MatterSpaceState,matter_space_rhs
    from docs.core.uet_spatial import laplacian_1d
    state=MatterSpaceState(np.array([-.5,.25,.75,-.25]),np.array([.1,.2,-.1,.3]),np.array([.02,-.03,.04,-.01]))
    results={}
    for mode in ('conserved','nonconserved'):
        cfg=MatterSpaceConfig(matter_dynamics=mode)
        s,t,v=state.C,state.space_response,state.space_rate
        lap=lambda x:laplacian_1d(x,.5,cfg.boundary_condition)
        mu_s=cfg.a_matter*s+cfg.b_matter*s**3-cfg.kappa_matter*lap(s)-cfg.coupling_g*s*t
        mu_t=cfg.a_space*t+cfg.b_space*t**3-cfg.kappa_space*lap(t)-cfg.coupling_g*s*s/2
        rhs=(cfg.mobility_matter*lap(mu_s) if mode=='conserved' else -cfg.mobility_matter*mu_s,
             v,(-v-cfg.mobility_space*mu_t)/cfg.tau_space)
        actual=matter_space_rhs(state,.5,cfg)[:3]
        error=max(float(np.max(np.abs(x-y))) for x,y in zip(rhs,actual))
        if error>1e-12:
            raise ValueError('current phase-field RHS differs from inspected ordinary comparator')
        results[mode]=error
    return results


def open_system_operator_controls():
    """Memory feeds dynamics; compare the actual declared linear filter.

    The covariance control does NOT establish an entire stochastic process,
    generate noise trajectories or supply a physical Kubo coefficient.
    """
    import hashlib
    import numpy as np
    from docs.core.uet_covariant_open_system import (KMSCoefficientRecord,MemoryKernelRecord,
        OpenSystemConfig,open_system_evolution,derive_noise_kernel)
    from docs.core.uet_o2_open_system_sk_kms import OpenSystemParameters,retarded_kernel
    l=np.array([[2.,.5],[.5,1.]])
    rec=KMSCoefficientRecord('synthetic_L',l,'formal control units',2.,'fixed control frame',
        'synthetic:action-discrimination-control',hashlib.sha256(b'synthetic:action-discrimination-control').hexdigest(),
        'SYNTHETIC_NOT_KUBO')
    tau=.7; dt=.1
    memory=MemoryKernelRecord(np.array([tau,tau]),rec)
    cfg=OpenSystemConfig(memory,'normalized',np.eye(2))
    history=np.array([[.2,-.1],[.3,.4],[-.2,.5]])
    state=np.array([.4,-.3]); source=np.array([.03,.1])
    expected_force=sum(dt*np.exp(-lag/tau)/tau*(l@f)
                       for lag,f in zip(np.array([2,1,0])*dt,history))
    result=open_system_evolution(state,history,dt,cfg,source)
    memory_error=float(np.max(np.abs(result.physical_rate-(-expected_force+source))))
    state_error=float(np.max(np.abs(result.physical_state-(state+dt*(-expected_force+source)))))
    lags=np.array([-.2,0,.2])
    covariance=derive_noise_kernel(lags,memory).covariance
    expected=np.array([2*rec.temperature*np.exp(-abs(t)/tau)/tau*l for t in lags])
    covariance_error=float(np.max(np.abs(covariance-expected)))
    pars=OpenSystemParameters(beta_th=2.,kappa=3.,chi=4.,gamma=.5)
    omega=.7
    kernel_error=abs(retarded_kernel(omega,pars)-(3-4*omega**2-.5j*omega))
    errors={'retarded_memory_rate':memory_error,'state_update':state_error,
            'classical_covariance':covariance_error,'local_inverse_oscillator_kernel':kernel_error}
    if max(errors.values())>1e-12:
        raise ValueError('current linear open-system operators differ from inspected comparator')
    return errors


def calculate():
    parent=exact_fixture(); p,c=Q(2),Q(3)
    before,after=exact_action_coefficients(parent,p,c,Q(3,2),Q(2))
    if before!=after:
        raise ValueError("coefficient identity failed")
    a,b=identify_cubic_source(Q(1),Q(5),Q(2),Q(28))
    prediction=cubic_root_bracket(a,b,Q(105,8),Q(2))
    if not prediction[0]<=Q(3,2)<=prediction[1]:
        raise ValueError('reserved synthetic source prediction failed')
    outer=rectangular_prediction_enclosure((a-Q(1,100),a+Q(1,100)),
        (b-Q(1,50),b+Q(1,50)),(Q(105,8)-Q(1,1000),Q(105,8)+Q(1,1000)),Q(2))
    static=static_state_at_response(Q(5),Q(3),Q(2),Q(4),Q(1,2))
    return {"status":"FORMAL_ACTION_CLASS_EQUIVALENCE_WITH_CONDITIONAL_STATIC_FALSIFIER",
        "coefficient_identity":before==after,"surjectivity_witness":"e=Zp=Zc=1; parent coefficients equal canonical comparator coefficients",
        "epsilon_zero_chart":"SINGULAR; original action boundary handled separately",
        "production_action_control":production_action_control(),"phase_field_operator_controls":phase_field_operator_controls(),
        "open_system_operator_controls":open_system_operator_controls(),
        "canonical_fixture":{k:str(v) for k,v in canonical_coefficients(*parent,p,c).items()},
        "static_derivative_control":{k:str(v) for k,v in static.items()},
        "calibrated_instrument_law":"u=A*z+B*z^3, A>=0, B>0 with declared static preparation and positive gains",
        "synthetic_fixture":{"A":str(a),"B":str(b),"reserved_source":"105/8","predicted_response_bracket":[str(x) for x in prediction],
                             "synthetic_joint_outer_enclosure":[str(x) for x in outer]},
        "falsification":"Predeclare joint calibration/source and output measurement sets; disjointness rejects specified model/protocol, not all UET or a shared ordinary comparator",
        "unique_UET_discriminator_against_constructed_scalar_comparator":False,
        "physical_acceptance":False,"experimental_rows_scored":0,"new_core_terms":0,
        "null_member":"e>0,h=xi=rho=0,d=initial_d_dot=0; no extra response sector signal",
        "alternatives_reviewed":["full nonminimal curvature action","prior two-mode/pole and MEMS","static quartic response","normalized conserved/nonconserved phase field","retarded trace postprocessor","tree-level O2/current symmetry","linear physical-memory and formal SK/KMS operators"],
        "scope_limit":"Audited existing action and connected observer routes, not every UET topic or any possible future physical theory",
        "next_for_effective_test":"Admit prepared matter-invariant source, zero offsets, common linear readout and joint omission/calibration sets; freeze A,B before held-out source",
        "next_for_unique_test":"An independently justified cross-system coefficient lock or physical source/detector relation outside comparator image; not a newly fitted term"}


def record():
    return {**calculate(),**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),
            "generator_path":Path(__file__).relative_to(ROOT).as_posix(),"evidence_class":"FORMAL_CONDITIONAL_NOT_PHYSICAL_VALIDATION"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--emit',action='store_true'); mode.add_argument('--check',action='store_true')
    args=p.parse_args()
    text=json.dumps(record(),ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    path=ROOT/OUTPUT
    if args.emit:
        if shutil.disk_usage(ROOT).free<100*1024*1024:
            raise SystemExit('Insufficient free space')
        path.write_text(text,encoding='utf-8',newline='\n')
    elif not path.exists() or path.read_text(encoding='utf-8')!=text:
        raise SystemExit('Missing or drifted evidence; check does not write')
    print('FORMAL_ACTION_CLASS_EQUIVALENCE_WITH_CONDITIONAL_STATIC_FALSIFIER; no physical score')


if __name__=='__main__':
    main()
