import numpy as np


class LivingStructure:
    def __init__(self, material="Basalt_Geopolymer"):
        """
        Model of a structure that transitions from Artificial to Natural.

        Physics/Biology Models:
        1. Material Degradation: Corrosion/Hydrolysis over time.
        2. Mineralization (Accretion): Growth of CaCO3 by marine organism.
        3. Load Transfer: Shift of structural burden.
        """
        self.material = material
        self.age_years = 0.0

        # Design Load (Force required to withstand waves/currents)
        self.design_load = 100.0  # Arbitrary Units (AU)

        # 1. Artificial Strength Properties (Initial)
        if material == "Basalt_Geopolymer":
            self.initial_strength = 250.0  # High tensile strength, Start strong
            self.degradation_rate = 0.005  # 0.5% per year (Very durable)
        elif material == "Steel_Concrete":
            self.initial_strength = 300.0  # Stronger initially
            self.degradation_rate = 0.05  # 5% per year (Rust/Corrosion)
        else:
            raise ValueError(f"Unknown material: {material}")

        self.current_artificial_strength = self.initial_strength

        # 2. Natural Strength Properties (Coral Rock)
        self.natural_mass = 0.0
        self.natural_strength = 0.0

        # Accretion Rate: How fast coral/algae build rock
        # Unit: Strength AU per year
        # Starts slow (recruitment), speeds up (growth), plateaus (space limit)
        self.accretion_base_rate = 3.0

    def update_year(self, dt_years=1.00):
        """
        Simulate one time step (typically 1 year).
        """
        self.age_years += dt_years

        # A. Artificial Degradation (Exponential Decay)
        # S_t = S_0 * (1 - r)^t
        # Linear approximation for simple steps: S_new = S_old * (1 - r*dt)
        loss = self.current_artificial_strength * self.degradation_rate * dt_years
        self.current_artificial_strength -= loss

        # B. Natural Accretion (Logistic Growth of Reef)
        # Rate depends on available surface area and established colony
        # Simple S-curve model logic:
        # Growth factor increases as reef establishes (Years 0-10), then steady

        growth_factor = 1.0
        if self.age_years < 5:
            growth_factor = 0.2 * self.age_years  # Establishing
        elif self.age_years < 20:
            growth_factor = 1.0 + (self.age_years - 5) * 0.1  # Exponential growth phase
        else:
            growth_factor = 2.5  # Mature reef complex (High deposition)

        added_strength = self.accretion_base_rate * growth_factor * dt_years
        self.natural_strength += added_strength

    def get_status(self):
        total_strength = self.current_artificial_strength + self.natural_strength
        safety_factor = total_strength / self.design_load

        return {
            "Age": f"{self.age_years:.1f} Years",
            "Artificial Str": f"{self.current_artificial_strength:.2f}",
            "Natural Str": f"{self.natural_strength:.2f}",
            "Total Str": f"{total_strength:.2f}",
            "Safety Factor": f"{safety_factor:.2f}",
        }
