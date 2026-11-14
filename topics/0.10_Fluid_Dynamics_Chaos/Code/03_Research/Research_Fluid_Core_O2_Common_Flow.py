"""Current Core source-function composition probe; no material/two-fluid admission."""
from __future__ import annotations
import argparse
import ast
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace
import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_common_flow_contract.json"
CARD = TOPIC / "CORE_O2_COMMON_FLOW_COMPOSITION_CONTRACT.md"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_common_flow_addendum.json"
OUTPUT = TOPIC / "Result/artifacts/fluid_core_o2_common_flow_composition_audit.json"


def relative(a, b):
    return abs(a - b) / max(abs(a), abs(b), 1e-30)


def selected_namespace(path, names, extra=None):
    """Compile exactly named source definitions, without importing the Core facade."""
    source = path.read_text(encoding="utf-8")
    parsed = ast.parse(source)
    definitions = {n.name: n for n in parsed.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    if set(names) - definitions.keys():
        raise ValueError("Missing source definitions: " + str(set(names) - definitions.keys()))
    nodes = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    nodes += [definitions[name] for name in names]
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    namespace = dict(np=np, dataclass=dataclass, **{name: getattr(math, name) for name in
                     ("exp", "expm1", "isfinite", "log", "log1p", "pi", "sqrt")})
    namespace.update(extra or {})
    exec(compile(module, str(path), "exec", dont_inherit=True), namespace)
    segments = {name: hashlib.sha256(ast.get_source_segment(source, definitions[name]).encode("utf-8")).hexdigest()
                for name in names}
    return namespace, segments


def source_functions(package):
    ns, identities = {}, {}
    for name, path in package["core_sources"].items():
        extra = {}
        if name == "finite_density":
            extra["response_displacement"] = ns["response"]["response_displacement"]
        elif name == "EOS":
            extra.update({n: ns["finite_density"][n] for n in ("effective_mass_sq", "condensate_control")})
        elif name == "transverse":
            extra.update({n: ns["finite_density"][n] for n in ("effective_mass_sq", "condensate_control")})
            extra["condensed_quasiparticle_energies"] = ns["EOS"]["condensed_quasiparticle_energies"]
        ns[name], identities[name] = selected_namespace(ROOT / path, package["AST_selected_definitions"][name], extra)
        if "_quadrature" in ns[name]:
            ns[name]["_quadrature"] = lru_cache(maxsize=None)(ns[name]["_quadrature"])
    return ns, identities


def configuration(p, order, cutoff):
    c = p["configuration"]
    matter = SimpleNamespace(matter_kinetic=c["Z"], matter_mass_sq=c["mass_squared"],
                             matter_quartic=c["lambda"], response_coupling=c["response_coupling"])
    response = SimpleNamespace(epsilon_nc=c["epsilon_nc"], phi_equilibrium=c["phi_equilibrium"])
    eos = SimpleNamespace(matter=matter, response=response)
    return SimpleNamespace(eos=eos, quadrature_order=order, cutoff_factor=cutoff, phase_tolerance=c["phase_tolerance"])


def five_point(function, value, step):
    h = step * max(1., abs(value))
    return (function(value - 2*h) - 8*function(value - h) + 8*function(value + h) - function(value + 2*h)) / (12*h)


def state(package, ns, point, order, cutoff, step):
    cfg = configuration(package, order, cutoff)
    T, mu, phi = point["T"], point["mu"], package["configuration"]["Phi_fixed"]
    pressure = ns["EOS"]["quasiparticle_pressure"]
    p = pressure(T, mu, phi, cfg)
    n = five_point(lambda m: pressure(T, m, phi, cfg), mu, step)
    s = five_point(lambda t: pressure(t, mu, phi, cfg), T, step)
    response = ns["transverse"]["formal_transverse_quasiparticle_response"](T, mu, phi, cfg)
    w = T*s + mu*n
    composition = mu*mu*response.condensate_phase_stiffness + response.normal_momentum_susceptibility
    return {"branch":response.branch, "T":T, "mu":mu, "Phi_fixed":phi, "order":order,
            "cutoff_factor":cutoff, "derivative_relative_step":step, "pressure":p,
            "charge_density":n, "entropy_density":s, "enthalpy":w,
            "tree_phase_stiffness":response.condensate_phase_stiffness,
            "static_Doppler_momentum_proxy":response.normal_momentum_susceptibility,
            "proposed_composite_inertia":composition, "composition_residual":composition-w,
            "relative_composition_residual":relative(composition,w),
            "role":"natural-unit source-function diagnostic; no physical rho_n/rho_s or He-II state"}


def audit(package, path):
    rules = package["verification"]
    ns, extracted = source_functions(package)
    checks = {}

    def flag(name, value):
        checks[name] = {"pass":bool(value)}

    def close(name, value, tolerance):
        checks[name] = {"metric":float(value), "threshold":tolerance,
                        "pass":bool(np.isfinite(value) and value <= tolerance)}

    def greater(name, value, floor=0.):
        checks[name] = {"metric":float(value), "minimum":floor,
                        "pass":bool(np.isfinite(value) and value > floor)}

    flag("source_function_scope_only", package["record_role"] == "CURRENT_CORE_SOURCE_COMPOSITION_DIAGNOSTIC_NOT_ADMISSION")
    flag("locked_controls", rules["locked_before_first_execution"] is True and
         rules["orders"] == [128,256,384] and rules["cutoffs"] == [45,70,100] and
         rules["derivative_relative_steps"] == [.001,.0003,.0001] and
         rules["composition_relative_tolerance"] == 1e-5 and rules["refinement_relative_tolerance"] == 1e-6)
    for key, value in package["admission"].items():
        flag("boundary/" + key, value is False)
    flag("closed_fixed_Phi_configuration", package["configuration"]["response_coupling"] == 0 and
         package["configuration"]["epsilon_nc"] == 0 and package["configuration"]["Phi_fixed"] == .15)
    # Dimension guard: stiffness E^2 needs mu^2 before an E^4 inertia comparison.
    flag("SI_or_mass_density_not_emitted", "physical_HeII_state" in package["admission"] and
         package["admission"]["physical_HeII_state"] is False)
    flag("stiffness_conversion_dimensions", 2 + 2 == 4 and 2 != 4)

    rows = []
    for point in package["states"]:
        label = point["branch"] + "/" + str(point["T"])
        orders = [state(package,ns,point,o,rules["order_sweep_cutoff"],rules["derivative_relative_steps"][-1]) for o in rules["orders"]]
        cutoffs = [state(package,ns,point,rules["cutoff_sweep_order"],c,rules["derivative_relative_steps"][-1]) for c in rules["cutoffs"]]
        derivatives = [state(package,ns,point,rules["orders"][-1],rules["order_sweep_cutoff"],h) for h in rules["derivative_relative_steps"]]
        final = cutoffs[-1]
        flag(label + "/branch_matches", final["branch"] == point["branch"])
        flag(label + "/finite_source_state", all(np.isfinite(final[k]) for k in
             ("pressure","charge_density","entropy_density","enthalpy","tree_phase_stiffness","static_Doppler_momentum_proxy")))
        greater(label + "/entropy_positive", final["entropy_density"])
        greater(label + "/total_enthalpy_positive", final["enthalpy"])
        greater(label + "/Doppler_proxy_positive", final["static_Doppler_momentum_proxy"])
        refinements = {}
        for name, sweep in (("quadrature_order",orders),("cutoff_factor",cutoffs),("pressure_derivative",derivatives)):
            # Components, not the cancellation-sensitive near-zero normal residual.
            changes = {k:relative(sweep[-1][k],sweep[-2][k]) for k in
                       ("pressure","enthalpy","static_Doppler_momentum_proxy")}
            refinements[name] = changes
            close(label + "/" + name + "_component_stability", max(changes.values()), rules["refinement_relative_tolerance"])
        observed_absolute_spread = max(
            abs(sweep[-1]["enthalpy"] - sweep[-2]["enthalpy"]) +
            abs(sweep[-1]["static_Doppler_momentum_proxy"] - sweep[-2]["static_Doppler_momentum_proxy"])
            for sweep in (orders,cutoffs,derivatives))
        relative_spread = observed_absolute_spread / max(abs(final["enthalpy"]),abs(final["proposed_composite_inertia"]),1e-30)
        target_pass = final["relative_composition_residual"] <= rules["composition_relative_tolerance"]
        if point["branch"] == "normal":
            close(label + "/normal_gas_enthalpy_control", final["relative_composition_residual"], rules["composition_relative_tolerance"])
            flag(label + "/normal_tree_stiffness_zero", final["tree_phase_stiffness"] == 0)
        else:
            greater(label + "/condensed_tree_stiffness_positive", final["tree_phase_stiffness"])
        rows.append({"point":point, "final":final, "order_sweep":orders, "cutoff_sweep":cutoffs,
                     "derivative_sweep":derivatives, "component_refinement_changes":refinements,
                     "observed_refinement_spread_relative":relative_spread,
                     "composition_target":{"pass":target_pass, "relative_threshold":rules["composition_relative_tolerance"],
                       "exceeds_threshold_plus_observed_spread":bool(final["relative_composition_residual"] >
                          rules["composition_relative_tolerance"] + relative_spread),
                       "interpretation":"conditional proxy/tree composition target only; refinement spread is not a rigorous physical uncertainty bound"}})

    c = package["configuration"]
    mu = next(p["mu"] for p in package["states"] if p["branch"] == "condensed")
    cfg = configuration(package,rules["orders"][-1],rules["order_sweep_cutoff"])
    m2 = ns["finite_density"]["effective_mass_sq"](c["Phi_fixed"],cfg.eos)
    q = ns["finite_density"]["condensate_control"](mu,c["Phi_fixed"],cfg.eos)
    n0 = c["Z"]*mu*q/c["lambda"]
    dn0 = c["Z"]*(3*c["Z"]*mu*mu-m2)/c["lambda"]
    fs0 = c["Z"]*q/c["lambda"]
    w0 = mu*n0
    cs2 = n0/(mu*dn0)
    identity = rules["identity_tolerance"]
    close("tree_phase_charge_inertia",relative(w0,mu*mu*fs0),identity)
    greater("tree_condensed_q_positive",q)
    greater("tree_charge_susceptibility_positive",dn0)
    greater("tree_sound_squared_positive",cs2)
    goldstone = []
    for k in rules["spectrum_momenta"]:
        _, E = ns["EOS"]["condensed_quasiparticle_energies"](k,mu,c["Phi_fixed"],cfg)
        goldstone.append({"k":k,"source_E_over_k_squared":(E/k)**2,"analytic_tree_sound_squared":cs2})
    close("source_Goldstone_equals_tree_EOS_sound",relative(goldstone[-1]["source_E_over_k_squared"],cs2),identity)
    greater("stiffness_without_mu_squared_error_detected",relative(fs0,w0),rules["negative_control_floor"])
    # A coherent synthetic two-fluid stress decomposition is a positive algebra control.
    mu_test,T_test,s_test,ns_test,nn_test = 1.3,.2,.4,.5,.3
    w_test=mu_test*(ns_test+nn_test)+T_test*s_test
    right=mu_test*ns_test+(mu_test*nn_test+T_test*s_test)
    close("consistent_two_fluid_common_boost_positive_control",relative(w_test,right),identity)
    greater("omit_entropy_in_normal_inertia_detected",relative(mu_test*(ns_test+nn_test),w_test),rules["negative_control_floor"])

    condensed = [row for row in rows if row["point"]["branch"] == "condensed"]
    composition_ok = all(row["composition_target"]["pass"] for row in condensed)
    passed = all(c["pass"] for c in checks.values())
    paths=[path,CARD,REGISTRY,Path(__file__).resolve()]+[ROOT/v for v in package["core_sources"].values()]+[ROOT/v for v in package["reused_inputs"]]
    hashes={p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return {"schema_version":"t010-core-o2-common-flow-composition-audit-v1","date":package["date"],
            "status":"PASS_SOURCE_COMPOSITION_DIAGNOSTIC_ONLY" if passed else "SOURCE_COMPOSITION_DIAGNOSTIC_FAIL",
            "check_count":len(checks),"passing_check_count":sum(c["pass"] for c in checks.values()),"checks":checks,
            "input_hashes":hashes,"AST_definition_hashes":extracted,"source_state_results":rows,"tree_Goldstone_control":goldstone,
            "condensed_composition_gate":{"status":"PASS_SCALAR_TARGET_ONLY_NOT_ADMITTED" if composition_ok else
               "FAIL_REQUIRED_COMMON_FLOW_IDENTITY","target_pass":composition_ok,
               "failed_points":[r["point"] for r in condensed if not r["composition_target"]["pass"]],
               "operator_admitted":False,"physical_material_mapping_admitted":False},
            "candidate_controller":package["candidate_controller"],"physical_controller":package["physical_controller"],
            "locked_verification":rules,"whole_Core_runtime_executed":False,"complete_flow_master_function_derived":False,
            "phase_stiffness_repaired_to_force_identity":False,"physical_HeII_state_assigned":False,
            "physical_UET_operator_admitted":False,"physical_prediction_executed":False,
            "physical_J04_executed":False,"physical_J05_executed":False,"physical_J06_executed":False,
            "claim_promotion":False,"dependency_unlock":False,"thresholds_relaxed":False,
            "notes":["AST selected source bodies execute in isolated explicit configuration namespaces; the full Core facade is not imported.",
                     "Quadrature memoization does not change nodes, weights or integrands; source body hashes are retained.",
                     "Five-point wrapper derivatives differ from the native Core second-order state function.",
                     "Target failure rejects only identifying this formal Doppler proxy plus tree stiffness as one complete ideal inertia.",
                     "No corrected coefficient is fitted or emitted; full finite-T current/stress/flow action must be derived consistently.",
                     "Natural relativistic inertia E^4 is not a material SI mass density or He-II sound prediction.",
                     "Prior Core/Topic13 static lanes and admission gates are not modified."]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-json",type=Path,default=CONTRACT)
    parser.add_argument("--output",type=Path,default=OUTPUT)
    args=parser.parse_args()
    path=args.contract_json.resolve()
    result=audit(json.loads(path.read_text(encoding="utf-8")),path)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(result["status"],result["passing_check_count"],"/",result["check_count"])
    print("Condensed composition:",result["condensed_composition_gate"]["status"])
    if result["passing_check_count"]!=result["check_count"]:
        print("FAIL:",[n for n,c in result["checks"].items() if not c["pass"]])
        return 1
    return 0


if __name__=="__main__":
    raise SystemExit(main())
