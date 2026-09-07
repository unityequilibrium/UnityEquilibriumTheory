"""Named tree elastic matter-scattering diagnostic, not a transport solver.

Reuses the declared flat O(2)/Phi action. No legacy comparator is overwritten.
The normal background is chi=0, Phi=Phi_equilibrium. Phi exchange is internal;
this does not identify the response variable with a physical particle.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from math import pi, sqrt
from pathlib import Path
import hashlib
import json
import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig, interaction_energy_density, matter_potential
from docs.core.uet_covariant_response import CovariantResponseConfig

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_action_normalized_elastic_scattering_audit.json"
BRANCH = "T13_NORMAL_TREE_ELASTIC_CONTACT_PLUS_PHI_EXCHANGE_V1"
EQUATION_ID = "uet.o2.thermal.normal_tree_elastic_scattering"
REGISTRY_OUT = ROOT / "docs/core/artifacts/uet_equation_correspondence_registry_topic13_elastic_scattering_addendum.json"


@dataclass(frozen=True)
class ActionInputs:
    z: float = 1.
    mass_squared: float = 1.
    quartic: float = .1
    epsilon: float = 1.
    response_kinetic: float = 1.
    response_mass_squared: float = .5
    response_coupling: float = .2

    def __post_init__(self):
        values = asdict(self)
        if not all(np.isfinite(v) for v in values.values()):
            raise ValueError("finite action coefficients required")
        if any(values[key] <= 0 for key in (
            "z", "mass_squared", "quartic", "epsilon",
            "response_kinetic", "response_mass_squared",
        )) or self.response_coupling < 0:
            raise ValueError("positive kinetic/mass/quartic inputs required")

    @property
    def mass(self):
        return sqrt(self.mass_squared/self.z)

    @property
    def coupling(self):
        return self.quartic/self.z**2

    @property
    def response_mass_sq(self):
        return self.response_mass_squared/self.response_kinetic

    @property
    def cubic(self):
        return sqrt(self.epsilon)*self.response_coupling/(self.z*sqrt(self.response_kinetic))


def amplitude(s, cosine, charges, cfg=ActionInputs()):
    """Real tree amplitude up to an irrelevant common minus sign."""
    if len(charges) != 4 or any(q not in (-1, 1) for q in charges):
        raise ValueError("four fixed charge labels +/-1 required")
    q1, q2, q3, q4 = charges
    x = np.asarray(cosine, dtype=float)
    if not np.isfinite(s) or s <= 4*cfg.mass**2 or np.any(~np.isfinite(x)) or np.any(abs(x)>1):
        raise ValueError("strict elastic physical kinematics required")
    if q1+q2 != q3+q4:
        return np.zeros_like(x)
    p_sq = s/4-cfg.mass**2
    t, u = -2*p_sq*(1-x), -2*p_sq*(1+x)
    factors = (int(q1 == -q2 and q3 == -q4),
               int(q1 == q3 and q2 == q4),
               int(q1 == q4 and q2 == q3))
    result = np.full_like(x, 2*cfg.coupling*sum(factors))
    if cfg.cubic:
        # A thermal integral samples every s>=4m^2. Do not insert an ad hoc width.
        if cfg.response_mass_sq >= 4*cfg.mass**2:
            raise ValueError("s-channel pole region requires a separate resummed branch")
        for factor, invariant in zip(factors, (s, t, u)):
            if factor:
                result += cfg.cubic**2/(invariant-cfg.response_mass_sq)
    return result


def differential_cross_section(s, cosine, charges, cfg=ActionInputs()):
    identical_final = charges[2] == charges[3]
    divisor = 2 if identical_final else 1
    return amplitude(s, cosine, charges, cfg)**2/(64*pi*pi*s*divisor)


def bose(energy, temperature):
    x = np.asarray(energy)/temperature
    if np.any(x <= 0) or np.any(~np.isfinite(x)):
        raise ValueError("strict normal branch positive excitation energies required")
    weight = np.exp(-x)
    return weight/(-np.expm1(-x))


def tagged_loss_rates(cfg=ActionInputs(), *, temperature=.25, mu=.2, momentum=1.,
                      radial_order=32, incoming_order=24, outgoing_order=16,
                      azimuth_order=16, cutoff=16., final_bose=True):
    """Tagged out-scattering only, not a linearized transport eigenvalue.

    Incoming target labels are counted once; no incoming 1/2 for a tagged leg.
    Outgoing angles cover the whole sphere with the identical-final 1/2.
    """
    if not (np.isfinite(temperature) and temperature > 0 and np.isfinite(mu) and abs(mu)<cfg.mass
            and np.isfinite(momentum) and momentum>0 and np.isfinite(cutoff) and cutoff>0):
        raise ValueError("positive T, momentum, cutoff and |mu|<m required")
    if any(isinstance(n, bool) or int(n)!=n or n<4 for n in
           (radial_order,incoming_order,outgoing_order,azimuth_order)):
        raise ValueError("integer quadrature orders >=4 required")
    r, rw = np.polynomial.legendre.leggauss(radial_order)
    r, rw = .5*cutoff*(r+1), .5*cutoff*rw
    inc, iw = np.polynomial.legendre.leggauss(incoming_order)
    out, ow = np.polynomial.legendre.leggauss(outgoing_order)
    az = 2*pi*(np.arange(azimuth_order)+.5)/azimuth_order
    angular_weight = ow[:,None]*(2*pi/azimuth_order)
    m = cfg.mass
    e1 = sqrt(momentum**2+m*m)
    rates = np.zeros((2,2))
    max_balance = 0.
    for p, wp in zip(r,rw):
        e2 = sqrt(p*p+m*m)
        total = e1+e2
        for c, wc in zip(inc,iw):
            dot = e1*e2-momentum*p*c
            s = 2*(m*m+dot)
            flux = sqrt((dot-m*m)*(dot+m*m))/(e1*e2)
            pstar = sqrt(s/4-m*m)
            gamma = total/sqrt(s)
            beta_x = p*sqrt(1-c*c)/total
            beta_z = (momentum+p*c)/total
            beta_sq = beta_x**2+beta_z**2
            beta_parallel = gamma*(beta_z*momentum-beta_sq*e1)/pstar
            beta_transverse = abs(beta_x*momentum)/pstar
            projection = (beta_parallel*out[:,None]
                          + beta_transverse*np.sqrt(1-out*out)[:,None]*np.cos(az)[None,:])
            e3 = total/2+gamma*pstar*projection
            e4 = total-e3
            measure = wp*wc*p*p/(4*pi*pi)*flux
            for i,q1 in enumerate((-1,1)):
                for j,q2 in enumerate((-1,1)):
                    ds = differential_cross_section(s,out,(q1,q2,q1,q2),cfg)
                    if final_bose:
                        enhancement=(1+bose(e3-q1*mu,temperature))*(1+bose(e4-q2*mu,temperature))
                    else:
                        enhancement=np.ones_like(e3)
                    integral=float(np.sum(angular_weight*ds[:,None]*enhancement))
                    rates[i,j] += measure*float(bose(e2-q2*mu,temperature))*integral
                    # Independent occupations check detailed balance, not just energy residual.
                    f1=float(bose(e1-q1*mu,temperature))
                    f2=float(bose(e2-q2*mu,temperature))
                    f3=bose(e3-q1*mu,temperature); f4=bose(e4-q2*mu,temperature)
                    forward=f1*f2*(1+f3)*(1+f4)
                    reverse=f3*f4*(1+f1)*(1+f2)
                    max_balance=max(max_balance,float(np.max(abs(forward-reverse)/np.maximum(forward,reverse))))
    return {"rates_by_tag_and_target": rates.tolist(), "rates": rates.sum(axis=1).tolist(),
            "max_detailed_balance_relative_error": max_balance,
            "role": "TAGGED_ELASTIC_LOSS_NOT_FULL_DAMPING_OR_TRANSPORT",
            "grid": {"radial":radial_order,"incoming":incoming_order,"outgoing":outgoing_order,
                     "azimuth":azimuth_order,"cutoff":cutoff}}


def cubic_from_production_potential(cfg, step=.25):
    """Mixed third difference of the actual interaction in canonical fields."""
    matter=CovariantMatterConfig(matter_kinetic=cfg.z,matter_mass_sq=cfg.mass_squared,
                                 matter_quartic=cfg.quartic,response_coupling=cfg.response_coupling)
    response=CovariantResponseConfig(epsilon_nc=cfg.epsilon,response_kinetic=cfg.response_kinetic,
                                    response_mass_sq=cfg.response_mass_squared)
    def v(x,y):
        return interaction_energy_density(y/sqrt(cfg.epsilon*cfg.response_kinetic),
                                          (x/sqrt(cfg.z),0.),response,matter)
    second_plus=v(step,step)-2*v(0.,step)+v(-step,step)
    second_minus=v(step,-step)-2*v(0.,-step)+v(-step,-step)
    return -(second_plus-second_minus)/(2*step**3)


def quartic_from_production_potential(cfg, step=.25):
    matter=CovariantMatterConfig(matter_kinetic=cfg.z,matter_mass_sq=cfg.mass_squared,
                                 matter_quartic=cfg.quartic)
    values=[matter_potential((n*step/sqrt(cfg.z),0.),matter) for n in (-2,-1,0,1,2)]
    return sum(w*v for w,v in zip((1,-4,6,-4,1),values))/(6*step**4)


def main():
    cfg=ActionInputs()
    contact=ActionInputs(response_coupling=0.)
    nodes,weights=np.polynomial.legendre.leggauss(48)
    s=8.
    cross={}
    for name,charges in (("like",(1,1,1,1)),("unlike",(1,-1,1,-1))):
        cross[name]=float(2*pi*np.dot(weights,differential_cross_section(s,nodes,charges,contact)))
    control_sigma=cfg.coupling**2/(16*pi*s)
    ratios={name:value/control_sigma for name,value in cross.items()}
    sequence=[]
    for n,ang,out,cut in ((24,16,12,12.),(40,24,16,16.),(64,32,24,20.)):
        sequence.append(tagged_loss_rates(cfg,radial_order=n,incoming_order=ang,
                                         outgoing_order=out,azimuth_order=out,cutoff=cut))
    differences=[float(np.max(abs(np.array(b["rates"])/np.array(a["rates"])-1)))
                 for a,b in zip(sequence,sequence[1:])]
    contact_rate=tagged_loss_rates(contact,radial_order=40,cutoff=16.)
    vertex=cubic_from_production_potential(cfg)
    checks={
        "quartic_matches_production_potential": bool(np.isclose(quartic_from_production_potential(cfg),cfg.coupling,rtol=1e-12)),
        "cubic_matches_production_interaction": bool(np.isclose(vertex,cfg.cubic,rtol=1e-12)),
        "contact_like_factor_eight": bool(np.isclose(ratios["like"],8.,rtol=1e-12)),
        "contact_unlike_factor_sixteen": bool(np.isclose(ratios["unlike"],16.,rtol=1e-12)),
        "positive_elastic_loss": all(all(v>0 for v in r["rates"]) for r in sequence),
        "detailed_balance": all(r["max_detailed_balance_relative_error"]<1e-10 for r in sequence),
        "last_refinement_below_declared_2e_minus3": differences[-1]<2e-3,
    }
    paths=["docs/core/uet_covariant_matter.py","docs/core/uet_covariant_response.py",
           "docs/scripts/audit/audit_topic13_action_normalized_elastic_scattering.py",
           "docs/core/test/test_topic13_action_normalized_elastic_scattering.py"]
    digest=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    artifact={
        "schema_version":"t13-action-elastic-scattering-v1",
        "major_result_id":BRANCH,"topic":"0.13_Thermodynamic_Bridge","closure_level":"PARTIAL",
        "equation_registry_ids":[EQUATION_ID],
        "registration_status":"CANDIDATE_DIAGNOSTIC_ADDENDUM_NOT_CENTRAL_ACCEPTANCE",
        "verification_status":"PASS_SCOPED_TREE_ELASTIC_DIAGNOSTIC" if all(checks.values()) else "WARN_ELASTIC_REFINEMENT_OR_MATCH",
        "what_is_closed":["Action-normalized charge-resolved elastic contact/Phi-exchange amplitude on a nonresonant normal background.",
                          "Full-solid-angle identical-final-state counting and finite-grid tagged elastic loss."],
        "equation_or_mapping":{
            "canonical":"chi_c=sqrt(Z)*chi; phi_c=sqrt(epsilon*K)*deltaPhi; lambda_c=lambda/Z^2; G=sqrt(epsilon)*h/(Z*sqrt(K)); M_Phi^2=U''/K",
            "amplitude":"M_abcd=2*lambda_c*(d_ab*d_cd+d_ac*d_bd+d_ad*d_bc)+G^2*[d_ab*d_cd/(s-M_Phi^2)+d_ac*d_bd/(t-M_Phi^2)+d_ad*d_bc/(u-M_Phi^2)] up to common minus sign",
            "cross_section":"d_sigma/d_Omega=|M|^2/(64*pi^2*s*S_final); S_final=2 for equal final charges, otherwise 1",
            "tagged_loss":"Gamma_q(k)=sum_r integral d^3p/(2*pi)^3 n_r v_Moller integral dOmega (d_sigma/dOmega)(1+n_3)(1+n_4)",
        },
        "ontology":{"C":"not identified with charge or mass","Phi":"effective response; internal propagator is a lane calculation, not a particle claim",
                    "R_gen":"derived history trace, no state/backreaction","R_obs":"excluded"},
        "units":{"m_T_mu_G":"natural energy","lambda":"dimensionless","sigma":"energy^-2","Gamma_loss":"energy"},
        "derivation_class":"TREE_ACTION_ELASTIC_QUASIPARTICLE_APPROXIMATION",
        "observable":"tagged elastic loss rate; not heat conductivity",
        "data_role":"SYNTHETIC_DERIVED_DIAGNOSTIC","config":asdict(cfg),
        "checks":checks,"contact_cross_section_ratios_to_legacy":ratios,
        "production_cubic":vertex,"resolution_sequence":sequence,"adjacent_relative_changes":differences,
        "contact_only_comparison":contact_rate,
        "exchange_to_contact_rate_ratio_same_grid":(np.array(sequence[1]["rates"])/np.array(contact_rate["rates"])).tolist(),
        "uncertainty_boundary":"Adjacent grid differences are numerical diagnostics, not a certified error bound or material uncertainty.",
        "source_hashes":{p:digest(p) for p in paths},
        "evidence_artifacts":[{"path":p,"sha256":digest(p)} for p in paths],
        "literature_context":[{"url":"https://www.damtp.cam.ac.uk/user/tong/qft/qfthtml/S3.html",
                               "section":"3.5 and 3.6.3","role":"primary lecture conventions for scalar exchange and invariant flux; no numeric input"}],
        "open_blockers":["full_linearized_collision_operator_and_current_vertex","response_external_inelastic_channels",
                         "finite_temperature_background_and_self_energy","resonant_width_and_loop_matching",
                         "full_SK_KMS_entropy_transport_and_material_SI_mapping"],
        "controlling_blocker":"full_species_response_collision_operator_not_just_tagged_elastic_loss",
        "dependency_unlocked":[],"full_core_unlock":False,"claim_promotion":False,
        "parameter_fitting_performed":False,"xie_2026_accessed":False,
        "claim_boundary":"New named tree elastic diagnostic only. No replacement of old comparator, no full transport, no physical Phi-particle claim, no Full Topic 13 closure.",
    }
    artifact["report"]={
        "MAJOR_RESULT_CLOSURE":artifact["closure_level"],"WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":[],
        "STATUS":artifact["verification_status"],"WHAT_CHANGED":"Charge-resolved contact plus nonresonant Phi exchange and explicit final-state counting.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,
        "CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Assemble gain/loss linearization with matter and response channels, then current/entropy matching.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    entry={
        "equation_id":EQUATION_ID,"version":BRANCH,"classification":"named_tree_elastic_diagnostic",
        "relation_or_code_path":artifact["equation_or_mapping"],
        "ontology":artifact["ontology"],"units":artifact["units"],"unit_lane":"natural_flat_3p1",
        "derivation_class":artifact["derivation_class"],
        "standard_physics_counterpart":"Canonical charged scalar contact and neutral-response exchange; Lorentz-invariant two-body phase space",
        "observable":artifact["observable"],"observable_mapping":{"status":"NATURAL_DIAGNOSTIC_ONLY","SI":"OPEN"},
        "data_role":artifact["data_role"],"verification_status":artifact["verification_status"],
        "assumptions":["tree normal background chi=0, Phi=Phi_equilibrium","positive epsilon and response kinetic",
                       "response mass below pair threshold for unregularized thermal integral",
                       "elastic matter sector only; no finite-T self-consistency or inelastic closure"],
        "controlling_blocker":artifact["controlling_blocker"],"claim_boundary":artifact["claim_boundary"],
        "implementation_paths":[paths[2]],"verifier_paths":[paths[3]],
        "evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(OUT.read_bytes()).hexdigest()}],
        "dependency_role":"diagnostic_only","physical_dependency_unlock":False,
    }
    REGISTRY_OUT.write_text(json.dumps({
        "schema_version":"uet-equation-registry-addendum-v1",
        "extends":"docs/core/artifacts/uet_equation_correspondence_registry.json",
        "status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED","equation_entries":[entry],
        "full_core_unlock":False,"claim_promotion":False,
    },indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,"contact_ratios":ratios,
                      "rates":sequence[-1]["rates"],"relative_changes":differences},indent=2))
    return 0 if all(checks.values()) else 1


if __name__=="__main__":
    raise SystemExit(main())
