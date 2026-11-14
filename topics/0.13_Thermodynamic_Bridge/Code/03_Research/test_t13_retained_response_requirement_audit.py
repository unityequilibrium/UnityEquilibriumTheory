"""Regression and adversarial checks of the declared response audit, not a material test."""
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
a=importlib.import_module("Research_T13_Retained_Response_Requirement_Audit")


class RetainedResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.math=a.algebra()
        cls.checks=a.symbolic_checks()
        cls.controls=a.negative_controls()

    def test_all_exact_checks(self):
        self.assertTrue(all(self.checks.values()),self.checks)

    def test_all_negative_controls(self):
        self.assertTrue(all(self.controls.values()),self.controls)

    def test_canonical_rhs_extracted_without_running_core(self):
        self.assertTrue(a.equal(a.source_drift(),self.math['drift']))

    def test_wrong_source_port_detected(self):
        text=(a.ROOT/a.CORE).read_text(encoding='utf-8')
        text=text.replace('dC = -config.mobility_matter * mu_matter + matter_drive',
                          'dC = -config.mobility_matter * mu_matter - matter_drive')
        self.assertFalse(a.equal(a.source_drift(text),self.math['drift']))

    def test_unmapped_source_arithmetic_fails_closed(self):
        import ast
        with self.assertRaises(ValueError):a.expression(ast.parse('mystery(C)',mode='eval').body,{'C':a.C})

    def test_reject_duplicate_source_assignment(self):
        import ast
        with self.assertRaises(ValueError):a.assignment(ast.parse('x=1\nx=2').body,'x')

    def test_two_ports_and_four_readouts_are_declared(self):
        self.assertEqual(self.math['B'].shape,(3,2))
        self.assertEqual(self.math['models'][1]['H'].shape,(4,2))
        a.validate_protocol(a.protocol())

    def test_baseline_subtraction_is_not_optional(self):
        p=a.protocol();p['baseline_subtracted']=False
        with self.assertRaises(ValueError):a.validate_protocol(p)

    def test_retuning_is_not_internal_learning(self):
        p=a.protocol();p['fixture']['coupling_g']=2
        with self.assertRaises(ValueError):a.validate_protocol(p)

    def test_missing_readout_factor_is_detected(self):
        self.assertTrue(self.checks['baseline_readout_derivative'])
        self.assertTrue(self.controls['omitted_C_squared_derivative_detected'])

    def test_magnitude_readout_is_not_magnitude_of_transfer(self):
        self.assertTrue(self.checks['local_absolute_readout_uses_branch_derivative'])
        # delta(C^2)=2*C_star*delta C, not (delta C)^2.
        self.assertNotEqual(s.diff(a.C**2,a.C).subs(a.C,a.c),0)

    def test_source_and_output_parities_both_required(self):
        self.assertTrue(self.checks['transfer_input_output_parity'])
        self.assertTrue(self.controls['omitted_input_reflection_detected'])

    def test_mixed_input_claim_cannot_be_inferred(self):
        p=a.protocol();p['ports_applied_separately']=False
        with self.assertRaises(ValueError):a.validate_protocol(p)
        self.assertTrue(self.controls['mixed_inputs_not_covered_by_single_port_magnitude'])

    def test_mixed_output_claim_has_counterexample(self):
        self.assertTrue(self.controls['mixed_readout_not_covered_by_separate_channels'])

    def test_finite_amplitude_scope_rejected(self):
        p=a.protocol();p['regime']='finite_amplitude_switching'
        with self.assertRaises(ValueError):a.validate_protocol(p)
        self.assertTrue(self.controls['finite_amplitude_has_nonzero_quadratic_readout_remainder'])

    def test_energy_stability_has_no_zero_loss_mode(self):
        self.assertTrue(self.checks['energy_matrix_and_loss_identity'])
        self.assertTrue(self.checks['positive_energy_principal_minors'])
        self.assertTrue(self.checks['loss_and_one_derivative_have_no_hidden_mode'])

    def test_common_denominator_at_zero_positive(self):
        self.assertTrue(a.equal(self.math['D'].subs(a.z,0),a.c**2*(1+6*a.r**2)))

    def test_resource_is_configured_not_topology_state(self):
        d=a.resource_source_audit()
        self.assertTrue(d['config_frozen'])
        self.assertEqual(d['internal_config_writes'],[])
        self.assertTrue(d['fitness_uses_interaction_and_probability'])
        self.assertFalse(d['resource_enters_probability_update'])
        self.assertFalse(d['threshold_changes_update_inside_loop'])

    def test_new_resource_feedback_would_be_noticed(self):
        text=(a.ROOT/a.RESOURCE).read_text(encoding='utf-8').replace(
            'config.selection_weight * interaction[i]',
            'config.initial_available_resource * config.selection_weight * interaction[i]')
        self.assertTrue(a.resource_source_audit(text)['resource_enters_probability_update'])

    def test_dynamic_dependency_requires_renewed_review(self):
        text=(a.ROOT/a.RESOURCE).read_text(encoding='utf-8').replace(
            'resource = float(config.initial_available_resource)',
            'resource = getattr(config, "initial_available_resource")')
        with self.assertRaises(ValueError):a.resource_source_audit(text)

    def test_frozen_label_and_physical_promotion_rejected(self):
        for key in ['frozen_label_is_learned','physical_acceptance']:
            p=a.protocol();p[key]=True
            with self.assertRaises(ValueError):a.validate_protocol(p)

    def test_calculation_is_offline_and_does_not_run_old_simulator(self):
        with patch.object(socket,'socket',side_effect=AssertionError('no network')):
            result=a.calculate()
        self.assertFalse(result['old_producers_rerun'])
        self.assertEqual(result['trajectories'],0)
        self.assertEqual(result['parameter_sweeps'],0)

    def test_read_only_check_never_emits(self):
        result=a.calculate()
        result['contract_review_status']='INCOMPLETE'
        payload=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
        with patch.object(a,'record',return_value=result),patch.object(Path,'is_file',return_value=True),\
             patch.object(Path,'read_bytes',return_value=payload.encode('utf-8')),\
             patch.object(Path,'write_text',side_effect=AssertionError('check must not write')):
            self.assertEqual(a.main(['--check']),0)

    def test_emit_and_check_mutually_exclusive(self):
        with self.assertRaises(SystemExit):a.main(['--check','--emit-report'])

    def test_stale_identity_stops_before_calculation(self):
        contract=deepcopy(a.load_json(a.ROOT/a.CONTRACT))
        contract['identities'][0]['sha256']='0'*64
        with patch.object(a,'load_json',return_value=contract),\
             patch.object(a,'calculate',side_effect=AssertionError('must stop before computing')):
            with self.assertRaises(ValueError):a.record()

    def test_actual_contract_and_record_are_deterministic(self):
        result=a.record()
        self.assertEqual(result,a.record())
        self.assertEqual(result['contract_review_status'],'INCOMPLETE')
        self.assertFalse(result['physical_acceptance'])


if __name__=='__main__':unittest.main()
