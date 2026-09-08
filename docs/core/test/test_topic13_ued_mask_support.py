import io
import pickle

import numpy as np
import pytest

from docs.scripts.audit.ued_pickle_static import read_inert
from docs.scripts.audit.audit_topic13_ued_mask_support import support_signals


def test_changing_mask_can_create_false_signal():
    on = np.array([[[2., 1.]], [[2., np.nan]]])
    off = np.array([[[1., 1.]], [[1., np.nan]]])
    common, masks, result = support_signals(on, off, [True, False])
    assert result['dynamic_baseline_subtracted'] == [0., .5]
    assert result['common_baseline_subtracted'] == [0., 0.]
    assert result['support_choice_max_difference'] == .5
    assert common.sum() == 1 and masks.sum() == 3
    assert np.isnan(on[1, 0, 1])


def test_sink_preserves_array_and_default_summary():
    array = np.array([[1., np.nan], [3., 4.]])
    stream = pickle.dumps(array, protocol=5)
    captured = []
    def sink(a, record):
        assert not a.flags.writeable
        captured.append(a.copy())
    with_sink, _ = read_inert(io.BytesIO(stream), numeric_sink=sink)
    without, _ = read_inert(io.BytesIO(stream))
    assert {k: v for k, v in with_sink.args.items() if k != 'values'} == {
        k: v for k, v in without.args.items() if k != 'values'}
    np.testing.assert_array_equal(with_sink.args['values'], without.args['values'])
    np.testing.assert_array_equal(captured[0], array)


def test_empty_intersection_fails_not_zero_filled():
    images = np.array([[[1., np.nan]], [[np.nan, 1.]]])
    with pytest.raises(ValueError):
        support_signals(images, images, [True, False])
