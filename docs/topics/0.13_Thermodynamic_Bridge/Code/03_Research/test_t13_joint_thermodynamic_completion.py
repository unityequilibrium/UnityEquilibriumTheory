"""Regression controls for the conditional reference, not empirical UET tests."""
import importlib.util
from pathlib import Path
import unittest

import sympy as s

spec = importlib.util.spec_from_file_location(
    "joint_thermodynamic_completion", Path(__file__).with_name("Research_T13_Joint_Thermodynamic_Completion.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class JointThermodynamicCompletionTests(unittest.TestCase):
    def assertZeros(self, values):
        for name, value in values.items():
            with self.subTest(identity=name):
                self.assertEqual(s.simplify(value), 0)

    def test_actual_core_homogeneous_expressions_match(self):
        self.assertZeros(m.core_projection_residuals())

    def test_core_source_mutation_is_detected(self):
        text = (m.ROOT/m.CORE).read_text(encoding="utf-8-sig")
        changed = text.replace("dPhi = state.space_rate.copy()", "dPhi = 2 * state.space_rate.copy()")
        self.assertNotEqual(changed, text)
        self.assertNotEqual(m.core_projection_residuals(changed)["dPhi"], 0)

    def test_first_law_ito_and_stratonovich_agree(self):
        self.assertZeros(m.first_law_residuals())

    def test_wrong_heat_sign_fails_in_drift_and_noise(self):
        result = m.first_law_residuals(heat_sign=-1)
        self.assertNotEqual(s.simplify(result["work_minus_heat_dt"]), 0)
        self.assertNotEqual(s.simplify(result["work_minus_heat_C_noise"]), 0)
        self.assertNotEqual(s.simplify(result["work_minus_heat_Pi_noise"]), 0)

    def test_no_independent_phi_noise_and_no_spurious_sde_drift(self):
        r = m.reference()
        for i, _ in enumerate(r["state"]):
            conversion = sum(r["noise"][k, j]*s.diff(r["noise"][i, j], x)
                             for k, x in enumerate(r["state"]) for j in range(2))/2
            self.assertEqual(conversion, 0)
        self.assertEqual(r["noise"][1, :], s.zeros(1, 2))

    def test_deterministic_limit_holds_coefficients_fixed(self):
        r = m.reference()
        eps = s.Symbol("epsilon", nonnegative=True)
        self.assertEqual((eps*r["noise"]).subs(eps, 0), s.zeros(3, 2))
        for x, drift in zip(r["state"], r["drift"]):
            self.assertEqual(s.simplify(m.generator(x, r)-drift), 0)

    def test_same_free_energy_at_one_bath_does_not_fix_heat(self):
        self.assertZeros(m.coarse_free_energy_residuals())
        r = m.reference()
        kappa = s.Symbol("kappa", positive=True)
        correction = 2*r["theta"]*kappa*r["Phi"]*r["Pi"]
        self.assertNotEqual(correction, 0)

    def test_source_ledger_is_not_force_port_work(self):
        r = m.reference()
        ledger = r["muC"]*r["JC"]+r["Pi"]*r["JP"]/r["MP"]
        port = r["JC"]/r["MC"]*r["drift"][0]+r["JP"]/r["MP"]*r["Pi"]
        self.assertEqual(s.simplify(ledger-port-(2*r["muC"]*r["JC"]-r["JC"]**2/r["MC"])), 0)
        self.assertNotEqual(s.simplify(ledger-port), 0)

    def test_no_physics_promotion_from_symbolic_checks(self):
        result = m.calculate()
        self.assertFalse(result["physical_acceptance"])
        self.assertFalse(result["unique_UET_discriminator"])
        self.assertEqual(result["new_core_terms"], 0)
        self.assertEqual(result["observational_rows"], 0)


if __name__ == "__main__":
    unittest.main()
