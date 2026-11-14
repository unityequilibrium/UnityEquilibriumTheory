"""
UET ICN Space Engine - Microgravity Perovskite Synthesis
========================================================
Axiomatic simulation of "Space-Grown" logic gates.

Target: Orbital Deposition (Zero-G / High-Vacuum)
Substrate: Perovskite Thin-Film
Market: Satellite Chip Supply (Medium-Node / High-Stability)
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
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Ensure project root is in path
current_file = Path(__file__).resolve()
project_root = current_file.parents[5] 
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from docs.core.uet_base_solver import UETBaseSolver
from docs.core.uet_parameters import get_params

class SpaceSynthEngine(UETBaseSolver):
    """
    Simulation of the "Perovskite Orbital Factory".
    Zero-G environment eliminates convective defects (Axiom 7).
    """

    def __init__(self, nx=64, ny=128, dt=0.01, mode="EARTH"):
        params = get_params("0.34")
        super().__init__(
            nx=nx, ny=ny, dt=dt, params=params, name=f"ICN_Space_{mode}",
            topic="0.34_Information_Centric_Nanofabrication", pillar="01_Engine"
        )
        self.mode = mode
        self.C = np.ones((self.ny, self.nx)) * 0.1 # Seed Flux
        self._initialize_saw_trap()

    def _initialize_saw_trap(self):
        self.I = np.ones((self.ny, self.nx))
        cx, cy = self.nx // 2, self.ny // 2
        r = self.nx // 4
        
        # S-Gate Logic Well (Acoustic Node)
        for y in range(self.ny):
            for x in range(self.nx):
                is_node = False
                if (x-cx)**2 + (y-(cy-r//2))**2 < (r//2)**2:
                    if x > cx: is_node = True
                if (x-cx)**2 + (y-(cy+r//2))**2 < (r//2)**2:
                    if x < cx: is_node = True
                if abs(x-cx) < 2 and abs(y-cy) < r:
                    is_node = True
                if is_node: self.I[y, x] = 0.0
                
        self.grad_I_y, self.grad_I_x = np.gradient(self.I, self.dx)

    def step(self, step_idx: int = 0):
        # 1. External Conditions (Axiom 4: Semi-Open)
        noise_level = 0.05 if self.mode == "EARTH" else 0.001 # 50x lower noise in orbit
        convection = 0.02 if self.mode == "EARTH" else 0.0    # No gravity convection in space!
        
        # Source Flux (Adding matter to the system - Axiom 1)
        self.C += 0.1 * self.dt # Increased flux for 500-step visibility
        
        # Convective Drift (Unintended displacement - Axiom 7)
        if convection > 0:
            self.C = np.roll(self.C, 1, axis=0) * (1-convection) + self.C * convection
            
        # 2. Gradient Drift (Resonant SAW Force)
        flux_x = self.C * self.grad_I_x
        flux_y = self.C * self.grad_I_y
        _, div_flux_x = np.gradient(flux_x, self.dx)
        div_flux_y, _ = np.gradient(flux_y, self.dx)
        self.C += self.params.beta * (div_flux_x + div_flux_y) * self.dt
        
        # 3. Vacuum Scouring (Active selection)
        v_scour = 0.5 * self.params.phi_loss
        self.C -= v_scour * self.C * self.I * self.dt
        
        self.C = np.clip(self.C, 0, 1.25)
        
        if (step_idx + 1) % 50 == 0:
            avg_c = np.mean(self.C)
            bar = "#" * int(avg_c * 40) + "." * (20 - int(avg_c * 40))
            sys.stdout.write(f"\r   [{self.mode} SYNTH] [{bar}] Step {step_idx+1}/500 | Purity: {1-np.mean(self.C*self.I):.2%}")
            sys.stdout.flush()

        self.time += self.dt
        self.step_count += 1

    def get_quality_metrics(self):
        target = (self.I < 0.1).astype(float)
        actual = (self.C > 0.15).astype(float)
        bg = (self.I > 0.5).astype(float)
        fidelity = np.sum(target * actual) / (np.sum(target) + 1e-9)
        defects = np.sum(bg * actual) / (np.sum(bg) + 1e-9)
        return fidelity, defects

def run_space_audit():
    print(f"\n{'='*70}\n🛰️ PEROVSKITE ORBITAL FACTORY: Space Synthesis Audit\nTargeting: High-Orbit Satellite Chips (Resonant Deposition)\n{'='*70}\n")
    
    # 1. Audit Earth-Based Prototype (High Entropy)
    e_solver = SpaceSynthEngine(mode="EARTH")
    e_solver.run(steps=500, verbose=True)
    f1, d1 = e_solver.get_quality_metrics()
    
    # 2. Audit Orbital Factory (Low Entropy)
    s_solver = SpaceSynthEngine(mode="SPACE")
    s_solver.run(steps=500, verbose=True)
    f2, d2 = s_solver.get_quality_metrics()
    
    print(f"\n\n📊 COMPONENT QUALITY REPORT:")
    print(f"   - [EARTH] Fidelity: {f1:.1%} | Defects: {d1:.1%} (Stability Blip)")
    print(f"   - [SPACE] Fidelity: {f2:.1%} | Defects: {d2:.1%} (Pristine Pattern)")
    print(f"\n🚀 CONCLUSION:")
    print(f"   Space Synthesis is {d1/max(1e-6, d2):.1f}x more pure due to Convective Zero-ing.\n")

if __name__ == "__main__":
    run_space_audit()
