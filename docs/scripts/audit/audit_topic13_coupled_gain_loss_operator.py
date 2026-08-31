"""Coupled normal matter/response 2<->2 gain-loss diagnostic.

This is a tree quasiparticle truncation, not a complete finite-temperature
theory. The neutral label denotes the canonical response mode in this lane,
not a new physical substance or a redefinition of Phi.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import pi, sqrt
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.linalg import eigh
from docs.core.uet_covariant_response import CovariantResponseConfig, response_potential
from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import (
    ActionInputs, bose,
)

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/core/artifacts/t13_coupled_gain_loss_operator_audit.json"
REGISTRY_OUT=ROOT/"docs/core/artifacts/uet_equation_correspondence_registry_topic13_gain_loss_addendum.json"
EQUATION_ID="uet.o2.thermal.normal_coupled_gain_loss"
CHANNELS=(
    ("++", (1,1,1,1)), ("--",(-1,-1,-1,-1)),
    ("+-",(1,-1,1,-1)), ("+0",(1,0,1,0)), ("-0",(-1,0,-1,0)),
    ("00",(0,0,0,0)), ("pair_conversion",(1,-1,0,0)),
)
# Independent refinement axes, fixed before evaluating their responses.
REFINEMENT_GRIDS={
    "reference":(18,8,12,10.),
    "radial":(24,8,12,10.),
    "angular":(18,12,12,10.),
    "azimuth":(18,8,16,10.),
    "cutoff":(18,8,12,12.),
}
DIAGNOSTIC_REFINEMENT_TOLERANCE=2e-3


@dataclass(frozen=True)
class MixtureInputs(ActionInputs):
    response_quartic: float=1.

    def __post_init__(self):
        super().__post_init__()
        if self.response_quartic<=0:
            raise ValueError("positive response quartic required")

    @property
    def neutral_quartic(self):
        return self.response_quartic/(self.epsilon*self.response_kinetic**2)


def mass(q,cfg):
    if q not in (-1,0,1):
        raise ValueError("species must be -1, 0 or 1")
    return sqrt(cfg.response_mass_sq) if q==0 else cfg.mass


def polarization(q):
    if q==0:
        return np.array([0.,0.,1.],complex)
    if q not in (-1,1):
        raise ValueError("species must be -1, 0 or 1")
    return np.array([1.,1.j*q,0.])/sqrt(2.)


def tensors(cfg):
    delta=np.eye(2)
    quartic=np.zeros((3,3,3,3))
    quartic[:2,:2,:2,:2]=2*cfg.coupling*(
        np.einsum("ab,cd->abcd",delta,delta)
        +np.einsum("ac,bd->abcd",delta,delta)
        +np.einsum("ad,bc->abcd",delta,delta))
    quartic[2,2,2,2]=6*cfg.neutral_quartic
    cubic=np.zeros((3,3,3))
    for a in (0,1):
        cubic[a,a,2]=cubic[a,2,a]=cubic[2,a,a]=-cfg.cubic
    return cubic,quartic


def channel_amplitude(s,t,u,charges,cfg=MixtureInputs()):
    if len(charges)!=4 or any(q not in (-1,0,1) for q in charges):
        raise ValueError("four valid species labels required")
    if any(np.any(~np.isfinite(x)) for x in (s,t,u)):
        raise ValueError("finite Mandelstam invariants required")
    q1,q2,q3,q4=charges
    if q1+q2!=q3+q4:
        return np.zeros_like(np.asarray(t),complex)
    cubic,quartic=tensors(cfg)
    legs=[polarization(q) for q in (q1,q2,-q3,-q4)]
    result=np.full(np.broadcast(np.asarray(s),np.asarray(t),np.asarray(u)).shape,
                   np.einsum("abcd,a,b,c,d",quartic,*legs),dtype=complex)
    for invariant,(a,b,c,d) in zip((s,t,u),((0,1,2,3),(0,2,1,3),(0,3,1,2))):
        left=np.einsum("abi,a,b->i",cubic,legs[a],legs[b])
        right=np.einsum("cdi,c,d->i",cubic,legs[c],legs[d])
        for internal in range(3):
            coefficient=left[internal]*right[internal]
            if abs(coefficient)==0:
                continue
            m2=cfg.mass**2 if internal<2 else cfg.response_mass_sq
            denominator=np.asarray(invariant)-m2
            if np.any(abs(denominator)<1e-12):
                raise ValueError("propagator pole requires separate resummation")
            result+=coefficient/denominator
    return result


def counting_weight(charges):
    q1,q2,q3,q4=charges
    initial=2 if q1==q2 else 1
    final=2 if q3==q4 else 1
    # Elastic phase space already contains a reaction and its reverse.
    reversal=2 if sorted((q1,q2))==sorted((q3,q4)) else 1
    return 1./(initial*final*reversal)


def boost(energy,momenta,beta):
    """Boost a batch of CM vectors; no cone/trajectory clipping."""
    b2=float(beta@beta)
    if b2==0:
        return np.asarray(energy)+np.zeros(len(momenta)),momenta.copy()
    gamma=1./sqrt(1-b2)
    projection=momenta@beta
    e=np.asarray(energy)
    return gamma*(e+projection),momenta+(
        ((gamma-1)*projection/b2+gamma*e)[:,None]*beta[None,:]
    )


def events(p1,p2,cosine,charges,out_cos,azimuth,cfg):
    masses=[mass(q,cfg) for q in charges]
    e1,e2=sqrt(p1*p1+masses[0]**2),sqrt(p2*p2+masses[1]**2)
    v1=np.array([0.,0.,p1]); v2=np.array([p2*sqrt(1-cosine*cosine),0.,p2*cosine])
    total=e1+e2; beta=(v1+v2)/total
    s=total*total-float((v1+v2)@(v1+v2))
    if s<=(masses[2]+masses[3])**2:
        return None  # Exact final-state threshold, not a numerical filter.
    root=sqrt(s)
    pin=sqrt((s-(masses[0]+masses[1])**2)*(s-(masses[0]-masses[1])**2))/(2*root)
    pout=sqrt((s-(masses[2]+masses[3])**2)*(s-(masses[2]-masses[3])**2))/(2*root)
    e3star=(s+masses[2]**2-masses[3]**2)/(2*root)
    e4star=(s+masses[3]**2-masses[2]**2)/(2*root)
    _,v1star=boost(np.array([e1]),v1[None,:],-beta)
    axis=v1star[0]/pin
    side=np.array([0.,1.,0.])
    transverse=np.cross(side,axis)
    x,az=np.meshgrid(out_cos,azimuth,indexing="ij")
    directions=(x[...,None]*axis+np.sqrt(1-x*x)[...,None]*(
        np.cos(az)[...,None]*transverse+np.sin(az)[...,None]*side)).reshape(-1,3)
    e3,v3=boost(np.full(len(directions),e3star),pout*directions,beta)
    e4,v4=boost(np.full(len(directions),e4star),-pout*directions,beta)
    energies=np.column_stack((np.full(len(e3),e1),np.full(len(e3),e2),e3,e4))
    momenta=np.stack((np.broadcast_to(v1,v3.shape),np.broadcast_to(v2,v3.shape),v3,v4),axis=1)
    t=(e1-e3)**2-np.sum((v1-v3)**2,axis=1)
    u=(e1-e4)**2-np.sum((v1-v4)**2,axis=1)
    return energies,momenta,s,t,u,pout/root


def vector_factors(energies,q,T,basis_order=0):
    neutral=(q==0).astype(float)
    values=[np.ones_like(q)/T,q/energies,neutral/energies,energies/T**2]
    names=["p/T","charge*p/E","neutral*p/E","E*p/T^2"]
    for power in range(1,basis_order+1):
        values.extend((q/energies*(energies/T)**power,neutral/energies*(energies/T)**power))
        names.extend((f"charge*p/E*(E/T)^{power}",f"neutral*p/E*(E/T)^{power}"))
        if power>=2:
            values.append((energies/T)**power/T)
            names.append(f"p/T*(E/T)^{power}")
    return np.stack(values,axis=-1),names


def affinities(energies,momenta,charges,T,basis_order=0):
    q=np.broadcast_to(np.asarray(charges),(len(energies),4))
    neutral=(q==0).astype(float)
    scalar=np.stack((q,energies/T,np.ones_like(q),neutral,(energies/T)**2,q*energies/T),axis=-1)
    factors,_=vector_factors(energies,q,T,basis_order)
    vector=factors[...,None]*momenta[:,:,None,:]
    return scalar,vector


def gain_loss(energies,charges,T,mu,psi,eta):
    exponents=(energies-np.asarray(charges)*mu)/T-eta*psi
    if np.any(exponents<=0):
        raise ValueError("perturbation left the positive Bose domain")
    n=np.exp(-exponents)/(-np.expm1(-exponents))
    f=n[:,0]*n[:,1]*(1+n[:,2])*(1+n[:,3])
    r=n[:,2]*n[:,3]*(1+n[:,0])*(1+n[:,1])
    return f,r


def gain_loss_witness(cfg=MixtureInputs(),T=.25,mu=.2):
    """Resolve non-null perturbations independently of the integration grid.

    Dividing a finite-difference residual by a nearly invariant affinity is
    ill-conditioned. Keep that old grid probe as a diagnostic, not a gate.
    These declared sample momenta and steps are not selected from a TTG curve.
    """
    rows=[]
    for name,charges in CHANNELS:
        E,_,*_=events(.7,1.3,.2,charges,np.array([-.8,.1,.7]),
                      np.array([.1,1.8,4.2]),cfg)
        q=np.asarray(charges)
        psi=np.sin(E/T)+.2*q*E/T+.3*(q==0)
        delta=psi[:,0]+psi[:,1]-psi[:,2]-psi[:,3]
        f,_=gain_loss(E,charges,T,mu,psi,0.)
        expected=f*delta
        derivatives=[]
        for eta in (1e-3,1e-4,1e-5):
            fp,rp=gain_loss(E,charges,T,mu,psi,eta)
            fm,rm=gain_loss(E,charges,T,mu,psi,-eta)
            actual=((fp-rp)-(fm-rm))/(2*eta)
            derivatives.append(float(np.max(abs(actual-expected))/np.max(abs(expected))))
        entropy=[]; affinity=[]
        for eta in (-.1,.1):
            fp,rp=gain_loss(E,charges,T,mu,psi,eta)
            logratio=np.log(fp)-np.log(rp)
            entropy.append(float(np.min((fp-rp)*logratio)))
            affinity.append(float(np.max(abs(logratio-eta*delta))))
        rows.append({"channel":name,"relative_derivative_errors":derivatives,
                     "minimum_event_entropy_production":min(entropy),
                     "max_log_affinity_error":max(affinity),
                     "max_abs_affinity":float(np.max(abs(delta)))})
    return {"incoming_momenta":[.7,1.3],"incoming_cosine":.2,
            "steps":[1e-3,1e-4,1e-5],"entropy_steps":[-.1,.1],"channels":rows}


def neutral_quartic_witness(cfg=MixtureInputs()):
    rc=CovariantResponseConfig(epsilon_nc=cfg.epsilon,
         response_kinetic=cfg.response_kinetic,response_mass_sq=cfg.response_mass_squared,
         response_quartic=cfg.response_quartic)
    v=lambda x:cfg.epsilon*response_potential(x/sqrt(cfg.epsilon*cfg.response_kinetic),rc)
    return [(v(-2*h)-4*v(-h)+6*v(0)-4*v(h)+v(2*h))/h**4 for h in (.02,.04)]


def operator_grid(cfg=MixtureInputs(),T=.25,mu=.2,radial=8,angular=6,azimuth=8,cutoff=8.,basis_order=0):
    if not np.isfinite(T) or not np.isfinite(mu) or T<=0 or abs(mu)>=cfg.mass or cfg.response_mass_sq>=4*cfg.mass**2:
        raise ValueError("strict nonresonant normal mixture required")
    if not np.isfinite(cutoff) or cutoff<=0:
        raise ValueError("positive finite momentum cutoff required")
    if any(isinstance(n,bool) or not isinstance(n,(int,np.integer)) or n<4 for n in (radial,angular,azimuth)):
        raise ValueError("integer quadrature orders >=4 required")
    if isinstance(basis_order,bool) or not isinstance(basis_order,(int,np.integer)) or basis_order<0 or basis_order>3:
        raise ValueError("declared basis order must be 0 through 3")
    nodes,weights=np.polynomial.legendre.leggauss(radial)
    ps,ws=.5*cutoff*(nodes+1),.5*cutoff*weights
    inc,iw=np.polynomial.legendre.leggauss(angular)
    out,ow=np.polynomial.legendre.leggauss(angular)
    az=2*pi*(np.arange(azimuth)+.5)/azimuth
    angle_weights=np.repeat(ow,azimuth)*2*pi/azimuth
    _,vector_names=vector_factors(np.ones(1),np.ones(1),T,basis_order)
    scalar=np.zeros((6,6)); vector=np.zeros((len(vector_names),len(vector_names))); rows=[]
    max_balance=max_energy=max_momentum=max_linear=0.
    eta=1e-6
    for name,charges in CHANNELS:
        local_s=np.zeros_like(scalar); local_v=np.zeros_like(vector); accepted=0
        scalar_activity=0.
        for p1,w1 in zip(ps,ws):
            e1=sqrt(p1*p1+mass(charges[0],cfg)**2)
            for p2,w2 in zip(ps,ws):
                e2=sqrt(p2*p2+mass(charges[1],cfg)**2)
                for c,wc in zip(inc,iw):
                    event=events(p1,p2,c,charges,out,az,cfg)
                    if event is None:
                        continue
                    E,P,s,t,u,phase=event
                    phi_s,phi_v=affinities(E,P,charges,T,basis_order)
                    ds=phi_s[:,0]+phi_s[:,1]-phi_s[:,2]-phi_s[:,3]
                    dv=phi_v[:,0]+phi_v[:,1]-phi_v[:,2]-phi_v[:,3]
                    amp=channel_amplitude(s,t,u,charges,cfg)
                    measure=(w1*w2*wc*p1*p1*p2*p2/(32*pi**4*e1*e2)
                             *phase/(16*pi*pi)*angle_weights*counting_weight(charges))
                    f,r=gain_loss(E,charges,T,mu,np.zeros_like(E),0.)
                    weight=measure*abs(amp)**2*f
                    local_s+=np.einsum("n,ni,nj->ij",weight,ds,ds)
                    local_v+=np.einsum("n,nic,njc->ij",weight,dv,dv)/3
                    scalar_activity+=float(weight.sum())
                    max_balance=max(max_balance,float(np.max(abs(f-r)/np.maximum(f,r))))
                    max_energy=max(max_energy,float(np.max(abs(E[:,0]+E[:,1]-E[:,2]-E[:,3]))))
                    max_momentum=max(max_momentum,float(np.max(abs(P[:,0]+P[:,1]-P[:,2]-P[:,3]))))
                    if accepted==0:
                        # Differentiate actual Bose gain/loss, not an assumed Jacobian.
                        psi=.05*phi_s[:,:,3]+.001*phi_s[:,:,4]
                        fp,rp=gain_loss(E,charges,T,mu,psi,eta)
                        fm,rm=gain_loss(E,charges,T,mu,psi,-eta)
                        predicted=f*(psi[:,0]+psi[:,1]-psi[:,2]-psi[:,3])
                        measured=((fp-rp)-(fm-rm))/(2*eta)
                        scale=max(float(np.max(abs(predicted))),float(np.max(f))*1e-8)
                        max_linear=max(max_linear,float(np.max(abs(measured-predicted)))/scale)
                    accepted+=1
        scalar+=local_s; vector+=local_v
        rows.append({"channel":name,"charges":list(charges),"counting_weight":counting_weight(charges),
                     "sampled_incoming_cells":accepted,"equilibrium_event_weight":scalar_activity,
                     "neutral_number_relaxation_form":float(local_s[3,3]),
                     "scalar_matrix":local_s.tolist(),"vector_matrix":local_v.tolist()})
    snorm=max(float(np.linalg.norm(scalar)),1e-300)
    vnorm=max(float(np.linalg.norm(vector)),1e-300)
    return {
        "state":{"config":asdict(cfg),"T":T,"mu":mu},
        "grid":{"radial":radial,"angular":angular,"azimuth":azimuth,"cutoff":cutoff},
        "basis_order":basis_order,
        "scalar_basis":["charge","E/T","total_count","neutral_count","(E/T)^2","charge*E/T"],
        "vector_basis":vector_names,
        "scalar_matrix":scalar.tolist(),"vector_matrix":vector.tolist(),"channels":rows,
        "max_detailed_balance_relative_error":max_balance,
        "max_energy_residual":max_energy,"max_momentum_residual":max_momentum,
        "near_null_first_cell_fd_relative_error":max_linear,
        "scalar_invariant_relative_residual":float(np.linalg.norm(scalar[:3,:]))/snorm,
        "momentum_null_relative_residual":float(np.linalg.norm(vector[0,:]))/vnorm,
        "scalar_min_eigenvalue_relative":float(np.linalg.eigvalsh(scalar)[0])/snorm,
        "vector_min_eigenvalue_relative":float(np.linalg.eigvalsh(vector)[0])/vnorm,
    }


def charge_response(record,cfg=None,T=None,mu=None,*,metric_order=192,metric_cutoff=24.):
    # Radial Bose covariance of one vector component. No fitted relaxation time.
    state=record["state"]
    cfg=MixtureInputs(**state["config"]) if cfg is None else cfg
    T=state["T"] if T is None else T
    mu=state["mu"] if mu is None else mu
    if asdict(cfg)!=state["config"] or T!=state["T"] or mu!=state["mu"]:
        raise ValueError("collision and current states must agree")
    if cfg.cubic==0:
        raise ValueError("decoupled sectors require separate momentum-null projection, not this inverse")
    if isinstance(metric_order,bool) or not isinstance(metric_order,(int,np.integer)) or metric_order<4 or not np.isfinite(metric_cutoff) or metric_cutoff<=0:
        raise ValueError("valid metric quadrature required")
    x,w=np.polynomial.legendre.leggauss(metric_order)
    p=.5*metric_cutoff*(x+1); w=.5*metric_cutoff*w
    size=len(record["vector_basis"])
    metric=np.zeros((size,size)); charge=enthalpy=0.
    for q in (-1,0,1):
        E=np.sqrt(p*p+mass(q,cfg)**2); f=bose(E-q*mu,T)
        F,_=vector_factors(E,np.full_like(p,q),T,record["basis_order"])
        measure=w*p**4*f*(1+f)/(6*pi*pi)
        metric+=np.einsum("n,ni,nj->ij",measure,F,F)
        charge+=float(np.sum(w*p*p/(2*pi*pi)*q*f))
        enthalpy+=float(np.sum(w*p*p/(2*pi*pi)*(E+p*p/(3*E))*f))
    projected=metric[1:,1:]-np.outer(metric[1:,0],metric[0,1:])/metric[0,0]
    source=metric[1:,1]-metric[1:,0]*metric[0,1]/metric[0,0]
    collision=np.asarray(record["vector_matrix"])[1:,1:]
    solution=np.linalg.solve(collision,source)
    response=float(source@solution)
    scale=np.sqrt(np.diag(projected))
    correlation=projected/np.outer(scale,scale)
    scaled_collision=collision/np.outer(scale,scale)
    rates,modes=eigh(collision,projected)
    if np.any(rates<=0):
        raise ValueError("positive active collision spectrum required; no artificial regulator")
    contributions=(modes.T@source)**2/rates
    return {"metric":metric.tolist(),"projected_charge_source":source.tolist(),
            "metric_grid":{"radial":metric_order,"cutoff":metric_cutoff},
            "finite_basis_charge_response":response,"units":"natural energy^2",
            "active_basis_count":size-1,
            "metric_scaled_collision_condition":float(np.linalg.cond(scaled_collision)),
            "metric_correlation_condition":float(np.linalg.cond(correlation)),
            "linear_solve_relative_residual":float(np.linalg.norm(collision@solution-source)/np.linalg.norm(source)),
            "generalized_active_rates":rates.tolist(),
            "response_by_relaxation_mode":contributions.tolist(),
            "slowest_mode_response_fraction":float(contributions[0]/response),
            "enthalpy_per_charge":enthalpy/charge if charge else None,
            "boundary":"Finite vector-basis, finite-grid projected charge response; not SI conductivity or complete two-fluid heat transport."}


def relative_momentum_witness():
    """A response-only momentum drift relaxes through G^4 mixed channels.

    Self-collisions conserve each sector's momentum at G=0. A finite charge
    density gives the projected charge current an overlap with relative drift;
    charge conjugation removes that overlap at mu=0.
    """
    rows=[]
    for mu in (.2,0.):
        for g in (.2,.1,0.):
            cfg=MixtureInputs(response_coupling=g)
            row=operator_grid(cfg,mu=mu,radial=6,angular=4,azimuth=4,cutoff=6.,basis_order=1)
            collision=np.asarray(row["vector_matrix"])
            rows.append({"mu":mu,"canonical_G":cfg.cubic,
                         "neutral_momentum_form":float(collision[5,5]),
                         "collision_matrix_norm":float(np.linalg.norm(collision)),
                         "charge_response":charge_response(row) if g else None,
                         "zero_coupling_status":"EXTRA_SECTOR_MOMENTUM_NULL_NOT_INVERTED" if not g else "COUPLED"})
    return {"grid":{"radial":6,"angular":4,"azimuth":4,"cutoff":6.,"basis_order":1},
            "relation":"L(neutral*p/T,neutral*p/T) proportional to G^4 at fixed masses and occupations",
            "rows":rows,"boundary":"Declared nonresonant 2-to-2 model only; not a measured thermalization rate."}


def main():
    cfg=MixtureInputs()
    sequence=[operator_grid(cfg,radial=n,angular=a,azimuth=b,cutoff=c)
              for n,a,b,c in ((6,4,6,6.),(8,6,8,8.),(12,8,10,10.))]
    for row in sequence:
        row["charge_response"]=charge_response(row,cfg)
    changes=[abs(b["charge_response"]["finite_basis_charge_response"]/a["charge_response"]["finite_basis_charge_response"]-1)
             for a,b in zip(sequence,sequence[1:])]
    witness=gain_loss_witness(cfg)
    neutral_vertex=neutral_quartic_witness(cfg)
    refinements={}
    for name,(n,a,b,c) in REFINEMENT_GRIDS.items():
        row=operator_grid(cfg,radial=n,angular=a,azimuth=b,cutoff=c)
        row["charge_response"]=charge_response(row)
        refinements[name]=row
        print("completed independent refinement: "+name,flush=True)
    reference=refinements["reference"]["charge_response"]["finite_basis_charge_response"]
    refinement_changes={name:abs(row["charge_response"]["finite_basis_charge_response"]/reference-1)
                        for name,row in refinements.items() if name!="reference"}
    metric_refined=charge_response(refinements["reference"],metric_order=256,metric_cutoff=32.)
    metric_change=abs(metric_refined["finite_basis_charge_response"]/reference-1)
    basis_grid=operator_grid(cfg,radial=18,angular=8,azimuth=12,cutoff=10.,basis_order=3)
    basis_results=[]
    for degree in range(4):
        _,names=vector_factors(np.ones(1),np.ones(1),.25,degree)
        record={**basis_grid,"basis_order":degree,"vector_basis":names,
                "vector_matrix":np.asarray(basis_grid["vector_matrix"])[:len(names),:len(names)].tolist()}
        basis_results.append(charge_response(record))
    basis_changes=[b["finite_basis_charge_response"]/a["finite_basis_charge_response"]-1
                   for a,b in zip(basis_results,basis_results[1:])]
    basis_refined=operator_grid(cfg,radial=24,angular=12,azimuth=16,cutoff=12.,basis_order=3)
    basis_refined["charge_response"]=charge_response(basis_refined)
    basis_quadrature_change=abs(basis_refined["charge_response"]["finite_basis_charge_response"]/basis_results[-1]["finite_basis_charge_response"]-1)
    drift=relative_momentum_witness()
    all_rows=sequence+list(refinements.values())+[{**basis_grid,"charge_response":basis_results[-1]},basis_refined]
    checks={
        "all_seven_channels_present":all(len(row["channels"])==7 and all(c["sampled_incoming_cells"] for c in row["channels"]) for row in all_rows),
        "detailed_balance":all(row["max_detailed_balance_relative_error"]<1e-10 for row in all_rows),
        "invariants":all(row["scalar_invariant_relative_residual"]<1e-10 and row["momentum_null_relative_residual"]<1e-10 for row in all_rows),
        "positive_quadratic_forms":all(row["scalar_min_eigenvalue_relative"]>-1e-12 and row["vector_min_eigenvalue_relative"]>-1e-12 for row in all_rows),
        "gain_loss_derivative":all(row["relative_derivative_errors"][-1]<1e-4 for row in witness["channels"]),
        "derivative_step_refinement":all(row["relative_derivative_errors"][1]<row["relative_derivative_errors"][0] for row in witness["channels"]),
        "nonlinear_entropy_and_affinity":all(row["minimum_event_entropy_production"]>=0 and row["max_log_affinity_error"]<1e-10 for row in witness["channels"]),
        "neutral_vertex_matches_production":bool(np.allclose(neutral_vertex,6*cfg.neutral_quartic,rtol=1e-9,atol=0)),
        "conversion_breaks_neutral_count":all(row["channels"][-1]["neutral_number_relaxation_form"]>0 for row in all_rows),
        "projected_response_positive":all(row["charge_response"]["finite_basis_charge_response"]>0 for row in all_rows),
        "nested_basis_variational_monotonicity":all(d>=-1e-10 for d in basis_changes),
        "nested_basis_solve_residual":all(row["linear_solve_relative_residual"]<1e-8 for row in basis_results),
        "spectral_response_reconstruction":all(abs(sum(row["response_by_relaxation_mode"])/row["finite_basis_charge_response"]-1)<1e-8 for row in basis_results),
        "relative_momentum_G_fourth_power":all(abs(drift["rows"][i+1]["neutral_momentum_form"]/drift["rows"][i]["neutral_momentum_form"]-1/16)<1e-12 for i in (0,3)),
        "decoupled_sector_momentum_null":all(drift["rows"][i]["neutral_momentum_form"]/drift["rows"][i]["collision_matrix_norm"]<1e-12 for i in (2,5)),
        "neutral_drift_charge_symmetry":drift["rows"][3]["charge_response"]["slowest_mode_response_fraction"]<1e-10,
    }
    paths=["docs/scripts/audit/audit_topic13_coupled_gain_loss_operator.py",
           "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
           "docs/core/uet_covariant_matter.py","docs/core/uet_covariant_response.py",
           "docs/core/test/test_topic13_coupled_gain_loss_operator.py"]
    sha=lambda path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    artifact={
        "schema_version":"t13-coupled-gain-loss-v1",
        "major_result_id":"T13_NORMAL_COUPLED_2TO2_GAIN_LOSS_DIAGNOSTIC",
        "topic":"0.13_Thermodynamic_Bridge","closure_level":"PARTIAL",
        "verification_status":"PASS_STRUCTURAL_GAIN_LOSS_REFINEMENT_OPEN" if all(checks.values()) else "WARN_GAIN_LOSS_VERIFICATION",
        "equation_registry_ids":[EQUATION_ID],"registration_status":"CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "what_is_closed":["Seven tree 2-to-2 channels with explicit reaction counting, Bose gain/loss and finite scalar/vector collision quadratic forms.",
                          "Charge, energy, momentum and truncation-number null directions; neutral-count conversion and finite-basis charge-current response.",
                          "Relative sector-momentum mode missing from the smallest basis; G^4 relaxation and zero-charge-density overlap control."],
        "equation_or_mapping":{
            "gain_loss":"F=f1*f2*(1+f3)*(1+f4); R=f3*f4*(1+f1)*(1+f2)",
            "linearization":"delta f=f*(1+f)*psi; delta(F-R)=F_eq*(psi1+psi2-psi3-psi4)",
            "quadratic_form":"L_ab=sum_reactions integral dPi_1234 |M|^2 F_eq Delta psi_a Delta psi_b/(S_in*S_out*S_reverse)",
            "counting":"S_reverse=2 for same incoming/outgoing species multiset, else 1; each conversion orientation listed once",
            "entropy":"(F-R)*log(F/R)>=0 for each reversible positive Bose event",
            "response":"R_Q=S_perp^T L_active^-1 S_perp after metric momentum projection",
        },
        "ontology":{"C":"not quasiparticle count or charge","Phi":"effective response, neutral excitation is a lane assumption not substance",
                    "R_gen":"not a state","R_obs":"excluded"},
        "state_variables":["f_minus(p)","f_plus(p)","f_response(p)"],
        "excluded_variables":["R_gen","R_obs"],
        "variable_meanings":{"q":"charge label -1,0,+1, not C","psi":"dimensionless Bose population affinity",
            "L":"linearized collision quadratic form, not a Lagrangian","S_perp":"momentum-projected charge-current source",
            "dPi_1234":"product d^3p_i/((2*pi)^3*2*E_i) times (2*pi)^4 delta^4(p1+p2-p3-p4)"},
        "units":{"collision_form":"energy^4","susceptibility":"energy^3","relaxation_rate":"energy","charge_response":"energy^2"},
        "unit_lane":"natural_units",
        "parameter_dimensions":{"T":1,"mu":1,"momentum":1,"mass_squared":2,"response_mass_squared":2,
            "response_coupling":1,"z":0,"epsilon":0,"response_kinetic":0,"quartic":0,"response_quartic":0},
        "constant_origin":"Declared synthetic action coefficients and state, not calibrated or fitted; phase-space factors from invariant measure.",
        "derivation_class":"tree_level_derivation",
        "approximation":"TREE_QUASIPARTICLE_2TO2_TRUNCATION_AND_FINITE_GALERKIN_BASIS",
        "observable":"finite-basis projected charge response, not physical thermal conductivity",
        "data_role":"SYNTHETIC_DERIVED_DIAGNOSTIC","config":asdict(cfg),"checks":checks,
        "sequence":sequence,"charge_response_adjacent_relative_changes":changes,
        "independent_refinements":refinements,"independent_refinement_relative_changes":refinement_changes,
        "metric_refinement_relative_change":metric_change,
        "diagnostic_refinement_tolerance":DIAGNOSTIC_REFINEMENT_TOLERANCE,
        "diagnostic_refinement_pass":all(d<DIAGNOSTIC_REFINEMENT_TOLERANCE for d in refinement_changes.values()) and metric_change<DIAGNOSTIC_REFINEMENT_TOLERANCE and basis_quadrature_change<DIAGNOSTIC_REFINEMENT_TOLERANCE,
        "nested_basis_grid":basis_grid,"nested_basis_results":basis_results,
        "nested_basis_relative_increases":basis_changes,
        "largest_basis_refined_grid":basis_refined,"largest_basis_quadrature_relative_change":basis_quadrature_change,
        "relative_momentum_witness":drift,
        "causal_status":"NOT_EVALUATED_LOCAL_COLLISION_FORM_ONLY",
        "ledger_status":"ON_SHELL_COLLISION_ENERGY_MOMENTUM_ONLY_NOT_FULL_OPEN_SYSTEM_LEDGER",
        "gain_loss_witness":witness,"neutral_quartic_derivative_witness":neutral_vertex,
        "initial_probe_failure":{"path":"docs/core/artifacts/t13_coupled_gain_loss_initial_probe_failure.json",
            "sha256":sha("docs/core/artifacts/t13_coupled_gain_loss_initial_probe_failure.json"),
            "diagnosis":"Near-null first-cell relative derivative test amplifies subtractive cancellation; retained in every grid row. Independent non-null multi-step probe uses the original 1e-4 criterion."},
        "convergence_status":"NOT_ACCEPTED_CONTINUUM_OR_BASIS_CLOSURE",
        "spurious_invariant":"Total quasiparticle number is conserved by this 2-to-2 truncation, not the full cubic/quartic action.",
        "open_blockers":["quadrature_and_basis_convergence","number_changing_higher_order_channels","finite_T_background_and_self_energy",
                         "full_SK_KMS_current_entropy_material_matching"],
        "controlling_blocker":"basis_completeness_and_physical_collision_current_matching",
        "source_hashes":{p:sha(p) for p in paths},
        "evidence_artifacts":[{"path":p,"sha256":sha(p)} for p in paths],
        "literature_context":[{"url":"https://arxiv.org/abs/hep-ph/9409250","role":"linearized Boltzmann/transport framework only; no numeric input"}],
        "dependency_unlocked":[],"full_core_unlock":False,"claim_promotion":False,
        "xie_2026_accessed":False,"parameter_fitting_performed":False,
        "claim_boundary":"Finite-grid 2-to-2 mixture diagnostic only; not full transport, SI calibration or Full Topic 13 closure."}
    artifact["report"]={
        "MAJOR_RESULT_CLOSURE":"PARTIAL","WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":[],
        "STATUS":artifact["verification_status"],"WHAT_CHANGED":"Added neutral response scattering and pair conversion with gain/loss, invariant-aware scalar/vector forms.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,
        "CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Extend and independently verify the current basis; match allowed number-changing channels and finite-T background before physical heat transport.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    entry={key:artifact[key] for key in ("ontology","units","unit_lane","variable_meanings","parameter_dimensions","constant_origin","derivation_class","approximation","observable","data_role","verification_status","controlling_blocker","claim_boundary")}
    entry.update({"equation_id":EQUATION_ID,"relation_or_code_path":artifact["equation_or_mapping"],
                  "standard_physics_counterpart":"Reversible Bose Boltzmann reaction form in a canonical three-mode scalar model",
                  "evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(OUT.read_bytes()).hexdigest()}],
                  "dependency_role":"diagnostic_only","physical_dependency_unlock":False})
    REGISTRY_OUT.write_text(json.dumps({"schema_version":"uet-equation-registry-addendum-v1",
        "extends":"docs/core/artifacts/uet_equation_correspondence_registry.json","status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "equation_entries":[entry],"full_core_unlock":False,"claim_promotion":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,"response_changes":changes,
                     "independent_changes":refinement_changes,"metric_change":metric_change,
                     "basis_response":[r["finite_basis_charge_response"] for r in basis_results],"basis_changes":basis_changes,
                     "largest_basis_quadrature_change":basis_quadrature_change,
                     "relative_drift_fraction":basis_results[-1]["slowest_mode_response_fraction"],
                     "last_charge_response":sequence[-1]["charge_response"],
                     "linearization_errors":[r["relative_derivative_errors"][-1] for r in witness["channels"]]},indent=2))
    return 0 if all(checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
