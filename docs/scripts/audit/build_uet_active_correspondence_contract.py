"""Build explicit standard-physics correspondence decisions for active pilots.

Only standard comparator/observable identities are closed here.  UET-specific
candidate rows remain open and cannot inherit the comparator's status.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
FORMULA_PATH = ROOT / "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json"
OUTPUT = ROOT / "docs/core/07_artifacts/correspondence/uet_active_correspondence_contract.json"


ACTIVE_TOPICS = {"0.11", "0.13"}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def standard(relation: str, observable: str, units: str, derivation: str) -> dict[str, Any]:
    return {
        "status": "STANDARD_COMPARATOR_CLOSED",
        "standard_counterpart": relation,
        "unit_lane": units,
        "observable_operator": observable,
        "derivation_class": derivation,
        "claim_ceiling": "standard comparator/observable definition only; not a UET derivation or prediction",
    }


def diagnostic(relation: str, observable: str) -> dict[str, Any]:
    return {
        "status": "STANDARD_DIAGNOSTIC_CLOSED",
        "standard_counterpart": relation,
        "unit_lane": "normalized_or_topic_specific",
        "observable_operator": observable,
        "derivation_class": "diagnostic_definition_or_numerical_estimator",
        "claim_ceiling": "internal diagnostic; fit/estimator is not a prediction",
    }


def open_candidate(reason: str) -> dict[str, Any]:
    return {
        "status": "OPEN_UET_CANDIDATE_MAPPING",
        "standard_counterpart": "no completed standard-physics correspondence for the UET extension",
        "unit_lane": "normalized_candidate_only",
        "observable_operator": "OPEN_MEASUREMENT_OPERATOR",
        "derivation_class": "candidate_constitutive_or_heuristic_ansatz",
        "claim_ceiling": "hypothesis/candidate only; no physical promotion",
        "reason": reason,
    }


MAPPINGS: dict[str, dict[str, Any]] = {
    # Topic 0.11: standard phase/order comparators and diagnostics.
    "PT-CH-EVOLUTION": standard("Cahn–Hilliard conserved gradient flow", "O[C] = field trajectory/order structure factor", "normalized_comparator", "standard constitutive comparator"),
    "PT-FREE-ENERGY": standard("Landau–Ginzburg/Cahn–Hilliard free-energy functional", "O[C] = field profile and free-energy diagnostic", "normalized_comparator", "standard effective-functional comparator"),
    "PT-CHEM-POTENTIAL": standard("functional derivative chemical potential δF/δC", "O[C] = chemical-potential field", "normalized_comparator", "derivative of declared comparator functional"),
    "PT-SPECTRAL-UPDATE": standard("semi-implicit Fourier discretization of conserved gradient flow", "O[C] = spectral mode trajectory", "normalized_numerical", "numerical approximation"),
    "PT-ORDER-PARAMETER": diagnostic("coarse-grained order-parameter magnitude", "O[C] = mean(|C|)"),
    "PT-DOMAIN-COUNT": diagnostic("domain-wall/sign-domain diagnostic", "O[C] = zero-crossing count"),
    "PT-BEC-TC": standard("ideal Bose-gas critical-temperature relation", "O[Tc] = transition-temperature estimate", "natural_or_SI_after_constants", "standard external relation"),
    "PT-UET-LEGACY-INFO": open_candidate("legacy information coupling has no closed standard counterpart or unit map"),
    "PT-UET-SPATIAL-INFO-CANDIDATE": open_candidate("spatial information coupling is a UET candidate, not a standard identity"),
    "PT-UET-SPATIAL-GAME-CANDIDATE": open_candidate("game-coupling force is a UET candidate with no standard constitutive derivation"),
    "PT-SPATIAL-SCALING-GATE": diagnostic("finite-size/scaling regression diagnostic", "O[data] = fitted exponent/quality metric"),
    "PT-SPATIAL-COEFFICIENT-SENSITIVITY": diagnostic("parameter-sensitivity/ablation diagnostic", "O[data] = lane comparison under declared sweep"),
    "PT-CORRELATION-LENGTH-DIAGNOSTIC": diagnostic("correlation-length estimator", "O[C] = autocorrelation crossing proxy"),
    "PT-FINITE-SIZE-SCALING-DIAGNOSTIC": diagnostic("finite-size scaling diagnostic", "O[C] = xi/L and Binder-style proxy"),
    "PT-CRITICAL-WINDOW-RELAXATION-DIAGNOSTIC": diagnostic("critical-window relaxation diagnostic", "O[C] = relaxation/correlation proxy"),
    "PT-OPERATOR-FORM-REQUIREMENT-GATE": diagnostic("model-form acceptance gate", "O[artifact] = requirement/gate status"),
    "PT-UET-SPATIAL-V2-CANDIDATE": open_candidate("nonlocal/game/information v2 is a UET candidate model"),
    "PT-UET-SPATIAL-V2-ABLATION": diagnostic("model ablation comparison", "O[data] = profile/xi comparison"),
    "PT-MODEL-C-CONSERVED-ORDER-DIAGNOSTIC": standard("Cahn–Hilliard conserved order-parameter comparator", "O[C] = conserved trajectory and structure factor", "normalized_comparator", "standard constitutive comparator"),
    "PT-CONSERVED-ORDER-CORE-CANDIDATE": open_candidate("opt-in conserved-order implementation is a UET candidate lane"),
    "PT-CONSERVED-ORDER-NUMERICS-GAP": diagnostic("stiffness/numerical stability diagnostic", "O[config] = high-k stiffness proxy"),
    "PT-CONSERVED-ORDER-SPECTRAL-CORE-CANDIDATE": open_candidate("spectral core is an implementation candidate, not a physical derivation"),
}

# Remaining 0.11 rows are explicitly diagnostic or open candidate rather than left
# implicit.  The known prefix prevents a new row from silently inheriting a claim.
for _formula_id in [
    "PT-CONSERVED-ORDER-SPECTRAL-SCALING", "PT-CONSERVED-ORDER-SPECTRAL-WINDOW-REPAIR",
    "PT-CONSERVED-ORDER-SPECTRAL-SPINODAL-WINDOW", "PT-CONSERVED-ORDER-SPECTRAL-SEED-MARGIN",
    "PT-CONSERVED-ORDER-SPECTRAL-FINITE-SIZE-REPLICATION", "PT-CONSERVED-ORDER-SPECTRAL-L16-RELAXATION-REPAIR",
    "PT-CONSERVED-ORDER-SPECTRAL-L16-ESTIMATOR-SENSITIVITY", "PT-CONSERVED-ORDER-SPECTRAL-L16-STRUCTURE-FACTOR-ESTIMATOR",
    "PT-CONSERVED-ORDER-SPECTRAL-STRUCTURE-FACTOR-MULTIGRID", "PT-CONSERVED-ORDER-SPECTRAL-STRUCTURE-FACTOR-L20-PROBE",
    "PT-CONSERVED-ORDER-SPECTRAL-STRUCTURE-FACTOR-ACCEPTANCE-RULE", "PT-CONSERVED-ORDER-SPECTRAL-ESTIMATOR-RECONCILIATION",
    "PT-CONSERVED-ORDER-SPECTRAL-CALIBRATION-SOURCE-SUPPORT", "PT-CONSERVED-ORDER-SPECTRAL-SOURCE-MANIFEST",
    "PT-CONSERVED-ORDER-SPECTRAL-FORMULA-BOUNDARY", "PT-CONSERVED-ORDER-SPECTRAL-LOWEST-MODE-CANDIDATE",
    "PT-CONSERVED-ORDER-SPECTRAL-ENSEMBLE-SUSCEPTIBILITY-LANE", "PT-CONSERVED-ORDER-SPECTRAL-ESTIMATOR-POLICY-SOURCE",
    "PT-CONSERVED-ORDER-SPECTRAL-POLICY-SOURCE-CANDIDATES", "PT-CONSERVED-ORDER-SPECTRAL-POLICY-FORMULA-BOUNDARY",
    "PT-CONSERVED-ORDER-SPECTRAL-FULL-TEXT-FORMULA-READINESS", "PT-CONSERVED-ORDER-SPECTRAL-SOURCE-ARCHIVE-LOCALIZATION",
    "PT-CONSERVED-ORDER-SPECTRAL-TEX-FORMULA-FRAGMENTS", "PT-CONSERVED-ORDER-SPECTRAL-SOURCE-ARCHIVE-POLICY",
    "PT-CONSERVED-ORDER-SPECTRAL-ESTIMATOR-NORMALIZATION-MAP", "PT-CONSERVED-ORDER-SPECTRAL-CH-FINITE-K-PREFLIGHT",
    "PT-CONSERVED-ORDER-SPECTRAL-CH-FINITE-K-ESTIMATOR-CANDIDATE",
]:
    MAPPINGS.setdefault(_formula_id, diagnostic("structure-factor/finite-size estimator diagnostic", "O[C] = structure-factor or xi estimator"))

MAPPINGS.update({
    "PT-BETA-UET": open_candidate("beta_UET is a UET candidate coupling and has no standard physical derivation"),
    "PT-BETA-ERROR": diagnostic("relative-error comparison diagnostic", "O[data] = relative error"),
    "PT-CH-FINITE-K-ACCEPTANCE-POLICY": diagnostic("finite-k estimator acceptance policy", "O[S(q)] = admissibility status"),
    "PT-CH-FINITE-K-EXTENDED-GRID-COVERAGE": diagnostic("finite-k grid coverage diagnostic", "O[S(q)] = accepted-row coverage"),
})

# Topic 0.13: standard thermodynamic identities and open UET mappings.
MAPPINGS.update({
    "T13-001": standard("coarse-grained combinatorial entropy/Stirling comparator", "O[E,N] = entropy proxy", "normalized_statistical", "standard statistical-mechanics comparator"),
    "T13-002": standard("thermodynamic identity 1/T = ∂S/∂E in the declared normalized model", "O[E,N] = temperature proxy", "normalized_statistical", "derivative of declared entropy comparator"),
    "T13-003": standard("equilibrium detailed-balance/contact condition", "O[E_A,N_A,E_B,N_B] = equilibrium ratio", "normalized_statistical", "standard equilibrium comparator"),
    "T13-004": standard("Landauer minimum energy k_B T ln 2", "O[T] = lower-bound energy", "SI_after_constants", "external standard identity"),
    "T13-005": standard("joule/electron-volt conversion", "O[E] = unit conversion", "SI", "external unit identity"),
    "T13-006": standard("Bekenstein bound", "O[R,E] = entropy upper-bound comparator", "natural_or_SI_after_constants", "external standard bound"),
    "T13-007": standard("Bekenstein–Hawking entropy", "O[A] = black-hole entropy comparator", "natural_or_SI_after_constants", "external standard identity"),
    "T13-008": standard("Unruh temperature", "O[a] = temperature comparator", "SI_after_constants", "external standard identity"),
    "T13-009": standard("Hawking temperature", "O[M] = temperature comparator", "SI_after_constants", "external standard identity"),
    "T13-010": standard("Cattaneo–Vernotte heat-flux relaxation", "O[T,q] = lag/phase/arrival", "normalized_comparator", "standard transport comparator"),
    "T13-011": open_candidate("vacuum-sink and matter-cooling update has no closed standard physical mapping"),
    "T13-012": standard("Josephson constant K_J = 2e/h", "O[V,f] = voltage-frequency conversion", "SI", "external standard identity"),
    "T13-013": standard("normalized transient thermal-grating signal", "O[TTG] = Delta_T(t;Lambda)/Delta_T(0;Lambda)", "dimensionless_observable", "standard measurement definition"),
    "T13-014": open_candidate("Phi-to-TTG signal is a UET observable hypothesis"),
    "T13-015": open_candidate("Phi-to-temperature calibration is open and source/calibration dependent"),
})


def build() -> dict[str, Any]:
    inventory = load(FORMULA_PATH)
    records = [row for row in inventory.get("records", []) if row.get("topic_id") in ACTIVE_TOPICS]
    missing = sorted({row.get("formula_id") for row in records} - set(MAPPINGS))
    if missing:
        raise ValueError(f"active formula rows missing explicit mapping: {missing}")
    rows = []
    status_counts: dict[str, int] = {}
    for source in records:
        mapping = MAPPINGS[source["formula_id"]]
        status_counts[mapping["status"]] = status_counts.get(mapping["status"], 0) + 1
        rows.append({"formula_id": source["formula_id"], "topic_id": source["topic_id"], "source": source.get("source"), "relation": source.get("relation"), **mapping})
    return {
        "schema_version": "1.0",
        "artifact": "uet_active_correspondence_contract",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS_WITH_OPEN_UET_CANDIDATES",
        "scope": sorted(ACTIVE_TOPICS),
        "row_count": len(rows),
        "mapping_status_counts": dict(sorted(status_counts.items())),
        "rows": rows,
        "rules": [
            "STANDARD_COMPARATOR_CLOSED means the standard counterpart is explicit; it does not mean UET derived it.",
            "STANDARD_DIAGNOSTIC_CLOSED means the observable/estimator role is explicit; it is not predictive evidence.",
            "OPEN_UET_CANDIDATE_MAPPING remains blocked until a UET derivation, units and measurement operator exist.",
        ],
        "next_controller": "close UET candidate mappings only with derivation, dimensional contract and observable evidence; do not inherit comparator status",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        result = build()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={result['audit_status']}")
        print(f"row_count={result['row_count']}")
        print(f"mapping_status_counts={result['mapping_status_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
