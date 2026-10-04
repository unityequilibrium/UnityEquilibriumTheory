"""Instantaneous normalized vector-state reference audit, not an admitted UET solver.

Uses canonical Core polynomial expressions without importing its migrated runtime.
No trajectory, SI calibration, external response, or F0-F8 promotion is performed.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT = TOPIC / "Data/03_Research/fluid_vector_state_research_contract.json"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_vector_state_addendum.json"
CORE = ROOT / "docs/core/02_equations/matter_space/uet_matter_space.py"
OUTPUT = TOPIC / "Result/artifacts/fluid_vector_state_contract_audit.json"


def source_expression(function, assignment):
    """Extract only one arithmetic expression; do not execute source modules."""
    tree = ast.parse(CORE.read_text(encoding="utf-8"))
    function_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    matches = [n.value for n in ast.walk(function_node) if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == assignment for t in n.targets)]
    if len(matches) != 1:
        raise ValueError("ambiguous canonical assignment: " + assignment)
    node = matches[0]
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load, ast.Attribute,
               ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd)
    if any(not isinstance(n, allowed) for n in ast.walk(node)):
        raise ValueError("canonical formula is no longer pure arithmetic")
    return ast.unparse(node), compile(ast.Expression(body=node), str(CORE), "eval")


def evaluate(expression, **values):
    return eval(expression, {"__builtins__": {}}, values)


class PeriodicOperators:
    def __init__(self, size):
        grid = np.arange(size) * (2 * np.pi / size)
        self.x, self.y = np.meshgrid(grid, grid, indexing="ij")
        k = np.fft.fftfreq(size, d=1 / size)
        self.k = np.meshgrid(k, k, indexing="ij")
        self.k2 = self.k[0] ** 2 + self.k[1] ** 2
        self.volume = (2 * np.pi) ** 2

    def derivative(self, field, axis):
        return np.fft.ifft2(1j * self.k[axis] * np.fft.fft2(field)).real

    def gradient(self, field):
        return np.stack([self.derivative(field, i) for i in range(2)])

    def laplacian(self, field):
        return np.fft.ifft2(-self.k2 * np.fft.fft2(field)).real

    def divergence(self, vector):
        return sum(self.derivative(vector[i], i) for i in range(2))

    def advection(self, velocity, field):
        return np.sum(velocity * self.gradient(field), axis=0)

    def integrate(self, field):
        return float(np.mean(field) * self.volume)

    def project(self, raw, rho):
        # rho*u_t = rho*raw - grad(p); solve Delta(p) = rho*div(raw).
        hats = np.stack([np.fft.fft2(raw[i]) for i in range(2)])
        dot = sum(self.k[i] * hats[i] for i in range(2))
        safe = np.where(self.k2 > 0, self.k2, 1)
        pressure_hat = -1j * rho * dot / safe
        pressure_hat[0, 0] = 0
        pressure = np.fft.ifft2(pressure_hat).real
        return raw - self.gradient(pressure) / rho, pressure


def validate_coefficients(c):
    if not all(np.isfinite(v) for v in vars(c).values()):
        raise ValueError("nonfinite coefficient")
    for name in ("b_matter", "kappa_matter", "mobility_matter", "b_space",
                 "kappa_space", "mobility_space", "tau_space", "rho0"):
        if getattr(c, name) <= 0:
            raise ValueError("positive coefficient required: " + name)
    if c.eta < 0 or c.a_space < 0 or c.coupling_g < 0:
        raise ValueError("outside selected parent-compatible coefficient domain")


def validate_closed_source(op, source):
    if abs(op.integrate(source)) > 1e-12 * max(op.integrate(np.abs(source)), 1):
        raise ValueError("closed conserved source has nonzero integral")


def rms(a):
    return float(np.sqrt(np.mean(np.square(a))))


def relative(a, b):
    return rms(np.asarray(a) - np.asarray(b)) / max(1, rms(a), rms(b))


def control_fields(op, locked):
    # Expressions are prelocked in the contract and restricted to basic trig arithmetic.
    env = {"x": op.x, "y": op.y, "sin": np.sin, "cos": np.cos}
    def field(key):
        node = ast.parse(locked[key], mode="eval")
        allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load,
                   ast.Constant, ast.Call, ast.Tuple, ast.Add, ast.Sub, ast.Mult, ast.Div,
                   ast.USub, ast.UAdd)
        for part in ast.walk(node):
            if not isinstance(part, allowed):
                raise ValueError("unsupported manufactured expression")
            if isinstance(part, ast.Call) and not (isinstance(part.func, ast.Name)
                                                   and part.func.id in ("sin", "cos")):
                raise ValueError("only trig calls are allowed")
        return eval(compile(node, "<locked_control>", "eval"), {"__builtins__": {}}, env)
    C, Phi, Q = (field(key) for key in ("C", "Phi", "Q"))
    stream = field("streamfunction")
    u = np.stack([op.derivative(stream, 1), -op.derivative(stream, 0)])
    JC, JP = field("J_C"), field("J_Phi")
    F = np.asarray(field("F_ext"))
    return C, Phi, Q, u, JC, JP, F


def audit_grid(size, c, rules, expressions):
    op = PeriodicOperators(size)
    C, Phi, Q, u, JC, JP, F = control_fields(op, rules["manufactured_fields"])
    validate_closed_source(op, JC)
    tol = rules["relative_identity_tolerance"]
    floor = rules["negative_control_work_floor"]
    checks = {}
    details = {}
    def check(name, metric, threshold=tol):
        checks[name] = {"metric": float(metric), "threshold": float(threshold),
                        "pass": bool(np.isfinite(metric) and metric <= threshold)}
    def potentials(C, Phi):
        env = dict(config=c, C=C, Phi=Phi, lap_C=op.laplacian(C), lap_Phi=op.laplacian(Phi))
        return (evaluate(expressions["mu_C"][1], **env), evaluate(expressions["mu_Phi"][1], **env))
    def density(C, Phi):
        local = evaluate(expressions["local_density"][1], config=c, C=C, Phi=Phi)
        return local + c.kappa_matter * np.sum(op.gradient(C)**2, axis=0)/2 + c.kappa_space * np.sum(op.gradient(Phi)**2, axis=0)/2
    def energy(C, Phi, Q, u):
        return op.integrate(density(C, Phi) + c.rho0*np.sum(u*u, axis=0)/2
                            + c.tau_space*Q*Q/(2*c.mobility_space))

    muC, muP = potentials(C, Phi)
    gc, gp = op.gradient(C), op.gradient(Phi)
    analyticC = c.a_matter*C+c.b_matter*C**3-c.kappa_matter*op.laplacian(C)-c.coupling_g*C*Phi
    analyticP = c.a_space*Phi+c.b_space*Phi**3-c.kappa_space*op.laplacian(Phi)-c.coupling_g*C*C/2
    check("canonical_mu_C_alignment", relative(muC, analyticC))
    check("canonical_mu_Phi_alignment", relative(muP, analyticP))
    force = muC*gc + muP*gp
    stress = c.kappa_matter*gc[:, None]*gc[None, :] + c.kappa_space*gp[:, None]*gp[None, :]
    stress_div = np.stack([sum(op.derivative(stress[i, j], j) for j in range(2)) for i in range(2)])
    check("stress_gauge", relative(force, op.gradient(density(C, Phi))-stress_div))
    check("reversible_mean_force_zero", rms(np.mean(force, axis=(1, 2))))
    check("independent_velocity_divergence", rms(op.divergence(u)))
    vortex = op.derivative(u[1], 0)-op.derivative(u[0], 1)
    checks["nonzero_vortical_state"] = {"metric": rms(vortex), "minimum": floor, "pass": rms(vortex)>floor}
    solenoidal_force, _ = op.project(force, c.rho0)
    details["solenoidal_force_rms"] = rms(solenoidal_force)
    checks["nonzero_solenoidal_force"] = {"metric": rms(solenoidal_force), "minimum": floor, "pass": rms(solenoidal_force)>floor}
    grad_u = np.stack([op.gradient(u[i]) for i in range(2)])
    strain = (grad_u+np.swapaxes(grad_u, 0, 1))/2
    viscous = op.integrate(2*c.eta*np.sum(strain*strain, axis=(0, 1)))
    check("viscous_factor_and_periodic_equivalence", relative(viscous, op.integrate(c.eta*np.sum(grad_u**2, axis=(0, 1)))))
    D = op.integrate(c.mobility_matter*np.sum(op.gradient(muC)**2, axis=0)+Q*Q/c.mobility_space) + viscous
    h = c.tau_space/c.mobility_space

    def ledger(velocity, matter_source, space_source, external, force_factor=1, omit_phi_advection=False):
        # These explicit RHS relations are the candidate; no integration is performed.
        Cdot = -op.advection(velocity, C)+c.mobility_matter*op.laplacian(muC)+matter_source
        Phidot = Q-op.advection(velocity, Phi)
        if omit_phi_advection:
            Phidot = Q
        Qdot = -op.advection(velocity, Q)+(-Q-c.mobility_space*muP+space_source)/c.tau_space
        raw = np.stack([-op.advection(velocity, velocity[i])+c.eta*op.laplacian(velocity[i])/c.rho0
                        +(force_factor*force[i]+external[i])/c.rho0 for i in range(2)])
        udot, pressure = op.project(raw, c.rho0)
        rate = op.integrate(muC*Cdot+muP*Phidot+h*Q*Qdot+c.rho0*np.sum(velocity*udot, axis=0))
        power = op.integrate(muC*matter_source+Q*space_source/c.mobility_space+np.sum(velocity*external, axis=0))
        residual = rate+D-power
        scale = max(1, abs(rate), D, abs(power))
        return {"rate": rate, "dissipation": D, "power": power, "residual": residual,
                "normalized_residual": abs(residual)/scale}, (Cdot, Phidot, Qdot, udot), pressure

    zeros = np.zeros_like(C)
    zeroF = np.zeros_like(u)
    closed, closed_rhs, _ = ledger(u, zeros, zeros, zeroF)
    opened, opened_rhs, _ = ledger(u, JC, JP, F)
    details["closed"] = closed
    details["open"] = opened
    check("closed_energy_ledger", closed["normalized_residual"])
    check("open_source_work_ledger", opened["normalized_residual"])
    check("nonnegative_dissipation", max(0, -D))
    for name, rhs, source, ext in (("closed", closed_rhs, zeros, zeroF), ("open", opened_rhs, JC, F)):
        check(name+"_scalar_mass", relative(op.integrate(rhs[0]), op.integrate(source)))
        momentum = np.array([op.integrate(c.rho0*rhs[3][i]) for i in range(2)])
        check(name+"_mean_momentum", relative(momentum, np.array([op.integrate(ext[i]) for i in range(2)])))
        check(name+"_rhs_incompressibility", rms(op.divergence(rhs[3])))

    workC = op.integrate(np.sum(u*muC*gc, axis=0))
    workPhi = op.integrate(np.sum(u*muP*gp, axis=0))
    work = workC+workPhi
    details["reciprocal_work"] = {"C": workC, "Phi": workPhi, "total": work}
    for key, value in (("total_work", work), ("Phi_work", workPhi)):
        checks[key+"_control_sensitive"] = {"metric": abs(value), "minimum": floor, "pass": abs(value)>floor}
    missing, _, _ = ledger(u, zeros, zeros, zeroF, force_factor=0)
    wrong, _, _ = ledger(u, zeros, zeros, zeroF, force_factor=-1)
    rate_error, _, _ = ledger(u, zeros, zeros, zeroF, omit_phi_advection=True)
    details["negative_controls"] = {"missing_reciprocal_force": missing["residual"],
                                   "wrong_force_sign": wrong["residual"], "silent_Pi_Q_substitution": rate_error["residual"]}
    check("missing_force_detected_with_expected_defect", relative(missing["residual"], -work))
    check("wrong_force_sign_detected_with_expected_defect", relative(wrong["residual"], -2*work))
    check("silent_rate_substitution_detected_with_expected_defect", relative(rate_error["residual"], workPhi))
    for name, result in (("missing_force", missing), ("wrong_sign", wrong), ("rate_substitution", rate_error)):
        checks[name+"_must_fail_ledger"] = {"metric": abs(result["residual"]), "minimum": floor,
                                          "pass": abs(result["residual"])>floor}

    V = np.asarray(ast.literal_eval(rules["manufactured_fields"]["boost"].split("=", 1)[-1]))[:, None, None]
    Pi = Q-op.advection(u, Phi)
    Pi_prime = Pi+op.advection(np.broadcast_to(V, u.shape), Phi)
    u_prime = u-V
    check("material_rate_Galilean_transform", relative(Pi_prime+op.advection(u_prime, Phi), Q))
    checks["Eulerian_material_rate_are_distinct"] = {"metric": rms(Pi-Q), "minimum": floor, "pass": rms(Pi-Q)>floor}
    boost, boosted_rhs, _ = ledger(u_prime, JC, JP, F)
    details["boosted_open"] = boost
    check("boosted_open_ledger", boost["normalized_residual"])
    for i, name in enumerate(("C", "Phi", "Q")):
        field = (C, Phi, Q)[i]
        expected = opened_rhs[i]+op.advection(np.broadcast_to(V, u.shape), field)
        check("boosted_"+name+"_rhs", relative(boosted_rhs[i], expected))
    expected_u = opened_rhs[3]+np.stack([op.advection(np.broadcast_to(V, u.shape), u[i]) for i in range(2)])
    check("boosted_velocity_rhs", relative(boosted_rhs[3], expected_u))
    check("boosted_power_shift", relative(boost["power"]-opened["power"], -op.integrate(np.sum(V*F, axis=0))))
    check("kinetic_boost_energy_shift", relative(energy(C, Phi, Q, u_prime)-energy(C, Phi, Q, u),
          op.integrate(-c.rho0*np.sum(V*u, axis=0)+c.rho0*np.sum(V*V, axis=0)/2)))

    # Zero-velocity scalar RHS recovers the canonical parent algebra (not its 1D stencil).
    parent_pi_rhs = evaluate(expressions["dPi"][1], state=SimpleNamespace(space_rate=Q),
                             config=c, mu_space=muP, space_drive=JP)
    check("frozen_zero_flow_parent_rate_algebra", relative(parent_pi_rhs, (-Q-c.mobility_space*muP+JP)/c.tau_space))
    check("zero_velocity_Pi_equals_Q", relative(Q-op.advection(zeroF, Phi), Q))
    Pi_dot = opened_rhs[2]-np.sum(opened_rhs[3]*gp, axis=0)-op.advection(u, opened_rhs[1])
    eps_frame = rules["finite_difference_steps"][-1]
    def reconstruct_pi(response, rate, velocity):
        return rate-op.advection(velocity, response)
    frame_fd = (reconstruct_pi(Phi+eps_frame*opened_rhs[1], Q+eps_frame*opened_rhs[2], u+eps_frame*opened_rhs[3])
                -reconstruct_pi(Phi-eps_frame*opened_rhs[1], Q-eps_frame*opened_rhs[2], u-eps_frame*opened_rhs[3]))/(2*eps_frame)
    check("Eulerian_Pi_coordinate_rhs_directional_derivative", relative(frame_fd, Pi_dot),
          rules["directional_derivative_tolerance"])
    naive_parent_pi = (-Pi-c.mobility_space*muP+JP)/c.tau_space
    frame_defect = rms(naive_parent_pi-Pi_dot)
    checks["unchanged_parent_Pi_rhs_is_detectably_different"] = {
        "metric": frame_defect, "minimum": floor, "pass": frame_defect>floor}
    details["Pi_coordinate_rhs"] = {"directional_relative_error": relative(frame_fd, Pi_dot),
                                    "unchanged_parent_rhs_rms_defect": frame_defect}
    zero_flow_acceleration, _ = op.project(force/c.rho0, c.rho0)
    initial_rest_pi_rhs = parent_pi_rhs-np.sum(zero_flow_acceleration*gp, axis=0)
    initial_rest_defect = rms(initial_rest_pi_rhs-parent_pi_rhs)
    checks["initial_rest_is_not_frozen_parent_evolution"] = {
        "metric": initial_rest_defect, "minimum": floor, "pass": initial_rest_defect>floor}
    details["initial_rest_parent_boundary"] = {
        "acceleration_rms": rms(zero_flow_acceleration),
        "Eulerian_Pi_rhs_defect_without_frozen_flow_constraint": initial_rest_defect}
    Cconst, Pconst = np.full_like(C, .4), np.full_like(Phi, -.1)
    mc0, mp0 = potentials(Cconst, Pconst)
    constant_force = mc0*op.gradient(Cconst)+mp0*op.gradient(Pconst)
    check("uniform_scalar_force_vanishes", rms(constant_force))

    # Independent central directional derivative of full polynomial/gradient/kinetic energy.
    dC = .2*np.sin(op.x-op.y+.2)
    dPhi = .15*np.cos(op.x+op.y+.1)
    dQ = .1*np.sin(op.y+.6)
    du = np.stack([.1*np.cos(op.y), .08*np.sin(op.x)])
    analytic_rate = op.integrate(muC*dC+muP*dPhi+h*Q*dQ+c.rho0*np.sum(u*du, axis=0))
    fd = []
    for eps in rules["finite_difference_steps"]:
        finite = (energy(C+eps*dC, Phi+eps*dPhi, Q+eps*dQ, u+eps*du)
                  -energy(C-eps*dC, Phi-eps*dPhi, Q-eps*dQ, u-eps*du))/(2*eps)
        fd.append({"step": eps, "relative_error": relative(finite, analytic_rate)})
    details["directional_derivative"] = fd
    check("directional_energy_derivative", min(row["relative_error"] for row in fd),
          rules["directional_derivative_tolerance"])

    # Young lower bound: this certifies only the polynomial, not PDE regularity.
    A1, B1 = c.b_matter/8, c.a_matter/2
    A2, B2 = c.b_space/4, c.a_space/2-c.coupling_g**2/(2*c.b_matter)
    lower = -min(B1, 0)**2/(4*A1)-min(B2, 0)**2/(4*A2)
    local = evaluate(expressions["local_density"][1], config=c, C=C, Phi=Phi)
    minorant = A1*C**4+B1*C**2+A2*Phi**4+B2*Phi**2
    check("Young_polynomial_minorant_on_control", max(0, float(np.max(minorant-local))))
    check("minorant_lower_bound_on_control", max(0, lower-float(np.min(minorant))))
    details["polynomial_bound"] = {"analytic_density_lower_bound": lower, "regularity_claim": False}
    return {"grid": size, "checks": checks, "details": details,
            "pass": all(row["pass"] for row in checks.values())}


def main():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    c = SimpleNamespace(**contract["coefficients"])
    validate_coefficients(c)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial-control-diagnostic", action="store_true")
    parser.add_argument("--output", type=Path, help="optional isolated diagnostic destination")
    args = parser.parse_args()
    rules = dict(contract["reference_verification"])
    if args.initial_control_diagnostic:
        rules["manufactured_fields"] = contract["control_design_history"]["initial_manufactured_fields"]
        rules["control_version"] = 1
    expressions = {name: source_expression(fn, name) for name, fn in
                   (("local_density", "matter_space_free_energy"),
                    ("mu_C", "matter_space_chemical_potentials"),
                    ("mu_Phi", "matter_space_chemical_potentials"), ("dPi", "matter_space_rhs"))}
    grids = [audit_grid(n, c, rules, expressions) for n in rules["grids"]]
    rejections = {}
    for name, value in (("rho0", 0), ("eta", -1), ("mobility_matter", 0),
                        ("mobility_space", 0), ("tau_space", 0), ("b_matter", 0),
                        ("b_space", 0), ("kappa_matter", 0), ("kappa_space", 0),
                        ("a_space", -1), ("coupling_g", -1), ("rho0", float("nan"))):
        values = dict(vars(c))
        values[name] = value
        try:
            validate_coefficients(SimpleNamespace(**values))
            rejected = False
        except ValueError:
            rejected = True
        rejections[name+"="+str(value)] = rejected
    op = PeriodicOperators(rules["grids"][0])
    try:
        validate_closed_source(op, np.ones_like(op.x))
        rejections["nonzero_mean_closed_source"] = False
    except ValueError:
        rejections["nonzero_mean_closed_source"] = True
    foundation = ROOT / contract["foundation_gate"]
    foundation_data = json.loads(foundation.read_text(encoding="utf-8"))
    parent_tree = ast.parse(CORE.read_text(encoding="utf-8"))
    parent_config = next(n for n in parent_tree.body if isinstance(n, ast.ClassDef) and n.name == "MatterSpaceConfig")
    parent_defaults = {n.target.id: ast.literal_eval(n.value) for n in parent_config.body
                       if isinstance(n, ast.AnnAssign) and n.value is not None}
    boundary_checks = {
        "locked_scalar_coefficients_match_parent_defaults": all(
            value == parent_defaults[name] for name, value in vars(c).items() if name not in ("rho0", "eta")),
        "normalized_periodic_2d_only": contract["unit_lane"] == "normalized" and contract["dimension"] == 2 and contract["domain"].startswith("periodic"),
        "claim_promotion_false": contract["claim_promotion"] is False,
        "dependency_unlock_false": contract["dependency_unlock"] is False,
        "physical_operator_not_admitted": contract["physical_uet_operator_admitted"] is False,
        "required_admission_still_blocked": all(contract["admission_gates"][g]["status"].startswith("BLOCKED") for g in ("F2", "F3", "F4", "F7", "F8")),
        "diagnostic_not_F5_admission": contract["admission_gates"]["F5"]["status"] == "DIAGNOSTIC_ONLY",
        "trace_not_independent_state": not set(("R_gen", "R_obs", "legacy_I")).intersection(contract["independent_state"]),
    }
    ok = all(g["pass"] for g in grids) and all(rejections.values()) and all(boundary_checks.values())
    inputs = [Path(__file__), CONTRACT, REGISTRY, CORE, TOPIC/"VECTOR_STATE_RESEARCH_CONTRACT.md",
              ROOT/contract["parent_contract"], foundation,
              ROOT/"docs/core/07_artifacts/correspondence/matter_space_ontology_contract.json",
              TOPIC/"Result/artifacts/fluid_state_velocity_representability_audit.json"]
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    artifact = {
        "schema_version": "t10-vector-state-contract-audit-v1",
        "status": "PASS_NORMALIZED_VECTOR_REFERENCE_IDENTITIES_ONLY" if ok else "FAIL_REFERENCE_AUDIT",
        "controlling_blocker": contract["controlling_blocker"],
        "claim_promotion": False, "dependency_unlock": False,
        "physical_uet_operator_admitted": False, "unit_lane": "normalized",
        "scope": "Manufactured instantaneous 2D periodic Fourier identities, not PDE trajectories or formal kernel proof.",
        "origin": "Conditional constitutive reference proposal; canonical scalar source algebra checked statically.",
        "thresholds": rules, "coefficients": contract["coefficients"],
        "canonical_source_expressions": {name: value[0] for name, value in expressions.items()},
        "input_hashes": hashes, "numpy_version": np.__version__,
        "grids": grids, "invalid_input_rejections": rejections, "claim_boundary_checks": boundary_checks,
        "reference_check_count": sum(len(g["checks"]) for g in grids)+len(rejections)+len(boundary_checks),
        "foundation_gate_status_observed": foundation_data.get("status", "not_exposed"),
        "admission_gates": contract["admission_gates"],
        "excluded": ["Core runtime import/integration", "timestep/spatial PDE convergence", "SI material calibration",
                     "external CFD", "He-II second sound", "chaos/performance", "well-posedness/global regularity"],
        "next_action": contract["next_action"],
    }
    output = args.output if args.output is not None else (
        ROOT/contract["control_design_history"]["initial_failure_artifact"] if args.initial_control_diagnostic else OUTPUT)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(artifact, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"status": artifact["status"], "reference_check_count": artifact["reference_check_count"],
                      "failed": {str(g["grid"]): [k for k, v in g["checks"].items() if not v["pass"]] for g in grids},
                      "negative_controls": grids[0]["details"]["negative_controls"]}, indent=2))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
