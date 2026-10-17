"""Generate methodological baseline and scoped pilots; never regenerate physics.

The immutable Topic13 evidence is read from its original research commit. It is
not merged into this checkout. Outputs are small contracts, not copied evidence.
Existing contracts are never overwritten. Review changed identities explicitly;
regenerating the inventory does not rerun or upgrade scientific results.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_calculation_completeness import (ROOT, BASELINE, GROUPS, SUPPORT, git,
    scientific_path, identity_hash, load_json, build_report, REPORT, review_payload_hash)

BASE_COMMIT = "35a01e65b6baf8a6ff34fae4a8744ccc3e3adf1d"
T13_COMMIT = "0f17012ffd6ad456c150b10e048efd868ce95588"
T13 = "docs/topics/0.13_Thermodynamic_Bridge"


def write(path: str, value: dict) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def make_contract(cid: str, profile: str, question: str, files: list[str], *,
                  commit: str | None = None, unknown: dict[str, str] | None = None) -> dict:
    unknown = unknown or {}
    evidence = [f"git:{commit}:{p}" if commit else p for p in files]
    components = []
    for group in sorted(GROUPS):
        missing = unknown.get(group)
        modeled = group in {"system_state", "processing", "numerics"}
        components.append({"id": group, "group": group,
                           "disposition": "UNKNOWN" if missing else ("MODELED" if modeled else "NOT_APPLICABLE"),
                           "reason": missing or ("Declared implementation/formal scope in pinned evidence; no material interpretation." if modeled else
                                     "Outside this bounded formal/synthetic result; no physical measurement claim."),
                           "evidence": evidence[:1] if not missing else [],
                           **({"owner": "FOUNDATION" if group == "system_state" else "EVIDENCE",
                               "next_action": missing} if missing else {})})
    identities = []
    for p in files:
        item = {"path": p, "kind": "git_blob" if commit else "working_file",
                "role": "code" if p.endswith(".py") else "evidence"}
        if commit:
            item["commit"] = commit
        item["sha256"] = identity_hash(ROOT, item)
        identities.append(item)
    contract = {
        "schema_version": "uet-calculation-contract-v1", "contract_id": cid,
        "profile": profile,
        "review": {"status": "INCOMPLETE" if unknown else "COMPLETE_FOR_SCOPE",
                   "reviewer": "agent:calculation-observation-standard-v1",
                   "rationale": "Methodological source/claim review only. Scientific results are inherited with original scope, not newly rerun or promoted.",
                   "coverage_evidence": evidence},
        "question": question,
        "output": {"quantity": "declared scoped result", "unit": "dimensionless",
                   "domain": "Only the approximation and input domain of the identified source evidence.",
                   "accuracy": "Inherit named source tolerances; no new physical accuracy claim.",
                   "claim_intent": "FORMAL_RESULT" if profile == "FORMAL" else "DIAGNOSTIC"},
        "model": {"formula_ids": [cid], "assumptions": "See identified source contract; symbols are lane-specific.",
                  "approximation": "Existing formal or normalized approximation, unchanged.",
                  "initial_boundary": "Source-defined initial state, boundary and reference; no inferred material state.",
                  "drive_environment": "Source-declared controls only; no acquired physical drive.",
                  "parameters": "Existing controls/calibration remain inputs; no fitting or new coefficient derivation."},
        "data_policy": {"uses_observations": profile == "PHYSICAL_COMPARISON", "calibration_ids": [],
                        "comparison_ids": [], "independent_validation": False,
                        "holdout_policy": "No holdout access, fitting, external validation or new blind-eligibility decision."},
        "observation": {"source_state": "Source-scoped state, not automatically a material state.",
                        "generated_trace": "Derived record only; not the full observable state.",
                        "carrier": "No physical carrier admitted by this metadata review.",
                        "observer_state": "Formal readout or source-described instrument; unknowns are in component ledger.",
                        "readout": "Existing source output, no new measurement mapping.",
                        "backaction": "No new source/receiver coupling; no claim of complete physical backaction.",
                        "frame": "declared source frame", "time_convention": "declared source convention",
                        "product_level": "formal/synthetic evidence" if profile != "PHYSICAL_COMPARISON" else "published/compiled observations",
                        "trace_scope": "not_used", "trace_used_as_complete_state": False, "corrections": []},
        "components": components,
        "error_budget": {"unit": "dimensionless", "numerical": "Existing saved verifier thresholds; not rerun here.",
                         "approximation": "Source approximation only; no physical extension.",
                         "measurement": "No independent physical acceptance in this review.",
                         "systematic": "Unadmitted physical effects remain limitations.",
                         "omissions": "No quantitative physical omission bound asserted.",
                         "dependence": "No independence or covariance invented.",
                         "acceptance": "Source-scoped formal/diagnostic conclusion only.", "omission_limit": None},
        "identities": identities, "entrypoints": [p for p in files if p.endswith(".py")] or files[:1],
        "evidence": evidence,
        "claim_boundary": "Methodological coverage only; no physical acceptance or change to existing scientific gates.",
        "next_action": "; ".join(unknown.values()) if unknown else "Reuse unchanged evidence; review on source, config, model, observable or scope change."
    }
    contract["review"]["scope_sha256"] = review_payload_hash(contract)
    return contract


def baseline() -> dict:
    tracked = git(ROOT, "ls-tree", "-r", "--name-only", BASE_COMMIT).decode().splitlines()
    legacy = sorted(p for p in tracked if scientific_path(p))
    registry_path = "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
    registry = load_json(ROOT / registry_path)
    routes = [{"route_id": e["equation_id"], "owner": "CORE",
               "paths": sorted(set(e.get("implementation_paths", []) + e.get("verifier_paths", []))),
               "claim_boundary": e.get("claim_boundary", "UNREVIEWED")}
              for e in registry["entries"]]
    for spec in sorted((ROOT / "docs/topics").glob("0.*/VERIFICATION_SPEC.md")):
        folder = spec.parent
        routes.append({"route_id": folder.name, "owner": folder.name,
                       "paths": [spec.relative_to(ROOT).as_posix()] + sorted(
                           p.relative_to(ROOT).as_posix() for p in folder.glob("Code/**/*.py")
                           if not p.name.startswith("test_")),
                       "claim_boundary": "UNREVIEWED: read local verification spec and controlling gate before reuse/promotion."})
    return {"schema_version": "uet-calculation-baseline-v1", "lineage": {
        "core_baseline_commit": BASE_COMMIT,
        "core_branch_at_capture": "codex/services/research-foundation-pilot",
        "origin_main_at_capture": "829c7150260452df186c46bdc653ad758983eaee",
        "topic13_evidence_commit": T13_COMMIT,
        "topic13_evidence_branch": "codex/research/t13-helium-joint-decision",
        "working_tree_preexisting_changes": 452,
        "scope_note": "Tracked baseline inventory plus scoped current-file identities. Distinct research trees are not merged; evidence review is not a clean whole-repository rerun."},
        "registry_identity": {"path": registry_path, "sha256": identity_hash(ROOT, {"path": registry_path, "kind": "working_file"})},
        "support_paths": sorted(SUPPORT), "embedded_contracts": [],
        "legacy_paths": legacy, "routes": routes}


def pilots() -> list[tuple[str, dict]]:
    result = []
    core_files = ["docs/core/01_contracts/MATTER_SPACE_RESEARCH_SPEC.md",
                  "docs/core/02_equations/matter_space/uet_matter_space.py",
                  "docs/core/02_equations/matter_space/uet_trace.py",
                  "docs/core/03_lanes/carrier_observer/uet_impact_effect.py",
                  "docs/core/05_tests/regression/root/test_matter_space_core.py"]
    c = make_contract("CORE_MATTER_SPACE_OBSERVER_V1", "SYNTHETIC",
        "Which state, drive, dissipation-history and receiver outputs are actually implemented?", core_files,
        unknown={"detector": "Physical receiver response/backaction and dimensional calibration remain unadmitted; retain synthetic scope."})
    c["model"]["formula_ids"] = ["uet.matter_space.physical_dynamics", "uet.trace.derived_observable", "uet.impact_effect.information_flow"]
    c["observation"].update(trace_scope="dissipation_history", generated_trace="R=G_ret*sigma; sigma is normalized dissipation, not an admitted physical entropy or full-state information measure.",
        readout="observer_record=observer_gain*carrier_payload; optional receiver update is an explicit normalized linear law.",
        observer_state="receiver_state and fixed gains; no physical instrument trajectory, response time or noise completion.")
    result.append(("docs/core/00_governance/calculation_contracts/matter_space_observer.json", c))
    he_files = [f"{T13}/Result/artifacts/t13_funding_heii_operator_domain_decision.json",
                f"{T13}/Result/artifacts/t13_twofluid_source_visibility.json",
                f"{T13}/Data/03_Research/he4_svp_second_sound_response_source_package.json"]
    c = make_contract("T13_HE4_OBSERVATION_ADMISSION_V1", "PHYSICAL_COMPARISON",
        "Can the frozen calibration supply an admitted same-state He-II second-sound comparison?", he_files,
        commit=T13_COMMIT, unknown={"system_state": "Select an admissible stationary condensed model and independent material state/current map; frozen normal calibration is not He-II.",
        "drive_environment": "Specify actual protocol and justified perturbation constraints.",
        "detector": "Derive the relevant observable operator; full-amplitude claims additionally require source/readout projections.",
        "frame_time": "Lock physical state, units and primary measurement frequency/time protocol.",
        "propagation": "Admit the longitudinal two-fluid mode on that same model domain."})
    c["output"].update(quantity="He-II second-sound phase velocity", unit="m s^-1",
        accuracy="No quantitative physical acceptance criterion admitted.")
    c["error_budget"]["unit"] = "m s^-1"
    c["data_policy"].update(calibration_ids=["Donnelly-Barenghi:superfluid-density:sound-derived"],
        comparison_ids=["Donnelly-Barenghi:second-sound:Table4.3"],
        holdout_policy="Source ancestry overlaps; not independent or blind validation; no new data consumed.")
    c["claim_boundary"] = "Frozen normal branch is not a condensed He-II prediction. Missing operator is not a global no-go or a proved rank/nonidentifiability result. Preserve existing BLOCKED physical gate."
    result.append((f"{T13}/calculation_contracts/he4_observation.json", c))
    kernel_files = [f"{T13}/Result/T13_INVARIANT_POLE_DISCRIMINATION_2026-10-15.md",
                    f"{T13}/Result/artifacts/t13_invariant_pole_discrimination.json"]
    c = make_contract("T13_NONLINEAR_INVARIANT_FORMAL_V1", "FORMAL",
        "Which existing kernel parameter combinations survive a Phi field-coordinate rescaling?", kernel_files, commit=T13_COMMIT)
    c["model"].update(formula_ids=["K4=L-B/(p-nu^2)", "p=a/Z", "B=epsilon*h^2/(2*Z)"],
        assumptions="Nonzero coupling; distinct real off-pole inputs; source-declared lossless branch.",
        approximation="Existing flat homogeneous tree-level normal branch only.",
        parameters="L,p,B are invariant combinations, not new predicted physical constants. Unknown decomposition into h and Z remains separate.")
    c["claim_boundary"] = "Formal inverse/interval design only; ordinary material poles may be equivalent. No acquired kernel, independent SI Phi scale or physical validation."
    result.append((f"{T13}/calculation_contracts/nonlinear_formal.json", c))
    c = make_contract("T13_NONLINEAR_PHYSICAL_ADMISSION_V1", "PHYSICAL_COMPARISON",
        "Do existing records measure the independently driven mechanical kernel required by the invariant test?", kernel_files,
        commit=T13_COMMIT, unknown={"system_state": "Independent material mode/state and base-Phi correspondence missing.",
        "drive_environment": "Acquire an eligible independently characterized drive/kernel package before physical scoring.",
        "detector": "Source/readout gain, phase, mode and units are not admitted.",
        "frame_time": "Lock physical frequency convention and coordinate conversion.",
        "propagation": "Instrument transfer and mode matching remain open."})
    c["claim_boundary"] = "No admitted physical kernel package. Reuse formal result without rerunning fixtures or treating a graphite inquiry as a helium prerequisite."
    result.append((f"{T13}/calculation_contracts/nonlinear_physical.json", c))
    astronomy = [
        ("0.3_Cosmology_Hubble_Tension", "H0_PUBLISHED_SUMMARY_V1", "Published scalar H0 comparison, not raw HST reduction", "km s^-1 Mpc^-1"),
        ("0.1_Galaxy_Rotation_Problem", "GALAXY_CATALOG_COVERAGE_V1", "SPARC/LITTLE THINGS working-copy comparison lineage", "km s^-1"),
        ("0.26_Cosmic_Dynamic_Frame", "DYNAMIC_FRAME_SOURCE_COVERAGE_V1", "Separate galaxy and spacecraft data/heuristic claim paths", "declared per sub-observable")]
    for topic, cid, question, unit in astronomy:
        folder = f"docs/topics/{topic}"
        files = [f"{folder}/DATA_MANIFEST.md", f"{folder}/VERIFICATION_SPEC.md"]
        c = make_contract(cid, "PHYSICAL_COMPARISON", question, files, unknown={
            "system_state": "Trace each published/catalog value to its actual upstream product and model role.",
            "frame_time": "Upstream frame, epoch/time and correction lineage are not fully audited.",
            "detector": "Do not infer raw instrument state from a compiled scalar/catalog.",
            "propagation": "Upstream observation/propagation processing remains source-specific.",
            "drive_environment": "Separate prescribed conditions from fitted/heuristic inputs."})
        c["output"].update(quantity=question, unit=unit)
        c["error_budget"]["unit"] = unit
        c["observation"].update(product_level="published scalar H0" if topic.startswith("0.3_") else "catalog/working-copy summary",
            frame="upstream reported frame; not independently verified",
            corrections=[{"id": "upstream-frame-and-instrument-processing", "state": "UNKNOWN",
                          "evidence": files[0]}])
        c["claim_boundary"] = "Source/coverage review only; no raw HST reprocessing, double correction, new cosmology claim or promotion of heuristic fits."
        result.append((f"{folder}/calculation_contracts/observation_coverage.json", c))
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--initialize", action="store_true", help="Create missing baseline/pilots once; never overwrite existing contracts.")
    p.add_argument("--record-local-lineage", action="store_true", help="Record the explicit incomplete/local-only policy on this producer's pinned Topic13 pilot metadata.")
    args = p.parse_args()
    if args.initialize:
        if not (ROOT / BASELINE).exists():
            write(BASELINE, baseline())
        for path, contract in pilots():
            if (ROOT / path).exists():
                raise SystemExit(f"Refusing to overwrite reviewed contract: {path}")
            write(path, contract)
    # Explicitly record unmerged source availability. This updates only this
    # producer's pilot metadata, never the pinned scientific source or result.
    for path in sorted((ROOT / T13 / "calculation_contracts").glob("*.json")):
        c = load_json(path)
        if args.record_local_lineage and any(i.get("commit") == T13_COMMIT for i in c["identities"]):
            c["review"]["status"] = "INCOMPLETE"
            c["review"]["rationale"] = "Scoped methodological review; original results are pinned to a distinct local research commit, not integrated or independently rerun in this checkout."
            for i in c["identities"]:
                if i.get("commit") == T13_COMMIT:
                    i["availability"] = "LOCAL_ONLY"
            row = next(x for x in c["components"] if x["group"] == "processing")
            row.update(disposition="UNKNOWN", reason="Clean public lineage integration of the pinned research commit remains open.",
                       owner="EVIDENCE", next_action="Review/integrate the exact owner evidence or package an authorized portable source before promotion.")
            write(path.relative_to(ROOT).as_posix(), c)
    report = build_report(ROOT)
    write(REPORT, report)
    print(json.dumps(report["summary"], sort_keys=True))
    if report["errors"]:
        raise SystemExit("\n".join(report["errors"]))


if __name__ == "__main__":
    main()
