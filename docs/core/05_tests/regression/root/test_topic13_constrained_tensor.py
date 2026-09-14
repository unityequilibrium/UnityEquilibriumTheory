import mpmath as mp
import numpy as np
from docs.scripts.audit.audit_topic13_constrained_tensor import multi_solve,tensor_response


def test_multi_rhs_matches_independent_lu_solves_with_pivot():
    with mp.workdps(70):
        a=mp.matrix([[0,2,1],[3,1,4],[2,5,1]])
        b=mp.matrix([[1,2,3],[4,6,1],[3,0,2]])
        x=multi_solve(a,b)
        for axis in range(3):
            assert max(abs(v) for v in x[:,axis]-mp.lu_solve(a,b[:,axis]))<mp.mpf("1e-65")


def test_cross_response_and_dissipation_match_known_constrained_matrix():
    g=np.array([[1.,0.,2.],[0.,1.,3.],[0.,0.,0.]])
    result=tensor_response([1.,1.,1.],[2.,3.,4.],[[1.,1.,0.]],[1.],[[0.],[0.],[1.]],g,80)
    expected=g[:2].T@np.linalg.inv([[3.,1.],[1.,4.]])@g[:2]
    np.testing.assert_allclose(np.array(result["response"],float),expected,atol=1e-14)
    assert abs(expected[0,1])>.01
    assert float(result["reciprocity_relative"])<1e-60
    assert float(result["balance_relative"])<1e-60
