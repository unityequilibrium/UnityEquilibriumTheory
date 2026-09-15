"""
UET Core v1.0.0 Comprehensive Test Suite
========================================
Validates new A13 (Inertia) and A14 (Viscosity) axioms in the Master Equation.
"""

import numpy as np
import unittest
import sys

from docs.core.core_paths import repo_root

# Add the project root to sys.path to ensure we use the local files, not installed packages
sys.path.insert(0, str(repo_root()))

from docs.core.uet_parameters import UETParameters
from docs.core.uet_master_equation import dynamics_step_complete, UETMasterEquation

class TestUETCoreUpgrade(unittest.TestCase):
    
    def test_overdamped_limit(self):
        """Verify that with tau_inertia=0, it reduces to standard diffusion."""
        # Disable ALL forces except alpha potential to check strict diff behavior
        params = UETParameters(alpha=1.0, gamma=0.0, kappa=0.0, beta=0.0, W_N=0.0, tau_inertia=0.0)
        C = np.array([1.0, 0.5, 0.0])
        dt = 0.1
        
        # dC/dt = -V'(C) = -alpha*(C-1)=0 for C=1
        # For C=0.5: dC/dt = -(0.5-1.0) = 0.5
        C_new = dynamics_step_complete(C, dt=dt, params=params)
        
        # C_new[1] should be 0.5 + 0.1*0.5 = 0.55
        self.assertAlmostEqual(C_new[1], 0.55)

    def test_inertial_overshoot(self):
        """Verify that tau_inertia > 0 allows the system to overshoot equilibrium."""
        # Setup: Quadratic potential centered at C=1.0
        params = UETParameters(alpha=10.0, kappa=0.0, beta=0.0, W_N=0.0, tau_inertia=0.5)
        
        N = 10
        C = np.zeros(N) # Use N > 1 for gradient calculation
        V = np.zeros(N)
        dt = 0.05
        
        # Evolution loop
        history = [C[5]]
        for _ in range(100):
            res = dynamics_step_complete(C, V=V, dt=dt, params=params)
            C = res[0]
            V = res[1]
            history.append(C[5])
            
        # Overshoot check
        max_c = max(history)
        print(f"Inertial peak: {max_c:.4f}")
        self.assertGreater(max_c, 1.0, "System failed to overshoot equilibrium despite inertia.")

    def test_dynamic_viscosity_scaling(self):
        """Verify that a0_viscosity amplifies forces in low-acceleration regimes."""
        params_no_a0 = UETParameters(alpha=1.0, W_N=0.0, a0_viscosity=0.0)
        params_with_a0 = UETParameters(alpha=1.0, W_N=0.0, a0_viscosity=10.0)
        
        N = 10
        C = np.ones(N) * 0.99
        dt = 0.1
        
        C_no_a0 = dynamics_step_complete(C, dt=dt, params=params_no_a0)
        C_with_a0 = dynamics_step_complete(C, dt=dt, params=params_with_a0)
        
        dist_no_a0 = abs(C_no_a0[5] - C[5])
        dist_with_a0 = abs(C_with_a0[5] - C[5])
        
        self.assertGreater(dist_with_a0, dist_no_a0)

    def test_class_state_management(self):
        """Verify that UETMasterEquation class manages C, V, I states correctly."""
        params = UETParameters(tau_inertia=0.1, W_N=0.0)
        engine = UETMasterEquation(params=params)
        
        N = 10
        C = np.zeros(N)
        dt = 0.1
        
        # First step initializes V
        engine.step(C, dt=dt)
        self.assertIsNotNone(engine.V)
        
        # Second step uses accumulated V
        v_prev = engine.V[5]
        engine.step(engine.C, dt=dt)
        self.assertNotEqual(engine.V[5], v_prev)

if __name__ == "__main__":
    unittest.main()
