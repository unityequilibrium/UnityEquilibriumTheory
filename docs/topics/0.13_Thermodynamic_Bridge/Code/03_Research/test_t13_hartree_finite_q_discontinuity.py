"""Independent finite-q shell, cut, continuation and non-promotion checks."""

import ast
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
import pytest

D = runpy.run_path(str(Path(__file__).with_name("Research_T13_Hartree_Finite_Q_Discontinuity.py")))


def artifact():
    return json.loads(D["OUTPUT"].read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def example():
    return artifact()["examples"][0]


def test_complex_inverse_shell_recovers_original_real_dispersion(example):
    for k in (.01, .2, 1., 10.):
        poles, residues, _ = D["P"]["complex_poles"](k, example["mu"], example["a"], example["b"])
        for mode in range(4):
            rsq, derivative, residue = D["complex_inverse_shell"](poles[0, mode], mode, example)
            original = D["R"]["inverse_shell"](poles[0, mode].real, mode, example["mu"], example["a"], example["b"])
            assert rsq == pytest.approx(k*k, abs=2e-12)
            assert derivative == pytest.approx(original[1], abs=2e-12)
            assert residue == pytest.approx(residues[0, mode], abs=1e-11)


def test_complex_shell_uses_analytic_derivative_not_absolute_value(example):
    ell, h = .06-.0002j, 1e-7
    rsq, derivative, _ = D["complex_inverse_shell"](ell, 2, example)
    plus = D["complex_inverse_shell"](ell+h, 2, example)[0]
    minus = D["complex_inverse_shell"](ell-h, 2, example)[0]
    assert derivative == pytest.approx((plus-minus)/(2*h), abs=1e-8)
    assert derivative.imag != 0
    assert rsq.imag != 0


def test_signed_bose_occupation_recovers_original_real_convention(example):
    poles = D["P"]["complex_poles"](.4, example["mu"], example["a"], example["b"])[0][0]
    for mode, energy in enumerate(poles):
        assert D["signed_occupation"](energy, mode, example["T"]) == pytest.approx(D["G"]["occupations"](energy.real, example["T"]), abs=1e-12)


def test_exact_positive_and_negative_thresholds_are_shifted_same_shell(example):
    q, v = .04, .25-.007j
    for positive, negative in ((2, 1), (3, 0)):
        kp, rp = D["threshold_root"](q, v, example, positive)
        km, rm = D["threshold_root"](q, v, example, negative)
        assert max(rp, rm) < 1e-11
        assert km-kp == pytest.approx(q, abs=1e-11)
        energy = D["P"]["complex_poles"]([kp, kp+q], example["mu"], example["a"], example["b"])[0][:, positive]
        assert energy[1]-energy[0] == pytest.approx(q*v, abs=1e-11)


def test_threshold_is_not_only_soft_root_minus_half_q(example):
    q, v = .04, .25-.007j
    finite, _ = D["threshold_root"](q, v, example, 2)
    soft, _ = D["P"]["velocity_root"](v, example, 2)
    assert abs(finite-(soft-q/2)) > 1e-5


def test_same_shell_density_matches_original_real_shell_numerator(example):
    q, v, k = .04, .3, .6
    poles, residues, _ = D["P"]["complex_poles"](k, example["mu"], example["a"], example["b"])
    for mode in range(4):
        actual, transverse, ell, _ = D["on_shell_density"](k, q, v, example, mode)
        original, tr_original = D["R"]["shell_coefficient"](np.array([k]), q, poles[0, mode].real, residues[:, mode], ell.real,
                                                            mode, q*v, example["T"], example["mu"], example["a"], example["b"])
        assert actual == pytest.approx(original, abs=1e-10)
        assert transverse == pytest.approx(tr_original, abs=1e-10)


def test_forward_angular_delta_roots_check_all_channels_not_only_same_shell(example):
    rows = D["independent_forward_shell_check"](.04, .3, example)
    assert any(row["forward_shell_checks"]["active_shell_count"] > 0 for row in rows)
    for row in rows:
        assert row["same_signed_active_shell_count"] == row["forward_shell_checks"]["active_shell_count"]
        assert max(row["joint_cut_error"], row["transverse_cut_error"], row["pair_cut_max"]) < D["CUT_TOLERANCE"]


def test_independent_full_radial_cut_matches_at_every_preregistered_point():
    for e in artifact()["examples"]:
        rows = e["original_finite_q_cut_checks"]
        assert len(rows) == len(D["Q_GRID"])*len(D["REAL_RAYS"])
        for row in rows:
            assert [r["original_full_radial_order"] for r in row["runs"]] == list(D["ORIGINAL_ORDERS"])
            assert max(row["runs"][-1]["finite_q_cut_errors"].values()) < D["CUT_TOLERANCE"]
            assert row["runs"][-1]["original_all_pair_cut_max"] == 0


def test_two_complex_tail_paths_agree_and_orders_converge(example):
    v, q = .25-.007j, .04
    horizontal, _ = D["spectral_tail"](q, v, example, 96)
    returned, _ = D["spectral_tail"](q, v, example, 96, "return_to_real")
    refined, _ = D["spectral_tail"](q, v, example, 128)
    assert max(D["errors"](horizontal, returned).values()) < D["TAIL_TOLERANCE"]
    assert max(D["errors"](horizontal, refined).values()) < D["TAIL_TOLERANCE"]


def test_finite_q_density_converges_to_soft_but_is_not_equal_to_it():
    for e in artifact()["examples"]:
        rows = e["complex_density_runs"]
        assert [row["q"] for row in rows] == list(D["Q_GRID"])
        assert max(rows[0]["difference_from_soft_density"].values()) > 1e-5
        for key in ("bubble", "mixed", "reverse", "loop_current"):
            errors = [r["difference_from_soft_density"][key] for r in rows]
            assert errors[2] < errors[1] < errors[0]


def test_complex_threshold_and_bose_domain_are_reported_not_global_proof():
    for e in artifact()["examples"]:
        for row in e["complex_density_runs"]:
            assert len(row["local_domain_checks"]) == 4
            for check in row["local_domain_checks"]:
                assert check["threshold_above_q_half"]
                assert check["shell_root_residual"] < 1e-11
                assert check["minimum_outgoing_energy_real"] > 0
                assert check["minimum_Bose_denominator"] > .01
    assert artifact()["certified_global_contour_homotopy"] is False
    assert artifact()["certified_global_cut_support"] is False


def test_natural_unit_scaling_with_q_and_same_velocity(example):
    factor, q, v = .77, .03, .3-.006j
    scaled = example | {"T": factor*example["T"], "mu": factor*example["mu"], "a": factor**2*example["a"],
                        "b": factor**2*example["b"], "s": factor**2*example["s"]}
    base, _ = D["spectral_tail"](q, v, example, 128)
    other, _ = D["spectral_tail"](factor*q, v, scaled, 128)
    for key, power in (("bubble", 0), ("mixed", 1), ("reverse", 1), ("loop_current", 2)):
        assert other[key] == pytest.approx(base[key]*factor**power, abs=1e-9)


def test_invalid_local_domain_and_pair_overlap_are_refused(example):
    for q, v in ((0., .3), (-.01, .3), (.05, .3), (.04, .1), (.04, .5), (.04, .3+.001j), (.04, .3-.02j), (np.nan, .3)):
        with pytest.raises(ValueError):
            D["spectral_tail"](q, v, example)
    for changed in ({"T": 0.}, {"b": 0.}, {"mu": 0.}, {"a": 1e-12, "b": 1e-12}):
        with pytest.raises(ValueError):
            D["spectral_tail"](.04, .3, example | changed)
    for order in (True, 16):
        with pytest.raises(ValueError):
            D["spectral_tail"](.04, .3, example, order)
    with pytest.raises(ValueError):
        D["spectral_tail"](.04, .3, example, contour="unknown")
    with pytest.raises(ValueError):
        D["threshold_root"](.04, .3, example, 4)


def test_artifact_is_discontinuity_not_claimed_finite_q_pole_or_physical_closure():
    record = artifact()
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["verification_status"] == "PASS_SCOPED_FINITE_Q_DISCONTINUITY"
    assert all(record["checks"].values())
    assert record["finite_q_discontinuity_computed"] is True
    assert len(record["report"]) == 11
    assert record["config"]["assigned_output_width"] is None
    assert record["thresholds"]["causal_leakage_unchanged"] == 1e-6
    for flag in ("finite_q_complex_pole_computed", "physical_mode_speed_emitted", "collision_rate_emitted", "controlled_truncation_error_established",
                 "joint_Phi_stationarity_derived", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "claim_promotion", "parameter_fitting",
                 "artificial_width", "clipping", "IR_filter", "imposed_Ward_projection", "xie_2026_accessed", "core_composition_gate_overwritten",
                 "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[flag] is False
    assert record["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    assert "R_gen" in record["excluded_variables"]


def test_evidence_hashes_preserve_predecessor_and_protected_core():
    record = artifact()
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((D["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    predecessor = json.loads((D["ROOT"]/D["PREVIOUS_ARTIFACT"]).read_text(encoding="utf-8"))
    assert D["R"]["predecessor_hashes_match"](predecessor)
    predecessor["evidence_artifacts"][0]["sha256"] = "0"*64
    assert not D["R"]["predecessor_hashes_match"](predecessor)


def test_audit_reads_only_derived_predecessor_and_never_calls_original_with_lower_z():
    code = Path(__file__).with_name("Research_T13_Hartree_Finite_Q_Discontinuity.py").read_text(encoding="utf-8")
    reads = [node for node in ast.walk(ast.parse(code)) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "read_text"]
    assert len(reads) == 1
    assert ast.unparse(reads[0].func.value) == "ROOT / PREVIOUS_ARTIFACT"
    assert D["PREVIOUS_ARTIFACT"].endswith("/t13_hartree_soft_poles.json")
    with pytest.raises(ValueError):
        D["R"]["validate"](.04, .01-.001j, .22, 1.05, .1, .1)
