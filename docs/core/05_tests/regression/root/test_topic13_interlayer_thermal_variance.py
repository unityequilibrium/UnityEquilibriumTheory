import numpy as np
import pytest
from scipy.constants import hbar,k
from docs.scripts.audit.audit_topic13_interlayer_thermal_variance import oscillator_variance,modal_covariance


def test_zero_temperature_and_classical_limit():
    w=np.array([1e9,2e9])
    np.testing.assert_allclose(oscillator_variance(w,0),hbar/(2*w),rtol=1e-14,atol=0)
    np.testing.assert_allclose(oscillator_variance(w,300),k*300/w**2,rtol=1e-8,atol=0)


def test_no_unstable_mode_clipping():
    for w in ([0.],[-1.],[float('nan')]):
        with pytest.raises(ValueError):oscillator_variance(w,100)


def test_degenerate_basis_phase_and_reduced_mass():
    w=np.array([1e12,1e12]); overlap=np.eye(2,dtype=complex)
    rotation=np.array([[1,1j],[1j,1]])/np.sqrt(2)
    a=modal_covariance(overlap,w,200,2.)
    b=modal_covariance(overlap@rotation,w,200,2.)
    np.testing.assert_allclose(a,b,rtol=1e-13,atol=1e-60)
    np.testing.assert_allclose(a,2*modal_covariance(overlap,w,200,4.),rtol=1e-14,atol=0)


def test_classical_full_matrix_inverse():
    omega=np.array([1e8,2e8]); angle=.37
    Q=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    expected=k*300*np.linalg.inv(Q@np.diag(omega**2)@Q.T)/3.
    np.testing.assert_allclose(modal_covariance(Q,omega,300,3.),expected,rtol=1e-10,atol=0)
