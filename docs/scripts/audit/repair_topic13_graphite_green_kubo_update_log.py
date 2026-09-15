"""Append the Topic 13 Green-Kubo source-boundary wave to the update log."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_green_kubo_source_boundary_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
MARKER = "### 2026-08-13 - Topic 13 public Green-Kubo source boundary"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    text = LOG.read_text(encoding="utf-8-sig")
    if MARKER not in text:
        entry = """
### 2026-08-13 - Topic 13 public Green-Kubo source boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: Three primary Green-Kubo candidate routes were source-identified. Khadem/Wemhoff provides a graphite stacking comparator, Oliveira/Greaney provides a graphite-defect Green-Kubo route, and the Jung et al. supplementary source provides three source-reported 300 K comparator rows with locators and plus-minus values. None is accepted as a UET physical Kubo coefficient.
WHAT_REMAINS_OPEN: No candidate reports base-Phi amplitude or UET space-response state; the candidates are not a Ding TTG state match, URL-only records have no local source hash, and the accepted physical Kubo record, finite-temperature normal component, entropy current, dissipative balance, SI map, and independent alpha_Phi_K remain open.
DEPENDENCY_UNLOCKED: External Green-Kubo comparator boundary only; no physical UET transport, alpha, Full Topic 13, Core, Gravity, Galaxy, or external-validation unlock.
STATUS: PASS_SCOPED_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the source-boundary audit """ + digest(AUDIT) + """, full-gate projection """ + digest(FULL) + """, major-result register """ + digest(REGISTER) + """, and dependency record """ + digest(DEPENDENCY) + """. Primary source routes: https://www.sciencedirect.com/science/article/abs/pii/S0009261413005307, https://www.sciencedirect.com/science/article/abs/pii/S0927025615001639, and https://www.rsc.org/suppdata/c7/nr/c7nr04455k/c7nr04455k1.pdf.
EQUATION_OR_MAPPING: kappa_i = 1/(k_B*T^2*V) * integral <J_i(t)J_i(0)>dt is retained as a standard-physics comparator. Missing Phi/space-response mapping prevents KuboCoefficientRecord acceptance; no Delta_Tq=alpha_Phi_K*Delta_Phi calibration is emitted.
VERIFICATION: Source locators, method/material identity, numeric comparator presence, no silent UET relabel, no local hash claim for URL-only records, no fit, no target data, no alpha, and no holdout access pass. Focused tests pass (2 passed); full gate remains blocked.
CONTROLLING_BLOCKER: physical_Kubo_coefficient_record_missing; the full Topic 13 controller remains dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing.
NEXT_ACTION: Obtain a permitted state-matched heat-current correlator or microscopic UET match containing units, temperature, chemical potential, base-Phi/space-response amplitude, uncertainty, locator, and source hash; otherwise retain this boundary.
CLAIM_BOUNDARY: This closes only the source-boundary question for public graphite/graphene Green-Kubo comparators. It is not a physical UET Kubo coefficient, Ding C_src, alpha calibration, TTG validation, external validation, or Full Topic 13 closure.
"""
        LOG.write_text(text.rstrip() + "\n" + entry.lstrip(), encoding="utf-8")
        changed = True
    else:
        changed = False
    print({"status": "PASS_TOPIC13_GREEN_KUBO_UPDATE_LOG", "changed": changed})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

