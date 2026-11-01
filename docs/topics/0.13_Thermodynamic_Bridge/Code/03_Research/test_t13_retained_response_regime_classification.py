"""Exact/adversarial tests for the declared formal regime audit, not material tests."""
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
a=importlib.import_module("Research_T13_Retained_Response_Regime_Classification")


class RegimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.math=a.algebra()
        cls.write=a.write_algebra()
        cls.control=a.controls()
        cls.checks=a.symbolic_checks()
        cls.neg=a.negative_controls()

    def test_all_symbolic_groups(self):
        self.assertTrue(all(self.checks.values()),self.checks)

    def test_all_negative_controls(self):
        self.assertTrue(all(self.neg.values()),self.neg)

    def test_source_actual_domain(self):
        self.assertEqual(a.source_domain()['nonnegative'],['a_space','coupling_g'])
        self.assertIn('finite real',a.source_domain()['a_matter'])

    def test_source_domain_widening_detected(self):
        text=(a.ROOT/a.CORE).read_text(encoding='utf-8')
        with self.assertRaises(ValueError):a.source_domain(text.replace('self.a_space < 0.0','self.a_space < -1.0'))

    def test_positive_parameter_check_change_detected(self):
        text=(a.ROOT/a.CORE).read_text(encoding='utf-8')
        with self.assertRaises(ValueError):a.source_domain(text.replace('<= 0.0', '< 0.0',1))

    def test_rhs_source_sign_change_detected(self):
        text=(a.ROOT/a.CORE).read_text(encoding='utf-8').replace(
            'dC = -config.mobility_matter * mu_matter + matter_drive',
            'dC = -config.mobility_matter * mu_matter - matter_drive')
        self.assertFalse(a.equal(a.source_law(text)[2],self.math['drift']))

    def test_negative_a_space_cannot_create_a_new_branch(self):
        p=list(a.COEX);p[2]=-1
        with self.assertRaises(ValueError):a.regime(p)

    def test_invalid_float_zero_mobility_or_coupling(self):
        for index,value in [(0,0.375),(5,0),(4,-1)]:
            p=list(a.COEX);p[index]=value
            with self.assertRaises(ValueError):a.validate_parameters(p)

    def test_origin_is_not_lost(self):
        self.assertTrue(a.equal(self.math['force'].subs({a.C:0,a.Phi:0}),s.zeros(2,1)))
        self.assertTrue(self.control['coexistence']['origin_is_strict_minimum'])

    def test_all_three_exact_roots_checked_for_admissibility(self):
        branches=self.control['branches']
        self.assertEqual([r['admissible'] for r in branches],[False,True,True])
        self.assertEqual([r['disposition'] for r in branches],['inadmissible','saddle_pair','strict_minimum_pair'])
        cubic=self.math['cubic'].subs(dict(zip(a.PARAMS,a.COEX)))
        self.assertTrue(all(a.equal(cubic.subs(a.Phi,s.sympify(row['Phi'])),0) for row in branches))

    def test_two_predeclared_controls(self):
        self.assertEqual(self.control['coexistence']['discriminant_numerator'],'13/64')
        self.assertEqual(self.control['noncoexistence']['A'],'-1/2')
        self.assertEqual(self.control['coexistence']['nonzero_minimum_pairs'],1)
        self.assertEqual(self.control['noncoexistence']['nonzero_minimum_pairs'],0)

    def test_critical_origin_complete_square_and_flat_boundary(self):
        V=self.math['potential'].subs({a.a:0,a.alpha:a.g**2/(2*a.b)})
        self.assertTrue(a.equal(V,a.b*(a.C**2-a.g*a.Phi/a.b)**2/4+a.beta*a.Phi**4/4))
        # Positive quartic Phi makes the zero-eigenvalue origin strict, not unstable.
        self.assertTrue(a.equal(V.subs({a.C:0,a.Phi:0}),0))

    def test_saddle_node_has_odd_leading_energy(self):
        d=s.Symbol('d',positive=True)
        # A=3 beta d^2, B=2 beta d^3 pins the positive double root.
        cubic=a.beta*a.Phi**3-3*a.beta*d**2*a.Phi+2*a.beta*d**3
        self.assertTrue(a.equal(cubic,a.beta*(a.Phi-d)**2*(a.Phi+2*d)))
        primitive=s.integrate(cubic,a.Phi)
        self.assertTrue(a.equal(s.diff(primitive,a.Phi,3).subs(a.Phi,d)/6,a.beta*d))

    def test_decoupling_is_not_two_opposite_Phi_states(self):
        mu_phi=self.math['force'][1].subs(a.g,0)
        self.assertTrue(a.equal(mu_phi,a.Phi*(a.alpha+a.beta*a.Phi**2)))
        self.assertTrue(a.equal(self.math['Hessian'][0,1].subs(a.g,0),0))

    def test_Hessian_controls_stability_not_discriminant_alone(self):
        self.assertTrue(self.checks['full_Hessian_determinant_is_2bC_squared_pprime'])
        self.assertEqual(self.control['branches'][1]['disposition'],'saddle_pair')
        self.assertTrue(self.checks['algebraic_minimum_has_positive_Hessian'])

    def test_energy_offset_is_not_erased(self):
        self.assertTrue(a.equal(self.control['final_energy_difference'],(-83+26*s.sqrt(13))/256))
        self.assertGreater(26**2*13-83**2,0)
        self.assertFalse(a.equal(self.control['final_energy_difference'],0))

    def test_full_resolvent_static_inverse_and_tau(self):
        for key in ['full_resolvent_equals_eliminated_transfer','DC_is_Hessian_inverse_with_source_mobilities',
                    'characteristic_denominator_has_tau_factor','source_ports_include_tau',
                    'zero_nonzero_CJC_transfer_difference']:
            self.assertTrue(self.checks[key])

    def test_positive_energy_excludes_hidden_zero_loss_mode(self):
        self.assertTrue(self.checks['quadratic_energy_stability_identity'])
        self.assertTrue(self.checks['zero_loss_mode_excluded_when_Hessian_SPD'])

    def test_C_gain_magnitude_difference_is_exact(self):
        self.assertEqual(self.control['origin_C_JC_DC_gain'],s.Rational(8,3))
        self.assertFalse(a.equal(self.control['gain_difference'],0))
        self.assertTrue(self.checks['gain_contrast_is_not_only_baseline'])

    def test_origin_cross_channel_zero_no_relative_error(self):
        self.assertTrue(a.equal(self.math['T'][0,1].subs({a.v:0,a.k:a.a,a.h:a.alpha}),0))
        self.assertTrue(self.neg['zero_gain_relative_error_scope_guard'])

    def test_signed_pair_input_output_symmetry(self):
        self.assertTrue(self.checks['signed_pair_symmetry_includes_sources_readouts'])
        self.assertTrue(self.neg['baseline_difference_not_a_gain_proof'])

    def test_squared_and_absolute_readout_at_origin(self):
        self.assertTrue(self.neg['origin_squared_readout_derivative_is_zero'])
        self.assertTrue(self.neg['origin_absolute_readout_one_sided_derivatives_disagree'])

    def test_U_reuse_without_any_old_producer(self):
        with patch.object(a.u,'calculate',side_effect=AssertionError('no old calculation')),\
             patch.object(a.u,'algebra',side_effect=AssertionError('no old algebra')),\
             patch.object(a.u,'main',side_effect=AssertionError('no old main')):
            self.assertTrue(a.inherited_u_check()['response_recovered'])

    def test_protocol_retuning_mixed_and_physical_claims_fail(self):
        for key in ['same_coefficients_for_histories','ports_applied_separately','baseline_subtracted',
                    'physical_acceptance','lifetime_claim','topology_learning','new_UET_discriminator',
                    'static_elimination_as_dynamics']:
            p=a.protocol();p[key]=not p[key]
            with self.assertRaises(ValueError):a.validate_protocol(p)
        bad=list(a.COEX);bad[4]+=1
        with self.assertRaises(ValueError):a.validate_history_coefficients(a.COEX,bad)
        a.validate_history_coefficients(a.COEX,a.COEX)
        self.assertTrue(self.neg['instantaneous_Phi_elimination_changes_response'])
        self.assertTrue(self.neg['higher_local_minimum_is_not_global'])

    def test_quintic_endpoints_continuous_not_C_infinity(self):
        self.assertTrue(self.checks['quintic_endpoint_state_rate_acceleration'])
        self.assertTrue(self.checks['write_inputs_and_endpoint_sources'])
        self.assertTrue(self.neg['quintic_is_not_infinitely_smooth_after_extension'])

    def test_write_identity_and_independent_polynomial_integration(self):
        for key in ['full_state_pointwise_energy_ledger','write_path_pointwise_ledger',
                    'independently_integrated_write_balance','exact_regression_write_balance',
                    'positive_Pi_loss_for_nonzero_target','zero_target_has_zero_work_loss',
                    'prescribed_write_satisfies_full_RHS']:
            self.assertTrue(self.checks[key])
        self.assertFalse(a.equal(self.control['write_work'],0))

    def test_wrong_ledger_port_factor_breaks_balance(self):
        self.assertTrue(self.neg['wrong_JPhi_work_normalization_breaks_ledger'])

    def test_offline_calculation_no_simulation(self):
        with patch.object(socket,'socket',side_effect=AssertionError('offline')),\
             patch.object(a.u,'calculate',side_effect=AssertionError('old producer')):
            result=a.calculate()
        for key in ['trajectories','parameter_sweeps','numerical_roots','new_model_terms']:
            self.assertEqual(result[key],0)
        self.assertFalse(result['old_producers_rerun'])

    def test_read_only_check_never_writes(self):
        result={'checks':{},'negative_controls':{},'contract_review_status':'INCOMPLETE'}
        payload=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
        with patch.object(a,'record',return_value=result),patch.object(Path,'is_file',return_value=True),\
             patch.object(Path,'read_bytes',return_value=payload.encode('utf-8')),\
             patch.object(Path,'write_text',side_effect=AssertionError('read only')):
            self.assertEqual(a.main(['--check']),0)

    def test_emit_has_only_one_declared_write(self):
        result={'checks':{},'negative_controls':{},'contract_review_status':'INCOMPLETE'}
        with patch.object(a,'record',return_value=result),patch.object(Path,'write_text',autospec=True) as write:
            self.assertEqual(a.main(['--emit-report']),0)
        self.assertEqual(write.call_count,1)
        self.assertEqual(write.call_args.args[0],a.ROOT/a.OUTPUT)

    def test_emit_check_exclusive(self):
        with self.assertRaises(SystemExit):a.main(['--check','--emit-report'])

    def test_stale_identity_stops_before_calculation(self):
        contract=deepcopy(a.load_json(a.ROOT/a.CONTRACT));contract['identities'][0]['sha256']='0'*64
        with patch.object(a,'load_json',return_value=contract),\
             patch.object(a,'calculate',side_effect=AssertionError('must not calculate')):
            with self.assertRaises(ValueError):a.record()

    def test_actual_contract_and_record_deterministic(self):
        result=a.record()
        self.assertEqual(result,a.record())
        self.assertEqual(result['contract_review_status'],'INCOMPLETE')
        self.assertFalse(result['physical_acceptance'])
        self.assertFalse(result['new_UET_discriminator'])


if __name__=='__main__':unittest.main()
