import numpy as np
from docs.scripts.audit.audit_topic13_ued_rotated_position import rotated_profile,fit_rotated
from docs.scripts.audit.audit_topic13_ued_voigt_position import profile,PARAMETERS


def test_rotation_contains_unrotated_form():
    y,x=np.indices((30,30),dtype=float);y+=227;x+=232
    p=[50,241.2,246.7,1.3,1.1,.7,.9,.02]
    np.testing.assert_allclose(rotated_profile(p+[np.pi],y,x),profile(p,y,x),rtol=1e-13)


def test_rotated_synthetic_center_recovered():
    y,x=np.indices((30,30),dtype=float);y+=227;x+=232
    p=[50,241.2,246.7,1.9,.7,.5,.3,.02]
    roi=rotated_profile(p+[np.pi+.3],y,x)
    scale=roi.max();base=dict(zip(PARAMETERS,p));base['amplitude']/=scale;base['offset']/=scale
    f=fit_rotated(roi,base)
    assert f['success'] and f['relative_residual_l2']<1e-6
    np.testing.assert_allclose(f['center_row_col'],p[1:3],atol=1e-5)
