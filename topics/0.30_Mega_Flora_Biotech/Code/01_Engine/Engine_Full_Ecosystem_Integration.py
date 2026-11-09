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

import sys
import os

# Import sibling modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from docs.core.uet_parameters import get_params
from Engine_Growth_Simulation import YggdrasilEngine

try:
    from Engine_Mycelial_Network import MycelialNetwork, BioEntity
except ImportError:
    # Handle potential import issues if paths are tricky
    pass


class YggdrasilEcoAdapter(YggdrasilEngine):
    """
    Wraps the YggdrasilEngine to work as a 'BioEntity' in the Mycelial Network.
    """

    def __init__(self, species_name="Yggdrasil-Eco", growth_rate=1.2, params=None):
        # Resolve parameters correctly instead of passing growth_rate as params
        actual_params = params if params else get_params("0.30")
        super().__init__(species_name=species_name, params=actual_params)
        
        # Override growth_rate after proper initialization
        self.growth_rate = growth_rate

        # Adaptation for MycelialNetwork
        self.type = "TREE"
        self.age = 0
        self.biomass_kg = 0.1  # Start small
        self.waste_input = 0  # Trees don't eat trash directly

        # Internal State tracking (sync with parent variables)
        self.height_m = 0.5
        self.diameter_cm = 1.0
        self.current_density = self.wood_density_start
        self.root_depth_m = 0.3

        self.history = []

    def receive_nutrients(self, amount):
        """
        Convert fungal nutrients directly into Biomass.
        Biomass = Energy Storage.
        """
        # 1 Unit Nutrient = 0.5 kg Biomass (Biological Conversion Efficiency)
        added_biomass = amount * 0.5
        self.biomass_kg += added_biomass
        # print(f"    [+] Tree absorbed {added_biomass:.2f} kg from Fungi")

    def process_waste(self):
        return 0  # Trees are not digesters

    def grow_one_year(self, year, genetic_factor=1.0):
        """
        Executes ONE year of the 'Adaptive Logic' from the parent class.
        Modified to use 'self.biomass_kg' which might have been boosted by Fungi.
        """
        self.age = year

        # --- LOGIC COPIED & ADAPTED FROM PARENT (Step-by-Step) ---

        # 1. Calculate Stress
        stress_ratio = (self.height_m * 100) / self.diameter_cm

        # 2. Smart Allocation
        if stress_ratio > 90:
            allocation_height = 0.2
            allocation_girth = 0.8
        else:
            allocation_height = 0.7
            allocation_girth = 0.3

        # 3. Age Factor
        age_factor = 1.0
        if year < 15:
            age_factor = 1.6 * genetic_factor  # Sprint + GMO
        elif year > 50:
            age_factor = 0.5

        # 4. Growth Power (Driven by Biomass!)
        # Crucial: If Biomass was boosted by Fungi, this 'growth_power' explodes.
        # Tapering Logic: Height growth slows down as it gets taller due to hydraulic tension
        h_tension_drag = max(0.1, 1.0 - (self.height_m / 250.0))
        growth_power = (self.biomass_kg**0.6) * self.growth_rate * age_factor * h_tension_drag

        # Apply Allocation rebalancing
        if self.height_m > 30.0:
            allocation_height *= 0.7
            allocation_girth *= 1.3

        delta_h = (growth_power * allocation_height) * 0.5
        delta_d = (growth_power * allocation_girth) * 0.2

        self.height_m += delta_h
        self.diameter_cm += delta_d

        # 5. Density
        if self.current_density < self.wood_density_max:
            self.current_density += allocation_girth * 10.0

        # 6. Recalculate Biomass (Physics Check)
        # We must sync the 'Biological Biomass' with 'Physical Volume'
        # But we KEEP the extra biomass from Fungi as 'Stored Energy' (Starch)
        # that didn't turn into wood yet (or assumes it drove the growth).
        # For simulation simplicity, we re-calculate physical mass:
        import math

        physical_volume = (math.pi * ((self.diameter_cm / 200) ** 2) * self.height_m) / 3
        physical_mass = physical_volume * self.current_density

        # Update Biomass: Max(Stored, Physical)
        # If we grew, we used the stored biomass.
        self.biomass_kg = max(self.biomass_kg, physical_mass)

        # 7. Roots
        target_root_depth = self.height_m * 0.7
        if self.root_depth_m < target_root_depth:
            self.root_depth_m += 0.5

        # 8. Stats
        resistance = (self.diameter_cm**3) * (self.current_density / 100.0)
        integrity_newtons = resistance * 50.0

        stats = {
            "year": year,
            "height_m": round(self.height_m, 2),
            "diameter_cm": round(self.diameter_cm, 2),
            "biomass_kg": round(self.biomass_kg, 1),
            "integrity_score": round(integrity_newtons, 0),
            "stress_ratio": round(stress_ratio, 1),
        }
        self.history.append(stats)
        return stats
