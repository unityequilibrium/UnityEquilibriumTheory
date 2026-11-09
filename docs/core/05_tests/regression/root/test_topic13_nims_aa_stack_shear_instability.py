"""Regression checks for the scoped NIMS structure/shear-mode diagnostic."""

import importlib.util
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[4]
    / "topics/0.13_Thermodynamic_Bridge/Code/03_Research/"
    / "Research_T13_NIMS_AA_Stack_Shear_Instability.py"
)
SPEC = importlib.util.spec_from_file_location("t13_nims_aa_shear", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NimsAaStackShearInstabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = MODULE.build_artifact()

    def test_source_identity_structure_and_scope_are_locked(self):
        self.assertTrue(self.report["checks"]["archive_hash_matches_locked_source"])
        self.assertTrue(self.report["checks"]["member_hash_matches_locked_source"])
        self.assertEqual(
            self.report["source"]["structure"]["spacegroup_number"],
            191,
        )
        self.assertEqual(
            self.report["source"]["structure"]["unitcell_atom_count"],
            2,
        )
        self.assertTrue(all(self.report["checks"].values()))
        self.assertFalse(self.report["scope_controls"]["accepted_as_ding_csrc"])
        self.assertFalse(self.report["scope_controls"]["alpha_phi_k_calibrated"])
        self.assertEqual(self.report["status"], "WARN_SCOPED_NIMS_AA_STACK_SHEAR_MODE_ROBUST_MATERIAL_MAPPING_OPEN")
        self.assertFalse(self.report["claim_promotion"])

    def test_negative_basal_modes_survive_all_fixed_variants(self):
        variants = self.report["reproduction"]["q_boundary_variants"]
        self.assertEqual(len(variants), 5)
        self.assertTrue(
            all(
                item["q_boundary_negative_mode_indices_zero_based"]
                for item in variants
            )
        )
        self.assertLessEqual(
            self.report["reproduction"]["negative_frequency_spread_THz"],
            MODULE.MODE_FREQUENCY_TOL_THz,
        )
        for item in variants:
            polarization = item["negative_subspace_cartesian_polarization_fraction"]
            self.assertGreater(polarization["basal_x"] + polarization["basal_y"], 0.999)
            self.assertLess(polarization["c_axis_z"], 0.001)

    def test_sum_rule_reduction_does_not_remove_the_mode(self):
        self.assertTrue(
            self.report["checks"][
                "translation_permutation_symmetrization_reduces_sum_rule_residual"
            ]
        )
        variants = {
            item["variant"]: item
            for item in self.report["reproduction"]["q_boundary_variants"]
        }
        self.assertLess(
            variants["traditional_translation_permutation_level_1"][
                "acoustic_sum_rule_max_residual_eV_A2"
            ],
            MODULE.ASR_RESIDUAL_TOL_EV_A2,
        )
        self.assertTrue(
            variants["traditional_translation_permutation_level_1"][
                "q_boundary_negative_mode_indices_zero_based"
            ]
        )

    def test_mesh_and_external_claim_boundaries_remain_explicit(self):
        self.assertTrue(
            self.report["checks"]["full_unsymmetrized_reciprocal_mesh_is_recorded"]
        )
        self.assertTrue(
            all(
                item["mesh_qpoint_count"] == 12 * 12 * 6
                for item in self.report["reproduction"]["q_boundary_variants"]
            )
        )
        self.assertIn(
            "natural ABAB graphite is unstable",
            self.report["major_result"]["claim_boundary"],
        )
        self.assertNotIn(
            "Phi_ij",
            self.report["equation_or_mapping"]["asr_diagnostic"],
        )


if __name__ == "__main__":
    unittest.main()
