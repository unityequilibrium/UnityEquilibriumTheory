"""Generate conditional reciprocal G/r dynamics evidence, never calibration."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import unittest

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_dynamic_thermoelastic_response import material_mode
from docs.core.uet_matter_strain_susceptibility import canonical_sources, thermal_matching
from docs.core.uet_reciprocal_thermal_dynamics import reciprocal_mode
from docs.core.uet_thermoelastic_spatial_compatibility import isotropic_stiffness, strain_map

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = 'docs/core/07_artifacts/topic13/t13_reciprocal_thermal_dynamics_audit.json'
REGISTRY = 'docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_reciprocal_thermal_dynamics_addendum.json'
ID = 'uet.thermal.reciprocal_material_response'
PROTECTED = ['docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json',
             'docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json']
EVIDENCE = ['docs/core/T13_RECIPROCAL_THERMAL_DYNAMICS.md',
            'docs/core/uet_reciprocal_thermal_dynamics.py',
            'docs/core/test/test_topic13_reciprocal_thermal_dynamics.py',
            'docs/scripts/audit/audit_topic13_reciprocal_thermal_dynamics.py',
            'docs/core/uet_dynamic_thermoelastic_response.py',
            'docs/core/uet_matter_strain_susceptibility.py',
            'docs/core/uet_covariant_matter.py', 'docs/core/uet_covariant_response.py',
            'docs/core/uet_thermoelastic_spatial_compatibility.py',
            'docs/core/07_artifacts/topic13/t13_matter_strain_susceptibility_matching_audit.json']


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    protected = {p: digest(p) for p in PROTECTED}
    matter = CovariantMatterConfig(matter_kinetic=1.2, matter_mass_sq=2.7,
                                  matter_quartic=.2, response_coupling=.84)
    response = CovariantResponseConfig(epsilon_nc=.5, phi_equilibrium=.1)
    sources = canonical_sources(matter, response, [.48, -.24, .36, 0., 0., 0.])
    match = thermal_matching(.8, sources)
    bare = isotropic_stiffness(5., 3.)
    stiffness = bare+match['delta_stiffness']
    beta = bare@np.array([.04, .04, .04, 0., 0., 0.])+match['delta_thermal_stress']
    p = dict(stiffness=stiffness, expansion=np.linalg.solve(stiffness, beta),
             coupling=match['G'], direction=[1., 0., 0.], q=1., rho=1., temperature=.8,
             heat_capacity=2.4+match['delta_heat_capacity'], conductivity=.3, relaxation=.2)
    r = dict(entropy_phi=match['entropy_phi_coefficient'], response_kinetic=1.2,
             response_curvature=.8+match['delta_phi_curvature'], response_gradient=.3,
             response_damping=.08)
    mode = reciprocal_mode(material_mode(**p), **r)
    initial = mode.initial_state(.03, phi=.02, pi=.004)
    times = np.linspace(0, 20, 161)
    states = mode.evolve_constant(times, initial)
    energy = np.einsum('ti,ij,tj->t', states, mode.metric, states)/2
    hot = mode.evolve_constant(times, mode.initial_state(.03))
    identity = np.max(np.abs(mode.metric@mode.matrix+mode.matrix.T@mode.metric+2*mode.dissipation_metric))
    balances = [mode.balance(x, heat=.004, force=.002) for x in states[::10]]
    ports = np.column_stack([mode.heat_port, mode.force_port])
    resolvent_error = 0.
    for s in (.1+.02j, .2+.8j, .3+3j, .4+10j):
        direct = np.linalg.solve(s*np.eye(len(mode.matrix))-mode.matrix, ports)[[6, mode.phi_index]]
        resolvent_error = max(resolvent_error, float(np.max(np.abs(direct-mode.laplace_transfer(s)))))
    wrong = mode.matrix.copy()
    wrong[6, mode.pi_index] = 0.
    one_sided_defect = float(np.linalg.norm(mode.metric@wrong+wrong.T@mode.metric+2*mode.dissipation_metric))
    conservative = reciprocal_mode(material_mode(**dict(p, conductivity=0., relaxation=0.)),
                                   **dict(r, response_damping=0.))
    conservative_identity = np.max(np.abs(conservative.metric@conservative.matrix+conservative.matrix.T@conservative.metric))
    tests = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromName(
        'docs.core.test.test_topic13_reciprocal_thermal_dynamics'))
    checks = {
        'independent_equation_covariance_and_limit_suite': tests.wasSuccessful() and tests.testsRun >= 14,
        'matching_G_and_r_carried_together': np.array_equal(mode.material.coupling, strain_map(p['direction']).T@match['G']) and mode.entropy_phi == match['entropy_phi_coefficient'],
        'positive_coupled_availability': np.min(np.linalg.eigvalsh(mode.metric)) > 0 and mode.schur_margin > 0,
        'reciprocal_matrix_balance': identity < 1e-12,
        'linear_entropy_balance': max(abs(b['linear_entropy_residual']) for b in balances) < 1e-12,
        'forced_availability_balance': max(abs(b['balance_residual']) for b in balances) < 1e-12,
        'dissipation_nonnegative': all(b['dissipation'] >= 0 for b in balances),
        'independent_laplace_elimination': resolvent_error < 1e-10,
        'conservative_limit_energy_identity': conservative_identity < 1e-12,
        'unforced_availability_nonincreasing': np.max(np.diff(energy)) < 1e-12 and energy[-1] < energy[0],
        'one_sided_r_is_rejected_by_balance': one_sided_defect > 1e-3,
        'heat_preparation_generates_response_without_response_force': np.max(np.abs(hot[:, mode.phi_index])) > 1e-7,
        'protected_whole_topic_files_unchanged': protected == {p: digest(p) for p in PROTECTED},
    }
    checks = {key: bool(value) for key, value in checks.items()}
    passed = all(checks.values())
    result = dict(
        schema_version='t13-reciprocal-thermal-dynamics-v1',
        major_result_id='T13_RECIPROCAL_MATERIAL_RESPONSE_ENERGY_ENTROPY',
        topic='0.13_Thermodynamic_Bridge', closure_level='CLOSED_FOR_LANE' if passed else 'OPEN',
        verification_status='PASS_CONDITIONAL_RECIPROCAL_THERMAL_DYNAMICS' if passed else 'FAIL_RECIPROCAL_THERMAL_DYNAMICS',
        what_is_closed=['Joint G/r feedback from the declared local thermodynamic potential.',
                        'Positive modal availability, reciprocal power cancellation and linear entropy balance.',
                        'Independent dynamic/resolvent and normalization/rotation/energy-unit checks.'] if passed else [],
        equation_registry_ids=[ID],
        equation_or_mapping={'response': 'z*Pi_dot=-a_q*phi-h.v+r*theta-gamma*Pi+f',
                             'heat': 'c*theta_dot=-T*b.w-T*r*Pi-q*J+Q',
                             'entropy': 'ds=b.v+c*theta/T+r*phi',
                             'availability_rate': 'W_dot=theta*Q/T+Pi*f-gamma*Pi^2-J^2/(T*k)',
                             'Fourier_loss': 'k*q^2*theta^2/T replaces J^2/(T*k) at tau=0'},
        ontology={'Phi': 'existing response displacement', 'Pi': 'response time derivative',
                  'material': 'v,w,theta and optional Cattaneo J', 'C': 'unchanged', 'R_gen_R_obs': 'excluded'},
        state_variables=['v[3]', 'w[3]', 'theta', 'J (tau>0 only)', 'phi', 'Pi'],
        excluded_variables=['R_gen', 'R_obs'],
        units={'v': '1', 'w_theta_phi': 'E', 'Pi': 'E^2', 'J_rho_A': 'E^4', 'b_h_c': 'E^3',
               'r_a_k': 'E^2', 'z_kappa_phi': '1', 'gamma_q_T': 'E', 'tau': 'E^-1', 'f': 'E^3', 'Q': 'E^5'},
        unit_lane='natural_units_not_SI', derivation_class='constitutive_ansatz',
        derivation_detail='Reciprocal forces and availability derived exactly within a declared quadratic potential, with external dissipation inputs.',
        observable='conditional material temperature and response transfer, not detector-calibrated TTG',
        data_role='SYNTHETIC_INTERNAL_NO_CALIBRATION',
        coefficient_origin='Same synthetic bare-plus-thermal increments as preceding susceptibility wave; not measured material coefficients.',
        checks=checks, test_count=tests.testsRun,
        metrics={'schur_margin': mode.schur_margin, 'energy_matrix_residual': float(identity),
                 'conservative_matrix_residual': float(conservative_identity), 'laplace_absolute_error': resolvent_error,
                 'one_sided_r_balance_defect': one_sided_defect, 'unforced_initial_availability': float(energy[0]),
                 'unforced_final_availability': float(energy[-1]),
                 'heat_only_initial_state_max_abs_phi': float(np.max(np.abs(hot[:, mode.phi_index]))),
                 'G': match['G'].tolist(), 'r': mode.entropy_phi},
        synthetic_contract={'temperature': .8, 'q': 1., 'rho': 1., 'conductivity': .3, 'relaxation': .2,
                            'response_kinetic': 1.2, 'response_gradient': .3, 'response_damping': .08,
                            'bare_phi_curvature': .8, 'bare_heat_capacity': 2.4, 'bulk': 5., 'shear': 3.,
                            'raw_mass_squared': 2.7, 'matter_kinetic': 1.2, 'matter_quartic': .2,
                            'response_coupling': .84, 'epsilon_nc': .5, 'raw_D': [.48, -.24, .36, 0., 0., 0.],
                            'bare_expansion': [.04, .04, .04, 0., 0., 0.], 'initial_entropy': .03,
                            'initial_phi': .02, 'initial_pi': .004, 'times': [0., 20., 161]},
        evidence_artifacts=[dict(path=p, sha256=digest(p)) for p in EVIDENCE],
        protected_full_closure_hashes=protected,
        input_policy='No experimental curve, setup metadata, calibration source or holdout is read by this generator/model as a computational input. Prior research artifact is hashed only.',
        open_blockers=['physical_D_Z_and_material_mode_identity_missing',
                       'vacuum_subtraction_and_material_double_counting_match_missing',
                       'physical_pump_initial_entropy_and_response_force_map_missing',
                       'microscopic_dissipation_SK_KMS_and_noise_match_missing',
                       'continuum_causal_boundary_and_detector_geometry_missing',
                       'nonlinear_mean_heating_and_full_entropy_current_missing'],
        controlling_blocker='physical_material_and_preparation_match_missing',
        dependency_unlocked='Conditional reciprocal pump/material design only',
        physical_dependency_unlock=False, full_core_unlock=False, claim_promotion=False,
        claim_boundary='Local quadratic natural-unit extension with external damping/transport; not accepted core action, physical alpha, Kubo/KMS, nonlinear total-energy closure or finite-cone proof. Separate He-4 Core-ready record is unchanged and not revalidated.')
    registry = dict(schema_version='uet-equation-registry-addendum-v1',
                    status='CANDIDATE_RECIPROCAL_MATERIAL_EXTENSION',
                    extends='docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json',
                    full_core_unlock=False, claim_promotion=False)
    entry = {key: result[key] for key in ('ontology', 'units', 'unit_lane', 'derivation_class', 'observable',
             'data_role', 'verification_status', 'controlling_blocker', 'claim_boundary', 'physical_dependency_unlock')}
    entry.update(equation_id=ID, version='1', classification='constitutive_lane',
                 relation_or_code_path=result['equation_or_mapping'],
                 standard_physics_counterpart='linear reciprocal thermoelastic/free-energy response and quadratic availability',
                 variables=result['ontology'], mathematical_role='reciprocal material-response feedback',
                 observable_mapping=result['observable'], parameter_dimensions=result['units'],
                 source_or_origin=result['coefficient_origin'],
                 assumptions=['constant reference T', 'linear bulk q>0 mode', 'positive joint Schur domain',
                              'external local material coefficients and dissipation', 'no microscopic noise match'],
                 symmetry_and_conservation='rotation and Phi normalization covariance; exact quadratic availability and linear entropy balances',
                 limiting_cases=['G=r=0 old comparator', 'k=gamma=0 conservation', 'Fourier tau=0', 'conducting DC'],
                 implementation_paths=[EVIDENCE[1]], verifier_paths=[EVIDENCE[2], EVIDENCE[3]],
                 evidence_class='INTERNAL_CONDITIONAL_DERIVATION', proof_status='quadratic identities with independent numerical checks',
                 evidence_artifacts=[dict(path=OUTPUT, sha256='GENERATED_AFTER_ARTIFACT')],
                 downstream_dependencies=['physical_pump_material_matching'], dependency_role='conditional_diagnostic_only',
                 failure_mode=result['open_blockers'], next_hardening_step='identify physical D/Z and pump ports; derive bath/noise and continuum contract')
    registry['equation_entries'] = [entry]
    return result, registry


def main():
    result, registry = build()
    (ROOT/OUTPUT).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    registry['equation_entries'][0]['evidence_artifacts'][0]['sha256'] = digest(OUTPUT)
    (ROOT/REGISTRY).write_text(json.dumps(registry, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(result['verification_status'])
    print(json.dumps(result['metrics'], indent=2))
    print('failed_checks='+','.join(key for key, value in result['checks'].items() if not value))
    return 0 if all(result['checks'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
