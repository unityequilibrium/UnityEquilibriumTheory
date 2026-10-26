"""Adversarial source/units/conditional-mapping tests, not BaTiO3 validation."""
from copy import deepcopy
import importlib
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch
import sympy as s

sys.path.insert(0,str(Path(__file__).resolve().parent))
a=importlib.import_module("Research_T13_BaTiO3_Static_Correspondence_Audit")


class BaTiO3AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=a.load_json(a.ROOT/a.INPUT)
        cls.math=a.algebra()
        cls.result=a.calculate()

    def test_source_subset_valid(self):
        sources,facts=a.validate_subset(self.data)
        self.assertEqual(len(sources),4);self.assertEqual(len(facts),11)

    def test_all_symbolic_checks(self):
        self.assertTrue(all(self.result['checks'].values()),self.result['checks'])

    def test_all_negative_controls(self):
        self.assertTrue(all(self.result['negative_controls'].values()),self.result['negative_controls'])

    def test_sources_are_not_metadata_only(self):
        d=deepcopy(self.data);d['sources'][0]['access']='METADATA_ONLY'
        with self.assertRaises(ValueError):a.validate_subset(d)

    def test_unknown_uncertainty_cannot_be_zero(self):
        d=deepcopy(self.data);d['facts'][0]['uncertainty']['value']='0'
        with self.assertRaises(ValueError):a.validate_subset(d)

    def test_no_cross_specimen_or_DFT_tuple(self):
        _,f=a.validate_subset(self.data)
        with self.assertRaises(ValueError):a.same_context(f['gamma8'],f['li_alpha111'])
        d=deepcopy(self.data);d['facts'][0]['context']='DFT_ZERO_T'
        with self.assertRaises(ValueError):a.validate_subset(d)

    def test_printed_minus_beta_and_factor_conventions(self):
        p=self.result['point_diagnostics']
        self.assertEqual(p['W2006_native_beta'],'-860000000')
        self.assertEqual(p['W2006_native_gamma'],'8000000000')
        self.assertEqual(p['Li_converted_coefficients_different_context']['delta'],'309040000000')
        self.assertNotEqual(p['W2006_native_delta'],p['Li_converted_coefficients_different_context']['delta'])

    def test_nominal_geometry_and_temperature_not_intervals(self):
        p=self.result['transformations']
        self.assertEqual(s.Rational(p['nominal_area_m2']),s.Rational(4,10**6))
        self.assertEqual(s.Rational(p['nominal_volume_m3']),s.Rational(12,10**10))
        self.assertEqual(s.Rational(p['temperature_K']),s.Rational(40815,100))
        self.assertFalse(p['converted_values_are_hard_intervals'])

    def test_frequency_is_not_DC_or_angular_frequency(self):
        p=self.result['transformations']
        self.assertEqual(p['frequency_Hz'],'10000')
        self.assertTrue(a.equal(s.sympify(p['omega_rad_s']),20000*s.pi))
        self.assertNotEqual(p['frequency_Hz'],p['omega_rad_s'])

    def test_wrong_frequency_unit_and_float_rejected(self):
        d=deepcopy(self.data);d['facts'][4]['unit']='Hz'
        with self.assertRaises(ValueError):a.validate_subset(d)
        with self.assertRaises(ValueError):a.exact(0.3)
        with self.assertRaises(ValueError):a.exact(True)

    def test_native_derivative_factors(self):
        self.assertTrue(a.equal(self.math['curvature'].coeff(a.P,4),5*a.Gn))
        self.assertTrue(a.equal(self.math['curvature'].coeff(a.P,6),7*a.Dn))
        self.assertTrue(a.equal(s.diff(self.math['native'],a.P).coeff(a.P,5),a.Gn))

    def test_conditional_series_and_sextic_absence(self):
        red=self.math['reduced']
        self.assertEqual(red.coeff(a.C,6),0)
        self.assertEqual(red.coeff(a.C,10),0)
        self.assertEqual(s.diff(red,a.C).coeff(a.C,5),0)
        self.assertEqual(s.diff(red,a.C,2).coeff(a.C,4),0)

    def test_linear_physical_scaling_keeps_sextic_nonzero(self):
        P0,f0=s.symbols('P0 f0',positive=True)
        scaled=self.math['native'].subs(a.P,P0*a.C)/f0
        self.assertTrue(a.equal(s.diff(scaled,a.C,6).subs(a.C,0),120*a.Gn*P0**6/f0))

    def test_degenerate_prestress_source_ensemble_rejected(self):
        for kwargs in [{'a_phi':0},{'a_phi':-1},{'reference_phi':1},
                       {'mechanical_source':1},{'ensemble':'fixed_D'}]:
            with self.assertRaises(ValueError):a.reduction_scope(**kwargs)
        a.reduction_scope()

    def test_coordinate_shift_cannot_drop_cubic(self):
        self.assertNotEqual(self.math['shifted_cubic'],0)
        self.assertTrue(self.result['checks']['strain_shift_generates_cubic'])

    def test_negative_relaxed_quartic_is_not_negative_bare(self):
        k,Q=s.symbols('k Q',positive=True)
        # A symbolic counterexample family, not a material fit.
        bare=k*Q**2
        relaxed=bare-2*k*Q**2
        self.assertTrue(bare.is_positive)
        self.assertTrue(relaxed.is_negative)
        self.assertTrue(self.result['checks']['Q_vs_energy_coupling_factor2'])

    def test_dimensions_density_volume_and_coefficient_bases(self):
        self.assertTrue(all(a.dimensions().values()))

    def test_dielectric_background_and_even_readout(self):
        self.assertTrue(self.result['checks']['permittivity_background_relation'])
        self.assertTrue(self.result['checks']['native_dielectric_map_even'])
        self.assertTrue(self.result['checks']['strain_P_squared_map_even'])

    def test_missing_alpha_covariance_and_scales_stay_unknown(self):
        d=self.result['point_diagnostics']
        for k in ['native_alpha','fit_covariance','scale_dictionary','Core_predicted_curve','Var_Phi']:
            self.assertIsNone(d[k])
        self.assertFalse(d['residual_is_full_error_bound'])

    def test_biased_phase_is_not_retained_memory(self):
        d=deepcopy(self.data);d['policy']['biased_branch_is_retained_memory']=True
        with self.assertRaises(ValueError):a.validate_subset(d)

    def test_physical_work_is_not_injection_work(self):
        self.assertTrue(self.result['checks']['force_port_vs_injection_work_difference'])
        d=deepcopy(self.data);d['policy']['physical_work_is_old_injection_work']=True
        with self.assertRaises(ValueError):a.validate_subset(d)

    def test_all_promotion_flags_rejected(self):
        for key in a.POLICY:
            d=deepcopy(self.data);d['policy'][key]=True
            with self.assertRaises(ValueError):a.validate_subset(d)

    def test_conditional_difference_not_physical_falsification(self):
        verdicts={x['interface']:x['outcome'] for x in self.result['correspondence_verdicts']}
        self.assertEqual(verdicts['conditional_reduced_polynomials'],'DIFFERENT')
        self.assertEqual(verdicts['full_joint_potential_and_ensemble'],'UNRESOLVED')
        self.assertFalse(self.result['physical_acceptance'])

    def test_offline_and_no_old_producer(self):
        with patch.object(socket,'socket',side_effect=AssertionError('offline')),\
             patch.object(a.old,'calculate',side_effect=AssertionError('old calculate')),\
             patch.object(a.old,'algebra',side_effect=AssertionError('old algebra')),\
             patch.object(a.old,'main',side_effect=AssertionError('old main')):
            r=a.calculate()
        self.assertFalse(r['old_producers_rerun'])
        self.assertEqual(r['new_core_terms'],0)

    def test_check_read_only(self):
        r={'checks':{},'negative_controls':{},'contract_review_status':'INCOMPLETE'}
        payload=json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
        with patch.object(a,'record',return_value=r),patch.object(Path,'is_file',return_value=True),\
             patch.object(Path,'read_bytes',return_value=payload.encode()),\
             patch.object(Path,'write_text',side_effect=AssertionError('read only')):
            self.assertEqual(a.main(['--check']),0)

    def test_emit_only_own_artifact(self):
        r={'checks':{},'negative_controls':{},'contract_review_status':'INCOMPLETE'}
        with patch.object(a,'record',return_value=r),patch.object(Path,'write_text',autospec=True) as write:
            self.assertEqual(a.main(['--emit-report']),0)
        self.assertEqual(write.call_count,1)
        self.assertEqual(write.call_args.args[0],a.ROOT/a.OUTPUT)

    def test_stale_identity_stops_before_calculate(self):
        c=deepcopy(a.load_json(a.ROOT/a.CONTRACT));c['identities'][0]['sha256']='0'*64
        with patch.object(a,'load_json',return_value=c),\
             patch.object(a,'calculate',side_effect=AssertionError('stop before compute')):
            with self.assertRaises(ValueError):a.record()

    def test_contract_record_deterministic_and_diagnostic(self):
        r=a.record();self.assertEqual(r,a.record())
        self.assertEqual(r['contract_review_status'],'INCOMPLETE')
        self.assertFalse(r['physical_acceptance'])
        c=a.load_json(a.ROOT/a.CONTRACT)
        self.assertEqual(c['profile'],'PHYSICAL_COMPARISON')
        self.assertEqual(c['output']['claim_intent'],'DIAGNOSTIC')


if __name__=='__main__':unittest.main()
