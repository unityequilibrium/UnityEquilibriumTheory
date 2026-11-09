from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("dual_channel",Path(__file__).with_name("Research_T13_Dual_Channel_Identifiability.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class DualChannelTests(unittest.TestCase):
    def test_complete_synthetic_design(self):
        self.assertFalse(m.calculation()["physical_acceptance"])

    def test_static_ambiguity_global_not_just_rank(self):
        for y in (Q(-2),Q(1),Q(3)):
            for t in (Q(-5),Q(0),Q(7)):
                self.assertEqual(m.equilibrium(y,Q(4),Q(3),Q(2),Q(1)),
                                 m.equilibrium(y,Q(4),Q(3)+t/4,Q(2)+t,Q(1)))

    def test_passive_rows_remain_collinear(self):
        rows=[]
        for y in (Q(1),Q(2)):
            z,r=m.equilibrium(y,Q(4),Q(3),Q(2),Q(1))
            rows.append((y,z,r))
        with self.assertRaises(ValueError):
            m.identify(*rows)

    def test_independent_auxiliary_control_identifies(self):
        first, second = (Q(1),Q(1),Q(5)), (Q(1),Q(2),Q(7))
        self.assertEqual(m.identify(first,second),(Q(3),Q(2)))

    def test_auxiliary_zero_primary_rejected(self):
        with self.assertRaises(ValueError):
            m.auxiliary_coefficient(Q(0),Q(1))

    def test_mass_weighted_not_equal_acceleration_coefficients(self):
        ell,a,b=m.observed_coefficients(Q(2),Q(2),Q(4),Q(3),Q(5),Q(3))
        self.assertEqual(m.reciprocity_residual(a,b,Q(2),Q(4),Q(5,3)),0)
        self.assertNotEqual(a,b)

    def test_wrong_gain_calibration_fails_reciprocity(self):
        self.assertNotEqual(m.reciprocity_residual(Q(2,5),Q(5,18),Q(2),Q(4),Q(1)),0)

    def test_unknown_gain_can_hide_same_sign_mismatch(self):
        # a=2,b=4 with mq=1,mr=1 is made reciprocal by Gr/Gq=2.
        self.assertEqual(m.reciprocity_residual(Q(2),Q(4),Q(1),Q(1),Q(2)),0)

    def test_opposite_signs_cannot_be_fixed_by_real_gain_ratio(self):
        for gain in (Q(-2),Q(-1),Q(1),Q(2)):
            self.assertGreater(m.reciprocity_residual(Q(2),Q(-4),Q(1),Q(1),gain),0)

    def test_zero_coupling_ordinary_limit(self):
        _,a,b=m.observed_coefficients(Q(0),Q(2),Q(4),Q(3),Q(5),Q(3))
        self.assertEqual((a,b),(0,0))

    def test_invalid_mass_gain_and_stiffness(self):
        for mq,mr,gq,gr in ((0,1,1,1),(1,-1,1,1),(1,1,0,1),(1,1,1,0)):
            with self.assertRaises(ValueError):
                m.observed_coefficients(Q(1),Q(mq),Q(mr),Q(gq),Q(gr),Q(1))
        with self.assertRaises(ValueError):
            m.equilibrium(Q(1),Q(0),Q(1),Q(1),Q(1))


if __name__=="__main__":
    unittest.main()
