import numpy as np
from docs.scripts.audit.audit_topic13_actuation_readout_identifiability import transfer


def test_reciprocal_gain_scaling_preserves_complex_response():
    omega=np.linspace(0,20,101)
    for s in (.1,2.,10.):
        np.testing.assert_allclose(transfer(omega,3./s,.7*s),transfer(omega,3.,.7),rtol=1e-14)


def test_more_frequencies_not_independent_gain_anchor():
    A=np.ones((100,2))
    assert np.linalg.matrix_rank(A)==1
    assert np.linalg.matrix_rank(np.vstack([A,[0,1]]))==2
