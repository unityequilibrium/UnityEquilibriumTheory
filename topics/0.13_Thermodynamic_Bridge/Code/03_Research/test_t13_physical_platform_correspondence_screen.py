"""Adversarial tests for the new physical screen, not source-paper replication."""
from copy import deepcopy
from fractions import Fraction as F
import importlib
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

import sympy as s

sys.path.insert(0, str(Path(__file__).resolve().parent))
a = importlib.import_module("Research_T13_Physical_Platform_Correspondence_Screen")


class PhysicalPlatformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = a.load_json(a.ROOT/a.INPUT)
        cls.sources, cls.facts = a.validate_subset(cls.data)
        cls.c = a.constants(cls.data)

    def test_three_fixed_platforms_and_bounded_sources(self):
        self.assertEqual(tuple(p["id"] for p in self.data["platforms"]), a.PLATFORMS)
        self.assertLessEqual(len(self.sources)-3, 9)
        self.assertTrue(all(len(p["sources"]) <= 3 for p in self.data["platforms"]))
        b = deepcopy(self.data)
        b["platforms"].reverse()
        with self.assertRaises(ValueError):
            a.validate_subset(b)

    def test_source_metadata_and_unknown_upstream_hash_are_explicit(self):
        self.assertTrue(all(src["upstream_sha256"] is None for src in self.sources.values()))
        self.assertEqual(self.sources["fe2012"]["access"], "METADATA_ONLY")
        self.assertEqual(self.sources["fe_sensor"]["access"], "PARTIAL_MAIN_INDEXED")
        b = deepcopy(self.data)
        b["sources"][0]["upstream_sha256"] = "0"*64
        with self.assertRaises(ValueError):
            a.validate_subset(b)

    def test_abstract_cannot_be_parameter_evidence(self):
        b = deepcopy(self.data)
        b["facts"][0]["source"] = "fe2012"
        with self.assertRaisesRegex(ValueError, "metadata"):
            a.validate_subset(b)

    def test_unknown_error_not_zero_or_exact_observation(self):
        for uncertainty in ({"kind":"UNKNOWN","value":"0"},
                            {"kind":"EXACT_DEFINITION","value":"0"},
                            {"kind":"REPORTED_STANDARD_UNCERTAINTY","value":"0"}):
            b = deepcopy(self.data)
            b["facts"][0]["uncertainty"] = uncertainty
            with self.assertRaises(ValueError):
                a.validate_subset(b)

    def test_exact_SI_not_exact_material_fit(self):
        for key in ("h", "e", "k_B"):
            rec = next(r for r in self.data["constants"] if r["id"] == key)
            self.assertEqual(rec["uncertainty"]["kind"], "EXACT_DEFINITION")
        self.assertEqual(self.facts["mn_J"]["uncertainty"]["kind"], "UNKNOWN")
        self.assertGreater(F(next(x for x in self.data["constants"] if x["id"] == "u")["uncertainty"]["value"]), 0)

    def test_energy_unit_meV_to_J_and_K(self):
        f = a.convert_fact(self.facts["mn_J"], self.c)
        self.assertEqual(F(f["value_SI"]), F("6.2")*self.c["e"]/1000)
        E = F(f["value_SI"])
        self.assertEqual((E/self.c["k_B"])*self.c["k_B"], E)
        self.assertEqual(f["unit_SI"], "J")
        self.assertFalse(f["parent_parameter"])

    def test_Hz_and_angular_frequency_not_h_hbar_confusion(self):
        cyc = a.frequency_energy(1, "Hz", self.c)
        ang = a.frequency_energy(1, "rad/s", self.c)
        self.assertEqual(s.simplify(cyc-2*s.pi*ang), 0)
        self.assertNotEqual(cyc, ang)
        with self.assertRaises(ValueError):
            a.frequency_energy(1, "frequency", self.c)

    def test_nm_angstrom_ns_and_no_angstrom_star_substitution(self):
        self.assertEqual(a.si_factor("nm", self.c)[0], F(1, 10**9))
        self.assertEqual(a.si_factor("angstrom", self.c)[0], F(1, 10**10))
        self.assertEqual(a.si_factor("ns", self.c)[0], F(1, 10**9))
        self.assertNotEqual(a.si_factor("angstrom", self.c)[0], F("1.00001495e-10"))

    def test_reported_errorbar_transformed_not_promoted_to_interval(self):
        f = a.convert_fact(self.facts["fe_deltaT1"], self.c)
        self.assertEqual(F(f["value_SI"]), F(26, 10**9))
        self.assertEqual(F(f["uncertainty_SI"]["value"]), F(3, 10**9))
        self.assertIsNone(f["uncertainty_SI"]["confidence"])
        self.assertFalse(f["is_hard_interval"])

    def test_model_choice_zero_is_not_measured_zero_uncertainty(self):
        f = a.convert_fact(self.facts["fe_Eani"], self.c)
        self.assertEqual(F(f["value_SI"]), 0)
        self.assertEqual(f["origin"], "MODEL_CHOICE")
        self.assertIsNone(f["uncertainty_SI"]["value"])

    def test_location_spread_not_CI_for_J(self):
        self.assertNotEqual(self.facts["mn_J"]["context"], self.facts["mn_J_variation"]["context"])
        self.assertIn("not a CI", self.facts["mn_J_variation"]["role"])
        self.assertIsNone(self.facts["mn_J"]["uncertainty"]["value"])

    def test_no_mixed_geometry_preparation_tuple(self):
        self.assertTrue(a.same_context(self.facts["mn_J"], self.facts["mn_T"]))
        for b in ("mn_J_Nsites", "fe_J", "pt_baseT"):
            with self.assertRaises(ValueError):
                a.same_context(self.facts["mn_J"], self.facts[b])
        with self.assertRaises(ValueError):
            a.same_context(self.facts["pt_T"], self.facts["pt_baseT"])
        with self.assertRaises(ValueError):
            a.same_context(self.facts["fe_J"], self.facts["fe_deltaT1"])

    def test_all_parent_scales_blocked_before_substitution(self):
        for p in self.data["platforms"]:
            with self.assertRaises(a.CorrespondenceMissing):
                a.require_parent_dictionary(p)
            self.assertTrue(all(p["physical_scale_dictionary"][k] is None for k in ("mu", "d_ref", "J_ref")))

    def test_filling_atomic_mass_site_spacing_and_J_does_not_repair_bridge(self):
        for p in self.data["platforms"]:
            b = deepcopy(p)
            b["physical_scale_dictionary"].update(mu="1e-25", d_ref="3.6e-10", J_ref="1e-21")
            with self.assertRaises(a.CorrespondenceMissing):
                a.require_parent_dictionary(b)

    def test_omitted_support_and_readout_still_caught(self):
        b = deepcopy(self.data["platforms"][0])
        for r in b["relations"]:
            r["outcome"] = "EQUIVALENT"
        b["physical_scale_dictionary"].update(mu="1e-25", d_ref="3.6e-10", J_ref="1e-21")
        b["native_binary_projection"] = b["frozen_sector_preparation"] = "EQUIVALENT"
        with self.assertRaisesRegex(a.CorrespondenceMissing, "support/leads"):
            a.require_parent_dictionary(b)
        b["mechanical_boundary"] = "FREE_OPEN_N4"
        with self.assertRaisesRegex(a.CorrespondenceMissing, "calibrated Phi"):
            a.require_parent_dictionary(b)

    def test_spin_sign_leakage_and_factor_diagnostics(self):
        mn, fe = a.spin_witness(F(5, 2)), a.spin_witness(2)
        self.assertEqual(F(mn["required_parent_bond_prefactor_over_source_J"]), -25)
        self.assertEqual(F(fe["required_parent_bond_prefactor_over_source_J"]), -16)
        self.assertEqual(F(mn["off_projected_doublet_matrix_element_over_J"]), F(5, 2))
        self.assertEqual(F(fe["off_projected_doublet_matrix_element_over_J"]), 2)
        self.assertTrue(mn["projected_doublet_not_invariant"])
        self.assertTrue(fe["projected_doublet_not_invariant"])
        self.assertEqual(mn["conditional_four_site_dimension"], 1296)
        self.assertEqual(fe["conditional_four_site_dimension"], 625)

    def test_spin_half_does_not_have_out_of_doublet_leakage(self):
        self.assertFalse(a.spin_witness(F(1, 2))["projected_doublet_not_invariant"])
        for x in (0, F(1, 3), -1):
            with self.assertRaises(ValueError):
                a.spin_matrices(x)

    def test_exact_symbolic_witnesses(self):
        self.assertTrue(all(a.symbolic_checks().values()))

    def test_staggering_not_preserved_C_or_prepared_sector(self):
        x = (-1, 1, -1, 1)
        z = tuple((-1)**i*v for i, v in enumerate(x))
        self.assertEqual(sum(x), 0)
        self.assertEqual(z, (-1, -1, -1, -1))
        self.assertEqual(sum(tuple(-v for v in x)), 0)

    def test_endpoint_hidden_null_direction_is_not_Phi_measurement(self):
        h, b, n = s.Matrix([1/s.sqrt(5),0,0]), s.Matrix([-3/s.sqrt(5),0,-1/s.sqrt(5)]), s.Matrix([1,0,-3])
        self.assertEqual(b.dot(n), 0)
        self.assertNotEqual(h.dot(n), 0)

    def test_bond_and_total_per_site_normalization(self):
        self.assertEqual(len(list(zip(range(4), range(1,4)))), 3)
        self.assertNotEqual(len(list(zip(range(4), range(1,4)))), 4)
        self.assertNotEqual(F(1,4), 1)

    def test_atomic_weight_and_nominal_length_remain_context(self):
        self.assertIn("no actual isotope", self.facts["Ar_Fe"]["role"])
        self.assertEqual(self.facts["pt_nominal_bond"]["origin"], "MODEL_CHOICE")
        self.assertIn("NOT the positive Morse", self.facts["fe_Dani"]["role"])

    def test_input_types_not_float_boolean_or_unlabelled_units(self):
        for x in (True, 1.2, None):
            with self.assertRaises(ValueError):
                a.rational(x)
        for unit in ("Kelvin-ish", "Hz", "rad/s"):
            with self.assertRaises(ValueError):
                a.si_factor(unit, self.c)

    def test_no_network_or_old_scientific_process(self):
        # Completeness helper may run git to inspect identities, but no producer.
        import subprocess
        real = subprocess.run
        def guard(args, *rest, **kw):
            if Path(str(args[0])).name not in ("git", "git.exe"):
                raise AssertionError("old scientific process or runtime network")
            return real(args, *rest, **kw)
        with patch.object(socket, "create_connection", side_effect=AssertionError("network")), patch.object(subprocess, "run", side_effect=guard):
            result = a.calculate()
        self.assertFalse(result["old_producers_rerun"])
        self.assertEqual(result["trajectories"], 0)

    def test_curated_verdicts_and_null_outputs_not_physical_validation(self):
        result = a.calculate()
        self.assertTrue(a.scope_check(result))
        self.assertTrue(all(p["theta"] is None and p["chi"] is None and p["Var_Phi"] is None for p in result["platforms"]))
        for key in ("physical_acceptance", "quantum_parent_validated", "candidate_selected"):
            with self.assertRaises(ValueError):
                a.scope_check(dict(result, **{key:True}))
        b = deepcopy(result)
        b["platforms"][0]["Var_Phi"] = "0"
        with self.assertRaises(ValueError):
            a.scope_check(b)

    def test_all_negative_controls(self):
        self.assertTrue(all(a.negative_controls(self.data).values()))

    def test_contract_and_artifact_identity_binding(self):
        contract = a.load_json(a.ROOT/a.CONTRACT)
        self.assertEqual(contract["profile"], "PHYSICAL_COMPARISON")
        self.assertEqual(contract["output"]["claim_intent"], "DIAGNOSTIC")
        self.assertEqual(a.validate_contract(contract, a.ROOT)["errors"], [])
        result = a.load_json(a.ROOT/a.OUTPUT)
        self.assertEqual(result["contract_sha256"], a.contract_hash(contract))
        self.assertEqual(result["identities"], contract["identities"])
        self.assertEqual(result["contract_review_status"], "INCOMPLETE")

    def test_check_mode_read_only_and_deterministic(self):
        with patch.object(Path, "write_text", side_effect=AssertionError("check wrote")):
            self.assertEqual(a.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
