import numpy as np
from docs.scripts.audit.audit_topic13_multibragg_positions import peak_probe


def test_centered_peak_and_boundary():
    image=np.ones((21,21));image[10,10]=100
    r=peak_probe(image,[10,10],4)
    assert r['peak_offset_pixels']==0 and r['centroid_offset_pixels']==0
    assert not r['peak_on_boundary']
    assert peak_probe(image,[6,10],4)['peak_on_boundary']


def test_missing_and_outside_not_filled():
    image=np.ones((21,21));image[10,10]=np.nan
    assert peak_probe(image,[10,10],4)['status']=='UNRESOLVED_PATCH'
    assert peak_probe(image,[0,0],4)['status']=='OUTSIDE'
