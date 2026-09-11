import numpy as np
from docs.scripts.audit.audit_topic13_interpolation_support import shell_defects,_interpolation_matrix


def test_positive_off_grid_mixture_cannot_match_both_energy_and_momentum():
    p=np.array([[-1.,0.,0.],[1.,0.,0.]])
    result=shell_defects(np.array([[.5],[.5]]),p,np.full(2,np.sqrt(2)),[[0.,0.,0.]],[1.],1.)
    assert result["max_momentum_over_energy_error"]==0
    assert abs(result["minimum_jensen_gap"]-(np.sqrt(2)-1))<1e-14
    assert result["max_energy_relative_error"]>.4


def test_single_matching_node_has_no_jensen_defect():
    result=shell_defects(np.eye(2),[[0.,0.,0.],[1.,0.,0.]],[1.,np.sqrt(2)],
                         [[0.,0.,0.],[1.,0.,0.]],[1.,np.sqrt(2)],1.)
    assert result["maximum_jensen_gap"]==0


def test_requested_support_saturation_is_measured_not_hidden():
    p=((0.,0.,0.),(1.,0.,0.)); e=(1.,np.sqrt(2))
    s=_interpolation_matrix((1.,),((.5,0.,0.),),(np.sqrt(1.25),),(1.,1.),p,e,cutoff=2.,support_order=64)
    assert np.count_nonzero(s)==2
    np.testing.assert_allclose(s.sum(axis=0),1.)
