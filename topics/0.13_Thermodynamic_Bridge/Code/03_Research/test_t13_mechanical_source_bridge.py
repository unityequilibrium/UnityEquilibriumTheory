from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('mechanical_source',Path(__file__).with_name('Research_T13_Mechanical_Source_Bridge.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class MechanicalSourceBridgeTests(unittest.TestCase):
    def test_zero_force_is_not_a_zero_coupling_loophole(self):
        for phi in map(Q,(-10,0,10)):
            self.assertEqual(m.source_free_acceleration((Q(0),Q(0)),Q(2),Q(1),Q(3),Q(1),Q(4),phi),(0,0))

    def test_negative_stiffness_can_amplify_seed_but_not_create_exact_seed(self):
        self.assertEqual(m.source_free_acceleration((Q(0),Q(0)),Q(1),Q(-2),Q(1),Q(1),Q(1),Q(0)),(0,0))
        self.assertGreater(m.source_free_acceleration((Q(1,10),Q(0)),Q(1),Q(-2),Q(1),Q(1),Q(1),Q(0))[0],0)

    def test_current_production_residual_and_source_parity(self):
        r=m.current_core_controls()
        self.assertEqual(r['nonzero_state_controls'],12)
        self.assertLessEqual(r['largest_acceleration_roundoff'],1e-13)

    def test_inverse_source_can_force_any_prescribed_state_locally(self):
        q=(Q(1,2),Q(1,3)); a=(Q(2,5),Q(-1,4)); args=(Q(2),Q(1),Q(3),Q(1,2),Q(4),Q(5,3))
        source=m.required_source(q,a,*args)
        free=m.source_free_acceleration(q,*args)
        self.assertEqual(tuple(args[0]*(x-y) for x,y in zip(a,free)),source)
        self.assertNotEqual(source,(0,0))  # Not independently supplied experimental force.

    def test_stable_normal_and_broken_backgrounds_are_not_interchanged(self):
        self.assertEqual(m.stationary_background(Q(2),Q(3),Q(0)),(2,2))
        with self.assertRaises(ValueError): m.stationary_background(Q(2),Q(3),Q(1))
        self.assertEqual(m.stationary_background(Q(-3),Q(3,4),Q(4)),(6,0))

    def test_scalar_modulation_about_background_is_proportional_to_background(self):
        v=(Q(2),Q(0)); zero=(Q(0),Q(0)); e,h=Q(1,2),Q(3,5); delta=Q(2,3)
        base=m.required_source(v,zero,Q(1),Q(-3),Q(3,4),e,h,Q(0))
        shifted=m.required_source(v,zero,Q(1),Q(-3),Q(3,4),e,h,delta)
        self.assertEqual(base,(0,0))
        self.assertEqual(tuple(x-y for x,y in zip(shifted,base)),tuple(-e*h*delta*x for x in v))

    def test_force_dimensions_are_consistent_not_an_optical_power_identity(self):
        from docs.core.uet_covariant_matter import NATURAL_UNIT_MATTER_DIMENSIONS as dm
        from docs.core.uet_covariant_response import NATURAL_UNIT_MASS_DIMENSIONS as dr
        chi=dm['matter_doublet']; phi=dr['phi']; expected=dm['matter_eom_residual']
        self.assertEqual({dm['matter_kinetic']+chi+2,dm['matter_mass_sq']+chi,
                          dm['matter_quartic']+3*chi,dr['epsilon_nc']+dm['response_coupling']+phi+chi},{expected})
        # J_J/(Z*hbar^2*beta): (J^3)/(J^2*s^2 * J/m) = m/s^2.
        self.assertEqual((3-2-1,0-2,0-(-1)),(0,-2,1))

    def test_invalid_action_domains_refused(self):
        for z,quartic in ((Q(0),Q(1)),(Q(1),Q(0))):
            with self.assertRaises(ValueError): m.source_free_acceleration((Q(0),Q(0)),z,Q(1),quartic,Q(1),Q(1),Q(0))

    def test_no_physical_source_or_validation_is_silently_added(self):
        r=m.calculate()
        for k in ('physical_source_operator_added','physical_test_run','physical_acceptance','new_material_parameter','new_data_acquired','new_held_out_rows'):
            self.assertFalse(r[k])


if __name__=='__main__': unittest.main()
