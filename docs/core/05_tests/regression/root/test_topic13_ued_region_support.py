import numpy as np
import pytest

from docs.scripts.audit.audit_topic13_ued_region_support import region_mask


def test_geometry_uses_row_column_order():
    mask = region_mask((100, 100), [20, 40], .1, 30)
    assert mask[50, 40]
    assert not mask[40, 50]
    assert not mask[50, 45]
    assert mask.sum() == 45


def test_origin_translation_preserves_region():
    a = region_mask((100, 100), [20, 40], .1, 30)
    b = region_mask((100, 100), [23, 42], .1, 30)
    np.testing.assert_array_equal(np.roll(a, (3, 2), axis=(0, 1)), b)


def test_invalid_calibration_rejected():
    with pytest.raises(ValueError):
        region_mask((10, 10), [5, 5], 0, 2)
