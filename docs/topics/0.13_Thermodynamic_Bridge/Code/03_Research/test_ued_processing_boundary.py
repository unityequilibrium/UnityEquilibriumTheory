"""Manufactured checks; none is a calibration of experimental image noise."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

_spec = importlib.util.spec_from_file_location(
    "t13_ued_processing_boundary", Path(__file__).with_name("Research_UED_Processing_Boundary.py"))
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
harmonic_gain = _module.harmonic_gain
paired_ratio = _module.paired_ratio
rotation_count = _module.rotation_count


def test_literal_loop_and_dynamic_rejection():
    assert rotation_count("for i in range(5):\n rotation_matrix.append(i)") == 5
    for code in ("for i in range(n):\n rotation_matrix.append(i)",
                 "for i in range(5):\n if i: rotation_matrix.append(i)",
                 "for i in range(5):\n rotation_matrix.append(i)\n break"):
        with pytest.raises(ValueError):
            rotation_count(code)


def test_harmonic_transfer():
    for m in range(1, 6):
        assert abs(harmonic_gain(5, m)) == pytest.approx(.2, abs=1e-14)
        assert abs(harmonic_gain(6, m)) < 1e-14
    for m in (0, 6):
        assert abs(harmonic_gain(5, m)) == pytest.approx(1.)
        assert abs(harmonic_gain(6, m)) == pytest.approx(1.)


def test_cyclic_image_operator_identity():
    values = np.array([1., 3., 5., 9., 2., 7.])
    shifts = np.stack([np.roll(values, i) for i in range(6)])
    np.testing.assert_allclose(shifts[:5].mean(0), (6*shifts.mean(0)-shifts[5])/5)
    assert np.ptp(shifts[:5].mean(0)) > 0
    assert np.ptp(shifts.mean(0)) == 0


def test_paired_ratio_is_off_weighted_not_equal_weighted():
    ratio, weighted, weights, _ = paired_ratio([200., 600.], [200., 300.])
    assert ratio == pytest.approx(1.6)
    assert weighted == pytest.approx(ratio)
    np.testing.assert_allclose(weights, [.4, .6])
    assert ratio != pytest.approx(1.5)


def test_paired_masks_and_no_support_rejection():
    ratio, weighted, weights, mask = paired_ratio(
        [[200., np.nan], [600., 300.], [99., 500.]],
        [[200., 400.], [300., 150.], [600., 99.]])
    np.testing.assert_allclose(ratio, [1.6, 2.])
    np.testing.assert_allclose(weighted, ratio)
    np.testing.assert_allclose(weights.sum(0), 1.)
    assert not mask[2].any()
    with pytest.raises(ValueError, match="no common support"):
        paired_ratio([99., np.nan], [200., 300.])
    with pytest.raises(ValueError):
        paired_ratio([np.inf], [200.])


def test_threshold_boundary_is_not_smooth_response():
    below = paired_ratio([99.999, 600.], [200., 300.])[0]
    above = paired_ratio([100.001, 600.], [200., 300.])[0]
    assert below == 2.
    assert above == pytest.approx(1.400002)
    assert paired_ratio([100., 600.], [200., 300.])[3].all()


def test_covariance_must_preserve_shared_sample_correlations():
    weights = np.ones((1, 5))/5
    independent = weights @ np.eye(5) @ weights.T
    shared = weights @ np.ones((5, 5)) @ weights.T
    assert independent.item() == pytest.approx(.2)
    assert shared.item() == pytest.approx(1.)


def test_source_drift_rejected_before_parsing(tmp_path):
    source = tmp_path / "changed.ipynb"
    source.write_text('{"cells": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="pinned notebook drift"):
        _module.inspect_notebook(source)
