import numpy as np
from docs.scripts.audit.audit_topic13_patch_position_sensitivity import patch_curve


def test_constant_ratio_and_baseline():
    off=np.ones((3,9,9));on=off*np.array([1.,1.,1.2])[:,None,None]
    r=patch_curve(on,off,[4.2,4.1],np.array([True,True,False]))
    np.testing.assert_allclose(r['baseline_subtracted'],[0,0,.2],atol=1e-15)
    assert r['pixels']==9


def test_invalid_patch_is_not_repaired():
    off=np.ones((3,9,9));on=off.copy();on[1,4,4]=np.nan
    assert patch_curve(on,off,[4,4],[True,False,False])['status']=='NONFINITE_PATCH'
    assert patch_curve(off,off,[-3,4],[True,False,False])['status']=='OUTSIDE'
    assert patch_curve(off,off*0,[4,4],[True,False,False])['status']=='NONPOSITIVE_DENOMINATOR'
