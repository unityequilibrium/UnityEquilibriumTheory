"""Exact response/requirement audit of the unchanged homogeneous unit fixture.

No trajectories, old producers, fitted parameters, physical observations or
network access. Source AST extraction is deliberately restricted and fail-closed.
"""
from __future__ import annotations

import argparse
import ast
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
STEM = "retained_response_requirement_audit"
CONTRACT = f"{TOPIC}/calculation_contracts/{STEM}.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_{STEM}.json"
CORE = "docs/core/02_equations/matter_space/uet_matter_space.py"
RESOURCE = "docs/core/03_lanes/persistence/uet_resource_selection.py"
CONTROLS = "docs/core/07_artifacts/provenance/resource_selection_dynamic_game_verification.json"
BASELINE = "8b2718bb1060463090393bdec44f5110f2c93549"
READOUTS = ("C", "C_squared", "Phi", "Pi")
PORTS = ("J_C", "J_Phi")
FIXTURE = {"a_matter": -1, "b_matter": 1, "a_space": 1, "b_space": 1,
           "coupling_g": 1, "mobility_matter": 1, "mobility_space": 1,
           "tau_space": 1, "kappa_matter": 1, "kappa_space": 1}
C, Phi, Pi, JC, JP = s.symbols("C Phi Pi J_C J_Phi", real=True)
c, r = s.symbols("c r", positive=True)
z = s.symbols("z")


def equal(a, b):
    if isinstance(a, s.MatrixBase) or isinstance(b, s.MatrixBase):
        a, b = s.Matrix(a), s.Matrix(b)
        return a.shape == b.shape and all(s.cancel(v) == 0 for v in a-b)
    return s.cancel(a-b) == 0


def functions(text):
    return {n.name: n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}


def assignment(nodes, name):
    found = [n.value for node in nodes for n in ast.walk(node)
             if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    if len(found) != 1:
        raise ValueError("source assignment is ambiguous: " + name)
    return found[0]


def expression(node, env):
    """Only the scalar arithmetic used by declared homogeneous RHS is admitted."""
    if isinstance(node, (ast.Name, ast.Attribute)):
        key = ast.unparse(node)
        if key not in env:
            raise ValueError("unmapped source symbol: " + key)
        return env[key]
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return s.Rational(str(node.value))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -expression(node.operand, env)
    if isinstance(node, ast.BinOp):
        a, b = expression(node.left, env), expression(node.right, env)
        operations = {ast.Add: lambda: a+b, ast.Sub: lambda: a-b,
                      ast.Mult: lambda: a*b, ast.Div: lambda: a/b, ast.Pow: lambda: a**b}
        if type(node.op) in operations:
            return operations[type(node.op)]()
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "copy" and not node.args and not node.keywords:
        return expression(node.func.value, env)
    raise ValueError("unsupported source arithmetic: " + ast.dump(node))


def source_drift(text=None):
    f = functions(text if text is not None else (ROOT/CORE).read_text(encoding="utf-8"))
    env = {"C": C, "Phi": Phi, "lap_C": 0, "lap_Phi": 0,
           "state.space_rate": Pi, "matter_drive": JC, "space_drive": JP}
    env.update({"config."+k: s.Integer(v) for k, v in FIXTURE.items()})
    mu = f["matter_space_chemical_potentials"]
    env["mu_matter"] = expression(assignment(mu.body, "mu_C"), env)
    env["mu_space"] = expression(assignment(mu.body, "mu_Phi"), env)
    rhs = f["matter_space_rhs"]
    branches = [n for n in rhs.body if isinstance(n, ast.If)
                and ast.unparse(n.test) == "config.matter_dynamics == 'conserved'" and n.orelse]
    if len(branches) != 1:
        raise ValueError("nonconserved source branch not identified")
    return s.Matrix([expression(assignment(branches[0].orelse, "dC"), env),
                     expression(assignment(rhs.body, "dPhi"), env),
                     expression(assignment(rhs.body, "dPi"), env)])


def resource_source_audit(text=None):
    text = text if text is not None else (ROOT/RESOURCE).read_text(encoding="utf-8")
    tree, f = ast.parse(text), functions(text)
    config = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ResourceSelectionConfig")
    frozen = any(isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "dataclass"
                 and any(k.arg == "frozen" and isinstance(k.value, ast.Constant) and k.value.value is True for k in d.keywords)
                 for d in config.decorator_list)
    field_names = {n.target.id for n in config.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)}
    selected = [f[n] for n in ("_fitness", "_advance_probabilities", "simulate_resource_selection")]
    if any(isinstance(n, (ast.Global, ast.Nonlocal)) or isinstance(n, ast.Call)
           and isinstance(n.func, ast.Name) and n.func.id in {"eval", "exec", "getattr", "setattr"}
           for fn in selected for n in ast.walk(fn)):
        raise ValueError("dynamic source dependencies require renewed review")
    attrs = {n.attr for n in ast.walk(f["_fitness"]) if isinstance(n, ast.Attribute)
             and isinstance(n.value, ast.Name) and n.value.id == "config"}
    fitness_args = [n.arg for n in f["_fitness"].args.args]
    advance_args = [n.arg for n in f["_advance_probabilities"].args.args]
    calls = [n for n in ast.walk(f["simulate_resource_selection"]) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == "_advance_probabilities"]
    call_names = {n.id for call in calls for arg in call.args for n in ast.walk(arg) if isinstance(n, ast.Name)}
    config_writes = []
    for fn in selected:
        for n in ast.walk(fn):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else []
            config_writes.extend(ast.unparse(t) for t in targets if ast.unparse(t).startswith("config."))
    loop = next(n for n in f["simulate_resource_selection"].body if isinstance(n, ast.For))
    threshold_in_loop = any(isinstance(n, ast.Attribute) and n.attr == "sustain_threshold" for n in ast.walk(loop))
    result = {"config_frozen": frozen, "interaction_and_costs_are_config":
              {"interaction_matrix", "behavior_cost", "maintenance_cost"}.issubset(field_names),
              "fitness_uses_interaction_and_probability": "interaction_matrix" in attrs and "probabilities" in fitness_args,
              "internal_config_writes": config_writes,
              "resource_enters_probability_update": "resource" in fitness_args+advance_args or "resource" in call_names
              or bool(attrs & {"initial_available_resource", "sustain_threshold"}),
              "threshold_changes_update_inside_loop": threshold_in_loop,
              "probability_update_call_count": len(calls),
              "scope": "current source dependency audit; no simulation, physical topology identification or universal learning definition"}
    if not frozen or not result["interaction_and_costs_are_config"] or config_writes or len(calls) != 2:
        raise ValueError("resource configuration/update structure changed")
    return result


@lru_cache(maxsize=1)
def algebra():
    drift = s.Matrix([C-C**3+C*Phi+JC, Pi, -Pi-Phi-Phi**3+C**2/2+JP])
    potential = C**4/4-C**2/2+Phi**4/4+Phi**2/2-C**2*Phi/2
    B = drift.jacobian([JC, JP])
    d = 1+3*r**2
    denominator = (z+2*c**2)*(z**2+z+d)-c**2
    models = {}
    for q in (1, -1):
        L = s.Matrix([[-2*c**2, q*c, 0], [0, 0, 1], [q*c, -d, -1]])
        K = s.Matrix([[1, 0, 0], [2*q*c, 0, 0], [0, 1, 0], [0, 0, 1]])
        H = s.Matrix([[z**2+z+d, q*c],
                      [2*q*c*(z**2+z+d), 2*c**2],
                      [q*c, z+2*c**2], [q*c*z, z*(z+2*c**2)]])/denominator
        P = s.Matrix([[2*c**2, -q*c, 0], [-q*c, d, 0], [0, 0, 1]])
        loss = s.Matrix([[2*c**2, -q*c, 0], [0, 0, 1]])
        models[q] = {"L": L, "K": K, "H": H, "P": P, "loss": loss}
    return {"drift": drift, "potential": potential, "B": B, "d": d,
            "D": denominator, "models": models}


def symbolic_checks():
    a = algebra(); plus, minus = a["models"][1], a["models"][-1]
    R, S, E = s.diag(-1, 1, 1), s.diag(-1, 1), s.diag(-1, 1, 1, 1)
    ideal = s.groebner([c**2-1-r, 2*r**3+r-1], c, r, domain=s.QQ)
    reduced = lambda x: ideal.reduce(s.expand(x))[1] == 0
    checks = {
        "canonical_source_matches_unit_rhs": equal(source_drift(), a["drift"]),
        "force_pair_from_same_potential": equal(s.Matrix([-s.diff(a["potential"], C)+JC, Pi,
                    -Pi-s.diff(a["potential"], Phi)+JP]), a["drift"]),
        "source_ports_from_rhs": equal(a["B"], s.Matrix([[1, 0], [0, 0], [0, 1]])),
        "equilibria_use_old_exact_relations": all(reduced(v) for q in (1, -1) for v in
                    a["drift"].subs({C:q*c, Phi:r, Pi:0, JC:0, JP:0})),
        "full_state_input_reflection": equal(a["drift"].subs({C:-C, JC:-JC}, simultaneous=True), R*a["drift"]),
        "source_port_reflection": equal(R*a["B"], a["B"]*S),
        "branch_jacobian_conjugacy": equal(minus["L"], R*plus["L"]*R),
        "readout_reflection_includes_C_squared_derivative": equal(minus["K"]*R, E*plus["K"]),
        "resolvent_equals_eliminated_response": all(equal(m["K"]*(z*s.eye(3)-m["L"]).inv()*a["B"],m["H"]) for m in a["models"].values()),
        "common_characteristic_denominator": all(equal((z*s.eye(3)-m["L"]).det(),a["D"]) for m in a["models"].values()),
        "transfer_input_output_parity": equal(minus["H"], E*plus["H"]*S),
        "all_eight_single_port_magnitude_relations": all(equal(minus["H"][i,j]**2,plus["H"][i,j]**2) for i in range(4) for j in range(2)),
        "energy_matrix_and_loss_identity": all(equal(m["L"].T*m["P"]+m["P"]*m["L"],-2*m["loss"].T*m["loss"]) for m in a["models"].values()),
        "positive_energy_principal_minors": all(equal(m["P"][:2,:2].det(),c**2*(1+6*r**2)) and equal(m["P"].det(),c**2*(1+6*r**2)) for m in a["models"].values()),
        "loss_and_one_derivative_have_no_hidden_mode": all(equal(s.Matrix.vstack(m["loss"][1,:],m["L"][2,:],m["loss"][0,:]).det(),c**2*(1+6*r**2)) for m in a["models"].values()),
        "jacobian_from_drift_at_each_branch": all(all(reduced(v) for v in a["drift"].jacobian([C,Phi,Pi]).subs({C:q*c,Phi:r,Pi:0})-m["L"]) for q,m in a["models"].items()),
        "baseline_readout_derivative": all(equal(s.Matrix([C,C**2,Phi,Pi]).jacobian([C,Phi,Pi]).subs(C,q*c),m["K"]) for q,m in a["models"].items()),
        "local_absolute_readout_uses_branch_derivative": all(equal(m["K"][1,:]/(2*c),s.Matrix([[q,0,0]])) for q,m in a["models"].items()),
        "nonlinearity_not_removed_by_fixed_coefficients": s.diff(a["potential"],C,3) == 6*C,
    }
    return checks


def protocol():
    return {"fixture": deepcopy(FIXTURE), "ports": list(PORTS), "readouts": list(READOUTS),
            "ports_applied_separately": True, "baseline_subtracted": True,
            "regime": "infinitesimal_response_at_equilibrium", "physical_acceptance": False,
            "source_of_history": "old_finite_preparation_not_rerun", "frozen_label_is_learned": False}


def validate_protocol(p):
    expected = protocol()
    if p != expected:
        raise ValueError("protocol/parameter/readout/claim scope differs from locked unit audit")


def rejected(call):
    try:
        call()
    except ValueError:
        return True
    return False


def negative_controls():
    a=algebra(); hp,hm=a["models"][1]["H"],a["models"][-1]["H"]
    bad_parameter=protocol();bad_parameter["fixture"]["coupling_g"]=2
    bad_frozen=protocol();bad_frozen["frozen_label_is_learned"]=True
    bad_physical=protocol();bad_physical["physical_acceptance"]=True
    dc=lambda x:s.cancel(x.subs(z,0))
    resource=resource_source_audit()
    return {
        "different_baseline_does_not_imply_different_gain": not equal(c,-c) and equal(hp[0,0],hm[0,0]),
        "coefficient_retuning_rejected": rejected(lambda:validate_protocol(bad_parameter)),
        "omitted_input_reflection_detected": not equal(hm,s.diag(-1,1,1,1)*hp),
        "omitted_C_squared_derivative_detected": not equal(hp[1,1],hp[0,1]),
        "mixed_inputs_not_covered_by_single_port_magnitude": dc((hp[0,0]+hp[0,1])**2-(hm[0,0]+hm[0,1])**2) != 0,
        "mixed_readout_not_covered_by_separate_channels": dc((hp[0,1]+hp[2,1])**2-(hm[0,1]+hm[2,1])**2) != 0,
        "finite_amplitude_has_nonzero_quadratic_readout_remainder": s.expand((c+C)**2-c**2-2*c*C) == C**2,
        "frozen_label_without_preparation_is_not_learned": rejected(lambda:validate_protocol(bad_frozen)),
        "ledger_is_not_resource_feedback": not resource["resource_enters_probability_update"] and not resource["threshold_changes_update_inside_loop"],
        "physical_promotion_rejected": rejected(lambda:validate_protocol(bad_physical)),
    }


def calculate():
    checks, controls = symbolic_checks(), negative_controls()
    source = resource_source_audit()
    if not all(checks.values()) or not all(controls.values()):
        raise ValueError("exact response/source audit failed")
    old = load_json(ROOT/CONTROLS)
    needed = ["costless_interaction_keeps_C_invariant", "costless_resource_changes_with_declared_cost",
              "same_cost_interaction_changes_C", "same_cost_interaction_does_not_change_ledger"]
    if not all(old["gates"][k] is True for k in needed):
        raise ValueError("inherited controls no longer support scoped separation")
    a=algebra()
    return {"source_baseline_commit": BASELINE, "sympy_version":s.__version__, "completed_sections": ["U0","U1","U2","U3"],
            "protocol": protocol(), "checks": checks, "negative_controls": controls,
            "exact_response": {"symbols": "c>0,r>0,c^2=1+r,2r^3+r-1=0,z=normalized Laplace frequency",
                  "denominator": str(s.expand(a["D"])),
                  "positive_branch": [[str(v) for v in row] for row in a["models"][1]["H"].tolist()],
                  "negative_branch_signs": [[1,-1],[-1,1],[-1,1],[-1,1]],
                  "denominator_domain": "No poles in Re(z)>=0 by positive quadratic energy and full-rank loss/derivative witness; no floating eigenvalue proof.",
                  "magnitude_scope": "Each separate readout and one port at a time only; |T_minus_ij(iw)|=|T_plus_ij(iw)|. Not mixed ports/readouts or finite-amplitude switching."},
            "resource_source_audit": source,
            "inherited_controls": {"path": CONTROLS,"rerun":False,"selected_gate_names":needed,
                    "original_scope":"declared interaction-versus-cost separation; not measured resource learning"},
            "history_dispositions": {"within_basin_Pi_pair":"old asymptotic convergence to same state; finite wait not exact reset",
                    "stable_basins":"prepared sign/basin memory; no gain-magnitude difference in declared eight linear channels",
                    "structural_matrix_update":"external fixed configuration in inspected resource lane, not internal A dynamics",
                    "hidden_arrangements_and_modes":"old N/O/P limitations reused; no new closure or physical preparation inferred"},
            "physical_acceptance":False,"new_model_terms":0,"old_producers_rerun":False,
            "trajectories":0,"parameter_sweeps":0,"quantum_parent_validated":False,
            "new_UET_discriminator":False,
            "next_controller":"physical-parent-preparation remains unchanged. Reopen a structural-response calculation only with a sourced missing requirement, independent restriction or admitted physical state/preparation/readout; no automatic new state/model/platform."}


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT),ROOT),**calculate()}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--check",action="store_true",help="read-only exact source/identity/artifact check")
    mode.add_argument("--emit-report",action="store_true",help="write only this new artifact")
    args=parser.parse_args(argv)
    result=record();payload=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(payload,encoding="utf-8",newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes()!=payload.encode("utf-8"):
        raise ValueError("artifact missing/stale; inspect before explicit --emit-report")
    print(json.dumps({"checks":len(result["checks"]),"negative_controls":len(result["negative_controls"]),
                      "physical_acceptance":False,"review":result["contract_review_status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
