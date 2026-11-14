"""Independent reaction counting, kinematics and Bose entropy checks."""
from dataclasses import replace
from itertools import product
from math import pi
import numpy as np
import pytest
from docs.scripts.audit import audit_topic13_coupled_gain_loss_operator as audit
from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import amplitude
from docs.core.uet_covariant_response import CovariantResponseConfig, response_potential

CFG = audit.MixtureInputs()


@pytest.mark.parametrize("charges", [c for _, c in audit.CHANNELS])
def test_on_shell_kinematics_and_mandelstam(charges):
    E, P, s, t, u, phase = audit.events(
        .7, 1.3, .2, charges, np.array([-.8, .1, .7]),
        np.array([.1, 1.8, 4.2]), CFG)
    m2 = np.array([audit.mass(q, CFG)**2 for q in charges])
    np.testing.assert_allclose(E**2 - np.sum(P*P, axis=-1),
                               np.broadcast_to(m2, E.shape), atol=2e-14)
    np.testing.assert_allclose(E[:, 0]+E[:, 1], E[:, 2]+E[:, 3], atol=2e-14)
    np.testing.assert_allclose(P[:, 0]+P[:, 1], P[:, 2]+P[:, 3], atol=2e-14)
    np.testing.assert_allclose(s+t+u, sum(m2), atol=2e-14)
    assert phase > 0


@pytest.mark.parametrize("charges", [c for _, c in audit.CHANNELS[:3]])
def test_matter_amplitudes_agree_with_independent_elastic_code(charges):
    s = 8.
    x = np.array([-.7, .2, .8])
    t = -2*(s/4-CFG.mass**2)*(1-x)
    u = -2*(s/4-CFG.mass**2)*(1+x)
    np.testing.assert_allclose(audit.channel_amplitude(s,t,u,charges,CFG),
                               amplitude(s,x,charges,CFG), atol=1e-15)


@pytest.mark.parametrize("q", [-1, 1])
def test_mixed_and_conversion_amplitudes(q):
    s, t, u = 7., np.array([-.2,-.8]), np.array([-3.,-2.4])
    expected = CFG.cubic**2*(1/(s-CFG.mass**2)+1/(u-CFG.mass**2))
    np.testing.assert_allclose(audit.channel_amplitude(s,t,u,(q,0,q,0),CFG), expected)
    expected = CFG.cubic**2*(1/(t-CFG.mass**2)+1/(u-CFG.mass**2))
    np.testing.assert_allclose(audit.channel_amplitude(s,t,u,(q,-q,0,0),CFG), expected)
    np.testing.assert_allclose(audit.channel_amplitude(s,t,u,(0,0,q,-q),CFG), expected)
    np.testing.assert_allclose(audit.channel_amplitude(s,t,u,(0,0,0,0),CFG), 6*CFG.neutral_quartic)


@pytest.mark.parametrize("z,k,eps", [(1.,1.,1.),(.25,4.,.5),(4.,9.,4.)])
def test_canonical_rescaling_and_production_response_derivative(z,k,eps):
    other = replace(CFG,z=z,mass_squared=z,quartic=CFG.coupling*z*z,
                    epsilon=eps,response_kinetic=k,response_mass_squared=.5*k,
                    response_coupling=CFG.cubic*z*np.sqrt(k/eps),
                    response_quartic=CFG.neutral_quartic*eps*k*k)
    rc = CovariantResponseConfig(epsilon_nc=eps,response_kinetic=k,
                                response_mass_sq=.5*k,response_quartic=other.response_quartic)
    step=.02
    v=lambda x:eps*response_potential(x/np.sqrt(eps*k),rc)
    fourth=(v(-2*step)-4*v(-step)+6*v(0)-4*v(step)+v(2*step))/step**4
    assert fourth == pytest.approx(6*CFG.neutral_quartic, rel=1e-9)
    for _, charges in audit.CHANNELS:
        np.testing.assert_allclose(audit.channel_amplitude(8.,-.5,-2.,charges,other),
                                   audit.channel_amplitude(8.,-.5,-2.,charges,CFG),rtol=1e-12)


def test_reaction_weights_match_full_ordered_species_sum():
    # Independently enumerate the 1/8 fully ordered four-leg Bose quadratic form.
    def key(q):
        return tuple(sorted((tuple(sorted(q[:2])),tuple(sorted(q[2:])))))
    multiplicities={}
    for q in product((-1,0,1),repeat=4):
        if sum(q[:2])==sum(q[2:]):
            multiplicities[key(q)]=multiplicities.get(key(q),0)+1
    assert len(multiplicities)==len(audit.CHANNELS)
    for _, q in audit.CHANNELS:
        assert audit.counting_weight(q)==multiplicities[key(q)]/8.


@pytest.mark.parametrize("charges", [c for _, c in audit.CHANNELS])
def test_actual_gain_loss_derivative_and_nonlinear_entropy(charges):
    E, P, *_ = audit.events(.7,1.3,.2,charges,np.array([-.8,.1,.7]),
                            np.array([.1,1.8,4.2]),CFG)
    T, mu=.25,.2
    psi=np.sin(E/T)+.2*np.asarray(charges)*E/T+.3*(np.asarray(charges)==0)
    delta=psi[:,0]+psi[:,1]-psi[:,2]-psi[:,3]
    f,r=audit.gain_loss(E,charges,T,mu,psi,0.)
    np.testing.assert_allclose(f,r,rtol=1e-12)
    errors=[]
    for eta in (1e-3,1e-4,1e-5):
        fp,rp=audit.gain_loss(E,charges,T,mu,psi,eta)
        fm,rm=audit.gain_loss(E,charges,T,mu,psi,-eta)
        measured=((fp-rp)-(fm-rm))/(2*eta)
        expected=f*delta
        errors.append(np.max(abs(measured-expected))/np.max(abs(expected)))
        # Independent logarithms test the Bose affinity, not a sign by construction.
        np.testing.assert_allclose(np.log(fp)-np.log(rp),eta*delta,atol=2e-14)
        assert np.min((fp-rp)*(np.log(fp)-np.log(rp)))>=0.
    assert errors[1] < errors[0]
    assert errors[-1] < 1e-6
    for eta in (-.1,.1):
        fp,rp=audit.gain_loss(E,charges,T,mu,psi,eta)
        assert np.min((fp-rp)*(np.log(fp)-np.log(rp)))>=0.


def test_decoupling_and_forbidden_channels():
    cfg=replace(CFG,response_coupling=0.)
    for q in ((1,0,1,0),(-1,0,-1,0),(1,-1,0,0),(0,0,1,-1),(1,1,0,0)):
        assert audit.channel_amplitude(8.,-.5,-2.,q,cfg)==0


def test_inverse_conversion_has_physical_threshold():
    assert audit.events(.1,.1,0.,(0,0,1,-1),np.array([0.]),np.array([0.]),CFG) is None
    assert audit.events(2.,2.,-.5,(0,0,1,-1),np.array([0.]),np.array([0.]),CFG) is not None


def test_no_regulator_at_propagator_pole():
    with pytest.raises(ValueError,match="pole"):
        audit.channel_amplitude(CFG.mass**2,-.5,-2.,(1,0,1,0),CFG)


@pytest.fixture(scope="module")
def grid():
    return audit.operator_grid(radial=4,angular=4,azimuth=4,cutoff=6.)


def test_collision_forms_nulls_positivity_and_conversion(grid):
    S=np.asarray(grid["scalar_matrix"]); V=np.asarray(grid["vector_matrix"])
    assert grid["scalar_invariant_relative_residual"]<1e-10
    assert grid["momentum_null_relative_residual"]<1e-10
    assert grid["max_detailed_balance_relative_error"]<1e-10
    assert grid["max_energy_residual"]<1e-12
    assert grid["max_momentum_residual"]<1e-12
    assert np.isfinite(grid["near_null_first_cell_fd_relative_error"])
    np.testing.assert_allclose(S,S.T,atol=1e-18)
    np.testing.assert_allclose(V,V.T,atol=1e-18)
    assert np.linalg.eigvalsh(S)[0]>=-1e-12*np.linalg.norm(S)
    assert np.linalg.eigvalsh(V)[0]>=-1e-12*np.linalg.norm(V)
    assert all(row["neutral_number_relaxation_form"]==0 for row in grid["channels"][:-1])
    assert grid["channels"][-1]["neutral_number_relaxation_form"]>0
    # Non-invariant trial directions must really dissipate, not a zero matrix.
    assert np.linalg.eigvalsh(S[3:,3:])[0]>0
    assert np.linalg.eigvalsh(V[1:,1:])[0]>0


def test_projected_response_satisfies_variational_equation(grid):
    result=audit.charge_response(grid)
    L=np.asarray(grid["vector_matrix"])[1:,1:]
    source=np.asarray(result["projected_charge_source"])
    solution=np.linalg.solve(L,source)
    assert source@solution == pytest.approx(result["finite_basis_charge_response"])
    assert result["finite_basis_charge_response"]>0
    assert min(result["generalized_active_rates"])>0
    for delta in (np.array([1.,-.3,.2]), np.array([-.2,.4,1.])):
        candidate=solution+delta
        assert 2*source@candidate-candidate@L@candidate <= source@solution+1e-13


def test_independent_witness_and_production_mutation(monkeypatch):
    record=audit.gain_loss_witness()
    assert all(r["relative_derivative_errors"][-1]<1e-6 for r in record["channels"])
    np.testing.assert_allclose(audit.neutral_quartic_witness(),6*CFG.neutral_quartic,rtol=1e-9)
    original=audit.response_potential
    monkeypatch.setattr(audit,"response_potential",lambda x,c:2*original(x,c))
    np.testing.assert_allclose(audit.neutral_quartic_witness(),12*CFG.neutral_quartic,rtol=1e-9)


@pytest.mark.parametrize("kwargs", [{"T":float("nan")},{"mu":float("nan")},{"T":0},
    {"mu":1.},{"radial":3},{"radial":4.5},{"angular":True},{"cutoff":0.}])
def test_invalid_normal_grid_rejected(kwargs):
    with pytest.raises(ValueError):
        audit.operator_grid(**kwargs)


def test_current_rejects_state_mismatch(grid):
    with pytest.raises(ValueError,match="states must agree"):
        audit.charge_response(grid,T=.3)


def test_natural_energy_dimensions(grid):
    scale=2.
    other=replace(CFG,mass_squared=CFG.mass_squared*scale**2,
                  response_mass_squared=CFG.response_mass_squared*scale**2,
                  response_coupling=CFG.response_coupling*scale)
    scaled=audit.operator_grid(other,T=.25*scale,mu=.2*scale,
                               radial=4,angular=4,azimuth=4,cutoff=6.*scale)
    np.testing.assert_allclose(np.array(scaled["scalar_matrix"])[3:,3:],
                               np.array(grid["scalar_matrix"])[3:,3:]*scale**4,rtol=1e-12)
    np.testing.assert_allclose(np.array(scaled["vector_matrix"])[1:,1:],
                               np.array(grid["vector_matrix"])[1:,1:]*scale**4,rtol=1e-12)
    original=audit.charge_response(grid)
    new=audit.charge_response(scaled,metric_cutoff=24.*scale)
    np.testing.assert_allclose(new["metric"],np.array(original["metric"])*scale**3,rtol=1e-12)
    assert new["finite_basis_charge_response"]==pytest.approx(original["finite_basis_charge_response"]*scale**2)
    np.testing.assert_allclose(new["generalized_active_rates"],np.array(original["generalized_active_rates"])*scale,rtol=1e-12)


def test_charge_conjugation_of_coupled_response(grid):
    negative=audit.operator_grid(mu=-.2,radial=4,angular=4,azimuth=4,cutoff=6.)
    sign=np.array([1,-1,1,1])
    np.testing.assert_allclose(np.array(negative["vector_matrix"])[1:,1:],
        (np.array(grid["vector_matrix"])*np.outer(sign,sign))[1:,1:],rtol=1e-12,atol=1e-22)
    assert audit.charge_response(negative)["finite_basis_charge_response"]==pytest.approx(
        audit.charge_response(grid)["finite_basis_charge_response"],rel=1e-12)


def test_nested_basis_contains_old_operator_and_variational_response(grid):
    larger=audit.operator_grid(radial=4,angular=4,azimuth=4,cutoff=6.,basis_order=2)
    np.testing.assert_allclose(np.array(larger["vector_matrix"])[:4,:4],grid["vector_matrix"],rtol=1e-12,atol=1e-22)
    assert audit.charge_response(larger)["finite_basis_charge_response"]>=audit.charge_response(grid)["finite_basis_charge_response"]
    assert audit.charge_response(larger)["linear_solve_relative_residual"]<1e-8
    result=audit.charge_response(larger)
    assert sum(result["response_by_relaxation_mode"])==pytest.approx(result["finite_basis_charge_response"],rel=1e-8)


def test_relative_momentum_coupling_and_charge_symmetry():
    witness=audit.relative_momentum_witness()
    for i in (0,3):
        full,half,zero=witness["rows"][i:i+3]
        assert half["neutral_momentum_form"]==pytest.approx(full["neutral_momentum_form"]/16,rel=1e-12)
        assert zero["neutral_momentum_form"]/zero["collision_matrix_norm"]<1e-12
        assert zero["charge_response"] is None
    assert witness["rows"][0]["charge_response"]["slowest_mode_response_fraction"]>.8
    assert witness["rows"][3]["charge_response"]["slowest_mode_response_fraction"]<1e-10


def test_no_inverse_of_decoupled_extra_momentum_null(grid):
    row=audit.operator_grid(replace(CFG,response_coupling=0),radial=4,angular=4,azimuth=4,cutoff=6.,basis_order=1)
    with pytest.raises(ValueError,match="decoupled sectors"):
        audit.charge_response(row)
