"""Integrate the Calorine/Zenodo candidate-route boundary into Topic 13."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"{label}: anchor not found")
    if count > 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def integrate_gate() -> bool:
    text = GATE.read_text(encoding="utf-8-sig")
    changed = False

    mapping_old = "'T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT': 'independent_csrc_acceptance_contract'}"
    mapping_new = (
        "'T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT': 'independent_csrc_acceptance_contract', "
        "'T13_CALORINE_ZENODO_NEP_BTE_CANDIDATE_BOUNDARY': 'calorine_zenodo_nep_bte_candidate_boundary'}"
    )
    if "T13_CALORINE_ZENODO_NEP_BTE_CANDIDATE_BOUNDARY" not in text:
        text = replace_once(text, mapping_old, mapping_new, "lane mapping")
        changed = True

    load_old = (
        '    independent_csrc_acceptance_path, independent_csrc_acceptance = load(\n'
        '        "docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json"\n'
        '    )\n'
    )
    load_new = load_old + (
        '    calorine_candidate_path, calorine_candidate = load(\n'
        '        "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"\n'
        '    )\n'
    )
    if "calorine_candidate_path, calorine_candidate" not in text:
        text = replace_once(text, load_old, load_new, "candidate load")
        changed = True

    evidence_old = (
        '            evidence(rel(independent_csrc_acceptance_path), independent_csrc_acceptance, {\n'
        '                "status": independent_csrc_acceptance.get("status"),\n'
        '                "accepted_for_full_topic13": independent_reproduction_ready,\n'
        '                "controlling_blocker": independent_csrc_acceptance.get("controlling_blocker"),\n'
        '            }),\n'
    )
    evidence_new = evidence_old + (
        '            evidence(rel(calorine_candidate_path), calorine_candidate, {\n'
        '                "status": calorine_candidate.get("status"),\n'
        '                "accepted_for_full_topic13": calorine_candidate.get("acceptance", {}).get("accepted_for_full_topic13"),\n'
        '                "controlling_blocker": calorine_candidate.get("controlling_blocker"),\n'
        '            }),\n'
    )
    if "evidence(rel(calorine_candidate_path)" not in text:
        text = replace_once(text, evidence_old, evidence_new, "candidate evidence")
        changed = True

    integration_old = (
        '    ding_public_supplementary_lane = discovered_lane_integrations.get(\n'
        '        "ding_public_supplementary_payload_boundary"\n'
        '    )\n'
    )
    integration_new = (
        '    calorine_candidate_lane = discovered_lane_integrations.get(\n'
        '        "calorine_zenodo_nep_bte_candidate_boundary"\n'
        '    )\n'
        '    if calorine_candidate_lane:\n'
        '        artifact["verification_status"]["source_package"][\n'
        '            "calorine_zenodo_nep_bte_candidate_boundary"\n'
        '        ] = calorine_candidate_lane\n'
        '        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n'
        '            "calorine_zenodo_nep_bte_candidate_boundary", None\n'
        '        )\n'
        + integration_old
    )
    if "calorine_candidate_lane = discovered_lane_integrations.get" not in text:
        text = replace_once(text, integration_old, integration_new, "candidate lane projection")
        changed = True

    if changed:
        GATE.write_text(text, encoding="utf-8")
    return changed


def append_manifest() -> bool:
    marker = "## Calorine/Zenodo NEP BTE Candidate Boundary (2026-08-13)"
    text = MANIFEST.read_text(encoding="utf-8-sig")
    if marker in text:
        return False
    block = f"""

{marker}

Public route: [Calorine thermal-conductivity BTE tutorial](https://calorine.materialsmodeling.org/get_started/thermal_conductivity_bte.html), [Zenodo tutorial inputs](https://zenodo.org/records/21198312), and the underlying graphite NEP/DFT package at [Zenodo 7811021](https://zenodo.org/records/7811021).

The route is source-located as a candidate independent reproduction path. Its public inputs include `graphite-prim.xyz` (MD5 `76a98ce37aa503552a23883c4054f64a`) and `nep-C.txt` (MD5 `6196d0146f2314249bc2c8b9b743cad5`), while the tutorial generates `fc2/fc3` and uses a small `16x16x8` mesh with RTA. No deposited mode-resolved `C_src(T)` rows, source-grade uncertainty/convergence package, Ding natural-graphite defect-state mapping, or base-Phi SI anchor is imported. The route remains comparison/candidate-only.

Artifact: `docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json` (SHA-256 `{sha256(ARTIFACT)}`).
"""
    MANIFEST.write_text(text.rstrip() + block, encoding="utf-8")
    return True


def append_update_log() -> bool:
    marker = "### 2026-08-13 - Calorine/Zenodo NEP BTE candidate boundary"
    text = UPDATE_LOG.read_text(encoding="utf-8-sig")
    if marker in text:
        return False
    artifact_hash = sha256(ARTIFACT)
    block = f"""

{marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_CALORINE_ZENODO_NEP_BTE_CANDIDATE_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: The public Calorine/Zenodo route is source-located. It provides graphite structure and NEP inputs for a future `fc2/fc3 -> phono3py BTE` reproduction, and its own documentation identifies the small tutorial supercell/mesh and RTA settings as convenience settings rather than converged graphite transport evidence.
WHAT_REMAINS_OPEN: No deposited mode-resolved `C_src(T)` rows, source-grade uncertainty/convergence package, Ding natural-graphite defect-state mapping, base-Phi SI anchor, or `alpha_Phi_K` is available from this route.
DEPENDENCY_UNLOCKED: Public candidate-route provenance only; no Ding source, alpha, bridge, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_CALORINE_NEP_BTE_CANDIDATE_BOUNDARY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json` (SHA-256 `{artifact_hash}`), a focused test, and full-gate source-package integration.
EQUATION_OR_MAPPING: Candidate route is `NEP graphite -> fc2/fc3 -> phono3py BTE -> C_src(T)`; Topic 13 still requires `C_src(T)=sum_mu c_mu(T)` in `J m^-3 K^-1` with uncertainty and an accepted material/state mapping. No `Delta_Tq = alpha_Phi_K * Delta_Phi` calibration is emitted.
VERIFICATION: Public documentation and Zenodo API inventory were checked. The route is explicitly marked candidate-only; no fit, tuning, alpha emission, target access, or holdout access was performed.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` remains the source controller; `alpha_Phi_K` remains independently unresolved. :codex-annotation{{index="1"}}
NEXT_ACTION: Only pursue a separately source-locked PBTE rerun if it can declare graphite defect/isotope state, converged `fc2/fc3` and q-mesh, mode-resolved `C_src(T)`, uncertainty, and independent no-fit/no-holdout controls. Otherwise retain this route as comparator provenance.
CLAIM_BOUNDARY: This closes only the public candidate-route boundary. It is not an accepted Ding-regime reproduction, UET transport validation, temperature prediction, `alpha_Phi_K` calibration, external validation, or Full Topic 13 closure.
"""
    UPDATE_LOG.write_text(text.rstrip() + block, encoding="utf-8")
    return True


def main() -> int:
    changed = integrate_gate()
    changed = append_manifest() or changed
    changed = append_update_log() or changed
    print({"changed": changed, "artifact_sha256": sha256(ARTIFACT)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
