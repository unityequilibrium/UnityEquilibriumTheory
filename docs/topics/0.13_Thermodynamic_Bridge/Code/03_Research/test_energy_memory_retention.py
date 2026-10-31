from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

import numpy as np

spec = importlib.util.spec_from_file_location(
    "retention", Path(__file__).with_name("Research_Energy_Memory_Retention.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RetentionStructureTests(unittest.TestCase):
    def test_unique_equilibrium_root_enclosure(self):
        lo, hi = m.equilibrium_bracket()
        f = lambda r: r**3 + r / 2 - Q(1, 2)
        self.assertLessEqual(f(lo), 0)
        self.assertGreaterEqual(f(hi), 0)
        self.assertLessEqual(hi-lo, Q(1, 2**60))

    def test_stationary_minima_and_hessian(self):
        p = m.reference_state()
        c, phi, _ = p
        self.assertGreater(2*c*c, 0)
        self.assertGreater(c*c*(1+6*phi*phi), 0)
        np.testing.assert_allclose(m.evolution(0, np.r_[p, 0., 0.])[:3], 0., atol=1e-14)
        p[0] *= -1
        np.testing.assert_allclose(m.evolution(0, np.r_[p, 0., 0.])[:3], 0., atol=1e-14)

    def test_reflection_symmetry_including_ledgers_and_common_phi_drive(self):
        a = np.array([1.1, 0.2, -0.3, 0., 0.])
        b = a.copy(); b[0] *= -1
        ra, rb = m.evolution(0., a, .001), m.evolution(0., b, .001)
        expected = ra.copy(); expected[0] *= -1
        np.testing.assert_array_equal(rb, expected)
        self.assertEqual(m.energy(a), m.energy(b))

    def test_local_energy_identity_on_an_exact_binary_rational_state(self):
        y = np.array([1., 0.5, -0.25, 0., 0.])
        rate = m.evolution(0., y, .001)
        c, phi, pi = y[:3]
        mu_c = -c+c**3-c*phi
        mu_p = phi+phi**3-c*c/2
        derivative = mu_c*rate[0] + mu_p*rate[1] + pi*rate[2]
        self.assertAlmostEqual(derivative+rate[3]-rate[4], 0., places=14)

    def test_zero_C_is_an_invariant_state_coordinate_without_C_drive(self):
        for phi, pi in ((0., 1.), (-2., .1), (.5, 0.)):
            self.assertEqual(m.evolution(0., np.array([0., phi, pi, 0., 0.]))[0], 0.)

    def test_basin_write_ramp_matches_existing_RHS(self):
        cstar, r, _ = m.reference_state()
        for sign in (1., -1.):
            for t in (0., .5, 1.):
                s = 3*t*t-2*t**3
                ds, dds = 6*t-6*t*t, 6-12*t
                y = np.array([sign*cstar*s, r*s, r*ds])
                state = m.fields(y)
                muc, mup = m.model.matter_space_chemical_potentials(state, m.DX, m.CONFIG)
                jc = np.full(4, sign*cstar*ds) + muc
                jp = np.full(4, r*dds+r*ds) + mup
                rhs = m.model.matter_space_rhs(state, m.DX, m.CONFIG, jc, jp)
                np.testing.assert_allclose([x[0] for x in rhs[:3]],
                                           [sign*cstar*ds, r*ds, r*dds], atol=1e-13)


if __name__ == "__main__":
    unittest.main()
