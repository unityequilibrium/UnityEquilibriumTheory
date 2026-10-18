from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("route_admission",Path(__file__).with_name("Research_T13_Physical_Route_Admission.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PhysicalRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=m.load_json(m.ROOT/m.SOURCE)
        cls.p=cls.source["supplement"]["table_s1_model_values"]

    def test_native_source_configuration_not_physical_acceptance(self):
        r=m.calculate(self.source)
        self.assertFalse(r["physical_acceptance"])
        self.assertEqual(r["experimental_rows_scored"],0)
        self.assertEqual(len(r["unmet_prerequisites"]),7)

    def test_voltage_square_identity(self):
        dc,ac=Q(54),Q(1,2)
        c0,c1,c2=m.voltage_harmonics(dc,ac)
        for c in (Q(-1),Q(-1,2),Q(0),Q(1,3),Q(1)):
            self.assertEqual((dc+ac*c)**2,c0+c1*c+c2*(2*c*c-1))

    def test_reported_voltage_convention_ratio(self):
        _,f,s=m.voltage_harmonics(Q(54),Q(1,2))
        self.assertEqual(s/f,Q(1,432))

    def test_no_dc_does_not_mean_harmonic_force_at_voltage_frequency(self):
        c0,c1,c2=m.voltage_harmonics(Q(0),Q(5))
        self.assertEqual(c1,0)
        self.assertEqual(c0,c2)
        self.assertGreater(c2,0)

    def test_dc_branch_residual_is_certified(self):
        r=m.dc_state(self.p,Q(54))
        lo,hi=r["y_interval"]
        wn,k,b=(Q(self.p[x]) for x in ("wn2","k32","beta2"))
        f=lambda y:wn**2*y+k*y**3-b*54**2/(1-y)**2
        self.assertLessEqual(f(lo),0)
        self.assertGreaterEqual(f(hi),0)
        self.assertGreater(r["monotonicity_lower_bound"],0)
        self.assertLessEqual(hi-lo,Q(1,2**50))

    def test_bias_changes_local_operator_not_just_drive_amplitude(self):
        zero=m.dc_state(self.p,Q(0))
        biased=m.dc_state(self.p,Q(54))
        self.assertEqual(zero["y_interval"],[0,0])
        self.assertEqual(zero["auxiliary_frequency_squared_interval"],[Q(self.p["wn2"])**2]*2)
        self.assertLess(biased["auxiliary_frequency_squared_interval"][1],zero["auxiliary_frequency_squared_interval"][0])

    def test_voltage_sign_does_not_change_pure_dc_branch(self):
        self.assertEqual(m.dc_state(self.p,Q(54)),m.dc_state(self.p,Q(-54)))

    def test_native_root_domain_refuses_high_voltage(self):
        with self.assertRaises(ValueError):
            m.dc_state(self.p,Q(200))

    def test_numerical_budget_is_bounded(self):
        for n in (0,65):
            with self.assertRaises(ValueError):
                m.dc_state(self.p,Q(54),n)

    def test_nested_brackets_refine(self):
        wide=m.dc_state(self.p,Q(54),32)["y_interval"]
        narrow=m.dc_state(self.p,Q(54),48)["y_interval"]
        self.assertLessEqual(wide[0],narrow[0])
        self.assertLessEqual(narrow[1],wide[1])

    def test_gap_bound_and_pole_guard(self):
        a=Q(1,10)
        lo,hi=m.gap_enclosure(a)
        for u in (-a,Q(0),a):
            self.assertLessEqual(lo,1/(1-u)**2)
            self.assertLessEqual(1/(1-u)**2,hi)
        for bad in (Q(-1),Q(1),Q(2)):
            with self.assertRaises(ValueError):
                m.gap_enclosure(bad)

    def test_inertial_harmonic_identity(self):
        for c in (Q(-1),Q(-1,2),Q(0),Q(1,3),Q(1)):
            derivative_form=c*(1-c*c)-c**3
            harmonic_form=-(c+(4*c**3-3*c))/2
            self.assertEqual(derivative_form,harmonic_form)


if __name__=="__main__":
    unittest.main()
