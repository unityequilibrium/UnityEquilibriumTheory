"""Independent soft-ray, exact streaming, static and protected-input checks."""

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("collisionless_soft", LOCAL/"Research_T13_Collisionless_Soft_Source.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
ROOT, PREFIX = M.ROOT, M.PREFIX


@pytest.fixture(params=M.MU_GRID)
def example(request):
    action = M.EFT.controls()
    return M.EFT.tree_state(request.param, action=action), action


@pytest.mark.parametrize("ratio", M.RAY_RATIOS)
def test_six_exact_streaming_channels_and_centred_finite_q_limit(example, ratio):
    state, action = example
    p, t = .02, .3
    ray = ratio*M.INT.dispersion_coefficients(state, action)["c"]
    prepared = M.soft_system(p, ray, .004, state, action)
    assert len(prepared["zero_pairs"]) == 6
    assert prepared["zero_drive_error"] < M.GATES["identity_relative"]
    assert abs(prepared["raw_stationary_phase_cancellation"]) < 1e-12
    errors = []
    for fraction in M.Q_OVER_P:
        q = p*fraction
        finite = M.finite_local_covariance(p, t, q, ray, .004, state, action)
        k, cosine = M.centre(p, t, q)
        target = M.soft_point(k, cosine, ray, .004, state, action)
        errors.append(M.VIRT.matrix_error(finite["local_covariance"], target["local_covariance"]))
        assert M.INT.relative(finite["pair_chi"], target["chi"]) < M.GATES["point_soft_relative"]
    assert errors[2] < errors[1] < errors[0] and errors[-1] < M.GATES["point_soft_relative"]


def test_covariance_momentum_derivative_matches_central_difference(example):
    state, action = example
    p, step = .02, .02*1e-4
    cp, derivative = M.covariance_momentum_jet(p, .004, state, action)
    plus = M.FQ.evolution_and_covariance(p+step, .004, state, action)[1]
    minus = M.FQ.evolution_and_covariance(p-step, .004, state, action)[1]
    assert M.VIRT.matrix_error(cp, M.FQ.evolution_and_covariance(p, .004, state, action)[1]) < 1e-9
    assert M.VIRT.matrix_error(derivative, (plus-minus)/(2*step)) < M.GATES["covariance_FD_relative"]


@pytest.mark.parametrize("a,b", [(1+.3j, .8j), (2+.1j, .01j), (1+.2j, 0j), (.1+.2j, 3j)])
def test_logarithmic_and_series_angular_moments_against_independent_quadrature(a, b):
    moments = M.angular_transport_moments(a, b)
    t, weights = np.polynomial.legendre.leggauss(512)
    reference = np.array([np.sum(weights*t**k/(a+b*t))/2 for k in range(4)])
    assert np.max(abs(moments-reference)) < 1e-10


def test_static_removable_streaming_endpoint_recovers_pressure_not_assigned_relaxation(example):
    state, action = example
    scale = M.INT.dispersion_coefficients(state, action)
    temperature = scale["c"]*scale["dispersion_scale"]/256
    source = M.stationary_soft_source(0j, state, action)
    value = M.soft_thermal(0j, temperature, state, action, 12)
    reference = M.CURV.thermal_response(temperature, state, action, 12)["chi_thermal"]
    assert M.INT.relative(value, reference) < 1e-9
    assert source["delta_mu"] == source["delta_xi"] == 0
    assert np.all(np.isfinite(M.soft_point(.02, 0., 0j, .004, state, action)["local_covariance"]))


def test_static_and_large_ray_tree_limits_are_different_ensembles(example):
    state, action = example
    static = M.stationary_soft_source(0j, state, action)
    high = M.stationary_soft_source(1e5j, state, action)
    assert high["tree_chi"] == pytest.approx(static["tree_chi_fixed_charge"], rel=1e-10)
    assert abs(static["tree_chi_static"]-static["tree_chi_fixed_charge"])/static["tree_chi_static"] > .01
    assert static["tree_chi_static"] == pytest.approx(M.CURV.source_jets(state, action)["first"][2], rel=1e-10)


def test_zero_temperature_and_decoupled_source_do_not_create_thermal_response(example):
    state, action = example
    ray = .5j*M.INT.dispersion_coefficients(state, action)["c"]
    assert M.soft_thermal(ray, 0., state, action) == 0
    assert np.max(abs(M.soft_point(.02, .3, ray, 0., state, action)["local_covariance"])) == 0
    modified = action | {"gamma": 0.}
    other = M.EFT.tree_state(state["mu"], action=modified)
    assert M.soft_point(.02, .3, ray, .004, other, modified)["chi"] == 0


def test_phi_coordinate_rescaling_is_not_a_material_calibration(example):
    state, action = example
    modified = M.EFT.rescale_Phi_coordinate(action, 2.)
    other = M.EFT.tree_state(state["mu"], action=modified)
    ray = .5j*M.INT.dispersion_coefficients(state, action)["c"]
    first = M.soft_point(.02, .3, ray, .004, state, action)["chi"]
    second = M.soft_point(.02, .3, ray, .004, other, modified)["chi"]
    assert second == pytest.approx(4*first, rel=1e-8)


def test_constant_vector_centre_is_preserved_across_all_q_levels(example):
    state, action = example
    k, t = .04, .3
    ray = (.6+.4j)*M.INT.dispersion_coefficients(state, action)["c"]
    target = M.extended_soft(k, t, ray, .004, state, action)
    errors = []
    for fraction in M.Q_OVER_P:
        q = k*fraction
        p, cosine = M.pair_from_centre(k, t, q)
        recovered = M.centre(p, cosine, q)
        assert recovered == pytest.approx((k, t), rel=1e-14)
        finite = M.extended_finite(p, cosine, q, ray, .004, state, action)
        errors.append(M.INT.relative(finite["chi"], target["chi"]))
    assert errors[2] < errors[1] < errors[0] and errors[-1] < M.GATES["point_soft_relative"]


def test_full_domain_rule_recovers_known_bose_moment_not_a_padded_cone():
    for split in M.TAILS:
        value = sum(weight*x**3*M.TH.bose(x) for x, weight in M.full_domain_nodes(48, split))
        assert value == pytest.approx(np.pi**4/15, rel=1e-12)


def test_extended_precision_is_an_equivalent_computation_not_an_action_change(example):
    state, action = example
    ray = (.6+.4j)*M.INT.dispersion_coefficients(state, action)["c"]
    low = M.extended_soft(.02, .3, ray, .004, state, action, digits=35)
    high = M.extended_soft(.02, .3, ray, .004, state, action, digits=50)
    original = M.soft_point(.02, .3, ray, .004, state, action)
    assert M.INT.relative(low["chi"], high["chi"]) < 1e-9
    assert M.INT.relative(original["chi"], high["chi"]) < M.GATES["method_relative"]


@pytest.mark.parametrize("p", [.005, .02, 2.])
def test_extended_characteristic_roots_reconstruct_the_same_full_domain_generator(example, p):
    state, action = example
    blocks = M.extended_gaussian_state(p, .004, state, action)
    basis = np.array(blocks["basis"].tolist(), dtype=complex)
    values = np.array([complex(value) for value in blocks["eigenvalues"]])
    kinetic, linear, potential = M.VIRT.matrices(p, state, action)
    direct = np.block([[np.zeros((3, 3)), np.eye(3)], [-np.linalg.solve(kinetic, potential), -np.linalg.solve(kinetic, (1j*linear).real)]])
    assert M.VIRT.matrix_error(direct@basis, basis@np.diag(values)) < 1e-10
    assert np.max(abs(np.linalg.eigvals(direct).real)) < 1e-9


def test_first_failure_and_finite_truncation_error_remain_visible():
    failure = json.loads((ROOT/(PREFIX+"Result/artifacts/t13_collisionless_soft_source_first_failure.json")).read_text())
    record = json.loads(M.OUTPUT.read_text())
    assert failure["verification_status"] == "FAIL_SCOPED_COLLISIONLESS_SOFT_SOURCE"
    assert failure["checks"]["thermal_tail"] is False and failure["checks"]["centred_refinement_improves_covariance_and_chi"] is False
    assert failure["thresholds"] == record["thresholds"]
    assert record["numerical_repair"]["finite_truncated_tail_gate_still_fails"] is True
    assert max(row["truncated_32_40_error_retained"] for row in record["thermal_examples"]) > M.GATES["tail_relative"]
    assert all(row["tail_error"] < M.GATES["tail_relative"] for row in record["thermal_examples"])


@pytest.mark.parametrize("case", ["angle", "negative_q", "real_ray", "negative_T", "moving", "nonzero_h", "angular_pole"])
def test_unadmitted_domains_rejected_not_filtered(example, case):
    state, action = example
    with pytest.raises(ValueError):
        if case == "angle":
            M.soft_point(.02, 1.1, .1j, .004, state, action)
        elif case == "negative_q":
            M.finite_local_covariance(.02, .3, -.001, .1j, .004, state, action)
        elif case == "angular_pole":
            M.angular_transport_moments(1j, 2j)
        else:
            M.soft_thermal(.1 if case == "real_ray" else .1j, -.004 if case == "negative_T" else .004,
                           M.EFT.tree_state(state["mu"], xi=.01 if case == "moving" else 0., h=.001 if case == "nonzero_h" else 0., action=action), action)


def test_artifact_registry_hashes_and_unpromoted_physical_boundaries():
    record = json.loads(M.OUTPUT.read_text())
    assert record["verification_status"] == "PASS_SCOPED_COLLISIONLESS_SOFT_SOURCE"
    assert len(record["point_examples"]) == 54 and len(record["thermal_examples"]) == 16
    assert all(record["checks"].values()) and len(record["report"]) == 11
    assert record["gaussian_collisionless_soft_ray_response_closed"] and record["static_pressure_endpoint_checked_for_prescription"]
    for key in ("full_loop_source_current_Ward_closed", "full_energy_exchange_ledger_closed", "full_collision_operator_computed", "physical_Kubo_emitted", "full_SK_KMS_matching_closed",
                "full_off_shell_source_matching_closed", "full_real_self_energy_matched", "full_two_loop_pressure_computed", "all_parent_modes_and_quantum_Phi_loops_included",
                "independent_alpha_Phi_K_admitted", "controlled_full_action_truncation_error_established", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion",
                "parameter_fitting", "assigned_width", "assigned_relaxation_time", "clipping", "cone_padding", "xie_2026_accessed"):
        assert record[key] is False
    assert record["thresholds"]["original_causal_leakage"] == 1e-6
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert "R_gen" in record["excluded_variables"]
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    registry = json.loads((ROOT/M.REGISTRY).read_text())
    assert all(x["verification_status"] == record["verification_status"] and x["controlling_blocker"] == record["controlling_blocker"] for x in registry["entries"])


def test_audit_runtime_path_allowlist_excludes_numeric_holdout(monkeypatch):
    accessed = []
    read_bytes, read_text = Path.read_bytes, Path.read_text
    def tracked_bytes(path):
        accessed.append(path.resolve())
        return read_bytes(path)
    def tracked_text(path, *args, **kwargs):
        accessed.append(path.resolve())
        return read_text(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_bytes", tracked_bytes)
    monkeypatch.setattr(Path, "read_text", tracked_text)
    record = M.audit()
    allowed = {(ROOT/x["path"]).resolve() for x in record["evidence_artifacts"]+record["protected_evidence_hashes"]}
    assert accessed and set(accessed) <= allowed and all(record["checks"].values())
    assert all("xie" not in x.name.lower() for x in accessed)
