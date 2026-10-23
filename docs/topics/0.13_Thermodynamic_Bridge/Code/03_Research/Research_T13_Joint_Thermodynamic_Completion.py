"""Exact checks for a conditional thermostat, NOT a new stochastic Core law.

No solver, random samples, measured data or fit. The report supplies the boundary,
measure and analytic arguments that finite symbolic tests cannot certify alone.
Only --emit-report writes the compact generated artifact; --check is read-only.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata, load_json

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
CONTRACT = f"{TOPIC}/calculation_contracts/joint_thermodynamic_completion.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_joint_thermodynamic_completion.json"
CORE = "docs/core/02_equations/matter_space/uet_matter_space.py"


def reference():
    C, Phi, Pi = s.symbols("C Phi Pi", real=True)
    aC, aP, g, JC, JP = s.symbols("a_C a_Phi g J_C J_Phi", real=True)
    bC, bP, MC, MP, tau, theta = s.symbols(
        "b_C b_Phi M_C M_Phi tau Theta", positive=True)
    omega = aC*C**2/2 + bC*C**4/4 + aP*Phi**2/2 + bP*Phi**4/4 - g*C**2*Phi/2
    muC, muP = s.diff(omega, C), s.diff(omega, Phi)
    energy = omega + tau*Pi**2/(2*MP)
    drift = s.Matrix([-MC*muC+JC, Pi, (-Pi-MP*muP+JP)/tau])
    noise = s.Matrix([[s.sqrt(2*MC*theta), 0], [0, 0],
                      [0, s.sqrt(2*MP*theta)/tau]])
    return dict(C=C, Phi=Phi, Pi=Pi, aC=aC, aP=aP, g=g, JC=JC, JP=JP,
                bC=bC, bP=bP, MC=MC, MP=MP, tau=tau, theta=theta,
                omega=omega, muC=muC, muP=muP, energy=energy, drift=drift,
                noise=noise, state=(C, Phi, Pi), DC=MC*theta, DP=MP*theta/tau**2)


def generator(f, r, c_noise_scale=1, pi_noise_scale=1):
    """Backward Itô generator; scales multiply diffusion, not noise amplitude."""
    C, _, Pi = r["state"]
    return s.expand(sum(a*s.diff(f, x) for a, x in zip(r["drift"], r["state"]))
                    + c_noise_scale*r["DC"]*s.diff(f, C, 2)
                    + pi_noise_scale*r["DP"]*s.diff(f, Pi, 2))


def _exact_zeros(expressions):
    result = {k: s.simplify(v) for k, v in expressions.items()}
    failed = {k: str(v) for k, v in result.items() if v != 0}
    if failed:
        raise ValueError(f"exact identity failed: {failed}")
    return {k: str(v) for k, v in result.items()}


def core_projection_residuals(source_text=None):
    """Read actual Core expressions in the declared homogeneous unit-cell limit.

    A tiny explicit AST interpreter projects integrals to one cell and spatial
    derivatives to zero. It neither imports/executes Core nor tests other lanes.
    Unsupported source changes fail closed instead of silently accepting a mirror.
    """
    r = reference()
    source_text = source_text if source_text is not None else (ROOT/CORE).read_text(encoding="utf-8-sig")
    tree = ast.parse(source_text)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    values = {
        "state.C": r["C"], "state.space_response": r["Phi"], "state.space_rate": r["Pi"],
        "config.a_matter": r["aC"], "config.b_matter": r["bC"],
        "config.a_space": r["aP"], "config.b_space": r["bP"],
        "config.coupling_g": r["g"], "config.mobility_matter": r["MC"],
        "config.mobility_space": r["MP"], "config.tau_space": r["tau"],
        "config.kappa_matter": s.Symbol("kappa_C"), "config.kappa_space": s.Symbol("kappa_Phi"),
        "C": r["C"], "Phi": r["Phi"], "dx": s.Integer(1), "spacing": s.Integer(1),
        "lap_C": s.Integer(0), "lap_Phi": s.Integer(0),
        "mu_matter": r["muC"], "mu_space": r["muP"],
        "matter_drive": r["JC"], "space_drive": r["JP"],
    }

    def evaluate(n):
        name = ast.unparse(n)
        if name in values:
            return values[name]
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            return s.Rational(str(n.value))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -evaluate(n.operand)
        if isinstance(n, ast.BinOp):
            a, b = evaluate(n.left), evaluate(n.right)
            operations = {ast.Add: lambda: a+b, ast.Sub: lambda: a-b,
                          ast.Mult: lambda: a*b, ast.Div: lambda: a/b, ast.Pow: lambda: a**b}
            if type(n.op) in operations:
                return operations[type(n.op)]()
        if isinstance(n, ast.Call):
            fn = ast.unparse(n.func)
            if fn in {"float", "integral_1d"}:
                return evaluate(n.args[0])
            if fn == "np.square":
                return evaluate(n.args[0])**2
            if fn == "gradient_energy_integral_1d":
                return s.Integer(0)
            if fn == "matter_space_free_energy":
                return r["omega"]
            if fn == "state.space_rate.copy":
                return r["Pi"]
        raise ValueError(f"unsupported homogeneous Core expression: {name}")

    def assignment(fn, name, nodes=None):
        nodes = functions[fn].body if nodes is None else nodes
        for n in nodes:
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
                return evaluate(n.value)
        raise ValueError(f"missing Core assignment: {fn}:{name}")

    def nonconserved_body(fn):
        nodes = [n for n in functions[fn].body if isinstance(n, ast.If)
                 and ast.unparse(n.test) == "config.matter_dynamics == 'conserved'"]
        branches = [n.orelse for n in nodes if n.orelse]
        if len(branches) != 1:
            raise ValueError(f"ambiguous nonconserved Core branch: {fn}")
        return branches[0]

    projected = {
        "omega": assignment("matter_space_free_energy", "local_density"),
        "muC": assignment("matter_space_chemical_potentials", "mu_C"),
        "muP": assignment("matter_space_chemical_potentials", "mu_Phi"),
        "energy": r["omega"] + assignment("matter_space_extended_energy", "kinetic"),
        "dC": assignment("matter_space_rhs", "dC", nonconserved_body("matter_space_rhs")),
        "dPhi": assignment("matter_space_rhs", "dPhi"),
        "dPi": assignment("matter_space_rhs", "dPi"),
        "sigmaC": assignment("matter_space_dissipation", "sigma_matter", nonconserved_body("matter_space_dissipation")),
        "sigmaPi": assignment("matter_space_dissipation", "sigma_space"),
    }
    expected = dict(omega=r["omega"], muC=r["muC"], muP=r["muP"], energy=r["energy"],
                    dC=r["drift"][0], dPhi=r["Pi"], dPi=r["drift"][2],
                    sigmaC=r["MC"]*r["muC"]**2, sigmaPi=r["Pi"]**2/r["MP"])
    return {k: s.simplify(v-expected[k]) for k, v in projected.items()}


def first_law_residuals(heat_sign=1):
    r = reference()
    C, Phi, Pi = r["state"]
    MC, MP, tau, theta = (r[k] for k in ("MC", "MP", "tau", "theta"))
    muC, JC, JP = (r[k] for k in ("muC", "JC", "JP"))
    aC = r["drift"][0]
    fC, fP = JC/MC, JP/MP
    bC, bP = r["noise"][0, 0], r["noise"][2, 1]
    # Work/heat as Stratonovich coefficients in the two independent Wiener ports.
    w_dt, w_C, w_P = fC*aC+fP*Pi, fC*bC, s.Integer(0)
    qC_dt = (fC-muC)*aC-r["DC"]*s.diff(muC, C)
    qP_dt = Pi**2/MP-theta/tau
    q_C, q_P = (fC-muC)*bC, -s.sqrt(2*theta/MP)*Pi
    # Conversion of dE=grad(E) o dX adds these two Itô terms.
    correction = MC*theta*s.diff(r["omega"], C, 2)+theta/tau
    deterministic = -MC*muC**2-Pi**2/MP+muC*JC+Pi*JP/MP
    return {
        "ito_energy_drift": generator(r["energy"], r)-deterministic-correction,
        "work_minus_heat_dt": generator(r["energy"], r)-w_dt+heat_sign*(qC_dt+qP_dt),
        "work_minus_heat_C_noise": muC*bC-w_C+heat_sign*q_C,
        "work_minus_heat_Pi_noise": tau*Pi*bP/MP-w_P+heat_sign*q_P,
        "ito_stratonovich_energy_correction": correction-
            (s.diff(r["energy"], C, 2)*bC**2+s.diff(r["energy"], Pi, 2)*bP**2)/2,
        "no_independent_Phi_noise": sum(r["noise"][1, j]**2 for j in range(2)),
    }


def coarse_free_energy_residuals():
    """Same one-temperature drift, different admissible intrinsic-entropy ledgers."""
    r = reference()
    temperature, T0, kappa = s.symbols("vartheta Theta_0 kappa", positive=True)
    Phi, Pi = r["Phi"], r["Pi"]
    intrinsic = kappa*Phi**2
    F = r["omega"]+(T0-temperature)*intrinsic
    U = s.simplify(F-temperature*s.diff(F, temperature))
    qref = s.Symbol("q_ref")
    qphysical = qref-2*T0*kappa*Phi*Pi
    return {
        "same_F_at_reference_bath": F.subs(temperature, T0)-r["omega"],
        "intrinsic_entropy_definition": -s.diff(F, temperature)-intrinsic,
        "internal_energy_differs": U-r["omega"]-T0*intrinsic,
        "first_law_intrinsic_heat_correction":
            2*T0*kappa*Phi*Pi+qphysical-qref,
    }


def calculate():
    r = reference()
    checks = {
        "core_homogeneous_projection": _exact_zeros(core_projection_residuals()),
        "R1_first_law": _exact_zeros(first_law_residuals()),
        "R1_free_energy_nonuniqueness": _exact_zeros(coarse_free_energy_residuals()),
    }
    if all(s.simplify(v) == 0 for v in first_law_residuals(-1).values()):
        raise ValueError("wrong heat sign was not rejected")
    return {
        "completed_rounds": ["R0", "R1"], "checks": checks,
        "negative_controls": {"wrong_heat_sign_rejected": True},
        "interpretation": "REF-E first law closes; HIST-F physical heat needs intrinsic entropy/measure.",
        "physical_acceptance": False, "new_core_terms": 0, "observational_rows": 0,
        "old_scientific_verifiers_rerun": False, "unique_UET_discriminator": False,
        "method": {"sympy": s.__version__, "arithmetic": "exact", "samples": 0},
        "limitations": ["No SI/microscopic correspondence", "No independent specialist review",
                        "No stochastic trajectory, finite-temperature retention lifetime or spatial/conserved proof"],
    }


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT), ROOT), **calculate()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only exact checks and artifact freshness")
    mode.add_argument("--emit-report", action="store_true", help="generate only the named compact artifact")
    args = parser.parse_args(argv)
    result = record()
    serialized = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(serialized, encoding="utf-8", newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes() != serialized.encode("utf-8"):
        raise ValueError("artifact absent/stale; review changed evidence before explicit --emit-report")
    print(json.dumps({"rounds": result["completed_rounds"], "exact_groups": len(result["checks"]),
                      "contract_review": result["contract_review_status"],
                      "physical_acceptance": False, "artifact": OUTPUT}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
