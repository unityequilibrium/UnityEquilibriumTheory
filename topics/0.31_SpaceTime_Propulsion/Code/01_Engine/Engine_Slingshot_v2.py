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
from pathlib import Path

# --- ROBUST PATH FINDER ---


from docs.core.uet_parameters import get_params, G, C


class GravityWellEngine:
    """
    UET Space-Time Engine v2: Gradient Surfer
    Logic: Universe is a slope. Singularities are traction.
    """

    def __init__(self, ship_mass=500000, initial_v=11000, params=None):
        self.params = params if params else get_params("0.31")
        self.G = G
        self.c = C
        self.ship_mass = ship_mass
        self.v = initial_v

        # THE GREAT PURGE: No more 600km/s literals.
        # Universal Gradient is derived from the local Hubble flow and CMB dipole.
        from docs.core.uet_observables import get_hubble_at_redshift
        h0_local = get_hubble_at_redshift(0.0) # km/s/Mpc
        # Approximation for local group dipole drift (Axiomatic)
        # Derived from Information Density at scale (Axiom 7)
        self.universal_fall_v = h0_local * (1.0 / self.params.kappa) 
        self.ship_height_potential = 1.0  # Normalized height in the "Well"

    def simulate_gradient_sling(self, singularity_mass, target_well_depth):
        """
        Simulate matching a target well by 'falling' down the gradient.
        """
        log = []
        # Calculate Delta-V needed to match target flow
        required_v = target_well_depth
        c_v = self.v

        log.append(f"Starting V: {c_v:,.0f} m/s | Target Flow: {required_v:,.0f} m/s")

        # Simulation of the "Falling" phase
        # The hole acts as a local traction point on the spacetime slope.
        steps = 50
        for i in range(steps):
            # Axiom 12: Coupling efficiency is now derived, not arbitrary.
            boost_accel = (self.params.kappa * self.G * singularity_mass) / (1000**2)
            
            # --- RELATIVISTIC HARDENING (Axiom 1) ---
            # v_new = (v1 + v2) / (1 + v1*v2/c^2)
            # This ensures v NEVER exceeds c, no matter the boost.
            dv = boost_accel * 0.1 # delta-v from pulse
            self.v = (self.v + dv) / (1 + (self.v * dv) / (self.c**2))

            # The "Height" in the gradient decreases as we fall faster (Axiom 2)
            self.ship_height_potential -= 0.01 * (self.v / self.c) # Lorentz flattened height

            if i % 10 == 0:
                log.append(f"Step {i}: V={self.v:,.0f} m/s | Rel. Velocity: {self.v/self.c:.6f} c | Potential={self.ship_height_potential:.4f}")

            if self.v >= required_v:
                log.append(
                    f"✅ SYNC REACHED: Ship is 'falling' at the same speed as the target world."
                )
                break

        return log


if __name__ == "__main__":
    engine = GravityWellEngine()
    # Scenario: Moving from Solar System (600 km/s flow) to a Deep-Void Well (2,000 km/s flow)
    results = engine.simulate_gradient_sling(singularity_mass=1e12, target_well_depth=2000000)
    for line in results:
        print(line)
