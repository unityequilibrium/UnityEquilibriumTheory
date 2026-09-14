import numpy as np
from docs.scripts.audit.audit_topic13_registration_shell_transfer import shell_transfer
from docs.scripts.audit.audit_topic13_baseline_registration_models import predict


def fixture():
    angle=np.arange(6)*np.pi/3
    p=np.concatenate([256+r*np.column_stack([np.cos(angle),np.sin(angle)]) for r in (10,20,30)])
    return p,np.repeat([1,2,3],6)


def test_true_affine_transfers_with_disjoint_shells():
    p,shells=fixture();actual=predict(p,np.array([.2,.3,.01,.02,-.01,.03]),'affine')
    for r in shell_transfer(p,actual,shells,'affine'):
        assert not set(r['training_indices'])&set(r['excluded_indices'])
        assert len(r['excluded_indices'])==6 and r['max_pixels']<1e-11


def test_shell_specific_bias_is_not_hidden():
    p,shells=fixture();actual=p.copy();actual[shells==3,0]+=2
    rows=shell_transfer(p,actual,shells,'affine')
    assert abs(rows[2]['rms_pixels']-2)<1e-10
