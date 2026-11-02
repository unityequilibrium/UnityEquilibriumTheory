"""SD04 conditional finite-density matrix integrands; no thermal state solver."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_matrix_tadpole_contract.json"
OUTPUT = TOPIC / "Result/artifacts/fluid_core_o2_matrix_tadpole.json"
LOCK = "722383f698ff5692a817c80612e054126b645b3cf44286074837509fff804cff"
FIRST_CODE = TOPIC / "Result/previews/core_o2_matrix_tadpole_first_verifier.py.txt"
FIRST_RESULT = TOPIC / "Result/previews/fluid_core_o2_matrix_tadpole_first_execution.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def mode_data(k, Y, D, mu):
    """Rest-frame integrand interface only; reject unstable/degenerate domains."""
    k, Y, D, mu = map(float, (k, Y, D, mu))
    if not all(math.isfinite(v) for v in (k,Y,D,mu)) or k <= 0 or Y-mu*mu < abs(D):
        raise ValueError("positive-momentum stable rest domain required")
    A, B = k*k+Y+D-mu*mu, k*k+Y-D-mu*mu
    R = math.sqrt(4*mu*mu*(k*k+Y)+D*D)
    if R == 0:
        raise ValueError("degenerate poles require a separate limit")
    high2 = k*k+Y+mu*mu+R
    low2 = A*B/high2
    if low2 <= 0:
        raise ValueError("positive poles required at k>0")
    delta = 2*R
    return math.sqrt(high2), math.sqrt(low2), ((high2-B)/delta,(B-low2)/delta), ((high2-A)/delta,(A-low2)/delta)

def zero_point(k,Y,D,mu):
    high,low,_,_ = mode_data(k,Y,D,mu)
    return (high+low)/2

def auxiliary(L,x,Y,D,mu,m_squared,coupling):
    """Declared gHF auxiliary stationary potential, not a stability minimum."""
    U=(m_squared-mu*mu)*x/2+coupling*x*x/4
    AY=Y-m_squared-2*coupling*x
    AD=D-coupling*x
    return U+L-AY*AY/(8*coupling)+AD*AD/(4*coupling)

def audit(contract_path=CONTRACT):
    checks={}; expressions={}; hashes={}
    canonical=json.loads(CONTRACT.read_text(encoding="utf-8"))
    def flag(name,value):
        checks[name]=bool(value)
    def identity(name,expression):
        flag(name,sp.simplify(expression)==0)
    def finish():
        return {"schema_version":"uet-topic10-matrix-tadpole-result-v1","date":canonical["date"],
                "status":"PASS_CONDITIONAL_MATRIX_STATE_PREREQUISITE_ONLY" if all(checks.values()) else "FAIL_CONDITIONAL_MATRIX_STATE_PREREQUISITE_ONLY",
                "check_count":len(checks),"passing_check_count":sum(checks.values()),"checks":checks,
                "expressions":expressions,"input_hashes":hashes,"evaluated_contract_hash":sha(contract_path),
                "method_gate":canonical["method_gate"],"admission":canonical["admission"],
                "physical_scales":canonical["physical_scales"],"method_controller":canonical["method_controller"],
                "physical_controller":canonical["physical_controller"],"thermal_integrals_executed":False,
                "interacting_state_computed":False,"state_root_solved":False,"full_2PI_counterterms_admitted":False,
                "external_source_vertex_computed":False,"physical_heat_current_computed":False,
                "SI_calibration_performed":False,"material_values_assigned":False,"physical_covariance_assigned":False,
                "new_benchmark_expansion":False,"claim_promotion":False,"dependency_unlock":False,
                "formal_verification":False,"external_replication":False,
                "scope":"matrix/IR/UV/auxiliary/source analytic prerequisites; not state, full renormalization, stability or material response"}
    flag("canonical_contract_lock",sha(CONTRACT)==LOCK)
    supplied=json.loads(Path(contract_path).read_text(encoding="utf-8"))
    flag("supplied_contract_exact",supplied==canonical)
    flag("all_admissions_false",all(v is False for v in canonical["admission"].values()) and len(canonical["admission"])==16)
    flag("all_method_gates_not_started",all(v=="NOT_STARTED" for v in canonical["method_gate"].values()) and len(canonical["method_gate"])==10)
    flag("all_physical_scales_null",all(v is None for v in canonical["physical_scales"].values()))
    flag("no_solver_benchmark_or_full_renormalization",all(canonical[k] is False for k in ["new_benchmark_expansions_authorized","condensed_state_solver_authorized","full_2PI_renormalization_admitted"]))
    for path,expected in canonical["prelocked_input_hashes"].items():
        p=ROOT/path;hashes[path]=sha(p) if p.is_file() else None
    flag("all_prelocked_inputs_fresh",hashes==canonical["prelocked_input_hashes"])
    if not all(checks.values()):
        return finish()
    for p in [CONTRACT,Path(__file__)]: hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    handoff=json.loads((ROOT/"docs/core/07_artifacts/topic13/core_he4_same_state_correspondence_2026_10_04.json").read_text())
    flag("published_Core_material_controller_retained",handoff["physical_transfer_admitted"] is False and handoff["controlling_blocker"]=="same_state_atomic_current_action_measure_and_low_T_remainder_not_admitted")
    k,Y,D,mu,w=sp.symbols("k Y D mu omega",positive=True)
    A=k*k+Y+D-mu*mu;B=k*k+Y-D-mu*mu
    K=sp.Matrix([[w*w+A,-2*mu*w],[2*mu*w,w*w+B]])
    det=(w*w+A)*(w*w+B)+4*mu*mu*w*w
    identity("full_matrix_determinant",K.det()-det)
    G=sp.Matrix([[w*w+B,2*mu*w],[-2*mu*w,w*w+A]])/det
    flag("full_matrix_inverse",sp.simplify(K*G)==sp.eye(2))
    R=sp.sqrt(4*mu*mu*(k*k+Y)+D*D);hi=k*k+Y+mu*mu+R;lo=k*k+Y+mu*mu-R;delta=2*R
    identity("pole_factorization",det-(w*w+hi)*(w*w+lo))
    identity("stable_low_pole_product",hi*lo-A*B)
    weights=[((hi-B)/delta,(B-lo)/delta),((hi-A)/delta,(A-lo)/delta)]
    for i,(a,b) in enumerate(weights):
        identity("residue_partition_"+str(i),a+b-1)
        identity("partial_fraction_"+str(i),a/(w*w+hi)+b/(w*w+lo)-G[i,i])
    identity("frequency_odd_offdiagonal",G[0,1]+G[0,1].subs(w,-w))
    flag("offdiagonal_not_identically_zero",G[0,1]!=0)
    flag("dropped_mixing_negative",sp.simplify(det-(w*w+A)*(w*w+B))!=0)
    fhi,flo=sp.symbols("fH fL")
    q11=weights[0][0]*fhi+weights[0][1]*flo
    q22=weights[1][0]*fhi+weights[1][1]*flo
    identity("trace_residues",q11+q22-(1+4*mu*mu/delta)*fhi-(1-4*mu*mu/delta)*flo)
    identity("traceless_residues",q11-q22+2*D*(flo-fhi)/delta)
    logdet=sp.log(det)/2
    identity("trace_log_Y_derivative",2*sp.diff(logdet,Y)-sp.trace(G))
    identity("trace_log_D_derivative",2*sp.diff(logdet,D)-(G[0,0]-G[1,1]))
    identity("trace_log_source_matrix_derivative",sp.diff(logdet,mu)-sp.trace(G*sp.diff(K,mu))/2)
    flag("normal_charge_shortcut_negative",sp.simplify(sp.diff(logdet,mu)+mu*sp.trace(G))!=0)
    C,q,T=sp.symbols("C q T",positive=True)
    low_gap=q+C-sp.sqrt(C*C+4*mu*mu*q)
    low_series=sp.series(low_gap,q,0,2).removeO()
    cs2=D/(D+2*mu*mu)
    identity("gapless_IR_speed",low_series.coeff(q).subs(C,D+2*mu*mu)-cs2)
    wL22=(q+2*D-low_gap)/(2*sp.sqrt(C*C+4*mu*mu*q))
    wL11=(q-low_gap)/(2*sp.sqrt(C*C+4*mu*mu*q))
    identity("Goldstone_thermal_radial_Q22_limit",sp.limit(T*q*wL22/low_gap,q,0).subs(C,D+2*mu*mu)-T)
    identity("Goldstone_thermal_radial_Q11_limit",sp.limit(T*q*wL11/low_gap,q,0).subs(C,D+2*mu*mu))
    e=sp.symbols("e",positive=True)
    identity("Bose_IR_leading_coefficient",sp.limit(e/(sp.exp(e/T)-1),e,0)-T)
    u,Y0=sp.symbols("u Y0",positive=True)
    # ell/k from the pole-sum/product identity avoids canceling large energies.
    inner=sp.sqrt(1+2*(Y-mu*mu)*u*u+((Y-mu*mu)**2-D*D)*u**4)
    scaled=sp.sqrt((1+(Y+mu*mu)*u*u+inner)/2)
    laurent=sp.expand(sp.series(scaled,u,0,8).removeO()/u)
    expected=1/u+Y*u/2-(Y*Y+D*D)*u**3/8+(Y**3+3*Y*D*D-2*mu*mu*D*D)*u**5/16
    identity("zero_point_UV_through_k_minus5",laurent-expected)
    flag("divergent_coefficients_no_explicit_mu",all(sp.diff(laurent.coeff(u,p),mu)==0 for p in [-1,1,3]))
    identity("finite_vacuum_mu_derivative",sp.diff(laurent,mu).coeff(u,5)+mu*D*D/4)
    E0=sp.sqrt(1/u**2+Y0);subtract=-E0-(Y-Y0)/(2*E0)+((Y-Y0)**2+D*D)/(8*E0**3)
    subseries=sp.series(subtract,u,0,6).removeO()
    reduced=sp.expand(laurent+subseries)
    flag("matrix_subtraction_removes_all_divergences",all(sp.simplify(reduced.coeff(u,p))==0 for p in [-1,1,3]))
    c5=((Y-Y0)**3+3*(Y-Y0)*D*D-2*mu*mu*D*D)/16
    identity("matrix_subtracted_k_minus5",reduced.coeff(u,5)-c5)
    omitted=sp.expand(reduced-sp.series(D*D/(8*E0**3),u,0,6).removeO())
    identity("scalar_only_subtraction_log_divergence",omitted.coeff(u,3)+D*D/8)
    identity("trace_tadpole_subtraction",2*sp.diff(subtract,Y)+1/E0-(Y-Y0)/(2*E0**3))
    identity("traceless_tadpole_subtraction",2*sp.diff(subtract,D)-D/(2*E0**3))
    identity("subtraction_mixed_derivative",sp.diff(subtract,Y,D)-sp.diff(subtract,D,Y))
    flag("moving_reference_negative",sp.simplify(sp.diff(subtract,Y0))!=0)
    x,m2,lam=sp.symbols("x m_squared lambda",positive=True)
    L=sp.Function("L")(Y,D,mu,T)
    omega=auxiliary(L,x,Y,D,mu,m2,lam)
    AY=Y-m2-2*lam*x;AD=D-lam*x
    identity("auxiliary_expansion",omega-(L-(Y-m2)**2/(8*lam)+D*D/(4*lam)+x*(Y-D-mu*mu)/2))
    identity("unrestricted_trace_gap",sp.diff(omega,Y)-(sp.diff(L,Y)-AY/(4*lam)))
    identity("unrestricted_traceless_gap",sp.diff(omega,D)-(sp.diff(L,D)+AD/(2*lam)))
    identity("unrestricted_mean_Ward",sp.diff(omega,x)-(Y-D-mu*mu)/2)
    identity("unrestricted_charge_envelope",sp.diff(omega,mu)-(sp.diff(L,mu)-mu*x))
    old=omega-AD*AD/(2*lam)
    flag("old_Hartree_traceless_sign_negative",sp.simplify(sp.diff(old,D)-sp.diff(omega,D))!=0)
    Ip,Im=sp.symbols("I_plus I_minus",real=True)
    Ygap=m2+2*lam*x+2*lam*Ip;Dgap=lam*x-lam*Im
    identity("gap_Ward_equals_shared_mean",Ygap-Dgap-mu*mu-(m2-mu*mu+lam*x+2*lam*Ip+lam*Im))
    ward=omega.subs(Y,mu*mu+D)
    flag("early_Ward_loses_x_equation",sp.diff(ward,x)==0)
    # Differentiate before evaluating the common one-loop gradient placeholders.
    dward=sp.diff(omega,Y)+sp.diff(omega,D)
    dward=dward.subs({sp.diff(L,Y):Ip/2,sp.diff(L,D):Im/2}).subs(Y,mu*mu+D)
    identity("reduced_scalar_gap",dward-(Ip+Im)/2-(D-mu*mu+m2)/(4*lam))
    recovery=D/lam+Im
    identity("condensate_recovery_equation",AD.subs(x,recovery)+lam*Im)
    reduced_source=(sp.diff(omega,mu)+2*mu*sp.diff(omega,Y)).subs({sp.diff(L,Y):Ip/2})
    identity("reduced_source_difference_requires_trace_gap",reduced_source-sp.diff(omega,mu)-mu*(Ip-AY/(2*lam)))
    missing_x=sp.simplify((Im/2+AD/(2*lam)).subs(Y,mu*mu+D))
    flag("arbitrary_x_after_Ward_negative",sp.diff(missing_x,x)!=0)
    flag("auxiliary_x_not_convex_stability_proof",sp.diff(omega,x,2)==0)
    expressions.update({"pole_high_squared":str(hi),"pole_low_squared":str(lo),"IR_speed_squared":str(cs2),
       "unsubtracted_UV":str(expected),"subtracted_k_minus5_coefficient":str(c5),
       "matrix_tadpole_trace":"2*partial_Y L","matrix_tadpole_traceless":"2*partial_D L",
       "reduced_gap":"D=mu^2-m_squared-2lambda*(I_plus+I_minus)","condensate_recovery":"x=D/lambda+I_minus",
       "source_density":"n=mu*x-partial_mu L at fixed Y,D", "full_counterterm_role":"NOT_ADMITTED"})
    for args in [(0,5,1,1),(1,1,1,1),(1,5,0,0)]:
        try:
            mode_data(*args);flag("invalid_numeric_domain:"+str(args),False)
        except ValueError:
            flag("invalid_numeric_domain:"+str(args),True)
    if FIRST_CODE.exists() or FIRST_RESULT.exists():
        flag("first_archive_pair_exists",FIRST_CODE.is_file() and FIRST_RESULT.is_file())
        if FIRST_CODE.is_file() and FIRST_RESULT.is_file():
            first=json.loads(FIRST_RESULT.read_text())
            flag("first_source_identity_retained",sha(FIRST_CODE)==first["input_hashes"][Path(__file__).relative_to(ROOT).as_posix()])
            startup=TOPIC / "Result/previews/core_o2_matrix_tadpole_startup_verifier.py.txt"
            flag("startup_only_root_discovery_repair_retained",startup.read_bytes().replace(b"parents[4]",b"parents[5]")==FIRST_CODE.read_bytes())
            for p in [FIRST_CODE,FIRST_RESULT,startup]:hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    return finish()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-json",type=Path,default=CONTRACT)
    parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args();result=audit(args.contract_json)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(result["status"],str(result["passing_check_count"])+"/"+str(result["check_count"]))
    return 0 if result["status"].startswith("PASS_") else 1

if __name__=="__main__":
    raise SystemExit(main())
