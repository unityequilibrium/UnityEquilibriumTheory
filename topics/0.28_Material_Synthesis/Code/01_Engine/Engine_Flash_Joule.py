import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)

# ==============================================================================
#  UET PROPRIETARY ENGINE - CONFIDENTIAL IP
# ==============================================================================

import math
import sys
from pathlib import Path

# --- ROBUST PATH FINDER ---


from docs.core.uet_parameters import get_params


class FlashJouleReactor:
    def __init__(self, voltage_volts=300, capacitor_farads=0.06, params=None):
        """
        Simulate a Flash Joule Heating Reactor Unit.
        """
        self.params = params if params else get_params("0.28")
        self.voltage = voltage_volts
        self.capacitance = capacitor_farads
        self.bank_energy = 0.5 * self.capacitance * (self.voltage**2)  # E = 0.5 * C * V^2

        # Material Properties (Approximate for Carbon Black / Biochar)
        self.specific_heat_carbon = 0.710  # J/g/K (Graphite approx)
        self.sublimation_point_impure = 3000.0  # K (Point where non-C volatiles leave)
        self.graphitization_temp = 2800.0  # K (Point where C starts aligning)

    def run_flash(self, sample_mass_g, resistance_ohm, pulse_duration_ms=100):
        """
        Execute a single flash pulse on a sample.
        """
        # 1. Energy Discharge Calculation
        # Power P = V^2 / R
        power_watts = (self.voltage**2) / resistance_ohm

        # Energy Delivered (Joules) = Power * Time
        time_seconds = pulse_duration_ms / 1000.0
        energy_input_joules = power_watts * time_seconds

        # Cap check (Cannot exceed capacitor bank storage)
        if energy_input_joules > self.bank_energy:
            energy_input_joules = self.bank_energy

        # 2. Thermodynamic Temperature Rise
        # Q = m * c * dT  =>  dT = Q / (m * c)
        delta_temp = energy_input_joules / (sample_mass_g * self.specific_heat_carbon)

        initial_temp = 300.0  # Kelvin (Room temp)
        final_temp = initial_temp + delta_temp

        # 3. Process Logic (Sublimation & Transformation)
        purity_score = 0.0  # 0 to 1.0 (100% Pure)
        yield_score = 0.0  # 0 to 1.0 (100% Conversion)
        volatiles_removed = False

        # A. Purification Phase (Sublimation)
        if final_temp > self.sublimation_point_impure:
            volatiles_removed = True
            purity_score = 0.99  # Very high purity ("Pristine")
        elif final_temp > 2000:
            purity_score = 0.80  # Decent, but some junk left
        else:
            purity_score = 0.10  # Dirty carbon

        # B. Graphitization Phase (Lattice Formation)
        if final_temp > self.graphitization_temp:
            # "Flash" Graphene (Turbostratic)
            # Higher temp = better crystallinity up to a point
            yield_score = 0.95  # High yield
        elif final_temp > 2000:
            yield_score = 0.30  # Amorphous carbon / some graphite
        else:
            yield_score = 0.0  # Still just waste

        # 4. Energy Efficiency Metric
        # kJ per gram of Graphene produced
        if yield_score > 0:
            maturity_mass = sample_mass_g * yield_score
            if maturity_mass > 0:
                energy_efficiency_kj_g = (energy_input_joules / 1000.0) / maturity_mass
            else:
                energy_efficiency_kj_g = float("inf")
        else:
            energy_efficiency_kj_g = float("inf")

        return {
            "peak_temp_k": final_temp,
            "energy_used_kj": energy_input_joules / 1000.0,
            "purity": purity_score,
            "yield_percent": yield_score * 100.0,
            "efficiency_kj_g": energy_efficiency_kj_g,
            "success": (final_temp > 2800),
        }


if __name__ == "__main__":
    # Test Run
    reactor = FlashJouleReactor(voltage_volts=400)  # Increased voltage for test
    result = reactor.run_flash(sample_mass_g=0.5, resistance_ohm=5.0, pulse_duration_ms=60)
    print(f"Test Result: {result}")
