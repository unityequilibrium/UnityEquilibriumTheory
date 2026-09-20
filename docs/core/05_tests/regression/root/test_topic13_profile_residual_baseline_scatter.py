import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_profile_residual_baseline_scatter import compare_residual


def test_centered_scatter_and_fixed_bias():
    model=np.ones((2,2));frames=np.array([model-.1,model+.1])
    r=compare_residual(frames,model)
    assert r['relative_mean_profile_residual']==0
    assert r['relative_observed_frame_scatter']==pytest.approx(np.sqrt(.02))
    shifted=compare_residual(frames,model-.2)
    assert shifted['relative_mean_profile_residual']==pytest.approx(.2)


def test_zero_scatter_not_invented_and_invalid_frames():
    frames=np.ones((2,2,2))
    assert compare_residual(frames,np.zeros((2,2)))['residual_to_frame_scatter'] is None
    with pytest.raises(ValueError):compare_residual(frames[:1],np.ones((2,2)))
