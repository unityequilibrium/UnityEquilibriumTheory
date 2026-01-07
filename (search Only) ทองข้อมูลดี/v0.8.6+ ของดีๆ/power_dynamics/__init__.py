"""
UET Power Dynamics Module - Consolidated Strategy & Simulation
"""

from .agents import Agent, TYPE_PROFILES
from .simulation import Population, run_simulation
from .wave import solve_wave_equation
from .analysis import analyze_cost_benefits, detect_equilibrium
from .report import generate_full_report, summarize_batch_results

__version__ = "1.0.0"
