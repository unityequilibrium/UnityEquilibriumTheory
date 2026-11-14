"""Independent Noether, omitted-contact and protected-input checks."""

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

LOCAL = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("thermal_noether", LOCAL/"Research_T13_Thermal_Noether_Response.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
ROOT, PREFIX = M.ROOT, M.PREFIX


@pytest.fixture(params=M.MU_GRID)
def example(request):
    action = M.EFT.controls()
    return M.EFT.tree_state(request.param, action=action), action


@pytest.mark.parametrize("momenta", M.MOMENTUM_TRIPLES)
def test_source_response_conserves_total_not_separate_fluctuation_charge(example, momenta):
    state, action = example
    for temperature in M.TEMPERATURES:
        for z in M.FREQUENCIES:
            record = M.source_balance(*momenta, z, temperature, state, action)
            for name in ("fluctuation_ward_error", "total_charge_ward_error", "rotating_energy_ward_error", "physical_energy_ward_error", "phase_contact_identity_error"):
                assert record[name] < M.GATES["ward_relative"]
            assert record["source_force_method_error"] < M.GATES["method_relative"]
            assert record["contact_method_error"] < M.GATES["method_relative"]


def test_moment_operator_follows_direct_unforced_euler_equations_for_arbitrary_covariance(example):
    state, action = example
    p, r, q = .02, .031, .02
    ap = M.FQ.evolution_and_covariance(p, .004, state, action)[0]
    ar = M.FQ.evolution_and_covariance(r, .004, state, action)[0]
    rng = np.random.default_rng(1927)
    response = rng.normal(size=(6, 6))+1j*rng.normal(size=(6, 6))
    derivative = ar@response+response@ap.T
    values = M.moments(response, p, r, q, state, action)
    derivatives = M.moments(derivative, p, r, q, state, action)
    phase_force = .5*np.einsum("ab,ab", M.MOD.cubic_tensor(state, action)[1], response[:3, :3])
    assert derivatives["density"]+1j*q*values["current"] == pytest.approx(np.sqrt(state["s"])*phase_force, rel=1e-12, abs=1e-12)
    assert abs(derivatives["rotating_energy"]+1j*q*values["rotating_flux"]) < 1e-12


def test_covariance_drive_has_no_first_order_rotating_energy_work(example):
    state, action = example
    drive = np.array([.3+.2j, -.7+.1j, .11-.13j])
    response, covariance, rhs = M.covariance_response(.02, .031, .03+.02j, .004, drive, state, action)
    assert abs(M.moments(rhs, .02, .031, .02, state, action)["rotating_energy"]) < 1e-12
    assert np.max(abs(covariance[:3, 3:]+covariance[:3, 3:].T)) < 1e-12
    assert np.all(np.isfinite(response))


def test_omitting_stationary_background_contact_is_detected(example):
    state, action = example
    record = M.source_balance(.02, .031, .02, .03+.02j, .004, state, action)
    assert record["total_charge_ward_error"] < 1e-9
    assert record["omitted_background_shift_ward_error"] > M.GATES["negative_control_minimum"]


def test_mean_and_covariance_energy_contacts_cancel_from_stationary_equation(example):
    state, action = example
    record = M.source_balance(.02, .031, .02, .03+.02j, .004, state, action)
    assert record["mean_energy_contact"] == pytest.approx(-record["explicit_energy_contact"], rel=1e-12, abs=1e-12)
    assert record["energy_contact_cancellation_error"] < 1e-9


def test_zero_temperature_has_no_thermal_response_or_assigned_rate(example):
    state, action = example
    record = M.source_balance(.02, .031, .02, .03+.02j, 0., state, action)
    assert all(record[key] == 0 for key in ("total_density", "total_current", "physical_energy", "physical_flux"))
    assert all(value == 0 for value in record["values"].values())


def test_decoupled_phi_source_does_not_create_matter_charge(example):
    state, action = example
    modified = action | {"gamma": 0.}
    other = M.EFT.tree_state(state["mu"], action=modified)
    record = M.source_balance(.02, .031, .02, .03+.02j, .004, other, modified)
    assert all(record[key] == 0 for key in ("total_density", "total_current", "physical_energy", "physical_flux"))


def test_phi_coordinate_rescaling_preserves_noether_contract(example):
    state, action = example
    modified = M.EFT.rescale_Phi_coordinate(action, 2.)
    other = M.EFT.tree_state(state["mu"], action=modified)
    first = M.source_balance(.02, .031, .02, .03+.02j, .004, state, action)
    second = M.source_balance(.02, .031, .02, .03+.02j, .004, other, modified)
    for key in ("total_density", "total_current", "physical_energy", "physical_flux"):
        assert second[key] == pytest.approx(2*first[key], rel=1e-8, abs=1e-12)
    assert second["total_charge_ward_error"] < 1e-9


@pytest.mark.parametrize("case", ["triangle", "q0_mismatch", "negative_T", "real_frequency", "moving", "nonzero_h"])
def test_unadmitted_inputs_rejected_not_repaired(example, case):
    state, action = example
    with pytest.raises(ValueError):
        if case == "triangle":
            M.source_balance(.02, .031, .001, .03+.02j, .004, state, action)
        elif case == "q0_mismatch":
            M.source_balance(.02, .031, 0., .03+.02j, .004, state, action)
        elif case == "nonzero_h":
            M.source_balance(.02, .031, .02, .03+.02j, .004, M.EFT.tree_state(state["mu"], h=.001, action=action), action)
        else:
            M.source_balance(.02, .031, .02, .02 if case == "real_frequency" else .03+.02j,
                             -.001 if case == "negative_T" else .004,
                             M.EFT.tree_state(state["mu"], xi=.01, action=action) if case == "moving" else state, action)


def test_artifact_and_registry_preserve_full_thermodynamic_and_holdout_boundaries():
    record = json.loads(M.OUTPUT.read_text())
    assert record["verification_status"] == "PASS_SCOPED_GAUSSIAN_NOETHER_RESPONSE"
    assert all(record["checks"].values()) and len(record["report"]) == 11
    assert record["gaussian_pair_local_charge_Ward_closed"] and record["first_order_Gaussian_energy_balance_closed"]
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
