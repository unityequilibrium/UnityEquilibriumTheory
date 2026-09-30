"""Audit whether the current Topic 10 scalar-to-velocity map can represent periodic vortical flow.

This is a scoped representability and source-structure audit. It does not run a
physical CFD case, modify the UET solver, or establish a result for every UET model.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


TOPIC = Path("docs/topics/0.10_Fluid_Dynamics_Chaos")
ENGINE_2D = TOPIC / "Code/01_Engine/Engine_UET_2D.py"
ENGINE_3D = TOPIC / "Code/01_Engine/Engine_UET_3D.py"
CORE_PARAMETERS = Path("docs/core/01_contracts/units/uet_parameters.py")
CORE_PACKAGE = Path("docs/core/__init__.py")
CORE_COMPAT = Path("docs/core/core_compat.py")
BASE_SOLVER = Path("docs/scripts/core/runners/uet_base_solver.py")
JOINT_PLAN = TOPIC / "Data/03_Research/fluid_thermal_joint_research_plan.json"
OPENAI_REVIEW = TOPIC / "OPENAI_NAVIER_STOKES_APPLICABILITY_2026-09-26.md"
TOLERANCE = 1.0e-12


def repository_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() and (parent / "docs" / "topics").exists():
            return parent
    raise RuntimeError("Could not locate repository root from this audit script")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_python(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def find_class(tree: ast.Module, name: str) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f"Required class not found: {name}")


def find_method(cls: ast.ClassDef, name: str) -> ast.FunctionDef:
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"Required method not found: {cls.name}.{name}")


def assigns_attr(node: ast.AST, attr: str) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr == attr and isinstance(
            child.ctx, (ast.Store, ast.Del)
        ):
            return True
    return False


def assigned_literal(cls: ast.ClassDef, name: str) -> Any:
    for node in ast.walk(cls):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Required literal assignment not found: {name}")


def assignment_to_self_attr(node: ast.AST, attr: str) -> ast.Assign | ast.AnnAssign | None:
    if not isinstance(node, (ast.Assign, ast.AnnAssign)):
        return None
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    if any(
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "self"
        and target.attr == attr
        for target in targets
    ):
        return node
    return None


def mobility_gradient_assignment(method: ast.FunctionDef, field: str, gradient: str) -> bool:
    for node in ast.walk(method):
        assignment = assignment_to_self_attr(node, field)
        if assignment is None or not isinstance(assignment, ast.Assign):
            continue
        value = assignment.value
        if not (
            isinstance(value, ast.BinOp)
            and isinstance(value.op, ast.Mult)
            and isinstance(value.left, ast.UnaryOp)
            and isinstance(value.left.op, ast.USub)
            and isinstance(value.left.operand, ast.Attribute)
            and isinstance(value.left.operand.value, ast.Name)
            and value.left.operand.value.id == "self"
            and value.left.operand.attr == "mobility_M"
            and isinstance(value.right, ast.Name)
            and value.right.id == gradient
        ):
            continue
        return True
    return False

def maximum_floor(method: ast.FunctionDef, field: str) -> float | None:
    for node in ast.walk(method):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "maximum" or len(node.args) < 2:
            continue
        first, second = node.args[:2]
        if (
            isinstance(first, ast.Attribute)
            and isinstance(first.value, ast.Name)
            and first.value.id == "self"
            and first.attr == field
        ):
            try:
                return float(ast.literal_eval(second))
            except (ValueError, TypeError):
                return None
    return None


def periodic_derivative(field: np.ndarray, axis: int, spacing: float) -> np.ndarray:
    return (np.roll(field, -1, axis=axis) - np.roll(field, 1, axis=axis)) / (2.0 * spacing)


def rms(field: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(field))))


def periodic_controls(grid_size: int) -> dict[str, float | bool]:
    length = 2.0 * math.pi
    spacing = length / grid_size
    x = np.arange(grid_size, dtype=float) * spacing
    y = np.arange(grid_size, dtype=float) * spacing
    xx, yy = np.meshgrid(x, y, indexing="xy")

    scalar = np.sin(2.0 * xx) + 0.5 * np.cos(3.0 * yy) + 0.35 * np.sin(xx + yy)
    scalar_dx = periodic_derivative(scalar, axis=1, spacing=spacing)
    scalar_dy = periodic_derivative(scalar, axis=0, spacing=spacing)
    mobility = 2.3
    gradient_u = -mobility * scalar_dx
    gradient_v = -mobility * scalar_dy
    gradient_divergence = (
        periodic_derivative(gradient_u, 1, spacing)
        + periodic_derivative(gradient_v, 0, spacing)
    )
    gradient_curl = (
        periodic_derivative(gradient_v, 1, spacing)
        - periodic_derivative(gradient_u, 0, spacing)
    )
    gradient_scale = max(rms(np.hypot(gradient_u, gradient_v)), np.finfo(float).eps)
    gradient_curl_relative = rms(gradient_curl) / gradient_scale

    # A smooth periodic divergence-free rotational target with nonzero vorticity.
    target_u = np.sin(yy)
    target_v = np.sin(xx)
    target_divergence = (
        periodic_derivative(target_u, 1, spacing)
        + periodic_derivative(target_v, 0, spacing)
    )
    target_curl = (
        periodic_derivative(target_v, 1, spacing)
        - periodic_derivative(target_u, 0, spacing)
    )
    target_scale = max(rms(np.hypot(target_u, target_v)), np.finfo(float).eps)
    target_divergence_relative = rms(target_divergence) / (target_scale / length)

    # Orthogonal Fourier projection onto the range of the same centered-gradient operator.
    # Its wave-number symbol is sin(k h)/h, not the continuum k.
    wave = 2.0 * math.pi * np.fft.fftfreq(grid_size, d=spacing)
    ky, kx = np.meshgrid(wave, wave, indexing="ij")
    symbol_x = np.sin(kx * spacing) / spacing
    symbol_y = np.sin(ky * spacing) / spacing
    denominator = symbol_x * symbol_x + symbol_y * symbol_y
    u_hat = np.fft.fft2(target_u)
    v_hat = np.fft.fft2(target_v)
    dot_hat = symbol_x * u_hat + symbol_y * v_hat
    potential_hat = np.zeros_like(dot_hat)
    nonzero = denominator > 64.0 * np.finfo(float).eps
    potential_hat[nonzero] = dot_hat[nonzero] / denominator[nonzero]
    projected_u = np.fft.ifft2(symbol_x * potential_hat).real
    projected_v = np.fft.ifft2(symbol_y * potential_hat).real
    projected_fraction = rms(np.hypot(projected_u, projected_v)) / target_scale
    best_residual = rms(
        np.hypot(target_u - projected_u, target_v - projected_v)
    ) / target_scale

    # Discrete integration-by-parts check across fixed deterministic test potentials.
    rng = np.random.default_rng(20260926 + grid_size)
    correlations: list[float] = []
    for index in range(8):
        if index == 0:
            test_potential = scalar
        elif index == 1:
            test_potential = np.cos(2.0 * xx - yy) + 0.2 * np.sin(3.0 * yy)
        else:
            test_potential = rng.normal(size=(grid_size, grid_size))
        phi_x = periodic_derivative(test_potential, 1, spacing)
        phi_y = periodic_derivative(test_potential, 0, spacing)
        numerator = abs(float(np.mean(target_u * phi_x + target_v * phi_y)))
        scale = max(target_scale * rms(np.hypot(phi_x, phi_y)), np.finfo(float).eps)
        correlations.append(numerator / scale)

    return {
        "grid_size": grid_size,
        "domain_length": length,
        "spacing": spacing,
        "constant_mobility": mobility,
        "gradient_velocity_curl_rms": rms(gradient_curl),
        "gradient_velocity_divergence_rms": rms(gradient_divergence),
        "gradient_velocity_curl_relative": gradient_curl_relative,
        "gradient_velocity_is_nonzero": gradient_scale > TOLERANCE,
        "rotational_target_divergence_rms": rms(target_divergence),
        "rotational_target_divergence_relative": target_divergence_relative,
        "rotational_target_vorticity_rms": rms(target_curl),
        "rotational_target_speed_rms": target_scale,
        "rotational_target_gradient_projection_fraction": projected_fraction,
        "rotational_target_best_relative_l2_residual": best_residual,
        "max_discrete_gradient_orthogonality_correlation": max(correlations),
        "pass": (
            gradient_curl_relative < TOLERANCE
            and gradient_scale > TOLERANCE
            and target_divergence_relative < TOLERANCE
            and rms(target_curl) > 0.1
            and projected_fraction < TOLERANCE
            and abs(best_residual - 1.0) < 1.0e-10
            and max(correlations) < TOLERANCE
        ),
    }


def rotational_convergence() -> dict[str, Any]:
    rows = [periodic_controls(n) for n in (16, 32, 64)]
    analytic_curl_rms = 1.0
    errors = [
        abs(float(row["rotational_target_vorticity_rms"]) - analytic_curl_rms)
        for row in rows
    ]
    orders = [
        math.log(errors[index] / errors[index + 1], 2.0)
        for index in range(len(errors) - 1)
    ]
    return {
        "analytic_continuum_vorticity_rms": analytic_curl_rms,
        "grids": rows,
        "observed_orders": orders,
        "minimum_order": min(orders),
        "second_order_control_pass": min(orders) >= 1.8,
    }


def source_audit(root: Path) -> dict[str, Any]:
    tree_2d = parse_python(root / ENGINE_2D)
    tree_3d = parse_python(root / ENGINE_3D)
    parameter_tree = parse_python(root / CORE_PARAMETERS)
    solver_2d = find_class(tree_2d, "UETFluidSolver")
    init_2d = find_method(solver_2d, "__init__")
    derive_2d = find_method(solver_2d, "_derive_uet_parameters")
    step_2d = find_method(solver_2d, "step")
    physical = find_class(tree_2d, "PhysicalProperties")
    solver_3d = find_class(tree_3d, "UETFluid3D")
    step_3d = find_method(solver_3d, "step")

    super_index = next(
        (
            index
            for index, node in enumerate(init_2d.body)
            if any(
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id == "super"
                for child in ast.walk(node)
            )
        ),
        None,
    )
    reset_indexes = [
        index
        for index, node in enumerate(init_2d.body)
        if assignment_to_self_attr(node, "mobility_M") is not None
        and isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and node.value.value == 0.5
    ]
    derived_assignment = any(
        assignment_to_self_attr(node, "mobility_M") is not None
        and isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Name)
        and node.value.id == "M"
        for node in ast.walk(derive_2d)
    )
    physical_fields = {
        node.target.id: ast.literal_eval(node.value)
        for node in physical.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.value is not None
    }
    physical_mobility_read = any(
        isinstance(node, ast.Attribute)
        and node.attr == "mobility"
        and isinstance(node.value, ast.Name)
        and node.value.id == "phys"
        for node in ast.walk(derive_2d)
    )
    bridge_value = assigned_literal(ast.Module(body=parameter_tree.body, type_ignores=[]), "FLUID_MOBILITY_BRIDGE")
    engine_defaults = {
        argument.arg: ast.literal_eval(default)
        for argument, default in zip(
            init_2d.args.args[-len(init_2d.args.defaults):],
            init_2d.args.defaults,
        )
    }
    defaults = {
        **engine_defaults,
        **{f"physical_{key}": value for key, value in physical_fields.items()},
    }
    viscosity = float(defaults["physical_viscosity"])
    density = float(defaults["physical_density"])
    dx = float(defaults["lx"]) / int(defaults["nx"])
    dy = float(defaults["ly"]) / int(defaults["ny"])
    dt = float(defaults["dt"])
    physical_kappa = viscosity / density
    stability_limit = 0.4 / (dt * (1.0 / dx**2 + 1.0 / dy**2))
    effective_kappa = min(physical_kappa, stability_limit)
    nominal_bridge_mobility = bridge_value / viscosity / density

    assignments_3d = sorted(
        {
            node.attr
            for node in ast.walk(solver_3d)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
            and node.attr in {"u", "v", "w", "velocity", "momentum", "pressure"}
            and isinstance(node.ctx, (ast.Store, ast.Del))
        }
    )
    floor_2d = maximum_floor(step_2d, "C")
    floor_3d = maximum_floor(step_3d, "C")
    checks = {
        "2d_scalar_gradient_velocity_map": (
            mobility_gradient_assignment(step_2d, "u", "gx")
            and mobility_gradient_assignment(step_2d, "v", "gy")
        ),
        "2d_derived_mobility_precedes_constructor_reset": (
            derived_assignment and super_index is not None
            and any(index > super_index for index in reset_indexes)
        ),
        "physical_properties_mobility_not_read_by_derivation": not physical_mobility_read,
        "2d_clipping_floor_present": floor_2d == 0.01,
        "3d_clipping_floor_present": floor_3d == 0.01,
        "3d_has_no_vector_velocity_momentum_or_pressure_state": not assignments_3d,
        "kappa_cap_expression_present": "stability_limit" in ast.unparse(derive_2d)
        and "min" in ast.unparse(derive_2d),
    }
    if not all(checks.values()):
        failures = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"Topic 10 source contract changed or audit failed: {failures}")

    return {
        "static_checks": checks,
        "2d": {
            "velocity_map": "u=-M*D_x(C), v=-M*D_y(C)",
            "mobility_derived_then_overridden_after_super_init": True,
            "effective_constructor_mobility": 0.5,
            "physical_property_mobility_default": physical_fields.get("mobility"),
            "physical_property_mobility_used_in_derivation": False,
            "bridge_constant": bridge_value,
            "bridge_constant_source_classification": "repository labels it an unverified placeholder",
            "nominal_bridge_formula_value_before_constructor_reset": nominal_bridge_mobility,
            "nominal_bridge_units": "not closed by the source contract",
            "default_grid": {
                "nx": int(defaults["nx"]),
                "ny": int(defaults["ny"]),
                "lx": float(defaults["lx"]),
                "ly": float(defaults["ly"]),
                "dx": dx,
                "dy": dy,
                "dt": dt,
            },
            "default_physical_input": {
                "density_kg_m3": density,
                "dynamic_viscosity_Pa_s": viscosity,
                "kinematic_viscosity_m2_s": physical_kappa,
                "stability_limit_m2_s": stability_limit,
                "effective_kappa_m2_s": effective_kappa,
                "cap_active": effective_kappa < physical_kappa,
            },
            "clip_floor": floor_2d,
            "clip_event_count": None,
            "clip_event_count_status": "not measured because the engine step was not executed",
        },
        "3d": {
            "evolved_scalar_states": ["C", "I"],
            "vector_velocity_momentum_pressure_assignments": assignments_3d,
            "velocity_state_status": "absent_in_current_UETFluid3D",
            "clip_floor": floor_3d,
            "clip_event_count": None,
            "clip_event_count_status": "not measured because the engine step was not executed",
        },
    }


def module_import_probe(root: Path, engine_path: Path) -> dict[str, Any]:
    code = (
        "import runpy,sys; "
        "runpy.run_path(sys.argv[1], run_name='uet_source_probe')"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", code, str(root / engine_path)],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "BLOCKED_TIMEOUT", "module_import_only": True}
    if result.returncode == 0:
        return {
            "status": "PASS_MODULE_IMPORT_ONLY",
            "module_import_only": True,
            "stdout_tail": result.stdout.splitlines()[-3:],
            "stderr_tail": result.stderr.splitlines()[-3:],
        }
    lines = [line.strip() for line in result.stderr.splitlines() if line.strip()]
    portable_lines = [
        line
        for line in lines
        if not line.startswith("File ")
        and not line.startswith("^")
    ]
    return {
        "status": "BLOCKED_MODULE_IMPORT",
        "module_import_only": True,
        "failure_tail": portable_lines[-3:],
    }


def build_report(root: Path) -> dict[str, Any]:
    source_records = {
        ENGINE_2D.as_posix(): {
            "source_role": "Topic 10 2D solver; parsed statically, not stepped",
            "evidence_state": "current checked-out source, content hash bound below",
            "unit_scope": "C and M are not dimensionally closed as an SI velocity mapping",
        },
        ENGINE_3D.as_posix(): {
            "source_role": "Topic 10 3D solver; parsed statically, not stepped",
            "evidence_state": "current checked-out source, content hash bound below",
            "unit_scope": "C and I scalar fields; no vector-velocity units are declared",
        },
        CORE_PARAMETERS.as_posix(): {
            "source_role": "Core parameter and mobility-placeholder source; parsed statically",
            "evidence_state": "current checked-out canonical parameter source, content hash bound below",
            "unit_scope": "bridge constant has no declared dimension in this source",
        },
        CORE_PACKAGE.as_posix(): {
            "source_role": "Core package import and compatibility surface",
            "evidence_state": "current checked-out source, content hash bound below",
            "unit_scope": "software import lifecycle, not a physical observable",
        },
        CORE_COMPAT.as_posix(): {
            "source_role": "Core compatibility resolver",
            "evidence_state": "current checked-out source, content hash bound below",
            "unit_scope": "module mapping, not a physical observable",
        },
        BASE_SOLVER.as_posix(): {
            "source_role": "Base solver lifecycle/logger source; not instantiated",
            "evidence_state": "current checked-out source, content hash bound below",
            "unit_scope": "grid spacings are source-defined; field ontology remains topic-owned",
        },
        JOINT_PLAN.as_posix(): {
            "source_role": "Joint Topic 10/13 plan and acceptance boundary",
            "evidence_state": "current checked-out planning record, content hash bound below",
            "unit_scope": "workflow contract; no physical units",
        },
        OPENAI_REVIEW.as_posix(): {
            "source_role": "OpenAI Navier-Stokes relevance mapping; method context only",
            "evidence_state": "local source-applicability review, not solver data",
            "unit_scope": "standard Navier-Stokes theorem obligations; not UET parameter input",
        },
    }
    source_hashes = []
    for relative, metadata in source_records.items():
        path = root / Path(relative)
        source_hashes.append(
            {
                "path": relative,
                "sha256": sha256(path),
                **metadata,
            }
        )

    source_state = source_audit(root)
    convergence = rotational_convergence()
    base_grid = next(row for row in convergence["grids"] if row["grid_size"] == 32)
    engine_imports = {
        "2d": module_import_probe(root, ENGINE_2D),
        "3d": module_import_probe(root, ENGINE_3D),
    }
    numerical_pass = (
        all(bool(row["pass"]) for row in convergence["grids"])
        and bool(convergence["second_order_control_pass"])
    )
    return {
        "schema_version": "t010-fluid-state-velocity-representability-audit-v1",
        "record_role": "scoped_research_result_not_global_physics_gate",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "topic": "0.10_Fluid_Dynamics_Chaos",
        "joint_program": "Topic 10 + Topic 13 + Core",
        "controller": "fluid_state_and_velocity_observable_correspondence_unestablished",
        "status": (
            "PASS_SCOPED_NO_GO_FOR_LEGACY_ROTATIONAL_FLOW"
            if numerical_pass
            else "FAIL_AUDIT_CONTROL"
        ),
        "claim_promotion": False,
        "dependency_unlock": False,
        "universal_uet_no_go": False,
        "scope": {
            "2d_target": "nonzero smooth periodic incompressible velocity with nonzero vorticity",
            "2d_legacy_map": "u=-M*grad(C), with one spatially constant scalar M per run",
            "domain_and_operator": "periodic square; matched second-order centered finite differences",
            "3d_scope": "static state-surface audit of the existing UETFluid3D class",
            "excluded": [
                "variable or singular mobility",
                "nonperiodic boundary-driven dynamics",
                "a separately registered velocity, momentum, stream-function, or vector-potential state",
                "physical CFD accuracy, external data, and theorem-level Navier-Stokes claims",
            ],
        },
        "2d_representability": {
            "scoped_disposition": "NO_GO_FOR_NONZERO_PERIODIC_INCOMPRESSIBLE_VORTICAL_TARGET",
            "continuum_reasoning": [
                "For constant M, curl(-M*grad(C))=0 for every sufficiently smooth scalar C.",
                "Incompressibility also requires Laplacian(C)=0.",
                "On a periodic domain, integration by parts gives integral(|grad(C)|^2)=-integral(C*Laplacian(C))=0; therefore grad(C)=0 and the represented velocity is zero.",
            ],
            "discrete_control": base_grid,
            "interpretation": "The tested rotational target has zero discrete divergence, nonzero discrete vorticity, a zero gradient-subspace projection to numerical tolerance, and a relative best-fit L2 residual of one. Boundary or stencil artifacts are excluded by the periodic matched-operator design.",
            "claim_boundary": "This closes only the declared constant-scalar-mobility gradient map for this periodic target class; it is not a no-go for all UET models or other domains.",
        },
        "refinement_control": convergence,
        "source_audit": source_state,
        "f0_f8_obligations": [
            {
                "stage": "F0 ontology",
                "status": "BLOCKED_FOR_NEW_CANDIDATE",
                "finding": "Legacy C/I scalar state does not declare an independent velocity or momentum state.",
            },
            {
                "stage": "F1 standard correspondence",
                "status": "SCOPED_NO_GO",
                "finding": "The declared constant-M scalar-gradient map cannot represent a nonzero periodic incompressible vortical target.",
            },
            {
                "stage": "F2 formula identity",
                "status": "SOURCE_LOCKED",
                "finding": "The inspected 2D implementation assigns u=-M*D_x(C), v=-M*D_y(C); source hashes are attached.",
            },
            {
                "stage": "F3 units",
                "status": "OPEN",
                "finding": "C, effective M, the bridge constant, and resulting velocity lack a closed dimensional map; only mu/rho has SI kinematic-viscosity units.",
            },
            {
                "stage": "F4 derivation class",
                "status": "HEURISTIC_BRIDGE",
                "finding": "The mobility bridge is explicitly marked as a placeholder and is not a derivation from Navier-Stokes momentum balance.",
            },
            {
                "stage": "F5 parameter and numerical behavior",
                "status": "SOURCE_AUDITED_RUNTIME_LIMITED",
                "finding": "Constructor mobility reset, default inactive kappa cap, and C floor are recorded; trajectory and clip counts were not executed.",
            },
            {
                "stage": "F6 observable map",
                "status": "PASS_FOR_ANALYTIC_REPRESENTABILITY_CONTROL",
                "finding": "Periodic divergence, vorticity, gradient projection, and refinement controls are measured and recorded.",
            },
            {
                "stage": "F7 evidence and provenance",
                "status": "PASS_INTERNAL_REPRODUCIBLE_ARTIFACT",
                "finding": "The audit script, source roles, units scope, and SHA-256 source identities are recorded; no external data were consumed.",
            },
            {
                "stage": "F8 admission and claim",
                "status": "BLOCKED_FOR_PHYSICAL_CANDIDATE",
                "finding": "No new state is registered or admitted; claim_promotion and dependency_unlock remain false.",
            },
        ],        "engine_runtime_probe": engine_imports,
        "execution_limits": {
            "engine_step_executed": False,
            "physical_solver_trajectory_run": False,
            "reason": "This wave verifies the velocity representation and source structure. Runtime import probes are reported separately; no solver trajectory or clipping event count is inferred from the manufactured controls.",
            "clip_counts": "unknown; clipping sites and floors are source-audited, but no engine step was executed",
        },
        "topic13_and_core_link": {
            "current_bridge": "Topic 13's source-locked He-4 normal-component shear-viscosity channel may be a later external input for a bounded shear-response pilot.",
            "limitations": "It is not a UET-predicted viscosity, thermal conductivity, complete two-fluid transport tensor, or admission of Topic 10 flow.",
            "required_before_coupling": [
                "Core admission of a separate velocity/momentum state and its ontology, units, derivation class, and observables",
                "Topic 13 frozen-parameter independent-response protocol and source uncertainty",
                "J05 reciprocal energy and entropy ledger with exchange and boundary/source work explicit",
            ],
        },
        "openai_research_utility": {
            "method_utility": "high_for_proof_scope_and_adversarial_test_design",
            "direct_uet_evidence": "none",
            "this_wave_connection": "Its theorem assumptions make divergence-free vector velocity, force regularity, and norm obligations explicit; the current 2D gradient mapping and 3D scalar-only state do not yet instantiate those theorem variables.",
            "source_review": OPENAI_REVIEW.as_posix(),
        },
        "next_blocker": "Register and audit a distinct velocity/momentum state contract through Core F0-F8 before any physical matched-flow J04, chaos J07, or runtime J08 candidate claim.",
        "verifier_provenance": {
            "path": Path(__file__).resolve().relative_to(root).as_posix(),
            "sha256": sha256(Path(__file__).resolve()),
            "role": "script that generated this result artifact",
        },        "input_hashes": source_hashes,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "finite_difference_tolerance": TOLERANCE,
            "random_seed_rule": "20260926 + grid_size; fixed deterministic controls",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = repository_root()
    report = build_report(root)
    if args.output is not None:
        output = args.output if args.output.is_absolute() else root / args.output
    else:
        output = root / TOPIC / "Result/artifacts/fluid_state_velocity_representability_audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"status={report['status']}")
    print(f"artifact={output.relative_to(root).as_posix()}")
    print(
        "minimum_rotational_refinement_order="
        f"{report['refinement_control']['minimum_order']:.6f}"
    )
    print(
        "2d_engine_import="
        f"{report['engine_runtime_probe']['2d']['status']}"
    )
    return 0 if report["status"] == "PASS_SCOPED_NO_GO_FOR_LEGACY_ROTATIONAL_FLOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())