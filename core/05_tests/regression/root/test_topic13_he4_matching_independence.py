import pytest
from docs.scripts.audit.audit_topic13_he4_matching_independence import matching


def test_matching_identity_is_not_independent_constraint():
    base=matching(7.,.02,-1.)
    for factor in (.5,1.,2.):
        m=matching(7.,factor*.02,-1.)
        assert m['reconstructed_alpha']==pytest.approx(-1.)
        assert m['Z']==pytest.approx(factor*base['Z'])
        assert 7.*factor*.02/base['Z']==pytest.approx(-factor)


def test_singular_or_nonfinite_matching_rejected():
    for values in [(1,0,1),(1,1,0),(float('nan'),1,1)]:
        with pytest.raises(ValueError):matching(*values)
