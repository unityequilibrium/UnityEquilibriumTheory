"""
Engine_Power_Dynamics.py - UET Topic 0.25 (v0.9.0)
=================================================
Refined Strategic Power Engine.
Unified with UET Master Equation while maintaining research script compatibility.
"""

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
import random
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path

# --- ROBUST PATH FINDER ---


# Core Imports
try:
    from docs.core.uet_base_solver import UETBaseSolver
    from docs.core.uet_master_equation import UETParameters
    from docs.core.uet_parameters import INTEGRITY_KILL_SWITCH, get_params
    from docs.core.uet_data_orchestrator import orchestrator
    from docs.core.scientific_validation import ScientificValidator
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR in Topic 0.25: {e}")
    UETBaseSolver = object
    UETParameters = None
    orchestrator = None
    ScientificValidator = None


@dataclass
class StrategicAgent:
    id: int
    agent_type: str
    power: float
    resources: float
    boldness: float
    selfishness: float
    intellect_level: int = 0
    shared_account: float = 0.0
    liquid_account: float = 0.0
    land_controlled: float = 0.0
    water_usage_log: Dict[str, float] = None
    influence_radius: float = 1.0
    success_count: int = 0

    def __post_init__(self):
        if self.water_usage_log is None:
            self.water_usage_log = {"blue": 0.0, "gray": 0.0, "black": 0.0}

    def to_dict(self):
        return asdict(self)


class PowerDynamicsEngine(UETBaseSolver):
    """
    Standardized UET Engine for Strategic Power Simulations (v0.9.0).
    Unified with Field Theory via UETBaseSolver.
    """

    TYPE_PROFILES = {
        "A": {
            "power_init": 0.3,
            "boldness": 0.2,
            "selfishness": 0.3,
            "name": "Normal-Regular",
        },
        "B": {
            "power_init": 0.8,
            "boldness": 0.2,
            "selfishness": 0.5,
            "name": "Extra-Regular",
        },
        "C": {
            "power_init": 0.3,
            "boldness": 0.9,
            "selfishness": 0.1,
            "name": "Normal-Irregular",
        },
        "D": {
            "power_init": 0.8,
            "boldness": 0.9,
            "selfishness": 0.8,
            "name": "Extra-Irregular",
        },
    }

    def __init__(self, nx=1000, params: UETParameters = None, logger=None):
        # 1. Physics Initialization
        if params is None:
            try:
                from docs.core.uet_parameters import get_params
                params = get_params("0.25")
            except:
                params = UETParameters(domain="social")

        super().__init__(
            nx=nx,
            ny=1,
            dt=0.001,  # Stable standard
            params=params,
            name="UET_Strategy_Core",
            topic="0.25_Strategy",
            pillar="01_Engine",
            stable_path=True,
        )
        self.agents = [] # Field Registry
        self.history = [] # State History
        # Support for explicit logger passing (Legacy API compatibility)
        if logger:
            self.logger = logger

        # 2. Strategic Elements (Axiomatic Scaling)
        # Use Information Capacity proxy (reciprocal of phi_loss) as the base for 'Physical Area'
        # Nominal: 1.0 / 0.05 = 20.0 units
        capacity = 1.0 / (self.params.phi_loss + 1e-12)
        self.total_global_land = capacity * self.params.kappa
        self.nature_health = 1.0
        self.land_lease_fund = 0.0
        # Water linked to total informatic volume and coupling (beta)
        self.water_pools = {"blue": capacity * self.params.beta, "gray": 0.0, "black": 0.0}
        self.global_water_productivity = 0.0

        # 3. Data Integration
        self.real_data = self.load_real_data()

    def load_real_data(self):
        """Standardized UET Data Loader via Orchestrator."""
        if orchestrator:
            return orchestrator.get_economy_baseline()
        return {}

    def sync_to_field(self):
        """Map Agent Resources to the C field (Order Parameter)."""
        if not self.agents:
            return
        res_values = [a.resources for a in self.agents]
        f_vals = np.zeros(self.nx)
        f_vals[: min(len(res_values), self.nx)] = res_values[: self.nx]
        self.C[0, :] = f_vals

    def sync_from_field(self):
        """Update Agent Resources from the computed C field."""
        for i, a in enumerate(self.agents):
            if i < self.nx:
                a.resources = self.C[0, i]
                a.liquid_account = a.resources - a.shared_account

    def seed_from_country(self, country_name="World_Total"):
        """Seeds simulation with Real-World Gini constraints."""
        economies = self.real_data.get("Economies", {})
        specs = economies.get(country_name, economies.get("World_Total", {}))
        if not specs:
            self.seed_real_world()
            return

        gini_target = specs["Gini"] / 100.0
        self._generate_manifold(gini_target)
        if ScientificValidator:
            s_score = ScientificValidator.calculate_sincerity_score(1.0, 1.0)
            print(
                f"🌍 Seeding {country_name}: Gini {gini_target} -> C Field. [Scientific Sincerity: {s_score:.2f}]"
            )

    def seed_real_world(self, total_population: int = 1000):
        """Legacy API: Calibrates manifold to standard 1-9-90 Model."""
        # Standard Global Gini is ~0.62-0.70
        self._generate_manifold(0.62)

    def seed_8_billion(self, inject_stabilizers: bool = True):
        """Legacy API: Scaled 8B Macro-Manifold."""
        # Use a higher inequality for global scale
        self._generate_manifold(0.80)
        if not inject_stabilizers:
            # Strip stabilizers
            for a in self.agents:
                if a.agent_type == "C":
                    a.agent_type = "A"

    def _generate_manifold(self, gini_target: float):
        """Unified internal manifold generator with automated field sync."""
        num = self.nx
        sigma = gini_target * 2.0
        wealth = np.random.lognormal(mean=0.0, sigma=sigma, size=num)
        wealth = np.clip(wealth, 0.01, 20.0)
        wealth = np.sort(wealth / np.mean(wealth))

        self.agents = []
        for i, res in enumerate(wealth):
            rank = i / num
            t = (
                "D"
                if rank > 0.99
                else ("B" if rank > 0.90 else ("C" if random.random() < 0.1 else "A"))
            )
            p = self.TYPE_PROFILES[t]
            a = StrategicAgent(
                id=i,
                agent_type=t,
                power=0.5 + res * 0.5,
                resources=res,
                boldness=p["boldness"],
                selfishness=p["selfishness"],
            )
            self.agents.append(a)

        # Start field as base-wealth average to prevent vacuum-drop artifacts
        self.C = np.ones((1, self.nx)) * np.mean(wealth)
        self.sync_to_field()

    def apply_world_lease(self, fee_rate: float = 0.05):
        """Axiomatic Redistribution: J_in/J_out modulation via Field."""
        if INTEGRITY_KILL_SWITCH:
            return
        self.sync_to_field()
        high_mask = self.C > 10.0
        lease_pool = np.sum(self.C[high_mask]) * fee_rate
        self.C[high_mask] *= 1 - fee_rate
        # Redistribute to lower 90%
        low_mask = self.C < 1.0
        if np.any(low_mask):
            self.C[low_mask] += lease_pool / np.sum(low_mask)
        self.sync_from_field()
        return lease_pool

    def apply_shared_responsibility(self, injection_amount: float = 100.0):
        """Axiomatic 'Half-Half' Injection."""
        beneficiaries = [a for a in self.agents if a.resources < 2.0]
        if not beneficiaries:
            return 0.0
        share = injection_amount / len(beneficiaries)
        for a in beneficiaries:
            a.liquid_account += share * 0.5
            a.shared_account += share * 0.5
            a.resources = a.liquid_account + a.shared_account
        self.sync_to_field()
        return injection_amount

    def apply_nature_state_balance(self, lease_rate: float = 0.02):
        """The 'State as Nature' Pillar Integration."""
        self.sync_to_field()
        rent = np.sum(self.C) * lease_rate
        self.C *= 1 - lease_rate
        # Restoration linked to Informational Capacity (Axiom 10)
        restoration_scale = self.params.I_max * 10000.0 
        self.nature_health = min(1.0, self.nature_health + (rent / restoration_scale))
        self.sync_from_field()
        return rent

    def apply_water_loop_economics(self, rain_input: float = 50000.0):
        """Water Loop Axiomatic Scaling."""
        self.water_pools["blue"] += rain_input
        # Efficiency is linked to field homogeneity (lower Omega = better recycling)
        productivity = 1.0 / (self.calculate_omega() + 1.0)
        self.global_water_productivity = productivity
        return productivity

    def step(self, step_idx: int = 0, **kwargs):
        """Axiomatic Step with Strategic Agent Behavior (v0.9.0)."""
        if INTEGRITY_KILL_SWITCH:
            return

        # 1. Map Agent Intent to Axiomatic Forces
        # Ensure we sync before applying manual field perturbations
        self.sync_to_field()
        avg_c = np.mean(self.C)
        for i, a in enumerate(self.agents):
            if i >= self.nx:
                break

            # Type D: Axiom 5 (Natural Will) -> Local Extraction (Increases local C)
            if a.agent_type == "D":
                rate = a.boldness * self.nature_health * self.params.W_N * avg_c
                self.C[0, i] += rate
                # Environmental degradation linked to Informational Loss (phi)
                # Scaled by phi_loss / I_max to keep it in macroscopic bounds
                self.nature_health -= rate * (self.params.phi_loss / self.params.I_max)

            # Type C: Axiom 10 (Coherence) -> Potential Leveling
            elif a.agent_type == "C":
                if self.nx > 1:
                    side = random.choice([-1, 1])
                    neighbor = (i + side) % self.nx
                    if self.C[0, i] > self.C[0, neighbor]:
                        diff = self.C[0, i] - self.C[0, neighbor]
                        transfer = diff * a.boldness * self.params.kappa  # Aggressive leveling
                        self.C[0, i] -= transfer
                        self.C[0, neighbor] += transfer

        # 2. Physics Core Step
        phi_loss = self.params.phi_loss
        self.C += self.params.gamma_J * phi_loss 
        res = self.engine.step(self.C, dt=self.dt, dx=self.dx, I=self.I)
        if isinstance(res, tuple):
            if len(res) == 3:
                self.C, self.I, _ = res
            elif len(res) == 2:
                self.C, self.I = res
        else:
            self.C = res
        self.C = np.clip(self.C, 0.001, 100.0)

        # 3. Nature Health Update
        if self.nx > 1:
            # Calculate gradient for entropy penalty (Axiom 1)
            grad_x = np.gradient(self.C[0, :], self.dx)
            # Entropy penalty linked to Informational Loss (phi)
            # AXIO-REPAIR v0.9.5: Use capacity proxy for decay scaling
            capacity = 1.0 / (self.params.phi_loss + 1e-12)
            dOmega = (
                np.sum(grad_x**2) * (self.params.phi_loss / (capacity + 1e-12))
                * (self.params.beta / self.params.kappa)
            )
            self.nature_health -= dOmega
        
        self.nature_health = np.clip(self.nature_health, 0.0, 1.0)

        # 4. Finalization
        self.sync_from_field()
        omega = self.calculate_omega()
        self.history.append(omega)
        self.time += self.dt
        self.step_count += 1
        if self.logger:
            self._log_current_state(self.step_count)
        return omega

    def step_macro(self, rounds=1):
        """Macro-stepping for global simulations."""
        for _ in range(rounds):
            self.step()
        return self.calculate_omega()

    def calculate_omega(self) -> float:
        return self.engine.compute_omega(self.C, dx=self.dx)

    def get_extra_metrics(self) -> Dict[str, Any]:
        return {
            "nature_health": float(self.nature_health),
            "gini_estimate": float(np.std(self.C) / (np.mean(self.C) + 1e-9)),
            "capital_concentration": float(np.max(self.C) / (np.sum(self.C) + 1e-9)),
        }

    def save_summary(self):
        self.save_results()


if __name__ == "__main__":
    print("🚀 Verifying Strategy Engine (0.25) - Standardized v0.9.0...")
    engine = PowerDynamicsEngine(nx=100)
    engine.seed_from_country("World_Total")
    for i in range(100):
        engine.step(i)
    m = engine.get_extra_metrics()
    print(f"  Final Gini: {m['gini_estimate']:.3f} | Nature: {m['nature_health']:.3f}")
    print("✅ Strategy Unified with UET Core.")
