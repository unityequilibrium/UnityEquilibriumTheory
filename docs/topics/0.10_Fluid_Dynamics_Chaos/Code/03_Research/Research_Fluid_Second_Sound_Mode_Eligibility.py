"""Scoped long-wave mode eligibility, not a UET/He-II prediction or PDE solver."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from Research_Fluid_Vector_State_Contract import (
    ROOT, TOPIC, CORE, PeriodicOperators, source_expression, evaluate
)

CONTRACT=TOPIC/"Data/03_Research/fluid_second_sound_mode_eligibility_contract.json"
PARENT=TOPIC/"Data/03_Research/fluid_vector_state_research_contract.json"
CARD=TOPIC/"SECOND_SOUND_MODE_ELIGIBILITY.md"
REGISTRY=ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_second_sound_mode_addendum.json"
OUTPUT=TOPIC/"Result/artifacts/fluid_second_sound_mode_eligibility_audit.json"


def rms(a):
    """Hermitian magnitude norm, also valid for purely imaginary defects."""
    return float(np.sqrt(np.mean(np.abs(np.asarray(a))**2)))


def relative(a,b):
    return rms(np.asarray(a)-np.asarray(b))/max(1,rms(a),rms(b))


def match_error(a,b):
    a,b=np.asarray(a),np.asarray(b)
    return float(min(max(abs(a[i]-b[j]) for i,j in enumerate(order))
                     for order in itertools.permutations(range(len(b))))/max(1,np.max(abs(a)),np.max(abs(b))))


def modes_json(a):
    return [dict(real=float(v.real),imag=float(v.imag)) for v in a]


def audit(contract,parent):
    c=SimpleNamespace(**parent["coefficients"])
    rules=contract["verification"]
    expressions={key:source_expression("matter_space_chemical_potentials",key)
                 for key in ("mu_C","mu_Phi")}
    def potentials(C,Phi,lap_C=0.,lap_Phi=0.):
        env=dict(config=c,C=C,Phi=Phi,lap_C=lap_C,lap_Phi=lap_Phi)
        return np.asarray([evaluate(expressions[key][1],**env) for key in ("mu_C","mu_Phi")])
    C0=rules["C0"]
    lo,hi=-1.,1.
    while potentials(C0,lo)[1]>0:lo*=2
    while potentials(C0,hi)[1]<0:hi*=2
    for _ in range(100):
        mid=(lo+hi)/2
        if potentials(C0,mid)[1]>0:hi=mid
        else:lo=mid
    Phi0=(lo+hi)/2
    mu0=potentials(C0,Phi0)
    A=c.a_matter+3*c.b_matter*C0*C0-c.coupling_g*Phi0
    B=-c.coupling_g*C0
    D=c.a_space+3*c.b_space*Phi0*Phi0
    H=np.array([[A,B],[B,D]])
    alpha=c.mobility_space/c.tau_space
    gamma=1/c.tau_space
    effective=A-B*B/D
    coeff=c.mobility_matter*effective
    checks={}
    tol=rules["identity_tolerance"]
    floor=rules["negative_control_floor"]
    def check(name,value,limit=tol):
        checks[name]=dict(metric=float(value),threshold=float(limit),
                          pass_=bool(np.isfinite(value) and value<=limit))
    def positive(name,value,bound=0.):
        checks[name]=dict(metric=float(value),minimum=float(bound),
                          pass_=bool(np.isfinite(value) and value>bound))
    check("uniform_Phi_equilibrium",abs(mu0[1]))
    positive("finite_positive_gap_stiffness",D)
    positive("stable_Hessian_determinant",np.linalg.det(H))
    positive("stable_effective_conserved_susceptibility",effective)
    positive("finite_positive_relaxation",gamma)
    fd=[]
    for eps in rules["field_directional_steps"]:
        columns=[]
        for axis in range(2):
            delta=np.zeros(2);delta[axis]=eps
            columns.append((potentials(C0+delta[0],Phi0+delta[1])
                            -potentials(C0-delta[0],Phi0-delta[1]))/(2*eps))
        numeric=np.column_stack(columns)
        fd.append(dict(step=eps,error=relative(numeric,H)))
    check("canonical_Hessian_directional_derivative",fd[-1]["error"],
          rules["hessian_derivative_tolerance"])
    op=PeriodicOperators(rules["projection_grid"])
    dC=np.sin(op.x)+0.13*np.cos(op.y)
    dPhi=0.19*np.cos(op.x-op.y)
    raw_force=mu0[0]*op.gradient(dC)+mu0[1]*op.gradient(dPhi)
    projected,pressure=op.project(raw_force/c.rho0,c.rho0)
    positive("linear_force_projection_control_nonzero",rms(raw_force),floor)
    check("linear_scalar_force_is_pressure_gradient",rms(projected))
    check("projected_linear_velocity_constraint",rms(op.divergence(projected)))
    check("complex_norm_pure_imaginary_control",abs(rms(np.array([1j,1j]))-1))
    positive("imaginary_matrix_work_defect_detected",
             rms(np.array([[0,1j],[1j,0]])),floor)
    equilibrium_roots=np.roots([1,gamma,alpha*D])
    gap=float(np.min(abs(equilibrium_roots)))
    positive("k0_fast_root_gap",gap)
    # P_lambda(0,0)=alpha*D is nonzero: the scalar zero root is simple.
    positive("simple_scalar_zero_root_derivative",alpha*D)
    reference=rules["two_fluid_controls"]
    rho=reference["rho_s"]+reference["rho_n"]
    a=reference["rho_s"]/rho*reference["T"]*reference["s"]/reference["c_p"]
    b=rho/reference["rho_n"]*reference["s"]
    speed=np.sqrt(a*b)
    HT=rho*reference["c_p"]/reference["T"]
    Hw=reference["rho_s"]*reference["rho_n"]/rho
    weight=np.diag([HT,Hw])
    check("reference_quadratic_flux_reciprocity",
          relative(HT*a,Hw*b))
    check("reference_flux_thermodynamic_identity",
          relative(HT*a,reference["rho_s"]*reference["s"]))
    positive("reference_availability_temperature_weight",HT)
    positive("reference_availability_relative_inertia",Hw)
    records=[]
    slopes=[]
    speeds=[]
    reference_damping=[]
    for k in rules["wavenumbers"]:
        z=k*k
        Ak,Dk=A+c.kappa_matter*z,D+c.kappa_space*z
        diffusion=c.mobility_matter*z
        scalar=np.array([[-diffusion*Ak,-diffusion*B,0],
                         [0,0,1],[-alpha*B,-alpha*Dk,-gamma]],dtype=float)
        full=np.zeros((4,4));full[:3,:3]=scalar
        full[3,3]=-c.eta*z/c.rho0
        eig=np.linalg.eigvals(scalar)
        slow=eig[np.argmin(abs(eig))]
        fast=np.delete(eig,np.argmin(abs(eig)))
        polynomial=[1,gamma+diffusion*Ak,alpha*Dk+diffusion*Ak*gamma,
                    diffusion*alpha*(Ak*Dk-B*B)]
        roots=np.roots(polynomial)
        prefix="k="+str(k)+"/"
        check(prefix+"characteristic_polynomial_eigen_match",match_error(eig,roots))
        check(prefix+"characteristic_root_residual",
              float(np.max(abs(np.polyval(polynomial,eig))))/max(1,np.linalg.norm(scalar)**3))
        check(prefix+"slow_rest_mode_nonoscillatory",abs(slow.imag))
        check(prefix+"slow_rest_mode_stable",max(0,float(slow.real)))
        positive(prefix+"fast_sector_remains_gapped",float(np.min(abs(fast))),gap/2)
        check(prefix+"full_shear_block_spectrum",
              match_error(np.linalg.eigvals(full),np.append(eig,-c.eta*z/c.rho0)))
        slopes.append(float(-slow.real/z))
        # This is a separate standard-physics operator, never the UET candidate.
        wave=np.array([[0,-1j*k*a],[-1j*k*b,0]],dtype=complex)
        wave_eig=np.linalg.eigvals(wave)
        check(prefix+"ideal_counterflow_acoustic_pair",
              match_error(wave_eig,np.array([1j*speed*k,-1j*speed*k])))
        check(prefix+"ideal_reference_positive_work_symmetrizer",
              rms(weight@wave+wave.conj().T@weight))
        # Wrong reciprocal sign produces imaginary work and real unstable poles.
        wrong=wave.copy();wrong[1,0]*=-1
        positive(prefix+"wrong_counterflow_sign_work_detected",
                 rms(weight@wrong+wrong.conj().T@weight),floor)
        positive(prefix+"wrong_counterflow_sign_instability_detected",
                 float(np.max(np.linalg.eigvals(wrong).real)),floor)
        DT,Dw=reference["D_T"],reference["D_w"]
        damped=wave-np.diag([DT*z,Dw*z])
        damped_eig=np.linalg.eigvals(damped)
        loss=weight@damped+damped.conj().T@weight
        check(prefix+"diffusive_reference_work_loss",
              relative(loss,-2*z*np.diag([HT*DT,Hw*Dw])))
        check(prefix+"reference_damping_order_k_squared",
              abs(float(np.mean(damped_eig.real))/z+(DT+Dw)/2))
        speeds.append(float(np.max(abs(damped_eig.imag))/k))
        reference_damping.append(float(-np.mean(damped_eig.real)/z))
        boost=rules["boost_velocity"]
        boosted=full-1j*boost*k*np.eye(4)
        check(prefix+"Galilean_rest_frame_spectrum",
              match_error(np.linalg.eigvals(boosted)+1j*boost*k,np.linalg.eigvals(full)))
        apparent=slow-1j*boost*k
        check(prefix+"advected_diffusive_apparent_speed",
              relative(abs(apparent.imag)/k,abs(boost)))
        # An even-in-k matrix with a nilpotent k=0 block can support acoustics:
        # this explicitly falsifies an overbroad parity/no-scalar-wave argument.
        massless=np.array([[0,1],[-alpha*c.kappa_space*z,0]])
        massless_speed=np.sqrt(alpha*c.kappa_space)
        check(prefix+"out_of_contract_massless_undamped_wave",
              match_error(np.linalg.eigvals(massless),
                          np.array([1j*massless_speed*k,-1j*massless_speed*k])))
        clamped=np.diag([-DT*z,0])
        check(prefix+"clamped_relative_motion_has_no_wave",rms(np.linalg.eigvals(clamped).imag))
        chart=np.diag([1.7,0.8,1.2,1.4])
        timescale=rules["unit_time_scale"]
        converted=chart@full@np.linalg.inv(chart)/timescale
        check(prefix+"finite_state_unit_chart_preserves_poles",
              match_error(np.linalg.eigvals(converted),np.linalg.eigvals(full)/timescale))
        records.append(dict(k=k,scalar_modes=modes_json(eig),
                            shear_mode=-c.eta*z/c.rho0,slow_coefficient=slopes[-1],
                            reference_modes=modes_json(wave_eig),
                            reference_damped_modes=modes_json(damped_eig),
                            reference_phase_speed=speeds[-1],
                            apparent_bulk_advection_speed=float(abs(apparent.imag)/k),
                            massless_undamped_control_speed=float(massless_speed),
                            unit_k=k/rules["unit_length_scale"]))
    check("finest_diffusive_slope_matches_simple_root_derivation",
          relative(slopes[-1],coeff),rules["small_k_slope_tolerance"])
    check("diffusive_slope_refinement",
          max(0,abs(slopes[-1]-coeff)-abs(slopes[0]-coeff)))
    check("finest_reference_acoustic_speed",
          relative(speeds[-1],speed),rules["small_k_slope_tolerance"])
    for item in checks.values():item["pass"]=item.pop("pass_")
    result=dict(checks=checks,reference_check_count=len(checks),
                pass_=all(item["pass"] for item in checks.values()),
                equilibrium=dict(C0=C0,Phi0=Phi0,mu_C0=float(mu0[0]),mu_Phi0=float(mu0[1]),
                                 A=A,B=B,D=D,effective_susceptibility=effective,
                                 predicted_diffusive_coefficient=coeff,alpha=alpha,gamma=gamma,
                                 fast_roots_k0=modes_json(equilibrium_roots)),
                canonical_Hessian_derivative_controls=fd,wavenumber_records=records,
                separate_two_fluid_reference=dict(controls=reference,a=a,b=b,
                                 ideal_phase_speed=float(speed),availability_weights=[HT,Hw],
                                 reference_damping_coefficient=reference_damping[-1],
                                 coefficient_origin="synthetic; not calibrated or physical He-II"),
                canonical_source_expressions={key:item[0] for key,item in expressions.items()})
    result["pass"]=result.pop("pass_")
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args()
    contract=json.loads(CONTRACT.read_text());parent=json.loads(PARENT.read_text())
    result=audit(contract,parent)
    paths=[Path(__file__),Path(__file__).with_name("Research_Fluid_Vector_State_Contract.py"),
           CONTRACT,PARENT,CARD,REGISTRY,CORE,
           ROOT/"docs/topics/0.13_Thermodynamic_Bridge/HE4_SECOND_SOUND_PROTOCOL_CARD.md",
           ROOT/"docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_continuum_relative_flow_addendum.json"]
    result.update(schema_version="t10-second-sound-mode-eligibility-audit-v2",
                  status="PASS_CURRENT_CANDIDATE_HYDRODYNAMIC_MODE_EXCLUSION_ONLY" if result["pass"] else "FAIL_MODE_ELIGIBILITY_AUDIT",
                  controlling_blocker=contract["controlling_blocker"],
                  coupled_branch_blocker=contract["coupled_branch_blocker"],
                  candidate_disposition="NOT_ELIGIBLE_AS_HYDRODYNAMIC_SECOND_SOUND_OPERATOR_UNDER_DECLARED_ASSUMPTIONS" if result["pass"] else "UNRESOLVED_AUDIT_FAILED",
                  harness_revision=contract["harness_revision"],
                  claim_promotion=False,dependency_unlock=False,physical_uet_operator_admitted=False,
                  physical_prediction_executed=False,scope=contract["candidate_assumptions"],
                  reference_scope=contract["reference_assumptions"],thresholds=contract["verification"],
                  input_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in paths},
                  excludes=["all-UET no-go","nonlinear propagation","finite-frequency He-II fit",
                            "SI material prediction","full entropy/FDT closure","PDE trajectory",
                            "formal kernel proof","Core/Topic 13 unlock"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",encoding="utf-8",newline="\n") as stream:
        stream.write(json.dumps(result,indent=2,allow_nan=False)+"\n")
    failed=[name for name,item in result["checks"].items() if not item["pass"]]
    print(json.dumps(dict(status=result["status"],checks=result["reference_check_count"],failed=failed)))
    return 0 if result["pass"] else 1


if __name__=="__main__":raise SystemExit(main())
