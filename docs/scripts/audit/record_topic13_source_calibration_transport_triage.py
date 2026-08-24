"""Record a fail-closed Topic 13 source and calibration triage wave."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
MATRIX = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"
FULL_GATE = TOPIC / "Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
RECORD_AUDIT = ROOT / "docs/core/artifacts/t13_closure_record_contract_audit.json"
ROUTE_ARTIFACTS = (
    ROOT / "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json",
    ROOT / "docs/core/artifacts/t13_bipm_specific_heat_source_audit.json",
    ROOT / "docs/core/artifacts/t13_kim_2018_graphite_green_kubo_external_input_audit.json",
    ROOT / "docs/core/artifacts/t13_calorine_full_lbte_stability_boundary_audit.json",
)
UPDATE_LOG = TOPIC / "UPDATE_LOG.md"
ROADMAP = TOPIC / "TOPIC13_FULL_CLOSURE_ROADMAP.md"
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-24.md"
MARKER = "### 2026-08-24 - Source, calibration, and transport route triage"
EXPECTED_BLOCKERS = {
    "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    "alpha_Phi_K_independent_calibration_missing",
    "normalized_beta_and_SI_scale_correspondence_missing",
    "physical_Kubo_coefficient_record_missing",
    "dimensional_phi_to_thermal_observable_map_missing",
    "material_regime_mapping_to_TTG_not_closed",
    "c_v_source_uncertainty_not_closed",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def append_once(path: Path, marker: str, body: str) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in existing:
        return False
    path.write_text(existing.rstrip() + "\n\n" + body.rstrip() + "\n", encoding="utf-8")
    return True


def validate_current_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    matrix = load_json(MATRIX)
    input_audit = load_json(INPUT_AUDIT)
    full_gate = load_json(FULL_GATE)
    raw_counts = matrix["closure_summary"]["current_subresult_counts"]
    expected_counts = {"CLOSED_AS_NO_GO": 5, "CLOSED_FOR_LANE": 21, "CLOSED_FOR_CORE": 0, "OPEN": 10}
    counts = {key: raw_counts.get(key, 0) for key in expected_counts}
    observed_blockers = {
        blocker
        for group in matrix["closure_summary"]["open_blocker_groups"].values()
        for blocker in group
    }
    if matrix["status"] != "BLOCKED_OPEN_T13_FULL_BRIDGE":
        raise RuntimeError("unexpected Topic 13 matrix status")
    if matrix["full_core_unlock"] is not False:
        raise RuntimeError("Topic 13 core unlock must remain false")
    if counts != expected_counts:
        raise RuntimeError(f"unexpected Topic 13 subresult counts: {raw_counts}")
    if observed_blockers != EXPECTED_BLOCKERS:
        raise RuntimeError(f"unexpected Topic 13 blocker set: {observed_blockers}")
    if not all(package["accepted_for_core"] is False for package in input_audit["packages"]):
        raise RuntimeError("a new Core package was accepted; use the package-specific promotion wave")
    if input_audit["holdout_policy"]["xie_2026_accessed"] is not False:
        raise RuntimeError("Xie 2026 holdout access is not allowed")
    if load_json(RECORD_AUDIT)["status"] != "PASS_T13_CLOSURE_RECORD_CONTRACT_OPEN":
        raise RuntimeError("closure-record contract is not in the expected open state")
    for path in ROUTE_ARTIFACTS:
        if not path.exists():
            raise RuntimeError(f"missing route artifact: {path}")
    if full_gate["status"] != "BLOCKED_OPEN_T13_FULL_BRIDGE":
        raise RuntimeError("canonical full gate is not blocked as expected")
    return matrix, input_audit, full_gate


def build_update(matrix: dict[str, Any], input_audit: dict[str, Any]) -> str:
    evidence_hashes = "; ".join(
        f"{path.name} `{sha256(path)}`" for path in (RECORD_AUDIT, INPUT_AUDIT, MATRIX, FULL_GATE)
    )
    blocker_count = len(EXPECTED_BLOCKERS)
    return f"""{MARKER}

MAJOR_RESULT_CLOSURE: `PARTIAL`; the canonical Full Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The current evidence routes were rechecked against the Core-level contracts. Lowitzer supplies a source-locked same-study `alpha_V`/`K_T` correction-input lane, BIPM supplies a source-locked volumetric `c_p` comparator, Kim 2018 supplies an external Green-Kubo comparator, and the existing Calorine full-LBTE run supplies a numerical-stability boundary. None of these routes supplies a Ding-equivalent `C_src`, a base-Phi/SI pair, or a physical UET Kubo record.
WHAT_REMAINS_OPEN: The matrix remains 21 `CLOSED_FOR_LANE`, 5 `CLOSED_AS_NO_GO`, 0 `CLOSED_FOR_CORE`, and 10 `OPEN` subresults across 7 blocker groups. The remaining Core results are base-Phi SI anchor, independent `alpha_Phi_K`, normalized beta/SI map, source-backed EOS, physical UET Kubo, physical SK/KMS transport match, physical entropy-production mapping, accepted numeric `C_src`, material/uncertainty closure, and physical heat-flux/entropy mapping.
DEPENDENCY_UNLOCKED: None. Comparator and numerical-boundary evidence remain lane-scoped; Gravity/GR, curved 3+1, and full constitutive transport stay locked.
STATUS: `{matrix['status']}`; `full_core_unlock={matrix['full_core_unlock']}`; `claim_promotion={matrix['claim_promotion']}`; `holdout_accessed={input_audit['holdout_policy']['xie_2026_accessed']}`.
WHAT_CHANGED: Audited the source/package contracts and regenerated the closure-record audit, three-package input audit, canonical Full Topic 13 gate, and closure matrix. No new numeric package was accepted and no source, threshold, fit, or holdout policy was changed.
EQUATION_OR_MAPPING: `y_TTG=Delta_Tq(t)/Delta_Tq(0)`; `y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)`; `Delta_Tq=alpha_Phi_K*Delta_Phi`; `C_src(T)=sum_mu c_mu(T)`; `Delta_Tq=Delta_u_ph/C_src(T)`. External `c_p`, `c_v`, and Green-Kubo values remain comparator inputs and are not relabeled as `Phi` or UET transport.
VERIFICATION: Closure-record contract `PASS` with zero failed checks; input-package audit `PASS` with 3 packages and 0 accepted for Core; canonical gate reports {blocker_count} blockers; closure matrix reports 10 major results and 36 subresults; Xie 2026 remains unread and no alpha fit was performed.
CONTROLLING_BLOCKER: The three independent package blockers remain: Ding-compatible `C_src`/material uncertainty, independent base-Phi SI alpha/beta scale, and physical Kubo/SK/KMS/entropy provenance.
NEXT_ACTION: Do not rerun existing comparators as a substitute. Obtain one authorized Ding-compatible payload or accepted same-regime reproduction, one independent base-Phi/SI response or dimensionful action anchor, and one state-matched physical Kubo record; admit each only through the fail-closed record contract.
CLAIM_BOUNDARY: This wave narrows source and derivation routes only. It does not close Full Topic 13, promote a comparator to UET evidence, use Xie 2026, infer `alpha_Phi_K`, or unlock Core/Gravity.
EVIDENCE_PATHS: `docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json`; `docs/core/artifacts/t13_bipm_specific_heat_source_audit.json`; `docs/core/artifacts/t13_kim_2018_graphite_green_kubo_external_input_audit.json`; `docs/core/artifacts/t13_calorine_full_lbte_stability_boundary_audit.json`; `docs/core/artifacts/t13_closure_record_contract_audit.json`; `docs/core/artifacts/t13_closure_input_package_audit.json`; `docs/core/artifacts/t13_topic13_closure_matrix.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.
EVIDENCE_HASHES: {evidence_hashes}.
"""


def build_roadmap() -> str:
    return """## Latest Source, Calibration, and Transport Triage (2026-08-24)

The source routes were checked against the three Core input packages without
accepting any new payload. Lowitzer and BIPM are source-locked thermodynamic
comparators, Kim 2018 is an external Green-Kubo comparator, and the existing
Calorine full-LBTE run is a numerical-stability boundary. They do not supply
the missing Ding-equivalent `C_src`, base-Phi/SI response pair, or physical UET
Kubo record.

The canonical matrix remains 21 `CLOSED_FOR_LANE`, 5 `CLOSED_AS_NO_GO`, 0
`CLOSED_FOR_CORE`, and 10 `OPEN` subresults. No dependency is unlocked and no
`alpha_Phi_K` value is emitted.

The next admissible state change requires one of the three missing packages:
an authorized or accepted same-regime Ding-compatible PBTE source, an
independent base-Phi/SI anchor, or a state-matched physical Kubo/SK/KMS record.
Existing comparators must not be rerun as substitutes.
"""


def build_ledger() -> str:
    return """## Topic 13 Source, Calibration, and Transport Triage

- area: `research-core`; secondary: `result-artifacts`
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`, `docs/core/artifacts`, and `WORK_LEDGER/2026`
- files/artifacts: source/calibration/transport triage recorder, Topic 13 update log, full-closure roadmap, and regenerated closure projections
- verification: closure-record contract PASS; three-package input audit PASS with 0 accepted for Core; full gate BLOCKED with 7 blockers; matrix 21 lane / 5 no-go / 0 Core / 10 open; Xie 2026 unread
- public-safety: `partial`
- result: Lowitzer/BIPM/Kim/Calorine evidence remains comparator or boundary evidence; no new Core subresult closes
- claim boundary: no Full Topic 13, alpha, physical UET transport, Core, Gravity, or external-validation promotion
- next action: obtain one admissible Ding-compatible C_src package, one independent base-Phi/SI response, or one physical state-matched Kubo package
"""


def main() -> None:
    matrix, input_audit, _ = validate_current_state()
    appended = {
        "update_log": append_once(UPDATE_LOG, MARKER, build_update(matrix, input_audit)),
        "roadmap": append_once(
            ROADMAP,
            "## Latest Source, Calibration, and Transport Triage (2026-08-24)",
            build_roadmap(),
        ),
        "ledger": append_once(LEDGER, "## Topic 13 Source, Calibration, and Transport Triage", build_ledger()),
    }
    print(
        json.dumps(
            {"status": "PASS_T13_SOURCE_CALIBRATION_TRANSPORT_TRIAGE_RECORDED", "appended": appended},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
