import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_ued_cut_signal import compare


def test_identical_cuts_have_no_difference():
    r=compare([[2,3],[2,3]],[[2,2],[2,2]],[-1,1])
    assert r['max_abs_cut_difference']==0
    np.testing.assert_allclose(r['pooled_baseline_subtracted_ratio'],[0,.5])


def test_pooling_is_denominator_weighted_not_average_ratio():
    r=compare([[1,2],[3,3]],[[1,1],[3,3]],[-1,1])
    np.testing.assert_allclose(r['pooled_baseline_subtracted_ratio'],[0,.25])
    assert r['max_abs_pooled_vs_unweighted_ratio']==.25


def test_invalid_support_or_time_rejected():
    for off,delay in [([[0,1],[1,1]],[-1,1]),([[1,1],[1,1]],[0,1]),([[1,1],[1,1]],[1,-1])]:
        with pytest.raises(ValueError): compare([[1,2],[1,2]],off,delay)
