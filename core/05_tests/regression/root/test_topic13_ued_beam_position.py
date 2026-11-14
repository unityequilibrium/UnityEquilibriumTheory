import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_ued_beam_position import position


def test_pixel_axes_and_translation():
    x=np.zeros((512,512));x[240,249]=3
    r=position(x,15)
    assert r['centroid_row_col']==[240.,249.]
    assert r['global_argmax_in_roi'] and r['boundary_intensity_fraction']==0


def test_boundary_and_brightness_are_reported_not_clipped():
    x=np.zeros((512,512));x[227,232]=1;x[0,0]=2
    r=position(x,15)
    assert not r['global_argmax_in_roi']
    assert r['boundary_intensity_fraction']==1


def test_invalid_input_rejected():
    x=np.zeros((512,512))
    with pytest.raises(ValueError): position(x,15)
    x[242,247]=-1
    with pytest.raises(ValueError): position(x,15)
