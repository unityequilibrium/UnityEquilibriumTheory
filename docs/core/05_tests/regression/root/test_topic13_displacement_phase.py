import numpy as np
from docs.scripts.audit.audit_topic13_displacement_phase import centroid_readout
from docs.core.uet_interlayer_mode_residue import shear_basis,cell_phase


def test_explicit_unequal_mass_readout():
    masses=np.array([2.,3.,5.,7.]); layers=np.array([0,1,0,1])
    positions=np.arange(12).reshape(4,3)/13; q=np.array([.2,.3,.4])
    vectors=np.eye(12,dtype=complex)
    basis,mu=shear_basis(masses,layers,[0,0,1],[1,0,0])
    expected=basis.T@(cell_phase(q,positions)[:,None]*vectors)/np.sqrt(mu)
    np.testing.assert_allclose(centroid_readout(vectors,q,positions,masses,layers),expected,atol=1e-15)


def test_rigid_translation_and_origin_shift():
    masses=np.array([2.,3.,5.,7.]); layers=np.array([0,1,0,1])
    positions=np.arange(12).reshape(4,3)/13
    translation=np.repeat(np.sqrt(masses),3)[:,None]*np.tile([1.,0.,0.],4)[:,None]
    np.testing.assert_allclose(centroid_readout(translation,np.zeros(3),positions,masses,layers),0,atol=1e-15)
    q=np.array([.2,.3,.4]); delta=np.array([.1,.2,.3]); vectors=np.eye(12)
    a=centroid_readout(vectors,q,positions,masses,layers)
    b=centroid_readout(vectors,q,positions+delta,masses,layers)
    np.testing.assert_allclose(b,np.exp(2j*np.pi*q@delta)*a,atol=1e-15)
