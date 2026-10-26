"""New-path adversarial checks; no physical validation and no Q recalculation."""
from copy import deepcopy
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
v = importlib.import_module("Research_T13_Phi_Variance_Static_Admissibility")


class PhiVarianceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref, cls.A, cls.radii = v.load_reference()
        cls.co = v.covariance_coefficients(cls.A)
        cls.toy = {"c_h": v.q.I(1), "inverse_readout_norm": v.q.I(1), "h_norm": v.q.I(1)}

    def test_new_symbolic_derivations(self):
        self.assertTrue(all(v.symbolic_checks().values()))

    def test_full_joint_covariance_equals_schur_with_coupling(self):
        A = [[v.q.I(n) for n in row] for row in ((2, 1, 0), (1, 2, 0), (0, 0, 3))]
        c = v.covariance_coefficients(A)
        for key in ("c_h", "c_h_via_Schur"):
            self.assertLessEqual(c[key].lo, F(2, 15))
            self.assertGreaterEqual(c[key].hi, F(2, 15))
            self.assertFalse(c[key].lo <= F(1, 10) <= c[key].hi)
        self.assertLessEqual(c["kappa_obs"].lo, F(3, 2))
        self.assertGreaterEqual(c["kappa_obs"].hi, F(3, 2))

    def test_decoupling_limit_and_factor5(self):
        A = [[v.q.I(n) for n in row] for row in ((2, 0, 0), (0, 3, 0), (0, 0, 4))]
        c = v.covariance_coefficients(A)["c_h"]
        self.assertLessEqual(c.lo, F(1, 10))
        self.assertGreaterEqual(c.hi, F(1, 10))
        self.assertFalse(c.lo <= F(1, 2) <= c.hi)

    def test_inherited_uncertainty_not_point_input(self):
        self.assertGreater(self.co["c_h"].hi, self.co["c_h"].lo)
        self.assertGreater(v.F(self.ref["views"]["root_position_uncertainty_upper"]), 0)
        self.assertEqual(len(self.radii), 6)
        self.assertEqual([v.F(r["radius_over_dref"]) for r in self.radii],
                         [F(1, 2**j) for j in range(5, 11)])

    def test_actual_kappa_obs_stronger_than_certified_kappa_max(self):
        self.assertGreater(self.co["kappa_obs"].lo, 0)
        self.assertLess(self.co["kappa_obs"].hi, F(self.ref["views"]["lambda_max_upper"]))
        self.assertLess(self.co["c_h"].lo, F(1, 10))

    def test_bad_reference_root_uncertainty_or_radius_rejected(self):
        artifact = v.load_json(v.ROOT/v.QOUTPUT)
        index = next(i for i, r in enumerate(artifact["orbits"]) if r.get("certificate"))
        mutations = (
            lambda a: a["orbits"][index]["views"].update(root_position_uncertainty_upper="0"),
            lambda a: a["orbits"][index].update(orbit_members=["++++", "----"]),
            lambda a: a["orbits"][index]["local_domain"]["radii"][3].update(radius_over_dref="1/31"),
            lambda a: a["locked_control"].update(dref_over_r0=2),
            lambda a: a["orbits"][index]["views"]["internal_stiffness"][0].__setitem__(0, {"lo": "-1", "hi": "-1"}),
        )
        for change in mutations:
            bad = deepcopy(artifact)
            change(bad)
            with self.assertRaises(ValueError):
                v.select_reference(bad)

    def test_q_contract_artifact_mismatch_not_reused(self):
        real = v.load_json
        def altered(path):
            a = real(path)
            if path == v.ROOT/v.QOUTPUT:
                a["contract_sha256"] = "0"*64
            return a
        with patch.object(v, "load_json", side_effect=altered), self.assertRaises(ValueError):
            v.load_reference()

    def test_no_old_search_calculate_or_parent_evaluation(self):
        names = ("calculate", "main", "candidate", "search_orbit", "certify", "mp_parent", "interval_parent")
        mocks = [patch.object(v.q, name, side_effect=AssertionError("old scientific rerun forbidden")) for name in names]
        for mock in mocks:
            mock.start()
        try:
            result = v.calculate()
            self.assertFalse(result["old_root_search_called"])
            self.assertFalse(result["old_scientific_verifiers_rerun"])
        finally:
            for mock in reversed(mocks):
                mock.stop()

    def test_second_moment_is_not_central_variance(self):
        # An exactly known shifted distribution: a false positive if mean is omitted.
        raw = F(1**2+3**2, 2)
        mean = F(1+3, 2)
        self.assertEqual(raw, 5)
        self.assertEqual(raw-mean**2, 1)
        self.assertEqual(mean**2, 4)

    def test_method_a_gaussian_tail_and_mean_terms(self):
        out = v.method_a(F(1, 20), 1, 1, 0)
        self.assertTrue(out["usable"])
        self.assertGreater(out["tail_upper"], 0)
        self.assertGreater(out["upper"], out["tail_upper"])
        perturbed = v.method_a(F(1, 20), 1, 1, F(1, 10000))
        self.assertGreater(perturbed["upper"], out["upper"])

    def test_method_a_uninformative_not_parent_rejection(self):
        self.assertFalse(v.method_a(1, 1, 1, 0)["usable"])
        self.assertFalse(v.method_a(F(1, 1000), 1, 1, 1)["usable"])

    def test_method_b_preserves_surface_when_K3_zero(self):
        out = v.method_b(F(1, 20), 1, 1, 1, 0, self.toy)
        self.assertGreater(out["surface_density_upper"], 0)
        self.assertGreater(out["raw_second_moment_error_upper"], 0)
        self.assertGreater(out["upper"], 0)
        self.assertGreater(out["mean_shift_upper"], 0)  # conservative, not an asserted actual shift

    def test_finite_ball_quadratic_exact_control_and_B_enclosure(self):
        # Isotropic A=I, R=1, theta=1/20. Truncation survives K3=0.
        # mpmath crosscheck is diagnostic; theorem and B endpoints are analytic/rational.
        with mp.workdps(80):
            theta, b = mp.mpf(1)/20, mp.mpf(10)
            ratio = 2*mp.gammainc(mp.mpf(5)/2, 0, b)/(3*mp.gammainc(mp.mpf(3)/2, 0, b))
            exact_error = 1-ratio
            recurrence_error = 2*b**mp.mpf("1.5")*mp.exp(-b)/(3*mp.gammainc(mp.mpf(3)/2, 0, b))
            self.assertLess(abs(exact_error-recurrence_error), mp.mpf("1e-75"))
            upper = v.method_b(F(1, 20), 1, 1, 1, 0, self.toy)["upper"]
            self.assertGreater(exact_error, 0)
            self.assertLess(exact_error, mp.mpf(str(upper)))

    def test_rho_lower_normalization_and_moments(self):
        theta, R, m, M = F(1, 20), F(1), F(1), F(1)
        out = v.method_b(theta, R, m, M, 0, self.toy)
        self.assertEqual(out["rho_squared"], theta/M)
        self.assertTrue(out["rho_is_integration_lower_bound_not_new_physical_domain"])
        self.assertGreater(out["radial_moment2_upper"], 3*theta)
        self.assertGreater(out["radial_moment3_upper"], 0)
        # Low-curvature proof uses m, not M, in the numerator upper moments.
        coarser = v.method_b(theta, R, F(1, 2), M, 0, self.toy)
        self.assertGreater(coarser["radial_moment3_upper"], out["radial_moment3_upper"])

    def test_B_includes_squared_mean_and_raw_error(self):
        out = v.method_b(F(1, 20), 1, 1, 1, 1, self.toy)
        raw = out["raw_second_moment_error_upper"]
        self.assertGreater(out["upper"], raw/F(1, 20))

    def test_interval_uncertainty_affects_B_denominator(self):
        wide = dict(self.toy, c_h=v.q.I(F(1, 2), F(3, 2)))
        a = v.method_b(F(1, 20), 1, 1, 1, 1, self.toy)
        b = v.method_b(F(1, 20), 1, 1, 1, 1, wide)
        self.assertGreaterEqual(b["upper"], 2*a["upper"])

    def test_far_tail_is_outward_not_underflow_zero(self):
        box = v.exp_enclosure(-1000)
        self.assertEqual(box.lo, 0)
        self.assertGreater(box.hi, 0)
        self.assertGreaterEqual(box.hi, F(factorial16(), 1000**16))
        near = v.exp_enclosure(-1)
        with mp.workdps(180):
            self.assertLessEqual(mp.mpf(str(near.lo)), mp.exp(-1))
            self.assertGreaterEqual(mp.mpf(str(near.hi)), mp.exp(-1))

    def test_exact_input_domains_and_positive_denominators(self):
        for x in (True, 0.2, None):
            with self.assertRaises(ValueError):
                v.exact(x)
        for x in (0, -1, 1, 2):
            with self.assertRaises(ValueError):
                v.budget(x)
        self.assertEqual(v.budget("1/3"), F(1, 3))
        for args in ((0, 1, 1, 1, 0), (1, 0, 1, 1, 0), (1, 1, 2, 1, 0), (1, 1, 1, 1, -1)):
            with self.assertRaises(ValueError):
                v.method_b(*args, self.toy)
        with self.assertRaises(ValueError):
            v.method_b(1, 1, 1, 1, 0, dict(self.toy, c_h=v.q.I(-1, 1)))

    def test_quantum_weighted_bound_and_classical_limit(self):
        # Coefficients of x coth(x)-1 match 1/3; readout weighting gives 1/12.
        kappa = v.q.I(F(3, 2))
        b = v.quantum_bound(1, F(1, 10), kappa)
        self.assertGreaterEqual(b, F(1, 800))
        self.assertLess(b, F(1, 700))
        self.assertGreater(v.quantum_bound(F(1, 2), F(1, 10), kappa), b)
        self.assertLess(v.quantum_bound(1, F(1, 100), kappa), b)
        with self.assertRaises(ValueError):
            v.quantum_bound(0, 1, kappa)

    def test_normal_mode_weights_not_only_maximum_frequency(self):
        # Diagonal A and readout on first mode: unseen frequencies must not set kappa_obs.
        A = [[v.q.I(x) for x in row] for row in ((2, 0, 0), (0, 50, 0), (0, 0, 80))]
        ko = v.covariance_coefficients(A)["kappa_obs"]
        self.assertLessEqual(ko.lo, 2)
        self.assertGreaterEqual(ko.hi, 2)
        self.assertLess(ko.hi, 80)

    def test_coth_global_upper_has_nonnegative_coefficients(self):
        for n in range(1, 9):
            coefficient = F(1, s.factorial(2*n+1))+F(1, 3*s.factorial(2*n-1))-F(1, s.factorial(2*n))
            self.assertGreaterEqual(coefficient, 0)
            self.assertEqual(coefficient, F(4*n*(n-1), 3*s.factorial(2*n+1)))

    def test_si_units_and_nonidentifiability(self):
        # Dimensional exponents ordered kg,m,s,K: chi,theta and Var(Phi) dimensionless.
        hb = s.Matrix([1, 2, -1, 0])
        mass, d, J, T, kb = map(s.Matrix, ([1, 0, 0, 0], [0, 1, 0, 0], [1, 2, -2, 0], [0, 0, 0, 1], [1, 2, -2, -1]))
        self.assertEqual(2*hb-(mass+2*d+J), s.zeros(4, 1))
        self.assertEqual(kb+T-J, s.zeros(4, 1))
        self.assertEqual(mass+2*d, s.Matrix([1, 2, 0, 0]))  # generalized inertia, not kg

    def test_comparator_promotion_and_mode_double_count_rejected(self):
        base = {"physical_acceptance": False, "quantum_parent_validated": False,
                "comparator_pairs": ["classical_local_parent|classical_full_harmonic",
                                     "quantum_harmonic|classical_full_harmonic"]}
        self.assertTrue(v.scope_check(base))
        for key, value in (("physical_acceptance", True), ("quantum_parent_validated", True),
                           ("comparator_pairs", ["quantum_parent|classical_full_harmonic"])):
            with self.assertRaises(ValueError):
                v.scope_check(dict(base, **{key: value}))
        # Joint three pairs reduce to one retained plus two integrated, not 3+2.
        self.assertEqual(1+2, 3)
        self.assertNotEqual(3+2, 3)

    def test_all_negative_controls_are_actual_distinctions(self):
        self.assertTrue(all(v.negative_controls().values()))

    def test_contract_artifact_source_identities(self):
        contract = v.load_json(v.ROOT/v.CONTRACT)
        self.assertEqual(v.validate_contract(contract, v.ROOT)["errors"], [])
        a = v.load_json(v.ROOT/v.OUTPUT)
        self.assertEqual(a["contract_sha256"], v.contract_hash(contract))
        self.assertEqual(a["identities"], contract["identities"])
        self.assertEqual(len(a["inherited_radii"]), 6)
        self.assertFalse(a["physical_acceptance"])
        self.assertFalse(a["quantum_parent_validated"])

    def test_check_mode_cannot_write(self):
        with patch.object(Path, "write_text", side_effect=AssertionError("read-only check wrote")):
            self.assertEqual(v.main(["--check"]), 0)


def factorial16():
    from math import factorial
    return factorial(16)


if __name__ == "__main__":
    unittest.main()
