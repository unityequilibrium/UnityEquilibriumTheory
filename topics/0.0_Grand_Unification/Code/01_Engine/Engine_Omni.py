"""
UET OMNI-ENGINE (The Grand Unification)
=======================================
Topic: 0.0 Grand Unification
Goal: The "Supreme Calculator" that drives all domains simultaneously.

Unifies:
1.  Galaxy Rotation (Gravity)
2.  Electroweak Mixing (Forces)
3.  Fluid Turbulence (Complexity)
4.  Mass Generation (Matter)
5.  Quantum Logic (Information)
6.  AI Cortex (Intelligence)

Theory:
All these systems are "Organs" of the same Information Field.
Changing the Global Parameter (beta) shifts them all instantly.
"""

import sys
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

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

# --- CORE IMPORTS ---
try:
    from docs.core.uet_parameters import UETParameters, get_params
    from docs.core.uet_base_solver import UETBaseSolver
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import core UET modules: {e}")
    sys.exit(1)

# --- TOPIC ENGINE LOADER ---
def load_topic_engine(topic_id: str, engine_file: str, class_name: str):
    """Dynamically loads an engine from a topic folder using standardized paths."""
    import importlib.util
    
    # Map Topic ID to folder (Standard 5x4 Grid)
    topic_dirs = {d.name.split('_')[0]: d for d in (ROOT / "docs" / "topics").iterdir() if d.is_dir()}
    topic_folder = topic_dirs.get(topic_id)
    
    if not topic_folder:
        raise ImportError(f"Topic {topic_id} folder not found in docs/topics/")
        
    engine_path = topic_folder / "Code" / "01_Engine" / engine_file
    
    if not engine_path.exists():
        # Fallback for legacy items if any
        engine_path = topic_folder / "Code" / engine_file
        
    if not engine_path.exists():
        raise ImportError(f"Engine file {engine_file} not found in {topic_id}")

    spec = importlib.util.spec_from_file_location(class_name, str(engine_path))
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name), module
    return None, None

# 1. Gravity (Topic 0.1)
UETGalaxyEngine, mod_galaxy = load_topic_engine("0.1", "Engine_Galaxy_V3.py", "UETGalaxyEngine")
GalaxyParams = mod_galaxy.GalaxyParams

# 2. Electroweak (Topic 0.6)
UETElectroweakSolver, _ = load_topic_engine("0.6", "Engine_Electroweak.py", "UETElectroweakSolver")

# 3. Fluid (Topic 0.10)
UETFluidSolver, _ = load_topic_engine("0.10", "Engine_UET_2D.py", "UETFluidSolver")

# 4. Mass (Topic 0.17)
UETMassEngine, _ = load_topic_engine("0.17", "Engine_Mass_Higgs.py", "UETMassEngine")

# 5. Quantum (Topic 0.18)
UETQuantumSolver, _ = load_topic_engine("0.18", "Engine_Quantum_Logic.py", "UETQuantumSolver")

# 6. AI (Topic 0.24)
UetcortexNeuralNet, _ = load_topic_engine("0.24", "UET_AI_Core.py", "UetcortexNeuralNet")

# 7. Economics (Topic 0.25)
PowerDynamicsEngine, _ = load_topic_engine("0.25", "Engine_Power_Dynamics.py", "PowerDynamicsEngine")

# 8. Atomic Physics (Topic 0.20)
UETAtomicEngine, _ = load_topic_engine("0.20", "Engine_Atomic_Hydrogen.py", "UETAtomicEngine")


@dataclass
class UniverseState:
    """Snapshot of the Entire Universe at a given Beta."""

    beta_phase: float
    galaxy_chi2: float
    weinberg_angle: float
    reynolds_critical: float
    tau_mass: float
    entanglement_entropy: float
    ai_learning_rate: float
    economic_omega: float
    atomic_error: float
    status: str
    audit_flags: dict # Map of component -> status (A/H)


class UETOmniEngine:
    """
    The Supreme Calculator.
    Orchestrates the Master Equation across all scales of reality.
    """

    def __init__(self):
        print("🌌 Initializing UET OMNI-ENGINE...")
        self.history = []

    def run_universe(self, beta: float = 1.0) -> UniverseState:
        """
        Runs one iteration of the Universe with a specific Vacuum Entropy (beta).
        """
        print(f"\n⚡ IGNITING UNIVERSE (Beta = {beta:.4f})...")
        
        # --- 1. COSMIC SCALE (Galaxy / Topic 0.1) ---
        print("  [1] Propagating Gravity...")
        p_gal = get_params("0.1", beta=beta)
        gal_params = GalaxyParams(mass_disk=1e10, radius_disk=3.0, mass_bulge=0.0, redshift=0.0, name="Cosmos")
        galaxy = UETGalaxyEngine(gal_params)
        galaxy.params = p_gal # Honest sync
        
        # Trigger actual calculation at a representative radius (e.g., 20 kpc)
        # and derive the effective Halo Ratio from total mass.
        # This replaces the stale 'M_I_ratio' property.
        r_probe = 20.0
        v_tot = galaxy.compute_velocity_at_radius(r_probe)
        # Halo Ratio = M_tot / M_bar
        # M_tot = (V^2 * r) / G
        from docs.core.uet_parameters import G_GALACTIC
        M_tot_derived = (v_tot**2 * r_probe) / G_GALACTIC
        
        # Calculate Baryonic Mass at that radius
        R_d = gal_params.radius_disk
        x = r_probe / R_d
        M_bar_r = gal_params.mass_disk * (1 - (1 + x) * np.exp(-x))
        halo_ratio = M_tot_derived / M_bar_r if M_bar_r > 0 else 1.0

        # --- 2. FUNDAMENTAL SCALE (Electroweak / Topic 0.6) ---
        print("  [2] Aligning Forces...")
        p_ew = get_params("0.6", beta=beta)
        ew_solver = UETElectroweakSolver(params=p_ew)
        # This method returns (pivot, corrected, status). We need the corrected value.
        _, eff_sin2_theta, _ = ew_solver.weinberg_angle_geometric()

        # --- 3. MACROSCOPIC SCALE (Fluid / Topic 0.10) ---
        print("  [3] Calculating Turbulence Limit...")
        p_fluid = get_params("0.10", beta=beta)
        fluid_solver = UETFluidSolver(params=p_fluid)
        re_c, _ = fluid_solver.predict_critical_reynolds()

        # --- 4. MATTER SCALE (Mass / Topic 0.17) ---
        print("  [4] Generating Mass Spectrum...")
        p_mass = get_params("0.17", beta=beta)
        mass_engine = UETMassEngine()
        mass_engine.params = p_mass
        tau_mass = mass_engine.predict_tau_mass(0.511, 105.66)

        # --- 5. INFORMATION SCALE (Quantum / Topic 0.18) ---
        print("  [5] Entangling Qubits...")
        p_quant = get_params("0.18", beta=beta)
        q_solver = UETQuantumSolver(num_qubits=2, params=p_quant)
        q_solver.apply_hadamard(0)
        q_solver.apply_cnot(0, 1)
        entropy = q_solver.calculate_entropy(1)

        # --- 6. INTELLIGENCE SCALE (AI / Topic 0.24) ---
        print("  [6] Training Cortex...")
        p_ai = get_params("0.24", beta=beta)
        ai_net = UetcortexNeuralNet(params=p_ai)
        X = np.random.randn(10, 2)
        y = np.random.randn(10, 1)
        loss = ai_net.train_step(X, y)

        # --- 7. STRATEGIC SCALE (Economics / Topic 0.25) ---
        print("  [7] Allocating Resources (World Bank Data)...")
        p_econ = get_params("0.25", beta=beta)
        econ_engine = PowerDynamicsEngine(params=p_econ)
        omega_econ = econ_engine.step(0)

        # --- 8. ATOMIC SCALE (Hydrogen / Topic 0.20) ---
        print("  [8] Checking Hydrogen Spectrum...")
        p_atom = get_params("0.20", beta=beta)
        atomic_engine = UETAtomicEngine()
        atomic_engine.params = p_atom
        h_alpha_theory = atomic_engine.transition_wavelength(3, 2)
        h_alpha_nist = 656.28
        atomic_err = abs(h_alpha_theory - h_alpha_nist) / h_alpha_nist * 100.0

        # --- SYNTHESIS ---
        state = UniverseState(
            beta_phase=beta,
            galaxy_chi2=halo_ratio,
            weinberg_angle=eff_sin2_theta,
            reynolds_critical=re_c,
            tau_mass=tau_mass,
            entanglement_entropy=entropy,
            ai_learning_rate=loss,
            economic_omega=omega_econ,
            atomic_error=atomic_err,
            status="STABLE" if 0.9 <= beta <= 1.1 else "UNSTABLE",
            audit_flags={
                "Gravity": "A" if p_gal.dynamic else "H",
                "Electroweak": "A" if p_ew.dynamic else "H",
                "Fluid": "A" if p_fluid.dynamic else "H",
                "Mass": "A" if p_mass.dynamic else "H",
                "Quantum": "A" if p_quant.dynamic else "H",
                "AI": "A" if p_ai.dynamic else "H",
                "Economy": "A" if p_econ.dynamic else "H",
                "Atomic": "A" if p_atom.dynamic else "H",
            }
        )
        self.history.append(state)
        return state

    def report(self, state: UniverseState):
        """Prints the Grand Dashboard."""
        print(f"\n💎 UET UNIVERSAL DASHBOARD (Beta={state.beta_phase})")
        print("=" * 60)
        print(f"  🌌 Gravity (Halo Ratio):      {state.galaxy_chi2:.4f} ({state.audit_flags['Gravity']})")
        print(f"  ⚛️  Electroweak (Angle):      {state.weinberg_angle:.5f} ({state.audit_flags['Electroweak']})")
        print(f"  🌊 Fluid (Crit Reynolds):     {state.reynolds_critical:.1f} ({state.audit_flags['Fluid']})")
        print(f"  ⚖️  Mass (Tau MeV):           {state.tau_mass:.2f} ({state.audit_flags['Mass']})")
        print(f"  🔮 Quantum (Entropy):         {state.entanglement_entropy:.4f} ({state.audit_flags['Quantum']})")
        print(f"  🧠 AI (Initial Loss):         {state.ai_learning_rate:.4f} ({state.audit_flags['AI']})")
        print(
            f"  💰 Economy (Wealth Omega):    {state.economic_omega:.4f} ({state.audit_flags['Economy']})"
        )
        print(f"  ⚛️  Atomic (H-Alpha Error):    {state.atomic_error:.4f}% ({state.audit_flags['Atomic']})")
        print("-" * 60)
        print(f"  STATUS: {state.status}")
        print("=" * 60)


if __name__ == "__main__":
    omni = UETOmniEngine()
    # 1. Run Standard Universe
    u_stable = omni.run_universe(beta=1.0)
    omni.report(u_stable)

    # 2. Run Chaotic Universe (High Entropy)
    # u_chaos = omni.run_universe(beta=0.1) # High disorder? Or beta is coupling...
    # Low beta = Low Coupling = High Entropy?
    # Let's try beta=10.0 (Super tight coupling, Rigid Universe)
    # u_rigid = omni.run_universe(beta=10.0)
    # omni.report(u_rigid)
