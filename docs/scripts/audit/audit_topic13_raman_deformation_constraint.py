"""Source-backed spectral projection, not a fitted UET material identification."""

import hashlib
import io
import json
from pathlib import Path
import unittest

import numpy as np
from scipy.constants import h, c, k as k_B

from docs.core.uet_raman_deformation_constraint import (
    spectral_constraint, absolute_slope_constraint, tensor_identifiability,
    oscillator_heat_capacity_ratio, independent_axial_design, hydrostatic_row,
)

ROOT = Path(__file__).resolve().parents[3]
SOURCE = 'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/hanfland_1989_raman_deformation_source_package.json'
OUTPUT = 'docs/core/07_artifacts/topic13/t13_raman_deformation_constraint_audit.json'
REGISTRY = 'docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_raman_deformation_addendum.json'
ID = 'uet.thermal.raman_mass_deformation_constraint'
EVIDENCE = [SOURCE, 'docs/core/03_lanes/topic13_support/T13_RAMAN_DEFORMATION_CONSTRAINT.md',
            'docs/core/03_lanes/thermal/uet_raman_deformation_constraint.py',
            'docs/core/test/test_topic13_raman_deformation_constraint.py',
            'docs/scripts/audit/audit_topic13_raman_deformation_constraint.py']
PROTECTED = ['docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json',
             'docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json']


def digest(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build():
    protected = {p: digest(p) for p in PROTECTED}
    package = json.loads((ROOT/SOURCE).read_text(encoding='utf-8-sig'))
    rows = {row['row_id']: row for row in package['rows']}
    expected = {'axial_modulus_a': 'GPa', 'axial_modulus_c': 'GPa'}
    for mode in ('E2g1', 'E2g2'):
        expected.update({mode+'_frequency': 'cm^-1', mode+'_pressure_log_slope': 'GPa^-1',
                         mode+'_absolute_pressure_slope': 'cm^-1 GPa^-1'})
    if len(rows) != len(package['rows']) or rows.keys() != expected.keys():
        raise ValueError('source row identity mismatch')
    for key, unit in expected.items():
        row = rows[key]
        if row['unit'] != unit or not row['locator'] or not row['source_notation']:
            raise ValueError('source unit or locator mismatch: '+key)
        if not np.isfinite([row['value'], row['uncertainty']]).all() or row['uncertainty'] < 0:
            raise ValueError('invalid source value/error: '+key)
    original = package['source']
    raw_valid = digest(original['local_path']) == original['sha256']
    a, axial = (rows[key]['value'] for key in ('axial_modulus_a', 'axial_modulus_c'))
    results = {}
    for mode in ('E2g1', 'E2g2'):
        freq, slope, absolute = (rows[mode+suffix] for suffix in ('_frequency', '_pressure_log_slope', '_absolute_pressure_slope'))
        table = spectral_constraint(freq['value'], slope['value'], frequency_error=freq['uncertainty'], slope_error=slope['uncertainty'])
        abstract = absolute_slope_constraint(freq['value'], absolute['value'], frequency_error=freq['uncertainty'], slope_error=absolute['uncertainty'])
        ti, ai = (value['pressure_derivative_sensitivity_envelope_J2_per_Pa'] for value in (table, abstract))
        results[mode] = dict(table_log_slope_route=table, abstract_absolute_slope_route=abstract,
                             union_sensitivity_envelope_J2_per_Pa=[min(ti[0], ai[0]), max(ti[1], ai[1])],
                             normalized_constraint_rhs_per_GPa=2*slope['value'],
                             frozen_frequency_single_oscillator_c_over_k_B={str(t): oscillator_heat_capacity_ratio(freq['value'], t) for t in (100., 200., 300.)},
                             screening_role='HARMONIC_FIXED_FREQUENCY_COMPARATOR_NOT_LOW_T_MATERIAL_DATA')
    ident = tensor_identifiability(a, axial, mode_count=2)
    ident = {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in ident.items()}
    target = np.array([-.4, -8.])
    recovered = independent_axial_design(a, axial, hydrostatic_row(a, axial)@target/2, target[1]/2)
    moduli = {axis: [1/(rows['axial_modulus_'+axis]['value']+rows['axial_modulus_'+axis]['uncertainty']),
                     1/(rows['axial_modulus_'+axis]['value']-rows['axial_modulus_'+axis]['uncertainty'])] for axis in ('a', 'c')}
    tests = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromName(
        'docs.core.test.test_topic13_raman_deformation_constraint'))
    checks = {
        'primary_pdf_hash_matches_reviewed_copy': raw_valid,
        'eight_unique_source_rows_with_units_and_errors': len(rows) == 8,
        'SI_defining_constants_match': (package['constants']['h_J_s'], package['constants']['c_m_per_s'], package['constants']['k_B_J_per_K']) == (h, c, k_B),
        'independent_conversion_uncertainty_and_rank_tests': tests.wasSuccessful() and tests.testsRun >= 12,
        'two_modes_do_not_identify_four_components': ident['rank'] == 2 and ident['unknown_count'] == 4 and ident['nullity'] == 2,
        'null_residual_small': ident['null_residual'] < 1e-14,
        'second_strain_design_recovers_synthetic_witness': np.max(np.abs(recovered-target)) < 1e-12,
        'source_uncertainty_discrepancy_retained': not package['uncertainty_policy']['full_uncertainty_closure'] and bool(package['uncertainty_policy']['source_precision_discrepancy']),
        'spectral_projections_positive': all(r['table_log_slope_route']['squared_gap_pressure_derivative_J2_per_Pa'] > 0 for r in results.values()),
        'oscillator_screen_bounded': all(0 < v <= 1 for r in results.values() for v in r['frozen_frequency_single_oscillator_c_over_k_B'].values()),
        'whole_topic_hashes_unchanged': protected == {p: digest(p) for p in PROTECTED},
    }
    checks = {key: bool(value) for key, value in checks.items()}
    passed = all(checks.values())
    record = dict(schema_version='t13-raman-deformation-constraint-v1', major_result_id='T13_GRAPHITE_RAMAN_DEFORMATION_PROJECTION',
        topic='0.13_Thermodynamic_Bridge', closure_level='CLOSED_FOR_LANE' if passed else 'OPEN',
        verification_status='PASS_SOURCE_BACKED_SPECTRAL_PROJECTION_FULL_D_OPEN' if passed else 'FAIL_RAMAN_DEFORMATION_CONSTRAINT',
        what_is_closed=['Eight source-reported spectral/modulus rows with PDF hash, row identity and uncertainty caveats.',
                        'SI mode-energy/pressure-susceptibility conversion and a measured hydrostatic deformation constraint.',
                        'Rank boundary and sufficient independent axial-strain design for the scalar two-component projection.'] if passed else [],
        equation_registry_ids=[ID],
        equation_or_mapping={'mode_energy': 'E=h*c*100*nu_cm; x_mode=E^2',
                             'pressure_susceptibility': 'dx_mode/dP=2*x_mode*delta0_GPa/1e9',
                             'constraint': '(-2/B_a,-1/B_c).(D_ab/x_mode,D_c/x_mode)=2*delta0',
                             'independent_axial_row': 'D_c/x_mode=2*dln(nu)/deps_zz at fixed in-plane strain'},
        ontology={'x_mode': 'squared measured mode energy, not automatically UET mass', 'D': 'conditional mode strain derivative',
                  'C_Phi_R_gen_R_obs': 'unchanged; no mode identification'},
        units={'x_mode': 'J^2', 'dx_dP': 'J^2 Pa^-1', 'D_over_x': '1', 'nu': 'cm^-1', 'B': 'GPa', 'delta0': 'GPa^-1'},
        unit_lane='SI_spectroscopic_not_base_Phi', derivation_class='derived_relation',
        observable='mode gap and hydrostatic squared-energy susceptibility',
        data_role='EXTERNAL_SPECTROSCOPIC_CONSTRAINT_WITH_SEPARATE_HARMONIC_SCREENING',
        source_state=package['material_state'], uncertainty_policy=package['uncertainty_policy'],
        source_row_hashes={key: hashlib.sha256(json.dumps(row, sort_keys=True, separators=(',', ':')).encode()).hexdigest() for key, row in rows.items()},
        primary_source=dict(path=original['local_path'], sha256=original['sha256'], role='LOCAL_ONLY_NOT_REDISTRIBUTED'),
        mode_results=results, identifiability=ident, axial_compressibility_sensitivity_envelopes_per_GPa=moduli,
        independent_axial_design_witness=dict(data_role='SYNTHETIC_ONLY', input_D_over_x=target.tolist(), recovered_D_over_x=recovered.tolist()),
        physical_D_tensor=None, alpha_Phi_K=None, full_source_uncertainty_accepted=False,
        checks=checks, test_count=tests.testsRun,
        evidence_artifacts=[dict(path=p, sha256=digest(p)) for p in EVIDENCE], protected_full_closure_hashes=protected,
        input_policy='Only named 1989 Raman package/PDF and code/tests. No Ding/Xie numeric inputs, TTG fit or holdout. Original study fit parameters remain labelled as such.',
        open_blockers=['same_state_independent_strain_direction_missing', 'source_uncertainty_convention_unresolved',
                       'UET_mode_identity_and_kinetic_residue_missing', 'momentum_resolved_dispersion_and_thermal_measure_missing',
                       'Phi_normalization_and_pump_interface_missing', 'source_300K_to_TTG_state_equivalence_missing'],
        controlling_blocker='independent_strain_and_UET_mode_identification_missing',
        dependency_unlocked='Low-interlayer-mode identification and independent-strain research design only',
        physical_dependency_unlock=False, full_core_unlock=False, claim_promotion=False,
        claim_boundary='Source-state spectral constraints, not full D, Phi calibration, branch heat capacity, TTG transport or UET validation. Oscillator screening is conditional. Separate He-4 status unchanged.')
    entry = {key: record[key] for key in ('ontology', 'units', 'unit_lane', 'derivation_class', 'observable', 'data_role',
             'verification_status', 'controlling_blocker', 'claim_boundary', 'physical_dependency_unlock')}
    entry.update(equation_id=ID, version='1', classification='observable_definition',
                 relation_or_code_path=record['equation_or_mapping'], variables=record['ontology'],
                 mathematical_role='measured projection and identifiability', standard_physics_counterpart='Raman eigenfrequency pressure/strain susceptibility',
                 observable_mapping=record['observable'], parameter_dimensions=record['units'],
                 source_or_origin='Hanfland et al. 1989 Tables I/II and abstract, exact SI constants, chain rule',
                 assumptions=['small hydrostatic perturbation', 'source pressure-fit derivatives', 'hexagonal scalar projection', 'UET mode identity open'],
                 symmetry_and_conservation='scalar symmetry restriction explicit; no new O(2) charge claim',
                 limiting_cases=['one mode rank one', 'two modes rank two for four unknowns', 'independent axial strain'],
                 implementation_paths=[EVIDENCE[2]], verifier_paths=[EVIDENCE[3], EVIDENCE[4]],
                 evidence_class='SOURCE_BACKED_DERIVED_SPECTRAL_CONSTRAINT', proof_status='chain-rule/unit/rank identities with independent tests',
                 failure_mode=record['open_blockers'], downstream_dependencies=['material_mode_identification'],
                 dependency_role='conditional_material_input_not_physical_unlock', next_hardening_step='same-state independent strain, dispersion and residue')
    registry = dict(schema_version='uet-equation-registry-addendum-v1', status='SCOPED_SPECTRAL_CONSTRAINT_NOT_UET_IDENTITY',
                    extends='docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json', equation_entries=[entry], full_core_unlock=False, claim_promotion=False)
    return record, registry


def main():
    record, registry = build()
    (ROOT/OUTPUT).write_text(json.dumps(record, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    registry['equation_entries'][0]['evidence_artifacts'] = [dict(path=OUTPUT, sha256=digest(OUTPUT))]
    (ROOT/REGISTRY).write_text(json.dumps(registry, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(record['verification_status'])
    print(json.dumps(record['mode_results'], indent=2))
    print('failed_checks='+','.join(key for key, value in record['checks'].items() if not value))
    return 0 if all(record['checks'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
