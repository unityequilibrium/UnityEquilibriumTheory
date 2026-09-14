import pytest
from docs.scripts.audit.audit_topic13_ued_cut_pooling import differences


def test_metadata_difference_is_not_variance():
    a=[dict(LTS_position=1,Delay_ps=6,Temperature_B=300)]
    b=[dict(LTS_position=1,Delay_ps=6,Temperature_B=301)]
    assert differences(a,b,['Temperature_B']) == {'Temperature_B':{'differing_rows':1,'maximum_absolute_difference':1}}


def test_alignment_required():
    with pytest.raises(ValueError): differences([dict(LTS_position=1,Delay_ps=6)],[dict(LTS_position=2,Delay_ps=6)],[])


def test_empty_or_unpaired_rejected():
    with pytest.raises(ValueError): differences([],[],[])
    with pytest.raises(ValueError): differences([{}],[],[])
