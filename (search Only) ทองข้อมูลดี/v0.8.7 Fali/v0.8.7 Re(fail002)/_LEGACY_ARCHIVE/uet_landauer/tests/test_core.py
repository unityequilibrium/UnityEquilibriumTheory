"""
Tests for UET Landauer Core Module
===================================

Verifies:
1. Energy per bit formula
2. Value function V = M(C/I)^α
3. Energy conservation
4. V connects C and I correctly
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from uet_landauer.core import (
    K_B,
    LN_2,
    energy_per_bit,
    value_function,
    information_energy,
    energy_rate,
    behavior_energy,
    LandauerParams,
    LandauerSystem,
)


class TestLandauerFormula:
    """Test Landauer's principle: E = k_B T ln(2)."""

    def test_energy_per_bit_at_300K(self):
        """E_bit at room temperature (300K) ≈ 2.87 × 10⁻²¹ J."""
        E = energy_per_bit(300)
        expected = K_B * 300 * LN_2
        assert np.isclose(E, expected, rtol=1e-10)
        assert np.isclose(E, 2.87e-21, rtol=0.02)  # Within 2%

    def test_energy_per_bit_at_0K(self):
        """E_bit at 0K should be 0."""
        E = energy_per_bit(0)
        assert E == 0

    def test_energy_scales_with_temperature(self):
        """E_bit should scale linearly with T."""
        E1 = energy_per_bit(300)
        E2 = energy_per_bit(600)
        assert np.isclose(E2 / E1, 2.0, rtol=1e-10)


class TestValueFunction:
    """Test V = M(C/I)^α."""

    def test_basic_value(self):
        """V = 1*(2/1)^1 = 2."""
        V = value_function(C=2.0, I=1.0, M=1.0, alpha=1.0)
        assert V == 2.0

    def test_value_with_mobility(self):
        """V = 0.5*(2/1)^1 = 1."""
        V = value_function(C=2.0, I=1.0, M=0.5, alpha=1.0)
        assert V == 1.0

    def test_value_with_exponent(self):
        """V = 1*(2/1)^2 = 4."""
        V = value_function(C=2.0, I=1.0, M=1.0, alpha=2.0)
        assert V == 4.0

    def test_value_symmetric_ci(self):
        """When C = I, V = M."""
        V = value_function(C=5.0, I=5.0, M=3.0, alpha=1.0)
        assert V == 3.0

    def test_value_increases_with_c(self):
        """V should increase when C increases."""
        V1 = value_function(C=1.0, I=1.0)
        V2 = value_function(C=2.0, I=1.0)
        assert V2 > V1

    def test_value_decreases_with_i(self):
        """V should decrease when I increases."""
        V1 = value_function(C=1.0, I=1.0)
        V2 = value_function(C=1.0, I=2.0)
        assert V2 < V1

    def test_zero_i_raises_error(self):
        """I = 0 should raise ValueError."""
        with pytest.raises(ValueError):
            value_function(C=1.0, I=0.0)


class TestInformationEnergy:
    """Test information to energy conversion."""

    def test_one_bit(self):
        """1 bit = E_bit."""
        E = information_energy(1.0, T=300)
        assert np.isclose(E, energy_per_bit(300))

    def test_many_bits(self):
        """N bits = N × E_bit."""
        N = 1000
        E = information_energy(N, T=300)
        assert np.isclose(E, N * energy_per_bit(300))


class TestLandauerSystem:
    """Test the complete system."""

    def test_initial_state(self):
        """System starts with C=I=1, V=M."""
        system = LandauerSystem()
        assert system.C == 1.0
        assert system.I == 1.0
        assert system.V == system.params.M

    def test_v_connects_c_and_i(self):
        """V should reflect C/I ratio."""
        system = LandauerSystem()

        # High C, low I → high V
        system.C = 10.0
        system.I = 1.0
        V_high = system.V

        # Low C, high I → low V
        system.C = 1.0
        system.I = 10.0
        V_low = system.V

        assert V_high > V_low
        assert V_high == 10.0
        assert V_low == 0.1

    def test_simulation_runs(self):
        """System should run without errors."""
        system = LandauerSystem()
        system.run(T=1.0, dt=0.01)
        assert len(system.history["t"]) == 100

    def test_energy_accumulates(self):
        """Energy should accumulate as system evolves."""
        system = LandauerSystem()
        system.C = 2.0
        system.I = 1.0
        system.run(T=1.0, dt=0.01)
        assert system.E > 0


class TestVConnectsCandI:
    """Specific tests for the core insight: V connects C and I."""

    def test_high_communication_high_value(self):
        """High C (openness) → high V."""
        V_open = value_function(C=10, I=1)
        V_closed = value_function(C=1, I=1)
        assert V_open > V_closed

    def test_high_isolation_low_value(self):
        """High I (closure) → low V."""
        V_open = value_function(C=1, I=1)
        V_closed = value_function(C=1, I=10)
        assert V_closed < V_open

    def test_balance_gives_mobility(self):
        """When C = I, V = M (stable)."""
        V = value_function(C=5, I=5, M=2.0)
        assert V == 2.0

    def test_v_is_ratio_dependent(self):
        """V depends on C/I ratio, not absolute values."""
        V1 = value_function(C=2, I=1)
        V2 = value_function(C=4, I=2)
        V3 = value_function(C=100, I=50)
        assert V1 == V2 == V3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
