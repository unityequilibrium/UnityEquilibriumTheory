"""
UET Landauer Full Simulator
============================

Complete simulation with:
- Multiple agents with C, I, V
- Energy tracking via Landauer
- Space recording behavior
- Visualization

Author: Santa (Original Vision)
Date: 2025-12-30
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional
import os

from .core import K_B, LN_2, energy_per_bit, value_function, LandauerParams, LandauerSystem
from .thermodynamics import ThermodynamicSystem, behavior_to_entropy
from .space import UniverseSpace


@dataclass
class Agent:
    """An agent with C (communication), I (isolation), and V (value)."""

    name: str
    C: float = 1.0  # Communication rate
    I: float = 1.0  # Isolation rate
    M: float = 1.0  # Mobility
    alpha: float = 1.0  # Exponent

    @property
    def V(self) -> float:
        """Value = M × (C/I)^α."""
        return value_function(self.C, self.I, self.M, self.alpha)

    @property
    def C_I_ratio(self) -> float:
        """Communication to Isolation ratio."""
        return self.C / self.I if self.I > 0 else float("inf")


@dataclass
class SimulationConfig:
    """Configuration for simulation."""

    T: float = 300.0  # Temperature (K)
    dt: float = 0.01  # Time step
    duration: float = 10.0  # Total time
    n_agents: int = 3  # Number of agents


class FullSimulator:
    """
    Complete UET Landauer Simulator.

    Implements the full vision:
    "พฤติกรรม → เสื่อมพลังงาน → บันทึกเป็นข้อมูลลงใน Space"
    """

    def __init__(self, config: Optional[SimulationConfig] = None):
        """Initialize simulator."""
        self.config = config or SimulationConfig()
        self.time = 0.0

        # Create agents
        self.agents: List[Agent] = []
        for i in range(self.config.n_agents):
            agent = Agent(
                name=f"Agent_{i}",
                C=np.random.uniform(0.5, 2.0),
                I=np.random.uniform(0.5, 2.0),
                M=1.0,
                alpha=1.0,
            )
            self.agents.append(agent)

        # Thermodynamic system
        self.thermo = ThermodynamicSystem(T=self.config.T)

        # Space for recording
        self.space = UniverseSpace(T=self.config.T)
        self.space.create_region("Simulation", radius=1.0)

        # History
        self.history = {
            "time": [],
            "agents": {a.name: {"C": [], "I": [], "V": []} for a in self.agents},
            "total_E": [],
            "total_S": [],
            "total_I_bits": [],
        }

    def step(self):
        """Advance one time step."""
        dt = self.config.dt

        for agent in self.agents:
            # Dynamics: C and I interact
            # When C > I: system opens more
            # When I > C: system closes more

            noise = np.random.normal(0, 0.01)
            dC = 0.1 * (agent.I - agent.C) + noise
            dI = -0.1 * (agent.I - agent.C) - noise

            agent.C = max(0.1, agent.C + dC * dt)
            agent.I = max(0.1, agent.I + dI * dt)

            # Record behavior in Space (based on activity)
            activity = abs(dC) + abs(dI)
            bits = activity * 1e18  # Scale to reasonable bit count

            if bits > 0:
                self.thermo.add_behavior(bits)
                self.space.record("Simulation", bits, source=agent.name)

        self.time += dt
        self.space.advance_time(dt)

        # Record history
        self._record_history()

    def _record_history(self):
        """Record current state to history."""
        self.history["time"].append(self.time)

        for agent in self.agents:
            self.history["agents"][agent.name]["C"].append(agent.C)
            self.history["agents"][agent.name]["I"].append(agent.I)
            self.history["agents"][agent.name]["V"].append(agent.V)

        self.history["total_E"].append(self.thermo.state.E)
        self.history["total_S"].append(self.thermo.state.S)
        self.history["total_I_bits"].append(self.thermo.state.I_bits)

    def run(self) -> dict:
        """Run full simulation."""
        steps = int(self.config.duration / self.config.dt)

        for _ in range(steps):
            self.step()

        # Verify thermodynamic laws
        verification = self.thermo.verify_laws()

        return {
            "duration": self.config.duration,
            "steps": steps,
            "final_E": self.thermo.state.E,
            "final_S": self.thermo.state.S,
            "final_I_bits": self.thermo.state.I_bits,
            "law_1_ok": verification["law_1"]["conserved"],
            "law_2_ok": verification["law_2"]["entropy_increased"],
            "agents": [(a.name, a.C, a.I, a.V) for a in self.agents],
        }

    def plot(self, save_path: Optional[str] = None):
        """Plot simulation results."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(
            'UET Landauer Simulation\n"พฤติกรรม → พลังงาน → ข้อมูลใน Space"',
            fontsize=14,
            fontweight="bold",
        )

        time = self.history["time"]

        # Plot 1: C, I, V for each agent
        ax1 = axes[0, 0]
        for agent in self.agents:
            data = self.history["agents"][agent.name]
            ax1.plot(time, data["V"], label=f"{agent.name} V", linewidth=2)
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Value (V)")
        ax1.set_title("V = M × (C/I)^α : Value Function")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: C/I ratio
        ax2 = axes[0, 1]
        for agent in self.agents:
            data = self.history["agents"][agent.name]
            C = np.array(data["C"])
            I = np.array(data["I"])
            ax2.plot(time, C / I, label=f"{agent.name}", linewidth=2)
        ax2.set_xlabel("Time")
        ax2.set_ylabel("C/I Ratio")
        ax2.set_title("Communication / Isolation Ratio")
        ax2.axhline(y=1.0, color="r", linestyle="--", alpha=0.5, label="Balance")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Energy (Landauer)
        ax3 = axes[1, 0]
        ax3.plot(time, self.history["total_E"], "b-", linewidth=2)
        ax3.set_xlabel("Time")
        ax3.set_ylabel("Energy (J)")
        ax3.set_title("E = k_B T ln(2) × I : Landauer Energy")
        ax3.grid(True, alpha=0.3)
        ax3.ticklabel_format(style="scientific", axis="y", scilimits=(0, 0))

        # Plot 4: Information in Space
        ax4 = axes[1, 1]
        ax4.plot(time, self.history["total_I_bits"], "g-", linewidth=2)
        ax4.set_xlabel("Time")
        ax4.set_ylabel("Information (bits)")
        ax4.set_title("Information Recorded in Space")
        ax4.grid(True, alpha=0.3)
        ax4.ticklabel_format(style="scientific", axis="y", scilimits=(0, 0))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Plot saved: {save_path}")

        return fig


# Quick verification
if __name__ == "__main__":
    print("=" * 60)
    print("UET Landauer Full Simulator")
    print("=" * 60)

    # Create and run simulation
    config = SimulationConfig(T=300.0, dt=0.01, duration=10.0, n_agents=3)

    sim = FullSimulator(config)

    print("\nRunning simulation...")
    results = sim.run()

    print(f"\nResults:")
    print(f"  Duration: {results['duration']} s")
    print(f"  Steps: {results['steps']}")
    print(f"  Final Energy: {results['final_E']:.4e} J")
    print(f"  Final Entropy: {results['final_S']:.4e} J/K")
    print(f"  Final Info: {results['final_I_bits']:.4e} bits")
    print(f"\nThermodynamic Laws:")
    print(f"  Law 1 (Conservation): {'✓' if results['law_1_ok'] else '✗'}")
    print(f"  Law 2 (Entropy↑): {'✓' if results['law_2_ok'] else '✗'}")

    print(f"\nAgents final state:")
    for name, C, I, V in results["agents"]:
        print(f"  {name}: C={C:.2f}, I={I:.2f}, V={V:.2f}")

    # Save plot
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_path = os.path.join(script_dir, "simulation_result.png")
    sim.plot(save_path=plot_path)

    print("\n" + "=" * 60)
    print("Full Simulator - READY")
    print("=" * 60)
