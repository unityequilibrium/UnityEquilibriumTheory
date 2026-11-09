"""Exact mathematical controls; no measured data or physical acceptance."""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import json

SPEC = importlib.util.spec_from_file_location(
    "observer_discrimination", Path(__file__).with_name("Research_T13_Observer_Discrimination.py"))
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class JointObserverTests(unittest.TestCase):
    def test_joint_clock_and_gain_equivalence(self):
        self.assertFalse(m.w1()["physical_operator_admitted"])

    def test_clock_rejection(self):
        for a in (Q(0), Q(-1)):
            with self.assertRaises(ValueError):
                m.joint_parameters(Q(1), Q(2), Q(4), Q(1), Q(0), a)

    def test_inherited_branch_domain(self):
        for b, p in ((Q(-1), Q(4)), (Q(1), Q(0))):
            with self.assertRaises(ValueError):
                m.joint_parameters(Q(1), b, p, Q(1), Q(0), Q(1))

    def test_zero_coupling_and_zero_gain(self):
        for b, g in ((Q(0), Q(1)), (Q(3), Q(0))):
            a0, d, p = m.joint_parameters(Q(2), b, Q(4), g, Q(1), Q(1))
            self.assertEqual(d, 0)
            self.assertEqual(m.pole(Q(0), a0, d, p), m.pole(Q(2), a0, d, p))

    def test_gain_sign_is_not_residue_sign(self):
        self.assertLess(m.joint_parameters(Q(1), Q(2), Q(4), Q(-1), Q(0), Q(1))[1], 0)

    def test_pole_exclusion(self):
        with self.assertRaises(ValueError):
            m.pole(Q(4), Q(2), Q(3), Q(4))

    def test_affine_contrast_zero_nonuniform_spacing(self):
        z = (Q(0), Q(2, 3), Q(2))
        y = tuple(3 * x + 5 for x in z)
        t, e = m.contrast(z, y, (Q(0),) * 3)
        self.assertEqual((t, e), (0, 0))

    def test_exact_pole_contrast_formula(self):
        z = (Q(0), Q(1, 3), Q(2))
        for p in (Q(-2), Q(3), Q(5)):
            y = tuple(m.pole(x, Q(7), Q(3), p) for x in z)
            expected = -Q(3) * (z[2] - z[0]) / ((p-z[0])*(p-z[1])*(p-z[2]))
            self.assertEqual(m.contrast(z, y, (Q(0),) * 3)[0], expected)

    def test_joint_error_bound_attainable_without_independence(self):
        z = (Q(0), Q(1), Q(2))
        delta = (Q(1, 100), Q(1, 50), Q(1, 25))
        t, e = m.contrast(z, (delta[0], -delta[1], delta[2]), delta)
        self.assertEqual(t, e)

    def test_unknown_gain_can_erase_shape(self):
        z = (Q(0), Q(1), Q(2))
        y = [m.pole(x, Q(5), Q(3), Q(4)) for x in z]
        gains = [Q(1) / v for v in y]
        self.assertEqual([g*v for g, v in zip(gains, y)], [1, 1, 1])

    def test_bound_drift_and_invalid_bounds(self):
        self.assertEqual(m.drift_error(Q(1,10), Q(2), Q(1,20), Q(1,100)), Q(13,50))
        with self.assertRaises(ValueError):
            m.drift_error(Q(-1), Q(2), Q(0), Q(0))

    def test_invalid_contrast_domain(self):
        for z, e in (((Q(0), Q(0), Q(2)), (Q(0),)*3),
                     ((Q(0), Q(1), Q(2)), (Q(-1), Q(0), Q(0)))):
            with self.assertRaises(ValueError):
                m.contrast(z, (Q(1),)*3, e)

    def test_small_nonzero_coupling_no_uniform_separation(self):
        z = (Q(0), Q(1, 100), Q(2), Q(100))
        for eps in (Q(1, 10), Q(1, 10**9)):
            p, d = m.uniform_affine_witness(z, eps)
            self.assertGreater(d, 0)
            self.assertTrue(all(abs(m.pole(x, Q(5), d, p)-5) <= eps/2 for x in z))

    def test_near_pole_sensitivity_not_silently_clipped(self):
        near = m.pole(Q(4)-Q(1,10**6), Q(0), Q(1), Q(4))
        self.assertEqual(near, -10**6)

    def test_bounded_design_control(self):
        r = m.w2()
        self.assertEqual(sum(x["candidates"] for x in r["design_search"]), 53)
        self.assertFalse(r["physical_acceptance"])

    def test_ordinary_pole_equivalence_over_many_inputs(self):
        for z in (Q(i, 7) for i in range(20)):
            uet = m.pole(z, Q(5), Q(3), Q(4))
            ordinary = Q(5) - Q(3)/(Q(4)-z)
            self.assertEqual(uet, ordinary)

    def test_new_admitted_source_requires_review_not_automatic_scoring(self):
        source = {"bounded_search_decision": {"admitted_discriminator_records": ["new-record"]}}
        contract = {"identities": [{"path": m.SOURCE}]}
        with patch.object(m, "identity_bytes", return_value=json.dumps(source).encode()):
            with self.assertRaisesRegex(ValueError, "admission changed"):
                m.w3(contract)

    def test_optional_source_fields_are_explicit_not_fabricated(self):
        source = {"bounded_search_decision": {"admitted_discriminator_records": [],
                  "status": "STOP", "reason": "no admitted kernel", "reopen_only_with": ["record"]},
                  "sources": [{"id": "control", "disposition": "not admitted"}]}
        contract = {"identities": [{"path": m.SOURCE, "commit": m.OWNER}]}
        with patch.object(m, "identity_bytes", return_value=json.dumps(source).encode()):
            result = m.w3(contract)
            self.assertIsNone(result["route_dispositions"][0]["missing"])
            self.assertFalse(result["route_dispositions"][0]["missing_field_recorded"])


if __name__ == "__main__":
    unittest.main()
