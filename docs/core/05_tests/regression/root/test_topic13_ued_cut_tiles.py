import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_ued_cut_tiles import tile_totals,BOUNDS


def test_partition_is_disjoint_and_complete():
    count=np.zeros((512,512),int)
    for a,b,c,d in BOUNDS: count[a:b,c:d]+=1
    assert np.all(count==1)
    np.testing.assert_array_equal(tile_totals(np.ones((512,512))),np.full(16,128**2))


def test_localized_signal_retains_position():
    x=np.zeros((512,512));x[400,200]=12
    t=tile_totals(x)
    assert t[13]==12 and t.sum()==12


def test_missing_support_not_silently_ignored():
    x=np.ones((512,512));x[0,0]=np.nan
    with pytest.raises(ValueError): tile_totals(x)
    with pytest.raises(ValueError): tile_totals(np.ones((256,256)))
