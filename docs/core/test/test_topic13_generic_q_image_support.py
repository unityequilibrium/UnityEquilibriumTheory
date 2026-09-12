import numpy as np
from docs.scripts.audit.audit_topic13_generic_q_image_support import footprint


def test_center_footprint_and_no_wrap():
    mask=footprint((7,7),(3.,3.))
    assert mask.sum()==9
    assert footprint((7,7),(-10.,3.)).sum()==0
    assert footprint((7,7),(0.,0.)).sum()==4


def test_mirror_preserves_centered_support():
    a=footprint((9,9),(4.2,2.3));b=footprint((9,9),(4.2,5.7))
    np.testing.assert_array_equal(a[:,::-1],b)
