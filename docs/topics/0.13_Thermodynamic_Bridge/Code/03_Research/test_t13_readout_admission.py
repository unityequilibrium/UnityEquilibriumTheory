from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('readout_admission',Path(__file__).with_name('Research_T13_Readout_Admission.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class ReadoutAdmissionTests(unittest.TestCase):
    def test_verified_real_member_profile(self):
        r=m.calculate(); p=r['profile']
        self.assertEqual(p['rows'],1001)
        self.assertEqual(p['duplicate_detuning_count'],0)
        self.assertEqual(p['domain_counts'],{'below_central_ideal_minimum':9,'inside_central_ideal_domain':589,'at_or_above_unit_magnitude':403})
        self.assertTrue(r['input_crc_reconstruction_verified'])

    def test_rates_have_same_units_and_no_two_pi_conversion_is_duplicated(self):
        rows=[(Q(0),Q(1,2))]
        self.assertEqual(m.profile(rows,Q(68,100),Q(164,100))['central_ideal_minimum_magnitude'],'17/58')
        self.assertEqual(m.profile(rows,Q(68),Q(164)),m.profile(rows,Q(68,100),Q(164,100)))

    def test_domain_boundaries_are_not_clipped(self):
        rows=[(Q(i),v) for i,v in enumerate((Q(0),Q(17,58),Q(1),Q(3,2)))]
        p=m.profile(rows,Q(68),Q(164))
        self.assertEqual(p['domain_counts'],{'below_central_ideal_minimum':1,'inside_central_ideal_domain':1,'at_or_above_unit_magnitude':2})
        self.assertEqual(p['clipped_or_dropped_rows'],0)

    def test_duplicates_remain_visible_not_silently_deduplicated(self):
        p=m.profile([(Q(0),Q(1,2))]*2,Q(1),Q(1))
        self.assertEqual(p['rows'],2); self.assertEqual(p['duplicate_detuning_count'],1)
        self.assertEqual(p['exact_duplicate_row_count'],1)

    def test_schema_missing_nonfinite_and_negative_magnitude(self):
        header='sep=,\nFig 3 (panel c) Experiment\ndetuning Delta,S21 absolute\n'
        for tail in ('0,\n','0,NaN\n','0,inf\n','0,1,2\n',''):
            with self.assertRaises((ValueError,ZeroDivisionError)):
                m.parse_rows(header+tail)
        with self.assertRaises(ValueError): m.parse_rows(header.replace('Experiment','Simulation')+'0,1\n')
        with self.assertRaises(ValueError): m.profile([(Q(0),Q(-1))],Q(1),Q(1))

    def test_global_gain_cannot_fix_incompatible_dynamic_range(self):
        r=m.gain_enclosure([Q(1,5),Q(7,5)],Q(1,3))
        self.assertFalse(r['closed_envelope_gain_only_possible'])
        self.assertEqual(Q(r['optimistic_minimum_uniform_amplitude_error']),Q(1,5))
        self.assertEqual(Q(r['envelope_optimizer_NOT_adopted_gain']),Q(6,5))

    def test_minimax_certificate_balances_upper_and_lower_violation(self):
        values=[Q(1,7),Q(4,3),Q(2,3)]; lower=Q(17,58)
        r=m.gain_enclosure(values,lower)
        g=Q(r['envelope_optimizer_NOT_adopted_gain']); e=Q(r['optimistic_minimum_uniform_amplitude_error'])
        self.assertEqual(max(values)-g,e); self.assertEqual(g*lower-min(values),e)
        for other in (g/Q(2),g+Q(1),Q(1)):
            self.assertGreaterEqual(max(Q(0),max(values)-other,other*lower-min(values)),e)

    def test_noiseless_closed_envelope_is_not_strict_inverse_admission(self):
        r=m.gain_enclosure([Q(1,2),Q(1)],Q(1,2))
        self.assertTrue(r['closed_envelope_gain_only_possible'])
        self.assertEqual(r['optimistic_minimum_uniform_amplitude_error'],'0')
        self.assertFalse(r['applied_gain_correction'])
        self.assertFalse(r['estimated_noise_distribution'])
        # Closed endpoint can correspond to unit transmission, excluded by finite inverse.
        self.assertIn('necessary',r['boundary'])

    def test_real_curve_gain_bound_is_not_a_fitted_correction(self):
        r=m.calculate()['profile']['global_gain_enclosure']
        self.assertFalse(r['closed_envelope_gain_only_possible'])
        self.assertGreater(Q(r['optimistic_minimum_uniform_amplitude_error']),Q(19,100))
        self.assertFalse(r['applied_gain_correction'])

    def test_gain_enclosure_degenerate_and_critical_boundaries(self):
        r=m.gain_enclosure([Q(1,4),Q(2)],Q(0))
        self.assertTrue(r['closed_envelope_gain_only_possible'])
        self.assertIsNone(r['noiseless_gain_upper_bound'])
        for values,lower in (([],Q(1,2)),([Q(0)],Q(1,2)),([Q(-1),Q(1)],Q(1,2)),([Q(1)],Q(2))):
            with self.assertRaises(ValueError): m.gain_enclosure(values,lower)

    def test_no_automatic_physical_promotion_or_blind_holdout(self):
        r=m.calculate()
        for field in ('physical_acceptance','theory_rejection','new_held_out_rows','unknown_effects_assigned_zero'):
            self.assertFalse(r[field])
        self.assertEqual(r['physical_residual_rows_scored'],0)


if __name__=='__main__':
    unittest.main()
