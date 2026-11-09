"""Source-linked normal-branch probes and exact conditional Hartree residual algebra."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_interacting_method_contract.json"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_interacting_method_addendum.json"
OUTPUT = TOPIC / "Result/artifacts/fluid_core_o2_interacting_method_audit.json"
PASS = "PASS_SOURCE_BRANCH_CONDITIONAL_ALGEBRA_ONLY"
FAIL = "INTERACTING_METHOD_ADMISSION_DIAGNOSTIC_FAIL"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    spec = importlib.util.spec_from_file_location("interacting_source_adapter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative(x, y):
    return abs(x-y) / max(abs(x), abs(y), 1e-30)


def residuals(mu, mass, coupling, x, Y, D, plus, minus):
    """All inputs are independent; no gapless or stationary substitution here."""
    return dict(R_rho=Y+D-mu*mu-2*coupling*x,
                R_Y=Y-mass-2*coupling*x-2*coupling*plus,
                R_D=D-coupling*x-coupling*minus,
                R_G=Y-D-mu*mu,
                determinant_zero=(Y+D-mu*mu)*(Y-D-mu*mu))


def witness(mu, mass, coupling, plus, minus, gapless=False):
    if gapless:
        x=(mu*mu-mass-2*coupling*plus)/coupling
        Y=mu*mu+coupling*x
        D=coupling*x
    else:
        x=(mu*mu-mass-coupling*(2*plus+minus))/coupling
        Y=mass+2*coupling*x+2*coupling*plus
        D=coupling*x+coupling*minus
    return dict(x=x,Y=Y,D=D), residuals(mu,mass,coupling,x,Y,D,plus,minus)


def source_functions(p):
    adapter=load(ROOT/p["source_adapter"])
    ns,ids={},{}
    for name,path in p["core_sources"].items():
        extra={}
        if name=="finite_density":
            extra["response_displacement"]=ns["response"]["response_displacement"]
        elif name=="self_energy":
            extra["effective_mass_sq"]=ns["finite_density"]["effective_mass_sq"]
        elif name=="thermo":
            extra["uet_o2_finite_temperature_self_energy_state"]=ns["self_energy"]["uet_o2_finite_temperature_self_energy_state"]
        elif name=="renormalized":
            extra.update(effective_mass_sq=ns["finite_density"]["effective_mass_sq"],
                         _thermal_one_loop_state=ns["thermo"]["_thermal_one_loop_state"],
                         _thermal_tadpole_and_derivative=ns["self_energy"]["_thermal_tadpole_and_derivative"],
                         _vacuum_terms=ns["vacuum"]["_vacuum_terms"])
        ns[name],ids[name]=adapter.selected_namespace(ROOT/path,p["AST_selected_definitions"][name],extra)
        # Value-preserving cache of the original pure coordinate/weight generator;
        # no new quadrature, np monkeypatch or source definition substitution.
        if "_quadrature" in ns[name]:
            ns[name]["_quadrature"]=lru_cache(maxsize=None)(ns[name]["_quadrature"])
    return ns,ids


def audit(p, path):
    checks={};errors=[];probes=[];controls=[];algebra=[];ids={}
    def flag(name,condition):
        checks[name]={"pass":bool(condition)}
    def close(name,value,tolerance):
        checks[name]={"pass":bool(math.isfinite(value) and abs(value)<=tolerance),
                      "value":float(value),"tolerance":float(tolerance)}
    flag("contract_identity",sha(CONTRACT)=="cfb4897d65ca0935eeffcecf710c29ca3c70ac60e591b85e8b7c95bf5ddca446")
    locked=json.loads(CONTRACT.read_text(encoding="utf-8"))
    flag("all_prelocked_values_unchanged",p==locked)
    flag("card_identity",sha(ROOT/p["card"])=="54df71448731c4d7d395a8b0845ef48f6096e8a5d292edb59dceb964e66dfa8d")
    flag("registry_identity",sha(REGISTRY)=="7849faf7a3d4ed570f31b089c0c804312c1533f204023cf4e69b3b9e2b971301")
    prior=json.loads((ROOT/p["prior_density_artifact"]).read_text(encoding="utf-8"))
    flag("prior_scope",prior["status"]=="PASS_LEADING_MEAN_DENSITY_GAUSSIAN_SUBSET_ONLY"
         and not prior["full_interacting_density_backreaction_completed"])
    flag("prior_sources_fresh",all((ROOT/f).is_file() and sha(ROOT/f)==h for f,h in prior["input_hashes"].items()))
    flag("no_method_gate_admitted",len(p["method_gate"])==10 and all(s=="NOT_STARTED" for s in p["method_gate"].values()))
    flag("no_physical_admission",len(p["admission"])==14 and all(v is False for v in p["admission"].values()))
    rules=p["verification"]
    def finish():
        paths=[path,Path(__file__).resolve(),REGISTRY,ROOT/p["card"],
               ROOT/p["prior_density_artifact"],ROOT/p["source_adapter"]]
        paths += [ROOT/f for f in p["core_sources"].values()]
        paths += [ROOT/f for f in prior["input_hashes"]]
        hashes={f.relative_to(ROOT).as_posix() if f.is_relative_to(ROOT) else f.name:sha(f) for f in paths}
        passed=all(c["pass"] for c in checks.values()) and len(probes)==12 and len(controls)==6 and len(algebra)==3 and not errors
        return dict(schema_version="t010-interacting-method-audit-v1",date=p["date"],
                    status=PASS if passed else FAIL,check_count=len(checks),
                    passing_check_count=sum(c["pass"] for c in checks.values()),checks=checks,
                    input_hashes=hashes,source_AST_definition_hashes=ids,locked_verification=rules,
                    normal_branch_probes=probes,normal_controls=controls,conditional_algebra=algebra,
                    execution_errors=errors,method_gate=p["method_gate"],admission=p["admission"],
                    normal_branch_and_conditional_algebra_supported=passed,
                    unit_powers=dict(residuals=2,determinant_zero=4),
                    physical_controller=p["physical_controller"],controlling_measured_blocker=p["candidate_controller"],
                    method_controller=p["method_controller"],
                    full_condensed_interacting_state_computed=False,full_Noether_Ward_completed=False,
                    physical_J04_executed=False,physical_J05_executed=False,physical_J06_executed=False,
                    physical_heat_current_matched=False,physical_material_frame_admitted=False,
                    formal_verification=False,external_math_review=False,whole_Core_runtime_executed=False,
                    useful_relative_error_certified=False,claim_promotion=False,dependency_unlock=False,
                    parameters_fitted=False,thresholds_relaxed=False,
                    source_execution="verbatim selected AST definitions; pure quadrature value memoization only",
                    primary_sources=p["primary_sources"],
                    notes=["Normal rejection is branch-specific, not a condensed-state no-go.",
                           "Exact Fraction witnesses are conditional source algebra; tadpoles are synthetic, not solved thermal integrals.",
                           "Goldstone replacement changes original stationarity obligations.",
                           "The normal-control state is separate from selected condensate and material observables.",
                           "No microscopic vacuum scheme match, finite-density symmetry-improved implementation, dynamic Ward or physical heat/frame mapping."])
    if not all(c["pass"] for c in checks.values()):
        return finish()
    try:
        ns,ids=source_functions(p)
        c=p["configuration"]
        cfg=SimpleNamespace(matter=SimpleNamespace(matter_kinetic=c["Z"],matter_mass_sq=c["mass_squared"],
                            matter_quartic=c["lambda"],response_coupling=c["response_coupling"]),
                            response=SimpleNamespace(epsilon_nc=c["epsilon_nc"],phi_equilibrium=c["phi_equilibrium"]))
        methods={"thermal":(ns["thermo"]["uet_o2_hartree_thermodynamic_state"],
                            "no self-consistent Hartree solution in the normal branch","pressure_stationarity_residual","condensate_contribution_included"),
                 "renormalized":(ns["renormalized"]["uet_o2_renormalized_hartree_normal_state"],
                                 "no renormalized Hartree solution in the normal branch","functional_stationarity_residual","condensed_branch_included")}
        for name,(solver,message,stationarity,condensed_flag) in methods.items():
            for point in p["selected_states"]:
                for n in rules["orders"]:
                    key=f"{name}/selected/{point['T']}/{n}"
                    try:
                        returned=solver(point["T"],point["mu"],c["Phi_fixed"],cfg,quadrature_order=n,
                                        cutoff_factor=rules["cutoff_factor"],component_count=2)
                    except ValueError as exc:
                        probes.append(dict(method=name,T=point["T"],mu=point["mu"],order=n,
                                           rejected=True,error_type=type(exc).__name__,message=str(exc)))
                        flag(key+"/expected_branch_rejection",str(exc)==message)
                    else:
                        probes.append(dict(method=name,T=point["T"],mu=point["mu"],order=n,rejected=False,
                                           returned_state=asdict(returned)))
                        flag(key+"/expected_branch_rejection",False)
            sweep=[]
            point=p["normal_control"]
            for n in rules["orders"]:
                state=solver(point["T"],point["mu"],c["Phi_fixed"],cfg,quadrature_order=n,
                             cutoff_factor=rules["cutoff_factor"],component_count=2)
                v=asdict(state)
                v.update(method=name,role=point["role"])
                sweep.append(v);controls.append(v)
                key=f"{name}/normal_control/{n}"
                flag(key+"/normal_domain",v["dressed_mass_sq"]>point["mu"]**2)
                flag(key+"/finite_scalars",all(math.isfinite(x) for x in v.values() if isinstance(x,float)))
                for field in (condensed_flag,"physical_kubo_coefficient_included","physical_si_mapping_included"):
                    flag(key+"/"+field,v[field] is False)
                close(key+"/gap",v["gap_residual"],rules["gap_absolute_tolerance"])
                close(key+"/functional_stationarity",v[stationarity],rules["gap_absolute_tolerance"])
                energy=-v["pressure"]+point["T"]*v["entropy_density"]+point["mu"]*v["charge_density"]
                close(key+"/Legendre",relative(v["energy_density"],energy),rules["Legendre_relative_tolerance"])
                expected_cutoff=rules["cutoff_factor"]*max(point["T"],abs(point["mu"]),math.sqrt(c["mass_squared"]),1.)
                close(key+"/solver_cutoff",relative(v["momentum_cutoff"],expected_cutoff),1e-14)
            for field in ("dressed_mass_sq","pressure"):
                close(name+"/last_order_refinement/"+field,relative(sweep[-1][field],sweep[-2][field]),
                      rules["refinement_relative_tolerance"])
        w=rules["rational_witness"];mu=Fraction(w["mu"]);mass=Fraction(w["mass_squared"])
        coupling=Fraction(w["lambda"]);plus=Fraction(w["I_plus"]);scale=Fraction(rules["energy_scale"])
        for raw in w["I_minus"]:
            minus=Fraction(raw);key="conditional/"+raw
            stationary,rs=witness(mu,mass,coupling,plus,minus)
            gapless,rg=witness(mu,mass,coupling,plus,minus,True)
            flag(key+"/positive_condensates",stationary["x"]>0 and gapless["x"]>0)
            flag(key+"/nonnegative_components",(plus+minus)/2>=0 and (plus-minus)/2>=0)
            flag(key+"/stationary_three_equations",all(rs[n]==0 for n in ("R_rho","R_Y","R_D")))
            flag(key+"/stationary_Goldstone_residual",rs["R_G"]==-2*coupling*minus)
            flag(key+"/gapless_replacement",all(rg[n]==0 for n in ("R_rho","R_Y","R_G")))
            flag(key+"/gapless_original_D_residual",rg["R_D"]==-coupling*minus)
            flag(key+"/original_stationary_determinant",bool(rs["determinant_zero"]==0)==bool(minus==0))
            flag(key+"/gapless_determinant",rg["determinant_zero"]==0)
            # Test the identity and its altered-coefficient negative control also
            # off either stationary/constrained point: independently varied x,Y,D.
            off=dict(x=Fraction(7,5),Y=Fraction(11,7),D=Fraction(3,10))
            ro=residuals(mu,mass,coupling,**off,plus=plus,minus=minus)
            flag(key+"/off_shell_identity",ro["R_G"]==ro["R_rho"]-2*ro["R_D"]-2*coupling*minus)
            wrong=ro["R_rho"]-ro["R_D"]-2*coupling*minus
            flag(key+"/wrong_coefficient_negative_control",wrong!=ro["R_G"])
            for name,v,r in (("stationary",stationary,rs),("gapless",gapless,rg),("off_shell",off,ro)):
                scaled=residuals(scale*mu,scale**2*mass,coupling,**{n:scale**2*x for n,x in v.items()},
                                 plus=scale**2*plus,minus=scale**2*minus)
                for field,power in (("R_rho",2),("R_Y",2),("R_D",2),("R_G",2),("determinant_zero",4)):
                    flag(key+"/"+name+"/unit_scale/"+field,scaled[field]==scale**power*r[field])
            algebra.append(dict(I_minus=raw,role="synthetic_exact_conditional_algebra_not_thermal_state",
                                original_stationary={n:str(x) for n,x in stationary.items()},
                                original_residuals={n:str(x) for n,x in rs.items()},
                                gapless_replacement={n:str(x) for n,x in gapless.items()},
                                gapless_original_residuals={n:str(x) for n,x in rg.items()},
                                off_shell_residuals={n:str(x) for n,x in ro.items()}))
    except (ValueError,FloatingPointError,RuntimeError) as exc:
        errors.append(dict(type=type(exc).__name__,message=str(exc)))
        flag("requested_controls_completed",False)
    flag("complete_selected_probes",len(probes)==12)
    flag("complete_normal_controls",len(controls)==6)
    flag("complete_algebra_witnesses",len(algebra)==3)
    return finish()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-json",type=Path,default=CONTRACT)
    parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args();path=args.contract_json.resolve()
    a=audit(json.loads(path.read_text(encoding="utf-8")),path)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(a,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(a["status"],a["passing_check_count"],"/",a["check_count"],flush=True)
    failed=[(n,c) for n,c in a["checks"].items() if not c["pass"]]
    if failed:print("FAIL",failed,flush=True)
    return 0 if a["status"]==PASS else 1


if __name__=="__main__":
    raise SystemExit(main())
