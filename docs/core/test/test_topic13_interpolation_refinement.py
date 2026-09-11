import numpy as np
from docs.scripts.audit.audit_topic13_interpolation_refinement import sphere_rule,grid,deficient_columns


def test_product_rules_integrate_second_and_fourth_sphere_moments():
    for name,count in (("product4x8",32),("product8x16",128)):
        d,w=sphere_rule(name)
        assert len(w)==count and np.all(w>0)
        np.testing.assert_allclose(w.sum(),1)
        np.testing.assert_allclose(np.linalg.norm(d,axis=1),1)
        np.testing.assert_allclose(d.T@(w[:,None]*d),np.eye(3)/3,atol=1e-14)
        np.testing.assert_allclose(w@d[:,0]**4,1/5,atol=1e-14)


def test_same_radius_support_cannot_resolve_independent_energy_and_constant():
    d,_=sphere_rule("product4x8")
    features=np.column_stack((np.ones(len(d)),np.full(len(d),np.sqrt(2)),d))
    assert deficient_columns(np.ones((len(d),1)),features,1e-12)==[0]


def test_grid_keeps_both_species_on_same_mass_shell():
    signs,p,e=grid(8,"product4x8",10.,1.2)
    assert len(e)==512
    assert set(signs)=={-1.,1.}
    np.testing.assert_allclose(e**2-np.sum(p*p,axis=1),1.2**2,atol=1e-12)
