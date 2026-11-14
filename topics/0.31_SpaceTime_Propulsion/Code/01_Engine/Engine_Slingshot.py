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

import math
import os
import sys
import numpy as np
from typing import List, Dict, Any

# sys.path Fix for docs
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from docs.core.uet_master_equation import UETMasterEquation
from docs.core.uet_parameters import UETParameters, get_params, G, C, HBAR, K_B

class SingularitySlingEngine:
    """
    UET Space-Time Engine: Singularity Gravitational Slingshot (SGS)
    v0.9.4: Clean Hardened Revision
    Objective: Integrate Core Relativistic Safeguards and Landauer Costs.
    """

    def __init__(self, ship_mass=500000, initial_v=11000, omega_coupling=1e9, 
                 tau_inertia=10.0, bio_resilience=0.0):
        self.G = G
        self.c = C
        self.hbar = HBAR
        self.k_b = K_B
        
        self.ship_mass = ship_mass
        self.v = initial_v
        self.omega_coupling = omega_coupling 
        
        # SHIP ENERGY SYSTEM (Topic 0.33)
        self.ship_energy = 1.0e15 # 1 Petajoule battery capacity
        self.temp_k = 300.0 # Standard operating temperature
        
        # BIOMIMETIC Stats
        self.bio_integrity = 100.0 
        self.bio_resilience = bio_resilience 
        self.regeneration_rate = 0.05 
        
        # PROPULSION PARAMETERS (Axiomatic Standard)
        # Note: tau_inertia > 0 ensures CORE LORENTZ CLAMP is active.
        self.params = get_params(
            "0.31", 
            tau_inertia=tau_inertia,
            origin="Topic 0.31 Clean Hardened"
        )
        self.solver = UETMasterEquation(self.params)
        
        # State Initialization
        N = 5
        self.C = np.ones(N)
        self.V = np.full(N, initial_v)
        self.I = np.zeros(N)

    def calculate_evap_time(self, mass_kg):
        return (5120 * math.pi * (self.G**2) * (mass_kg**3)) / (self.hbar * (self.c**4))

    def get_lorentz_factor(self):
        """Relativistic Penalty: γ = 1 / sqrt(1 - v^2/c^2)"""
        ratio = self.v / self.c
        if ratio >= 0.999999: return 1000.0 # Numerical limit for penalty
        return 1.0 / math.sqrt(1.0 - ratio**2)

    def simulate_sling(self, singularity_mass_kg, distance_m, duration_s) -> List[Dict[str, Any]]:
        dt = 0.005 
        steps = int(duration_s / dt)
        results = []
        
        current_mass = singularity_mass_kg
        evap_time = self.calculate_evap_time(singularity_mass_kg)
        mass_decay_rate = singularity_mass_kg / evap_time if evap_time > 0 else 0

        for s in range(steps):
            if current_mass <= 1e-10 or self.bio_integrity <= 0.0 or self.ship_energy <= 0.0:
                break

            # 1. RELATIVISTIC ACCELERATION (γ-Scaling)
            gamma = self.get_lorentz_factor()
            accel_raw = (self.G * current_mass * self.omega_coupling) / (distance_m**2)
            
            # Acceleration drops as ship approaches c
            accel_phys = accel_raw / (gamma**2)
            j_in_pulse = np.full(5, accel_phys) 
            
            # 2. BIOMIMETIC SHIELD & LANDAUER COST
            # Hull Damage increases with velocity gradient
            damage = ( (self.v ** 2) / (self.c ** 2) * 5.0 ) + (accel_phys / 1e8)
            real_damage = max(0, damage - self.bio_resilience)
            self.bio_integrity -= real_damage
            
            # SELF-REPAIR (Costing Petajoules)
            if self.bio_integrity < 100.0 and self.ship_energy > 0:
                repair_units = self.regeneration_rate * self.bio_resilience
                self.bio_integrity = min(100.0, self.bio_integrity + repair_units)
                
                # Energy Cost (Topic 0.13): Each 1% repair re-aligns 1e20 bits
                # Cost = count * k_B * T * ln(2)
                # Re-calibrated to petajoule scale
                energy_cost = repair_units * 1e22 * self.k_b * self.temp_k * math.log(2)
                self.ship_energy -= energy_cost

            # Step UET Core (Core now enforces v < c internally)
            res = self.solver.step(
                C=self.C, V=self.V, I=self.I, 
                J_in=j_in_pulse, J_out=np.zeros(5), 
                dt=dt, dx=1.0
            )
            self.C, self.V, self.I = res
            self.v = np.mean(self.V)

            if s % (max(1, steps // 5)) == 0:
                results.append({
                    "time": s * dt, "velocity": self.v,
                    "bio_integrity": self.bio_integrity, "energy": self.ship_energy
                })

        return results
