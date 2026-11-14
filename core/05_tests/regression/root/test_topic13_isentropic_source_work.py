import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_isentropic_source_work import tangent


def test_constraint_tangent():
    j=np.array([[2.,1.],[1.,3.]])
    np.testing.assert_allclose(j@tangent(j,[4.,5.]),[-4.,-5.])


def test_singular_and_invalid_constraints():
    with pytest.raises(np.linalg.LinAlgError): tangent([[1,1],[1,1]],[1,1])
    with pytest.raises(ValueError): tangent([[1,0],[0,1]],[np.nan,1])
