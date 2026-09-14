import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_ued_voigt_position import profile,fit_roi


def test_known_synthetic_position_and_scale():
    y,x=np.indices((30,30),dtype=float);y+=227;x+=232
    p=[50.,241.2,246.7,1.3,1.1,.7,.9,.02]
    roi=profile(p,y,x)
    for start in ('source','peak'):
        f=fit_roi(roi*123,start=start)
        assert f['success']
        np.testing.assert_allclose(f['centroid_row_col'],p[1:3],atol=1e-5)
        assert f['relative_residual_l2']<1e-6


def test_invalid_input_or_start_rejected():
    with pytest.raises(ValueError): fit_roi(np.zeros((30,30)))
    with pytest.raises(ValueError): fit_roi(np.ones((30,30)),start='unknown')
