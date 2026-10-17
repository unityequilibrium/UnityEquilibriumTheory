from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('source_feedback',Path(__file__).with_name('Research_T13_Source_Feedback.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class SourceFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=m.load_json(m.ROOT/m.SOURCE)

    def test_general_incident_polynomial_has_correct_source_operator(self):
        k,b,a,d,g=Q(2),Q(3),Q(4,5),Q(-1,3),Q(7,5)
        cs=m.incident_source_coefficients(k,b,a,d,g)
        for x in map(Q,(-2,-1,0,1,2,3)):
            self.assertEqual(m.evaluate_source(cs,x),(k*x+b*x**3)*(a*a+(d+g*x)**2))

    def test_zero_duffing_mechanics_has_apparent_cubic_incident_curve(self):
        cs=m.incident_source_coefficients(Q(1),Q(0),Q(3,4),Q(0),Q(1))
        self.assertEqual(cs,(Q(9,16),0,1,0,0))
        self.assertGreater(cs[2],0)
        for x in (Q(1,2),Q(1),Q(3,2)):
            q=m.evaluate_source(cs,x)
            n=q/(Q(9,16)+x*x)
            self.assertEqual(n,x)  # Correct internal source restores a LINEAR law.

    def test_detuning_and_duffing_add_even_and_quintic_terms(self):
        cs=m.incident_source_coefficients(Q(1),Q(2),Q(3,4),Q(1,2),Q(1))
        self.assertNotEqual(cs[1],0); self.assertNotEqual(cs[3],0); self.assertGreater(cs[4],0)

    def test_exact_drift_determinant_matches_characteristic(self):
        self.assertEqual(m.check_characteristic_at_fixed_point(Q(1),Q(3,5),Q(4,5)),5)
        self.assertEqual(m.check_characteristic_at_fixed_point(Q(9,16),Q(3,5),Q(9,20)),5)

    def test_inconsistent_fixed_point_is_refused(self):
        with self.assertRaises(ValueError):
            m.check_characteristic_at_fixed_point(Q(1),Q(1),Q(1))

    def test_hurwitz_certificate_is_positive_polynomial_not_sweep_claim(self):
        # H3 is quadratic in t; exact equality at three points certifies this identity.
        for t in (Q(0),Q(1,4),Q(1)):
            cs=(Q(23,2),Q(265,16)+t,Q(57,8)+10*t,Q(9,16)+3*t)
            h2,h3,stable=m.hurwitz(cs)
            self.assertEqual(h2,Q(5867,32)+Q(3,2)*t)
            self.assertEqual(h3,Q(315375,256)+Q(11579,8)*t+15*t*t)
            self.assertTrue(stable)
        self.assertTrue(all(x>0 for x in (Q(315375,256),Q(11579,8),Q(15))))

    def test_positive_characteristic_coefficients_alone_do_not_certify_stability(self):
        cs=m.characteristic_coefficients(Q(1,10),Q(1,100),Q(1),Q(1),Q(1),Q(10),Q(1))
        self.assertTrue(all(x>0 for x in cs))
        self.assertFalse(m.hurwitz(cs)[2])

    def test_magnitude_recovers_occupation_but_not_detuning_sign(self):
        for delta in (Q(-1),Q(1)):
            tr,ti=m.transmission_components(Q(3,4),Q(1,2),delta)
            n,delta2=m.infer_occupation(Q(3,4),Q(1,2),Q(25,8),tr*tr+ti*ti)
            self.assertEqual(n,1); self.assertEqual(delta2,1)

    def test_complex_port_recovers_signed_detuning(self):
        for delta in (Q(-1),Q(1)):
            tr,ti=m.transmission_components(Q(3,4),Q(1,2),delta)
            self.assertEqual(m.infer_complex_port(Q(1,2),tr,ti),(Q(3,4),delta))

    def test_complex_mismatch_can_also_ambiguate_internal_occupation(self):
        occupations=[]
        for delta in (Q(0),Q(-16,7)):
            self.assertEqual(m.mismatch_magnitude_squared(Q(1),Q(1,2),Q(3,5),Q(4,5),delta),Q(13,20))
            occupations.append(1/(1+delta*delta))
        self.assertEqual(occupations,[Q(1),Q(49,305)])
        self.assertNotEqual(occupations[0],occupations[1])

    def test_unverified_complex_phase_is_not_assumed_normalized(self):
        with self.assertRaises(ValueError):
            m.mismatch_magnitude_squared(Q(1),Q(1,2),Q(1),Q(1),Q(0))

    def test_absolute_csv_value_must_be_squared(self):
        # Critical hanger: magnitude=4/5 at delta=1, a=port=3/4.
        flux=Q(25,12)
        correct=m.infer_occupation(Q(3,4),Q(3,4),flux,Q(16,25))[0]
        wrong=m.infer_occupation(Q(3,4),Q(3,4),flux,Q(4,5))[0]
        self.assertEqual(correct,1); self.assertNotEqual(correct,wrong)

    def test_invalid_or_singular_inverse_is_not_clipped(self):
        for r in (Q(-1),Q(1),Q(2),Q(1,10)):
            with self.assertRaises(ValueError):
                m.infer_occupation(Q(1),Q(1,2),Q(1),r)
        with self.assertRaises(ValueError):
            m.infer_complex_port(Q(1,2),Q(1),Q(0))
        for p in (Q(0),Q(2)):
            with self.assertRaises(ValueError):
                m.transmission_components(Q(1),p,Q(1))

    def test_actual_member_headers_override_generic_readme_separator(self):
        rows=m.inspect_curated_headers(self.source)
        self.assertEqual(self.source['data_record']['readme']['advertised_separator'],'semicolon')
        self.assertEqual({r['delimiter'] for r in rows},{','})
        self.assertEqual({r['role'] for r in rows},{'experiment','simulation'})
        self.assertTrue(all(r['columns']==['detuning Delta','S21 absolute'] for r in rows))

    def test_header_drift_requires_new_review(self):
        s=deepcopy(self.source); s['headers'][0]['header']=s['headers'][0]['header'].replace('absolute','complex')
        with self.assertRaises(ValueError):
            m.inspect_curated_headers(s)

    def test_numeric_exposure_is_not_hidden_as_header_scope(self):
        s=deepcopy(self.source); s['headers'][0]['numeric_rows_decoded']=1
        with self.assertRaises(ValueError):
            m.inspect_curated_headers(s)

    def test_no_physical_score_or_archive_acquisition_claim(self):
        r=m.calculate(self.source)
        self.assertFalse(r['physical_acceptance']); self.assertEqual(r['numeric_rows_scored'],0)
        self.assertEqual(r['numeric_rows_decoded'],0); self.assertFalse(r['large_archive_download'])
        self.assertEqual(r['new_UET_terms'],0)
        self.assertEqual(r['admission']['static_cubic_source_score'],'NOT_ADMITTED')


if __name__=='__main__':
    unittest.main()
