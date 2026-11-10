"""Mutation test for the parent physics tests (wave B1). Run from the repo root."""
import importlib, subprocess, sys, json

MUTATIONS = {
    "potential_derivative_sign": ("docs.core.02_equations.covariant.uet_covariant_response", "response_potential_derivative", "lambda f: (lambda *a, **k: -f(*a, **k))"),
    "potential_derivative_x1.01": ("docs.core.02_equations.covariant.uet_covariant_response", "response_potential_derivative", "lambda f: (lambda *a, **k: 1.01*f(*a, **k))"),
    "curvature_coupling_x2": ("docs.core.02_equations.covariant.uet_covariant_response", "curvature_factor_base_derivative", "lambda f: (lambda *a, **k: 2*f(*a, **k))"),
    "curvature_factor_drop_eps": ("docs.core.02_equations.covariant.uet_covariant_response", "curvature_factor", "lambda f: (lambda phi, c: 1.0 + (f(phi, c) - 1.0) / c.epsilon_nc)"),
    "portal_sign": ("docs.core.02_equations.covariant.uet_covariant_matter", "interaction_energy_density", "lambda f: (lambda *a, **k: -f(*a, **k))"),
    "effective_lambda_x1.1": ("docs.core.02_equations.covariant.uet_covariant_response", "effective_cosmological_constant", "lambda f: (lambda *a, **k: 1.1*f(*a, **k))"),
    "response_stress_x0.99": ("docs.core.02_equations.covariant.uet_covariant_response", "response_stress_tensor", "lambda f: (lambda *a, **k: 0.99*f(*a, **k))"),
    "matter_potential_x1.01": ("docs.core.02_equations.covariant.uet_covariant_matter", "matter_potential", "lambda f: (lambda *a, **k: 1.01*f(*a, **k))"),
}
TESTS = ["docs/core/05_tests/physics/test_parent_derivation.py", "docs/core/05_tests/physics/test_parent_offdiagonal.py",
         "docs/core/05_tests/physics/test_exchange_identity.py", "docs/core/05_tests/physics/test_fidelity_static_vacuum.py"]
CHILD = r'''
import importlib, sys, pytest
mod = importlib.import_module({mod!r})
orig = getattr(mod, {name!r})
setattr(mod, {name!r}, ({wrap})(orig))
sys.exit(pytest.main(["-q", "-x", "-p", "no:cacheprovider", *{tests!r}]))
'''
out = {}
for key, (mod, name, wrap) in MUTATIONS.items():
    r = subprocess.run([sys.executable, "-c", CHILD.format(mod=mod, name=name, wrap=wrap, tests=TESTS)], capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l.lower()][-1:]
    out[key] = {"caught": r.returncode != 0, "summary": last[0] if last else r.stdout[-200:]}
    print(key, out[key], flush=True)
print(json.dumps({k: v["caught"] for k, v in out.items()}))
