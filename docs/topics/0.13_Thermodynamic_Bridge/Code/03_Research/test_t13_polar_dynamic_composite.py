"""Independent checks and physical-admission boundaries for dynamic IR work."""

import hashlib
import json
from math import pi
from pathlib import Path
import runpy

import numpy as np
import pytest

M = runpy.run_path(str(Path(__file__).with_name("Research_T13_Polar_Dynamic_Composite.py")))
ARGS = (.0025, .22, .1085, .1085, .21656093467342244)


def test_classical_static_returns_preceding_cartesian_composite():
    q, t, x, stiffness, c = ARGS
    assert M["classical_response"](q, 0j, t, x, stiffness, c) == pytest.approx(x*t/(16*stiffness**2*q))
    expected = M["POLAR"]["static_response"](q, t, 1.05, x, 1., 1.)["cartesian_longitudinal_composite_susceptibility"]
    assert M["classical_response"](q, 0j, t, x, stiffness, c).real == pytest.approx(expected)


def test_pair_scattering_momentum_integral_is_independent_of_closed_log():
    q, t, x, stiffness, c = ARGS
    for ratio in (0j, .3+.4j, 1.4+.6j, .8j, -.3+.4j):
        z = ratio*c*q
        direct = M["classical_loop_integral"](q, z, t, x, stiffness, c)
        closed = M["classical_response"](q, z, t, x, stiffness, c)
        assert direct == pytest.approx(closed, rel=1e-8)


def test_point_spectral_sum_matches_actual_matsubara_frequency_sum():
    for e, f in ((.029, .041), (.07, .07), (.13, .07)):
        for harmonic in (0, 1):
            result = M["point_matsubara_check"](e, f, .22, harmonic, 256)
            assert result["relative_disagreement"] < 1e-7


def test_coincident_static_scattering_is_not_silently_dropped():
    e, t = .07, .22
    ne = M["bose"](e, t)
    expected = ne/(2*e**3)+ne*(1+ne)/(2*t*e*e)
    assert M["point_thermal_bubble"](e, e, t) == pytest.approx(expected)
    assert M["point_thermal_bubble"](e, e+1e-12, t) == pytest.approx(expected, rel=1e-9)
    assert M["point_thermal_bubble"](e, e, 0.) == 0.


def test_real_axis_pair_and_landau_channels_match_phase_space():
    q, t, x, stiffness, c = ARGS
    channels = []
    for ratio in (.4, 1.6):
        result = M["spectral_phase_space_check"](q, ratio*c*q, t, x, stiffness, c)
        assert result["relative_disagreement"] < 1e-9
        assert result["direct_phase_space"] > 0
        channels.append(result["channel"])
    assert channels == ["THERMAL_SCATTERING", "PAIR_CREATION"]


def test_threshold_divergence_is_not_replaced_by_width_or_clipping():
    q, t, x, stiffness, c = ARGS
    with pytest.raises(ValueError, match="singular"):
        M["spectral_response"](q, c*q, t, x, stiffness, c)
    values = [M["spectral_response"](q, (1+epsilon)*c*q, t, x, stiffness, c) for epsilon in (.1, .01, .001)]
    assert values[0] < values[1] < values[2]


def test_quantum_thermal_static_and_dynamic_tend_to_classical_ir():
    _, t, x, stiffness, c = ARGS
    errors = []
    for q in M["Q_REFINEMENT"]:
        z = (.3+.4j)*c*q
        quantum = M["thermal_dispersion"](q, z, t, x, stiffness, c)
        classical = M["classical_response"](q, z, t, x, stiffness, c)
        errors.append(abs(quantum/classical-1))
    assert errors[2] < errors[1] < errors[0]
    assert errors[-1] < .01


def test_retarded_analytic_conjugation_and_time_transform():
    q, t, x, stiffness, c = ARGS
    z = (.3+.4j)*c*q
    value = M["classical_response"](q, z, t, x, stiffness, c)
    assert M["classical_response"](q, -z.conjugate(), t, x, stiffness, c) == pytest.approx(value.conjugate())
    assert M["time_transform_check"](q, z, t, x, stiffness, c)["relative_disagreement"] < 1e-8
    assert M["classical_time_response"](-1., q, t, x, stiffness, c) == 0
    assert M["classical_time_response"](0., q, t, x, stiffness, c) == pytest.approx(x*t*c/(8*pi*stiffness**2))
    assert M["classical_time_response"](4/(c*q), q, t, x, stiffness, c) < 0


def test_two_frequency_protocols_are_not_a_single_static_relaxation_pole():
    q, t, x, stiffness, c = ARGS
    chi0 = M["classical_response"](q, 0j, t, x, stiffness, c).real
    times = []
    for ratio in (.2, 1.):
        omega = ratio*c*q
        value = M["classical_response"](q, 1j*omega, t, x, stiffness, c).real
        times.append((chi0/value-1)/omega)
    assert abs(times[0]/times[1]-1) > .1


def test_gaussian_source_contact_is_required_for_current_ward_identity():
    result = M["source_current_check"](.13, [.1, -.04, .02], .1085, .21656)
    assert result["source_Hessian_residual"] < 1e-10
    assert result["Ward_residual"] < 1e-10
    assert result["without_contact_Ward_residual"] > .1
    kernel = M["phase_current_kernel"](.13, [.1, -.04, .02], .1085, .21656)
    np.testing.assert_allclose(kernel, kernel.T, atol=1e-14)
    assert np.linalg.eigvalsh(kernel).min() > -1e-14


def test_full_gaussian_fdt_not_thermal_difference_is_checked():
    for pair in (True, False):
        result = M["detailed_balance_check"](.13, .07, .22, pair)
        assert result["detailed_balance_residual"] < 1e-12
        assert result["FDT_relative_residual"] < 1e-12
        assert result["positive_commutator"]


def test_zero_temperature_thermal_part_vanishes_but_vacuum_continuum_does_not():
    q, _, x, stiffness, c = ARGS
    assert M["spectral_response"](q, 1.6*c*q, 0., x, stiffness, c) == 0
    assert M["spectral_response"](q, .4*c*q, 0., x, stiffness, c, False) == 0
    assert M["spectral_response"](q, 1.6*c*q, 0., x, stiffness, c, False) == pytest.approx(x*c/(32*pi*stiffness**2))
    assert M["classical_response"](q, .8j*c*q, 0., x, stiffness, c) == 0j


def test_energy_and_time_units_scale_without_si_calibration():
    q, t, x, stiffness, c = ARGS
    scale = 2.3
    z, time = (.3+.4j)*c*q, 2/(c*q)
    original = M["classical_response"](q, z, t, x, stiffness, c)
    scaled = M["classical_response"](q*scale, z*scale, t*scale, x*scale**2, stiffness*scale**2, c)
    assert scaled == pytest.approx(original/scale**2)
    original_time = M["classical_time_response"](time, q, t, x, stiffness, c)
    scaled_time = M["classical_time_response"](time/scale, q*scale, t*scale, x*scale**2, stiffness*scale**2, c)
    assert scaled_time == pytest.approx(original_time/scale)
    kernel = M["phase_current_kernel"](.13, [.1, -.04, .02], stiffness, c)
    scaled_kernel = M["phase_current_kernel"](.13*scale, np.array([.1, -.04, .02])*scale, stiffness*scale**2, c)
    np.testing.assert_allclose(scaled_kernel, kernel*scale**2, atol=1e-13)


def test_artifact_preserves_physical_and_background_blockers():
    record = json.loads(M["OUTPUT"].read_text(encoding="utf-8"))
    assert all(record["checks"].values())
    assert record["closure_level"] == "CLOSED_FOR_LANE"
    assert record["full_Cartesian_response_assembled"] is False
    assert record["amplitude_phase_hybrid_response_included"] is False
    for field in ("microscopic_real_axis_response_admitted", "joint_Phi_stationarity_derived", "renormalized_order_parameter_matched", "microscopic_IR_resummation_derived", "controlled_truncation_error_established", "microscopic_SK_KMS_matched", "physical_Kubo_emitted", "g1_physical_unlock", "g2_science_unlock", "full_core_unlock", "core_composition_gate_overwritten", "claim_promotion", "parameter_fitting", "xie_2026_accessed", "phase_mass_added", "IR_filter", "clipping", "threshold_broadening", "C_relabelled_as_charge_or_mass", "R_gen_added_as_state"):
        assert record[field] is False
    for item in record["evidence_artifacts"]+record["protected_evidence_hashes"]:
        assert hashlib.sha256((M["ROOT"]/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    assert record["examples"][0]["T_over_linear_phase_energy_domain"] > 1
    assert set(record["report"]) == {"MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY"}


def test_invalid_inputs_do_not_trigger_silent_repairs():
    q, t, x, stiffness, c = ARGS
    for values in ((0., t, x, stiffness, c), (q, -t, x, stiffness, c), (q, t, x, -stiffness, c), (q, t, x, stiffness, 1.1)):
        with pytest.raises(ValueError):
            M["classical_response"](values[0], 0j, *values[1:])
    for z in (.1, -.1j, complex("nan")):
        with pytest.raises(ValueError):
            M["classical_response"](q, z, t, x, stiffness, c)
    with pytest.raises(ValueError):
        M["phase_current_kernel"](0., [0., 0., 0.], stiffness, c)


def test_audit_path_reads_only_declared_code_and_artifact_inputs(monkeypatch):
    accessed = []
    original_text, original_bytes = Path.read_text, Path.read_bytes
    def track(path):
        resolved = path.resolve()
        relative = resolved.relative_to(M["ROOT"]).as_posix()
        assert "/Data/" not in relative
        assert "xie" not in relative.lower()
        assert "/Code/" in relative or "/artifacts/" in relative or "/07_artifacts/" in relative
        accessed.append(relative)
    def read_text(path, *args, **kwargs):
        track(path)
        return original_text(path, *args, **kwargs)
    def read_bytes(path, *args, **kwargs):
        track(path)
        return original_bytes(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", read_text)
    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    record = M["audit"]()
    declared = {v["path"] for v in record["evidence_artifacts"]+record["protected_evidence_hashes"]}
    assert set(accessed) == declared
    assert record["xie_2026_accessed"] is False
