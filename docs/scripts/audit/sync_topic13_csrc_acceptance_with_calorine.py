"""Add the Calorine candidate evaluation to the independent C_src contract."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_REL = "docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json"
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_reproduction_audit.json"
CANDIDATE_REL = "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"
SENSITIVITY_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/reproduction/t13_calorine_pbte/isotope_mass_sensitivity/t13_calorine_isotope_mass_sensitivity_audit.json"
UNCERTAINTY_REL = "docs/core/07_artifacts/topic13/t13_calorine_state_uncertainty_decomposition_audit.json"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    contract_path = ROOT / CONTRACT_REL
    sensitivity = json.loads((ROOT / SENSITIVITY_REL).read_text(encoding="utf-8-sig"))
    uncertainty = json.loads((ROOT / UNCERTAINTY_REL).read_text(encoding="utf-8-sig"))
    contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    audit = json.loads((ROOT / AUDIT_REL).read_text(encoding="utf-8-sig"))
    candidate_path = ROOT / CANDIDATE_REL
    candidate = json.loads(candidate_path.read_text(encoding="utf-8-sig"))
    source = candidate.setdefault("source", {})
    source.pop("underlying_graphite_nep_record_url", None)
    source.pop("underlying_graphite_nep_record_doi", None)
    source["zenodo_record_role"] = "byte source for the local tutorial input files"
    source["upstream_model_origin"] = {
        "locator": "https://github.com/brucefan1983/GPUMD/blob/master/potentials/nep/C_2024_NEP4.txt",
        "role": "upstream model origin identified by the Zenodo tutorial record; local bytes remain pinned by Zenodo hash",
    }
    source["related_zenodo_record_7811021"] = {
        "locator": "https://zenodo.org/records/7811021",
        "role": "related rotational-disorder record, not the nep-C.txt input source",
    }
    for item in source.get("tutorial_inputs", []):
        if item.get("name") == "nep-C.txt":
            item["upstream_model_origin_locator"] = source["upstream_model_origin"]["locator"]
            item["provenance_note"] = "Zenodo record supplies the local bytes; the record identifies the GPUMD path as the model origin."
    candidate.setdefault("checks", {})["upstream_model_origin_recorded"] = True
    candidate["generated_at"] = date.today().isoformat()
    candidate_path.write_text(json.dumps(candidate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    major = contract["major_result"]
    closed = "Calorine/Zenodo candidate PBTE reproduction is evaluated with numeric C_src rows and latest q-mesh preflight, but rejected for full Ding acceptance because material/state equivalence and source-grade uncertainty are not closed"
    if closed not in major["what_is_closed"]:
        major["what_is_closed"].append(closed)
    open_item = "Calorine candidate material/state equivalence and source-grade uncertainty"
    if open_item not in major["what_is_remains_open"]:
        major["what_is_remains_open"].append(open_item)
    contract["candidate_evaluations"]["calorine_zenodo_nep_bte_candidate_reproduction"] = {
        "accepted_for_full_topic13": False,
        "source_route": "INDEPENDENT_PBTE_REPRODUCTION",
        "audit_status": audit["status"],
        "material_equivalent_to_ding": audit["checks"]["material_state_match_to_ding"],
        "volumetric_csrc_rows_present": bool(audit["reproduction"]["c_src_rows_latest_mesh"]),
        "mode_heat_capacity_input_unit": "eV K^-1 per mode per primitive cell",
        "si_csrc_output_unit": "J m^-3 K^-1",
        "latest_mesh_pair_relative_change": audit["reproduction"]["convergence"]["latest_pair"]["max_relative_change"],
        "numerical_preflight_pass": audit["checks"]["latest_mesh_pair_preflight_pass"],
        "source_grade_uncertainty_present": audit["checks"]["source_grade_uncertainty_present"],
        "target_fit_performed": audit["checks"]["fit_performed"],
        "alpha_Phi_K_fit_performed": audit["checks"]["alpha_Phi_K_fit_performed"],
        "holdout_accessed": audit["checks"]["holdout_accessed"],
        "byte_source_locator": candidate["source"]["zenodo_record_url"],
        "isotope_mass_sensitivity_status": sensitivity["status"],
        "state_uncertainty_decomposition_status": uncertainty["status"],
        "natural_composition_mass_envelope": uncertainty["components"]["natural_composition_mass_envelope"]["value"],
        "mesh_numerical_envelope": uncertainty["components"]["mesh_numerical_envelope"]["value"],
        "source_grade_uncertainty_closed": uncertainty["checks"]["source_grade_uncertainty_present"],
        "upstream_model_origin_locator": candidate["source"]["upstream_model_origin"]["locator"],
        "provenance_boundary_repaired": True,
        "reason": "Numeric candidate output is reproducible, but the public Calorine state is not demonstrated equivalent to Ding natural-graphite TTG and it has no source-grade statistical/systematic uncertainty package.",
    }
    evidence = {
        "path": AUDIT_REL,
        "sha256": digest(AUDIT_REL),
        "summary": {
            "role": "Calorine candidate reproduction evaluation",
            "accepted_for_full_topic13": False,
            "material_state_match_to_ding": False,
            "source_grade_uncertainty_present": False,
        },
    }
    if not any(item.get("path") == AUDIT_REL for item in major["evidence_artifacts"]):
        major["evidence_artifacts"].append(evidence)
    else:
        for item in major["evidence_artifacts"]:
            if item.get("path") == AUDIT_REL:
                item.update(evidence)
    candidate_evidence = {
        "path": CANDIDATE_REL,
        "sha256": digest(CANDIDATE_REL),
        "summary": {
            "role": "Calorine candidate provenance boundary",
            "upstream_model_origin_recorded": True,
            "accepted_for_full_topic13": False,
        },
    }
    if not any(item.get("path") == CANDIDATE_REL for item in major["evidence_artifacts"]):
        major["evidence_artifacts"].append(candidate_evidence)
    else:
        for item in major["evidence_artifacts"]:
            if item.get("path") == CANDIDATE_REL:
                item.update(candidate_evidence)
    for relative, role, summary in (
        (
            SENSITIVITY_REL,
            "Calorine isotope-mass state sensitivity",
            {"status": sensitivity["status"], "source_grade_uncertainty_present": False},
        ),
        (
            UNCERTAINTY_REL,
            "Calorine state uncertainty decomposition",
            {"status": uncertainty["status"], "source_grade_uncertainty_present": False},
        ),
    ):
        item = {"path": relative, "sha256": digest(relative), "summary": {"role": role, **summary}}
        if not any(existing.get("path") == relative for existing in major["evidence_artifacts"]):
            major["evidence_artifacts"].append(item)
        else:
            for existing in major["evidence_artifacts"]:
                if existing.get("path") == relative:
                    existing.update(item)
    contract["generated_at"] = date.today().isoformat()
    contract["acceptance"]["accepted_independent_reproduction_available"] = False
    contract["acceptance"]["accepted_for_full_topic13"] = False
    contract["acceptance"]["status"] = "BLOCKED"
    contract["acceptance"]["controlling_blocker"] = "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    contract["claim_promotion"] = False
    contract["controlling_blocker"] = "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    contract["next_controller"] = "Obtain an authorized Ding numeric package or a same-regime PBTE reproduction with material/state equivalence and source-grade uncertainty; the Calorine candidate remains numeric comparison evidence only and must not calibrate alpha_Phi_K."
    contract["claim_boundary"] = "Source acceptance policy plus explicit Calorine candidate evaluation; no candidate is accepted for Ding C_src, no alpha_Phi_K is emitted, no holdout is used, and Full Topic 13 remains open."
    contract_path.write_text(json.dumps(contract, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_SYNCED_CSRC_ACCEPTANCE_CALORINE_EVALUATION", "artifact": CONTRACT_REL, "calorine_audit_sha256": digest(AUDIT_REL), "accepted_for_full_topic13": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
