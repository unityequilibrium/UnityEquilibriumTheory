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

import numpy as np
import sys
from pathlib import Path

# --- ROBUST PATH FINDER ---


from docs.core.uet_parameters import get_params


class OceanGenerator:
    def __init__(self, battery_capacity_wh=10.0, params=None):
        """
        Energy Harvesting Model for Ocean Heat Sink.
        """
        self.params = params if params else get_params("0.29")
        # 1. TEG Specs (Bi2Te3 - Bismuth Telluride optimized for low temp)
        self.seebeck_coeff = 200e-6  # V/K per couple
        self.num_couples = 4000  # Large array embedded in wall
        self.internal_resistance = 2.0  # Ohms

        # 2. Piezo Specs (PVDF Ribbons in Chimney)
        self.piezo_coeff = 0.5  # Watts per (m/s flow)^2 (Simplified efficiency)

        # 3. Storage (LiFePO4 Cell)
        self.battery_capacity = battery_capacity_wh  # Watt-hours
        self.current_energy = battery_capacity_wh * 0.5  # Start at 50%

        # 4. Consumption Specs
        self.sleep_load = 0.05  # Watts (MCU Sleep + Sensors)
        self.tx_load = 1.5  # Watts (LoRa Transmission)
        self.tx_duration = 2.0  # Seconds
        self.tx_interval = 900  # Seconds (15 mins)
        self.time_since_tx = 0.0

    def update(self, delta_t, flow_velocity, dt_seconds=60):
        """
        Update energy balance for dt seconds.
        Returns: Power_In, Power_Out, Battery_Level_%
        """
        # A. Power Generation
        # TEG: V = N * S * dT
        voltage = self.num_couples * self.seebeck_coeff * abs(delta_t)
        # P = V^2 / 4R (Matched load condition max power)
        p_thermal = (voltage**2) / (4 * self.internal_resistance)

        # Piezo: P ~ v^2
        p_kinetic = self.piezo_coeff * (flow_velocity**2)

        power_in = p_thermal + p_kinetic

        # B. Power Consumption
        # Base load
        energy_used = self.sleep_load * dt_seconds

        # Transmission burst logic
        self.time_since_tx += dt_seconds
        if self.time_since_tx >= self.tx_interval:
            # Transmit!
            tx_energy = self.tx_load * self.tx_duration
            energy_used += tx_energy
            self.time_since_tx = 0

        # Converter Efficiency (Losses)
        power_efficicency = 0.85
        energy_stored = (power_in * dt_seconds) * power_efficicency

        # C. Update Battery
        # Convert Joules (Ws) to Wh -> / 3600
        net_wh = (energy_stored - energy_used) / 3600.0

        self.current_energy += net_wh

        # Clamp Battery
        self.current_energy = max(0.0, min(self.current_energy, self.battery_capacity))

        battery_pct = (self.current_energy / self.battery_capacity) * 100.0

        return {
            "P_Thermal": p_thermal,
            "P_Kinetic": p_kinetic,
            "P_Total_In": power_in,
            "Battery_Pct": battery_pct,
        }

    def get_status(self):
        return f"Battery: {self.current_energy/self.battery_capacity*100:.1f}%"
