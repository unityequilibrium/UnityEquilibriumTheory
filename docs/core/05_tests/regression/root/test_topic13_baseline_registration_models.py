import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_baseline_registration_models import fit_map,predict


def test_known_maps_and_left_out_point():
    p=np.array([[0.,0.],[0,10],[10,0],[10,10],[3,4]])+250
    for kind,params in [('translation',[.3,-.4]),('similarity',[.3,-.4,.01,.02]),('affine',[.3,-.4,.01,.02,.03,-.02])]:
        target=predict(p,np.array(params),kind)
        fitted=fit_map(p[:-1],target[:-1],kind)
        np.testing.assert_allclose(predict(p,fitted,kind),target,rtol=0,atol=1e-12)


def test_affine_rank_deficiency_rejected():
    p=np.array([[0.,0.],[1,1],[2,2]])
    with pytest.raises(ValueError):fit_map(p,p,'affine')
