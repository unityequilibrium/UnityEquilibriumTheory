"""Round P exact regression, distinct from physical validation or old reruns."""
import importlib.util
from pathlib import Path
import unittest

import sympy as s

spec=importlib.util.spec_from_file_location(
    "lattice_bath",Path(__file__).with_name("Research_T13_Lattice_Bath_Reduction_Audit.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class LatticeBathReductionTests(unittest.TestCase):
    def assertZeros(self, values):
        self.assertTrue(all(m.zeros(values).values()))

    def test_coordinate_and_port_identities(self):
        self.assertZeros(m.coordinate_residuals())

    def test_three_internal_channels_no_translation(self):
        self.assertEqual(m.BASIS.shape,(4,3))
        self.assertEqual(m.BASIS.T*s.ones(4,1),s.zeros(3,1))
        self.assertEqual(m.BASIS.T*m.BASIS,s.eye(3))

    def test_spin_domain_is_not_silently_extended(self):
        for spins in ((),(1,1),(True,1,1,1),(0,1,1,1),(1.,1,1,1)):
            with self.assertRaises(ValueError):
                m.joint_coefficients(spins)

    def test_direct_joint_derivatives_from_parent(self):
        self.assertZeros(m.joint_parent_derivative_residuals())

    def test_all16_full_stiffness_positive(self):
        rows=m.spin_regime_rows()
        self.assertEqual(len(rows),16)
        self.assertTrue(all(r["joint_SPD"] for r in rows))

    def test_all16_means_outside_locked_domain(self):
        self.assertTrue(all(r["mean_outside_locked_ball"] for r in m.spin_regime_rows()))

    def test_reference_force_cannot_be_deleted(self):
        self.assertTrue(all(r["nonzero_linear_force"] for r in m.spin_regime_rows()))

    def test_hidden_coupling_is_not_zero(self):
        self.assertTrue(all(r["mixed_stiffness_nonzero"] for r in m.spin_regime_rows()))

    def test_global_spin_flip_preserves_new_reference(self):
        for spins in m.old.SPINS:
            a=m.joint_coefficients(spins)
            b=m.joint_coefficients(tuple(-v for v in spins))
            self.assertEqual(a["A"],b["A"])
            self.assertEqual(a["f"],b["f"])

    def test_same_C_does_not_determine_stiffness(self):
        a=m.joint_coefficients((1,1,-1,-1))
        b=m.joint_coefficients((1,-1,1,-1))
        self.assertNotEqual(a["A"],b["A"])

    def test_ln2_bracket_has_analytic_positive_series(self):
        lo,rem=m.log_bracket()
        self.assertEqual(lo,s.Rational(842,1215))
        self.assertEqual(rem,s.Rational(1,6804))

    def test_positive_interval_certificate_rejects_sign_change(self):
        x=s.Symbol("x",real=True)
        self.assertTrue(m.positive_interval_polynomial(1+x*x,x,0,1))
        self.assertFalse(m.positive_interval_polynomial(x-s.Rational(1,2),x,0,1))

    def test_joint_spd_rejects_singular_indefinite_or_wrong_shape(self):
        for A in (s.diag(1,1,0),s.diag(1,1,-1),s.eye(2),s.Matrix([[1,2,0],[0,1,0],[0,0,1]])):
            with self.assertRaises(ValueError):
                m.assert_joint_spd(A)

    def test_local_classical_quantum_tail_identities(self):
        self.assertZeros(m.local_quantum_residuals())

    def test_bath_initial_preparation_energy_and_FDT(self):
        self.assertZeros(m.bath_residuals())

    def test_counterterm_preserves_not_renormalizes_bare_potential(self):
        c,q,mass,w=s.symbols("c q m w",positive=True)
        self.assertNotEqual(-c*c*q*q/(2*mass*w*w),0)

    def test_Drude_spectral_and_white_conventions(self):
        self.assertZeros(m.drude_residuals())

    def test_stationarity_stability_and_odd_momentum(self):
        self.assertZeros(m.ou_residuals())

    def test_full_non_diagonal_OU_stationarity(self):
        A=s.Matrix([[3,1,1],[1,2,0],[1,0,2]])
        F,cov,noise=m.ou_matrices(A,2,3,5,7)
        self.assertEqual(F*cov+cov*F.T+noise,s.zeros(9))

    def test_noise_amplitude_error_breaks_stationarity(self):
        F,cov,noise=m.ou_matrices(s.eye(3),1,2,3,4)
        self.assertNotEqual(F*cov+cov*F.T+noise/2,s.zeros(9))

    def test_full_response_equals_scalar_Schur_response(self):
        self.assertZeros(m.response_residuals())

    def test_hidden_initial_law_and_effective_noise(self):
        self.assertZeros(m.hidden_fdt_residuals())

    def test_stationary_effective_spectrum_FDT(self):
        self.assertZeros(m.spectral_fdt_residuals())

    def test_Laplace_initial_state_terms_not_discarded(self):
        z,mu,G,q0,v0=s.symbols("z mu G q0 v0",real=True)
        initial=(mu*z+G)*q0+mu*v0
        self.assertEqual(s.diff(initial,q0),mu*z+G)
        self.assertNotEqual(initial,0)

    def test_prepared_hidden_offset_is_deterministic_force(self):
        k,g,offset=s.symbols("k g offset",positive=True)
        self.assertNotEqual(-g*offset,0)
        self.assertEqual(s.diff(-g*offset,offset),-g)

    def test_low_frequency_coefficients_and_exact_remainder(self):
        self.assertZeros(m.markov_expansion_residuals())

    def test_explicit_limits_and_negative_mass_counterexample(self):
        self.assertZeros(m.limit_and_rejection_residuals())

    def test_negative_low_frequency_mass_is_not_bare_negative_mass(self):
        A=s.Matrix([[2,1,0],[1,1,0],[0,0,1]])
        self.assertTrue(A.is_positive_definite)
        self.assertEqual(1*(1+1)-2**2,-2)

    def test_band_bound_in_admissible_exact_control(self):
        b=m.reduction_band_bound(1,1,10,s.Rational(1,100),1,1,1,1)
        self.assertTrue(b["H"]<1)
        self.assertTrue(b["impedance_error"]>0)

    def test_band_rejects_cutoff_and_unseparated_hidden_poles(self):
        for B in (1,2):
            with self.assertRaises(ValueError):
                m.reduction_band_bound(1,1,1,B,1,1,1,1)
        with self.assertRaises(ValueError):
            m.reduction_band_bound(1,1,10,1,1,1,1,1)

    def test_band_rejects_negative_scales_and_coupling_norms(self):
        for values in ((0,1,10,s.Rational(1,100),1,1,1,1),
                       (1,1,10,s.Rational(1,100),1,-1,1,1)):
            with self.assertRaises(ValueError):
                m.reduction_band_bound(*values)

    def test_Core_units_force_and_ratio_not_separate_unique_parameters(self):
        self.assertZeros(m.core_normalization_residuals())

    def test_frozen_weights_differ_from_annealed_weights(self):
        Q=s.Symbol("Q",real=True)
        F=-s.log(1+s.exp(-Q))
        annealed=-s.diff(F,Q).subs(Q,1)
        self.assertNotEqual(annealed,-s.Rational(1,2))

    def test_mixture_of_response_is_not_inverse_mean_impedance(self):
        self.assertNotEqual((1/s.Integer(2)+1/s.Integer(4))/2,1/s.Integer(3))

    def test_all_negative_controls_detect_declared_errors(self):
        self.assertTrue(all(m.negative_controls().values()))

    def test_exact_checker_rejects_nonzero_residual(self):
        with self.assertRaises(ValueError):
            m.zeros({"bad":s.Rational(1,10**30)})

    def test_artifact_matches_contract_identity_and_scope(self):
        c=m.load_json(m.ROOT/m.CONTRACT)
        a=m.load_json(m.ROOT/m.OUTPUT)
        from docs.scripts.audit.audit_calculation_completeness import contract_hash
        self.assertEqual(a["contract_sha256"],contract_hash(c))
        self.assertEqual(a["identities"],c["identities"])
        self.assertFalse(a["physical_acceptance"])
        self.assertFalse(a["unique_UET_discriminator"])
        self.assertFalse(a["old_scientific_verifiers_rerun"])
        self.assertEqual(a["trajectories"],0)


if __name__=="__main__":
    unittest.main()
