import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_local_variance_identifiability import target_weights,renamed_null_test


def test_identifiable_target_without_full_populations():
    result=renamed_null_test([[1.,1.]],[1.,1.])
    assert result['identifiable_at_numerical_tolerance']
    assert result['rank']==1


def test_positive_witness_for_ambiguous_target():
    a=np.array([[1.,1.]])
    result=renamed_null_test(a,[1.,2.])
    witness=result['synthetic_witness']
    plus=np.array(witness['n_plus']);minus=np.array(witness['n_minus'])
    np.testing.assert_allclose(a@plus,a@minus,atol=1e-14)
    assert np.min(plus)>0 and np.min(minus)>0
    assert abs(witness['target_difference'])>0
    assert 'energy_difference' not in witness


def test_target_weights_and_invalid_frequency():
    np.testing.assert_allclose(target_weights(np.eye(2),[2.,4.]),[.5,.25])
    with pytest.raises(ValueError):target_weights(np.eye(2),[0.,4.])
