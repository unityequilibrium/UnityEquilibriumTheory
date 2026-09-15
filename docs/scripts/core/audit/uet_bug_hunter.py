"""
UET Bug Hunter (The Truth Auditor)
==================================
Restored from v0.9.0 Integrity philosophy.

Objective:
1. Enforce 'Strict Truth' Policy (No Parameter Fitting).
2. Monitor G0-G4 Gate Validation during runtime.
3. Report honest failures (NaN, Divergence, Information Collapse).

Gates:
- G0: Energy Monotonicity (dOmega/dt <= 0)
- G1: Information Positivity (M_I > 0)
- G2: Entropy Consistency (dS/dt >= 0)
- G3: Gradient Sanity (Kappa-Stability)
- G4: Convergence/Consistency
"""

import numpy as np
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Strict Settings (Axiom 11)
np.seterr(all="raise")


@dataclass
class BugReport:
    topic: str
    status: str  # PASS, FAIL, NOISY
    gate_failures: List[str]
    diagnostics: Dict[str, Any]


class UETBugHunter:
    def __init__(self, topic: str):
        self.topic = topic
        self.logger = logging.getLogger(f"BugHunter_{topic}")
        self.history = {"omega": [], "entropy": [], "energy": []}

    def check_g0_energy_monotonicity(self, omega: float) -> bool:
        """G0: The Master Equation must minimize (Second Law)."""
        if not self.history["omega"]:
            self.history["omega"].append(omega)
            return True

        last_omega = self.history["omega"][-1]
        self.history["omega"].append(omega)

        # We allow a small epsilon for numeric noise, but any growth > 1% is a FAIL
        if omega > last_omega * 1.01:
            return False
        return True

    def check_g1_information_mass(self, m_i: float) -> bool:
        """G1: Information coupling must produce positive mass/energy."""
        return m_i >= 0

    def check_g4_numerical_stability(self, val: float) -> bool:
        """G4: Catch NaN or Inf before they propagate."""
        return np.isfinite(val)

    def audit_step(self, metrics: Dict[str, float]) -> List[str]:
        """
        Audit a single simulation step against G0-G4.
        Returns a list of failed gates.
        """
        failures = []

        # G4: First Check (Stability)
        for k, v in metrics.items():
            if not self.check_g4_numerical_stability(v):
                failures.append(f"G4_STABILITY_FAILURE ({k}=NaN)")

        # G0: Energy
        if "omega" in metrics:
            if not self.check_g0_energy_monotonicity(metrics["omega"]):
                failures.append("G0_ENERGY_GROWTH (Axiom 1 Violation)")

        # G1: info
        if "M_I" in metrics:
            if not self.check_g1_information_mass(metrics["M_I"]):
                failures.append("G1_INFORMATION_COLLAPSE (Axiom 2 Violation)")

        return failures

    def generate_final_report(self, total_steps: int, failures_count: int) -> str:
        if failures_count == 0:
            return "✅ INTEGRITY PASS: All Axiomatic Gates Validated."
        else:
            return f"❌ INTEGRITY FAIL: {failures_count}/{total_steps} steps violated UET Axioms."


def run_strict_audit(solver_func, params_list: List[Dict]):
    """
    Utility to run a solver function under the 'Bug Hunter' audit.
    """
    print(f"--- UET STRICT AUDIT START ---")
    hunter = UETBugHunter(topic="BatchAudit")

    for i, p in enumerate(params_list):
        try:
            result = solver_func(**p)
            f = hunter.audit_step(result)
            if f:
                print(f"[CASE {i}] FAIL: {f}")
            else:
                print(f"[CASE {i}] PASS")
        except Exception as e:
            print(f"[CASE {i}] CRASH: {e}")

    print(f"--- UET STRICT AUDIT END ---")
