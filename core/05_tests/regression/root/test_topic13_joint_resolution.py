import numpy as np
from docs.scripts.audit.audit_topic13_joint_resolution import spectral_response


def test_spectral_matches_pseudoinverse_and_retains_signed_modes():
    values=np.array([-2.,0.,1.e-13,3.])
    source=np.arange(12.).reshape(4,3)
    result,rank,negative=spectral_response(values,np.eye(4),source,1.e-12)
    expected=source.T@np.linalg.pinv(np.diag(values),rcond=1.e-12)@source
    np.testing.assert_allclose(result,expected)
    assert rank==2 and negative==1


def test_cutoff_diagnostic_does_not_change_eigenvalues():
    values=np.array([0.,1.e-13,1.])
    before=values.copy()
    _,coarse,_=spectral_response(values,np.eye(3),np.ones((3,1)),1.e-10)
    _,fine,_=spectral_response(values,np.eye(3),np.ones((3,1)),1.e-14)
    assert coarse==1 and fine==2
    np.testing.assert_array_equal(values,before)
