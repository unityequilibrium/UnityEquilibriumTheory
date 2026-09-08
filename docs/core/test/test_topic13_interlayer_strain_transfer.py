"""Source-model derivatives cannot authorize a cross-state calibration."""

import numpy as np

from docs.scripts.audit.audit_topic13_interlayer_strain_transfer import assess


def inputs():
    return ({'rows': {'reference_spacing': {'value': 3.2},
                     'fixed_plane_gamma': {'value': 1.6729, 'uncertainty': .0002}}},
            {'primitive_lattice_angstrom': np.diag([2.46, 2.13, 7.078739719]).tolist()})


def test_independent_central_derivative():
    source, mode = inputs()
    result = assess(source, mode)
    eps = 1e-5
    gamma = source['rows']['fixed_plane_gamma']['value']
    x_plus = ((1+eps)**(-3*gamma))**2
    x_minus = ((1-eps)**(-3*gamma))**2
    derivative = (np.log(x_plus)-np.log(x_minus))/(2*eps)
    np.testing.assert_allclose(result['source_state_log_squared_energy_strain_derivative'],
                               derivative, rtol=1e-9)


def test_no_extrapolation_or_calibration():
    source, mode = inputs()
    result = assess(source, mode)
    assert result['full_fit_domain_membership'] == 'OUTSIDE'
    assert not result['cross_model_transfer_allowed']
    assert result['corrected_MP48_frequency'] is None
    assert result['physical_D_tensor'] is None
    assert result['alpha_Phi_K'] is None


def test_domain_overlap_does_not_prove_same_model():
    source, mode = inputs()
    mode['primitive_lattice_angstrom'][2][2] = 6.4
    result = assess(source, mode)
    assert result['full_fit_domain_membership'] == 'NOT_ESTABLISHED'
    assert not result['cross_model_transfer_allowed']
