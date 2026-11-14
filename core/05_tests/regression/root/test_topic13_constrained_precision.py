import mpmath as mp
import numpy as np
from docs.scripts.audit.audit_topic13_constrained_precision import constrained_response


def test_high_stiffness_retains_small_response():
    t=1e64
    result=constrained_response(np.ones(3),[1.,2.,3.],[[1.,1.,0.]],[t],[[0.],[0.],[1.]],[1.,-1.,0.],100)
    with mp.workdps(90):
        exact=(3+4*mp.mpf(t))/(2+3*mp.mpf(t))
        assert abs(mp.mpf(result["response"])-exact)<mp.mpf("1e-34")
        assert mp.mpf(result["balance_relative"])<mp.mpf("1e-30")


def test_constraints_remove_source_component_without_fit():
    result=constrained_response([1.,1.],[2.,3.],[[0.,0.]],[0.],[[1.],[0.]],[7.,2.],80)
    assert abs(float(result["response"])-4/3)<1e-14
    assert float(result["constraint_max"])<1e-40
