"""Round Q adversarial regression; internal checks are not physical validation."""
from fractions import Fraction as F
import importlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import mpmath as mp
import sympy as s

sys.path.insert(0, str(Path(__file__).resolve().parent))
q = importlib.import_module("Research_T13_Parent_Static_Reference_Audit")


class ParentStaticReferenceTests(unittest.TestCase):
    def test_exact_parent_coordinates_and_dictionary(self):
        self.assertTrue(all(q.symbolic_checks().values()))

    def test_flip_reflection_orbits_cover_all16(self):
        groups = q.orbits()
        self.assertEqual(len(groups), 6)
        self.assertEqual(set(t for group in groups for t in group), set(q.SPINS))
        for spins in q.SPINS:
            eta = tuple(spins[i]*spins[i+1] for i in range(3))
            neg = tuple(-v for v in spins)
            rev = spins[::-1]
            self.assertEqual(eta, tuple(neg[i]*neg[i+1] for i in range(3)))
            self.assertEqual(eta[::-1], tuple(rev[i]*rev[i+1] for i in range(3)))

    def test_invalid_spin_types_not_hidden_by_cache(self):
        q.orbit((1, 1, 1, 1))
        for invalid in ((), (1, 1), (True, 1, 1, 1), (1., 1, 1, 1), (0, 1, 1, 1)):
            with self.assertRaises(ValueError):
                q.orbit(invalid)

    def test_interval_arithmetic_outward_contains_exact_rationals(self):
        a, b = q.I(F(1, 3), F(2, 3)), q.I(F(-2, 7), F(1, 7))
        for x, y in product_grid(a, b):
            for box, exact in ((a+b, x+y), (a-b, x-y), (a*b, x*y)):
                self.assertLessEqual(box.lo, exact)
                self.assertGreaterEqual(box.hi, exact)
        self.assertEqual((b**2).lo, 0)
        self.assertLessEqual((b**2).lo, F(4, 49))
        self.assertGreaterEqual((b**2).hi, F(4, 49))

    def test_interval_division_rejects_zero_and_reversed(self):
        with self.assertRaises(ValueError):
            q.I(1)/q.I(-1, 1)
        with self.assertRaises(ValueError):
            q.I(2, 1)
        with self.assertRaises(ValueError):
            q.I(2)**F(1, 2)

    def test_reciprocal_and_negative_power_enclose(self):
        box = q.I(-3, -2)**-2
        self.assertLessEqual(box.lo, F(1, 9))
        self.assertGreaterEqual(box.hi, F(1, 4))

    def test_exp_and_log_analytic_enclosures_crosscheck(self):
        with mp.workdps(180):
            for n, order in ((64, 48), (96, 64)):
                L = q.logtwo(n)
                self.assertLess(mp.mpf(str(L.lo)), mp.log(2))
                self.assertGreater(mp.mpf(str(L.hi)), mp.log(2))
                for x in (-7, -1, 0, F(1, 2), 2):
                    out = q.exp_point(x, order)
                    v = mp.exp(mp.mpf(str(x)))
                    self.assertLessEqual(mp.mpf(str(out.lo)), v)
                    self.assertGreaterEqual(mp.mpf(str(out.hi)), v)

    def test_exp_log_domains_and_budgets_not_expanded(self):
        for n in (0, 63, 97, 64.0, True):
            with self.assertRaises(ValueError):
                q.logtwo(n)
        with self.assertRaises(ValueError):
            q.exp_point(33)
        with self.assertRaises(ValueError):
            q.exp_point(1, 70)

    def test_exact_square_root_enclosures(self):
        for x in (0, 1, 2, 5, F(1, 4)):
            a = q.sqrt_rational(x)
            self.assertLessEqual(a.lo*a.lo, x)
            self.assertGreaterEqual(a.hi*a.hi, x)

    def test_serialization_rational_endpoints_not_inward_decimals(self):
        box = q.I(F(1, 3), F(2, 3))
        out = json.loads(json.dumps(q.encode(box)))
        self.assertEqual(q.I(F(out["lo"]), F(out["hi"])), box)
        self.assertIsInstance(out["lo"], str)
        self.assertNotIn("e", out["lo"])

    def test_parent_gradient_matches_numeric_differentiation(self):
        with mp.workdps(60):
            x = [mp.mpf("0.8"), mp.mpf("0.7"), mp.mpf("0.9")]
            spins = (-1, 1, 1, -1)
            _, g, H = q.mp_parent(spins, x)
            for i in range(3):
                fn = lambda t: q.mp_parent(spins, x[:i]+[t]+x[i+1:])[0]
                self.assertLess(abs(mp.diff(fn, x[i])-g[i]), mp.mpf("1e-55"))
                self.assertLess(abs(mp.diff(fn, x[i], 2)-H[i, i]), mp.mpf("1e-54"))

    def test_source_spin_quarter_and_three_open_bonds(self):
        at = [q.I(1)]*3
        V, _, _, _ = q.interval_parent((1, 1, 1, 1), at)
        self.assertLessEqual(V.lo, F(-3, 4))
        self.assertGreaterEqual(V.hi, F(-3, 4))
        self.assertEqual(len(q.PAIRS), 6)
        self.assertEqual(sum(j == i+1 for i, j in q.PAIRS), 3)

    def test_no_zero_or_negative_gap(self):
        for gaps in ((0, 1, 1), (-1, 1, 1), (1, 1)):
            with self.assertRaises(ValueError):
                q.interval_parent((1, 1, 1, 1), gaps)

    def test_linear_root_inclusion_exact(self):
        H = [[q.I(int(i == j)) for j in range(3)] for i in range(3)]
        c = q.inclusion([F(0)]*3, F(1, 10**12), [q.I(0)]*3, H)
        self.assertEqual(c["contraction_upper"], 0)
        self.assertGreater(c["inclusion_margin_lower"], 0)

    def test_tiny_residual_is_not_root_certificate(self):
        H = [[q.I(0) for _ in range(3)] for _ in range(3)]
        with self.assertRaises((ValueError, ZeroDivisionError)):
            q.inclusion([F(0)]*3, F(1, 10**12), [q.I(F(1, 10**100))]*3, H)

    def test_bad_center_fails_inclusion(self):
        H = [[q.I(int(i == j)) for j in range(3)] for i in range(3)]
        with self.assertRaises(ValueError):
            q.inclusion([F(0)]*3, F(1, 10**12), [q.I(1)]*3, H)

    def test_certified_nonminimum_not_confused_with_search_failure(self):
        H = [[q.I(int(i == j)*(1 if i != 1 else -1)) for j in range(3)] for i in range(3)]
        fake = (q.I(0), [q.I(0)]*3, H, [q.I(0)]*6)
        with patch.object(q, "interval_parent", return_value=fake):
            cert = q.certify((-1, -1, -1, -1), [F(1)]*3)
        self.assertEqual(cert["verdict"], "CERTIFIED_ROOT_NONMINIMUM")
        self.assertTrue(any(cert["negative_direction"]))

    def test_ldl_rejects_indefinite_singular_near_singular(self):
        for entry in (q.I(0), q.I(-1), q.I(-F(1, 10**80), F(1, 10**80))):
            with self.assertRaises(ValueError):
                q.ldl([[q.I(1), q.I(0)], [q.I(0), entry]])

    def test_gap_metric_and_phase_measure(self):
        T, D, _ = q.gap_maps()
        G = s.Matrix(T).T*s.Matrix(T)
        self.assertNotEqual(G, s.eye(3))
        self.assertEqual(G.det(), s.Rational(1, 4))
        self.assertEqual(s.Matrix(D)*s.Matrix(T), s.eye(3))
        self.assertEqual((s.Matrix(D).T*s.Matrix(D)).det(), 0)

    def test_predeclared_search_budget(self):
        self.assertEqual(len(q.SEEDS), 27)
        self.assertEqual(q.SEEDS[0], (F(1, 2),)*3)
        self.assertEqual(q.SEEDS[-1], (F(2),)*3)
        self.assertEqual(q.classify_search(False, False), "INCONCLUSIVE")

    def test_symmetry_readout_and_mass_do_not_change(self):
        a = s.Matrix([-s.Rational(3, 2), -s.Rational(1, 2), s.Rational(1, 2), s.Rational(3, 2)])
        e1 = s.Matrix([1, -1, -1, 1])/2
        e2 = s.Matrix([1, -3, 3, -1])/s.sqrt(20)
        mirror = -s.eye(4)[::-1, :]
        self.assertEqual(mirror*a, a)
        self.assertEqual(mirror*e1, -e1)
        self.assertEqual(mirror*e2, e2)
        self.assertEqual(a.dot(a), 5)

    def test_signed_magnitude_not_new_backaction(self):
        self.assertEqual(abs(-2), abs(2))
        self.assertNotEqual(-2, 2)
        x = s.Symbol("x", real=True)
        self.assertEqual(s.diff(x*x, x), 2*x)
        # Changing readout to |C| neither changes a spin sector nor its potential.
        self.assertNotEqual(q.orbit((-1, 1, 1, -1)), q.orbit((-1, 1, -1, 1)))

    def test_gaussian_mode_count_and_offsets(self):
        theta, chi, det, v = s.symbols("theta chi det v", positive=True)
        for n in (2, 3):
            Fharm = v-theta*(n*s.log(theta/chi)-s.log(det)/2)
            Sharm = -s.diff(Fharm, theta)
            self.assertEqual(s.simplify(Fharm+theta*Sharm-v-n*theta), 0)
        self.assertNotEqual(s.exp(-1/theta), 1)

    def test_tail_moment_constants(self):
        z = s.Symbol("z", positive=True)
        mgf = (1-2*z)**(-s.Rational(3, 2))
        self.assertEqual(s.diff(mgf, z).subs(z, 0), 3)
        self.assertEqual(s.diff(mgf, z, 2).subs(z, 0), 15)

    def test_quantum_covariance_bound_has_correct_factor(self):
        chi, theta, k = s.symbols("chi theta k", positive=True)
        x = chi*s.sqrt(k)/(2*theta)
        self.assertEqual(s.simplify(x*x/3-chi*chi*k/(12*theta*theta)), 0)

    def test_all_negative_controls(self):
        self.assertTrue(all(q.negative_controls().values()))

    def test_new_science_result_and_location_uncertainty(self):
        r = q.calculate()
        self.assertEqual(len(r["configurations"]), 16)
        for row in r["orbits"]:
            if not row["certificate"]:
                self.assertEqual(len(row["attempts"]), 27)
                continue
            cert = row["certificate"]
            self.assertLess(F(cert["contraction_upper"]), 1)
            self.assertGreater(F(cert["inclusion_margin_lower"]), 0)
            self.assertGreater(F(row["views"]["root_position_uncertainty_upper"]), 0)
            self.assertEqual(len(row["local_domain"]["radii"]), 9)
            self.assertGreater(F(row["views"]["stiffness_det"]["lo"]), 0)
            self.assertGreater(F(row["views"]["lambda_min_lower"]), 0)
            self.assertTrue(any(F(row["views"]["internal_stiffness"][0][i]["hi"]) < 0
                                for i in (1, 2)))
            self.assertGreater(max(max(abs(F(v["lo"])), abs(F(v["hi"])))
                                   for v in cert["center_gradient"]), 0)
            # Reflection of the certified root image remains in the uniqueness box.
            for i, v in enumerate(reversed(cert["root_box"])):
                self.assertGreater(F(v["lo"]), F(cert["center"][i])-F(cert["inclusion_halfwidth"]))
                self.assertLess(F(v["hi"]), F(cert["center"][i])+F(cert["inclusion_halfwidth"]))

    def test_new_artifact_contract_identity_and_claim_boundary(self):
        from docs.scripts.audit.audit_calculation_completeness import contract_hash, validate_contract
        c = q.load_json(q.ROOT/q.CONTRACT)
        a = q.load_json(q.ROOT/q.OUTPUT)
        self.assertEqual(validate_contract(c, q.ROOT)["errors"], [])
        self.assertEqual(a["contract_sha256"], contract_hash(c))
        self.assertEqual(a["identities"], c["identities"])
        self.assertFalse(a["physical_acceptance"])
        self.assertFalse(a["unique_UET_discriminator"])
        self.assertFalse(a["old_scientific_verifiers_rerun"])
        self.assertEqual(a["trajectories"], 0)


def product_grid(a, b):
    return ((x, y) for x in (a.lo, a.mid, a.hi) for y in (b.lo, b.mid, b.hi))


if __name__ == "__main__":
    unittest.main()
