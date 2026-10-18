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


def unadmitted_measurement_partition(state: str, quantity: str) -> dict:
    """Admission topology only: UNKNOWN components do not become physical equations."""
    def system(sid: str, description: str) -> dict:
        return {"id": sid, "state": description, "state_accounting": {
            "kind": "INDEPENDENT", "state_ids": [f"candidate.{sid}_state"], "owner_ids": [],
            "rule": "Unadmitted state-vector placeholder, not an asserted number of physical degrees of freedom or an energy law; system_state/detector gaps remain open."}}
    return {
        "role_mode": "RELATIONAL", "accounting_component_id": "system_state",
        "boundary": "Admission topology only: sample, drive and receiver are distinct candidate systems. Their state laws, applicable time protocol, physical units and error budget are not admitted by this graph. No missing coupling is set to zero.",
        "systems": [system("sample", state), system("drive", "Unadmitted physical drive state/protocol"),
                    system("receiver", "Unadmitted receiver state/readout calibration")],
        "couplings": [
            {"id": "drive_to_sample", "source": "drive", "target": "sample", "kind": "SIGNAL", "component_id": "drive_environment", "map": "UNKNOWN source-to-state operator; no fitted target-derived input admitted"},
            {"id": "sample_to_receiver", "source": "sample", "target": "receiver", "kind": "DETECTION", "component_id": "detector", "map": "UNKNOWN state-to-readout operator in the declared physical protocol"},
            {"id": "receiver_to_sample", "source": "receiver", "target": "sample", "kind": "BACKACTION", "component_id": "detector", "map": "UNKNOWN feedback; no omission bound supplied"},
            {"id": "receiver_to_drive", "source": "receiver", "target": "drive", "kind": "BACKACTION", "component_id": "detector", "map": "UNKNOWN direct/mediated feedback within the source-readout protocol"}],
        "observables": [{"id": "candidate_reading", "detector_id": "receiver", "target_systems": ["sample"],
            "quantity": quantity, "readout_map": "UNKNOWN physical operator, not a complete-state measurement",
            "component_id": "detector", "backaction_targets": ["sample", "drive"],
            "backaction_scope_reason": "Assess the sampled state and its drive separately; topology is provisional and additional coupled systems require substantive scope review."}]
    }


ASTRONOMY_INPUTS = {
    "0.3_Cosmology_Hubble_Tension": ["Code/03_Research/Research_Hubble_Comparison.py", "Code/01_Engine/Engine_Cosmology.py",
        "Data/03_Research/source_lock_manifest.json",
        "docs/data/external/cosmology/hubble_tension/planck_2018/source_record.json",
        "docs/data/external/cosmology/hubble_tension/shoes_2022/source_record.json",
        "docs/data/external/constants/codata/fine_structure/source_record.json"],
    "0.1_Galaxy_Rotation_Problem": ["Code/03_Research/Research_Galaxy_Rotation.py",
        "Code/01_Engine/Engine_Galaxy_V3.py", "Data/03_Research/sparc_data.json"],
    "0.26_Cosmic_Dynamic_Frame": ["Code/03_Research/Research_Cosmic_Flows.py",
        "Data/03_Research/Laniakea_Flows.json", "Data/03_Research/source_lock_manifest.json",
        "Data/Cosmicflows_3_Subset.csv", "Data/Pioneer_Anomaly_Data.csv"]
}
ASTRONOMY_CODE_COMMIT = "829c7150260452df186c46bdc653ad758983eaee"  # All five source hashes match the former local pin.


def adopt_offline_product(contract: dict, topic: str, root: Path = ROOT) -> dict:
    """Bind local source/product scope, without running a scientific producer."""
    prefix = f"docs/topics/{topic}/"
    files = [p if p.startswith("docs/") else prefix+p for p in ASTRONOMY_INPUTS[topic]]
    existing = {i["path"]: i for i in contract["identities"]}
    for path in files:
        if path not in existing or path.endswith(".py"):
            item = {"path": path, "kind": "working_file", "role": "code" if path.endswith(".py") else "input"}
            if path.endswith(".py"):
                item.update(kind="git_blob", commit=ASTRONOMY_CODE_COMMIT)
            item["sha256"] = identity_hash(root, item)
            if path in existing:
                existing[path].clear()
                existing[path].update(item)
            else:
                contract["identities"].append(item)
    contract["review"]["rationale"] = "W8 source/product admission review only. Scientific code evidence is pinned to public main 829c71502 after verifying all five hashes equal the original local f7ba82307 evidence; unrelated uncommitted producer work is not integrated or certified. Unchanged local input products are identified separately. Upstream observation and physical claims remain INCOMPLETE."
    contract["entrypoints"] = sorted(set(contract["entrypoints"] + [files[0]]))
    contract["observation"]["system_partition"] = {
        "role_mode": "RELATIONAL", "accounting_component_id": "system_state",
        "boundary": "Offline analysis of fixed published/catalog working products. Input numbers and analysis configuration are computational states, not a reconstruction of every cosmic or instrument degree of freedom. Upstream frame/correction/measurement uncertainty remains in the component ledger; no new raw telescope reduction or physical trajectory is performed.",
        "systems": [
            {"id": "data_product", "state": "Published estimates or catalog/landmark working inputs and recorded uncertainties",
             "state_accounting": {"kind": "INDEPENDENT", "state_ids": ["product.input_vector"], "owner_ids": [], "rule": "Input vector counted once as a statistical/computational object, not additional physical energy or a raw source state."}},
            {"id": "analysis", "state": "Declared processing configuration excluding the already counted input vector",
             "state_accounting": {"kind": "INDEPENDENT", "state_ids": ["analysis.configuration"], "owner_ids": [], "rule": "Configuration is separate from source inputs; output is a derived record, not an independent physical substance."}}],
        "couplings": [
            {"id": "product_readout", "source": "data_product", "target": "analysis", "kind": "DETECTION", "component_id": "processing", "map": "Existing offline read/compare or visualization operator; upstream instrument response is not recreated"},
            {"id": "offline_feedback", "source": "analysis", "target": "data_product", "kind": "BACKACTION", "component_id": "offline_read_only", "map": "No source-input update or coupling to an observing spacecraft in the declared offline calculation"}],
        "observables": [{"id": "analysis_record", "detector_id": "analysis", "target_systems": ["data_product"],
            "quantity": contract["output"]["quantity"], "readout_map": "Primary verifier and product-level contract; no claim to recover raw astronomical state",
            "component_id": "processing", "backaction_targets": ["data_product"],
            "backaction_scope_reason": "Read-only offline product analysis; physical upstream response/corrections remain separate unknowns rather than a new spacecraft feedback simulation."}]
    }
    if not any(c["id"] == "offline_read_only" for c in contract["components"]):
        contract["components"].append({"id": "offline_read_only", "group": "processing", "disposition": "NOT_APPLICABLE",
            "reason": "The declared offline calculation reads fixed products; source-input update/physical detector feedback is not part of this software protocol. This is not a universal physical-isolation claim.", "evidence": [files[0]]})
    if topic.startswith("0.3_"):
        contract["model"]["assumptions"] = "Published Planck/SH0ES scalar references and source-locked constant policy only; source values are embedded in the verifier, not loaded from raw HST data. The compared cosmology law remains a model assumption, not a first-principles derivation established here."
        contract["error_budget"]["measurement"] = "Published scalar uncertainties only; script combines them in quadrature. Cross-covariance and adequacy for a joint cosmological likelihood are not established by this review."
        contract["next_action"] = "Audit the embedded scalar-to-source-record parity, covariance/likelihood assumptions and physical justification of the fixed beta law; do not apply a new HST velocity correction to a published H0 scalar."
    elif topic.startswith("0.1_"):
        contract["model"]["assumptions"] = "Primary verifier uses the SPARC working copy; LITTLE THINGS is listed in the manifest but is not automatically a numeric acceptance input. Distance/inclination/mass-to-light and extraction lineage remain unreviewed."
        contract["next_action"] = "Trace SPARC working rows to source/product, units, distance/inclination and mass-model assumptions plus uncertainties; keep LITTLE THINGS separate unless a declared verifier actually uses it. No new fit or rerun without changed evidence."
    else:
        contract["model"]["assumptions"] = "Primary result is Laniakea working-landmark visualization/provenance; Cosmicflows and Pioneer inputs are separately hashed, not numeric model-acceptance residuals."
        processing = next(c for c in contract["components"] if c["id"] == "processing")
        processing.update(disposition="UNKNOWN", owner="research-core",
            reason="Producer labels an internal visualization artifact claim_class D; external-replication meaning is unsupported by this run. Preserve unrelated dirty producer work and resolve its claim metadata before promotion.",
            next_action="Review and reconcile the existing producer's claim label in its owner wave; no source/data rewrite or physical acceptance here.")
        contract["next_action"] = "Separate landmark visualization from Cosmicflows frame/calibration analysis and Pioneer residual/thermal-recoil comparison. Reconcile the producer's unsupported external claim label before promotion; raw preprocessing and quantitative residual gates remain open."
    contract["claim_boundary"] = "Offline source/product coverage and diagnostic scope only; no raw HST reduction, upstream correction duplication, new cosmology/galaxy validation, external replication or promotion of heuristic fits. Code evidence is the named committed version, not unrelated dirty producer work."
    return contract


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
    c["observation"]["system_partition"] = {
      "role_mode": "RELATIONAL",
      "accounting_component_id": "system_state",
      "boundary": "Same normalized one-dimensional C/Phi/Pi dynamics and candidate receiver; source-time convention, configured periodic/zero-flux boundary and inherited numerical tolerances only. The aggregate is a view, not a new state. No physical carrier, detector mapping or source backaction is admitted.",
      "boundary_change": {
        "baseline_identity": "docs/core/00_governance/calculation_contract_baselines/matter_space_observer_legacy.json",
        "baseline_contract_id": "CORE_MATTER_SPACE_OBSERVER_V1",
        "baseline_contract_sha256": "6d11ee73d8c65ae830696c0ddcdb16c4ca3f72f7b5872061322d5d5f7d96f23d",
        "component_id": "system_state",
        "outcome": "EQUIVALENT",
        "explanation": "Bookkeeping equivalence only: the old C/Phi/Pi state projects identically to the new independent owners; source_system adds no coordinate or energy. Dynamics and readout functions are unchanged. This does not admit the UNKNOWN physical detector or assert physical completeness."
      },
      "systems": [
        {"id": "C_system", "parent_id": "source_system", "state": "C collective coordinate in the declared normalized lane", "state_accounting": {"kind": "INDEPENDENT", "state_ids": ["matter_space.C"], "owner_ids": [], "rule": "C is initialized once; its contribution belongs to the common Omega, not an independently additive duplicate energy."}},
        {"id": "response", "parent_id": "source_system", "state": "Phi and Pi; memory state of this model, not a detector record", "state_accounting": {"kind": "INDEPENDENT", "state_ids": ["matter_space.Phi", "matter_space.Pi"], "owner_ids": [], "rule": "Phi/Pi are initialized once; Pi storage is tau/(2*M_Phi) integral Pi^2. The shared C/Phi interaction is counted only in Omega."}},
        {"id": "D", "state": "Candidate normalized receiver state; physical instrument realization UNKNOWN", "state_accounting": {"kind": "INDEPENDENT", "state_ids": ["candidate.receiver_state"], "owner_ids": [], "rule": "Toy receiver state is not a copy of source state or source energy; physical receiver storage and feedback remain UNKNOWN in the detector component."}},
        {"id": "source_system", "state": "Joint description of C/Phi/Pi, not an extra coordinate", "categories": ["normalized", "coupled_response"], "state_accounting": {"kind": "AGGREGATE", "state_ids": [], "owner_ids": ["C_system", "response"], "rule": "Use the existing Omega plus Pi storage once, including -g*C^2*Phi/2 once; do not sum this aggregate as a new energy on top of its owners."}}
      ],
      "couplings": [
        {"id": "C_to_response", "source": "C_system", "target": "response", "kind": "INTERNAL", "component_id": "system_state", "map": "Paired variational coupling in Omega; see matter_space_rhs"},
        {"id": "response_to_C", "source": "response", "target": "C_system", "kind": "INTERNAL", "component_id": "system_state", "map": "Response enters mu_C; this is not detector backaction"},
        {"id": "candidate_detection", "source": "response", "target": "D", "kind": "DETECTION", "component_id": "detector", "map": "Candidate readout of a generated trace from C/Phi history; carrier and physical detector correspondence remain UNKNOWN"},
        {"id": "D_to_C_assessment", "source": "D", "target": "C_system", "kind": "BACKACTION", "component_id": "detector", "map": "Physical source feedback unadmitted; not inferred from a recorded signal"},
        {"id": "D_to_response_assessment", "source": "D", "target": "response", "kind": "BACKACTION", "component_id": "detector", "map": "Physical response-sector feedback unadmitted; existing no-trace-feedback implementation is not proof of physical isolation"}
      ],
      "observables": [
        {"id": "candidate_receiver_readout", "detector_id": "D", "target_systems": ["C_system", "response"], "quantity": "Selected normalized receiver record, not the complete source state", "readout_map": "Existing toy gain/payload relation only; material detector correspondence UNKNOWN", "component_id": "detector", "backaction_targets": ["C_system", "response"], "backaction_scope_reason": "Both independent source owners are assessed; source_system is their nonadditive view, not a third affected state. No physical feedback route is admitted by this review."}
      ]
    }
    c["identities"].insert(0, {
        "path": "docs/core/00_governance/calculation_contract_baselines/matter_space_observer_legacy.json",
        "kind": "working_file",
        "role": "evidence", "sha256": "2a67ca63b40c0bcec2bb47653e36e218cadf460a3ea12ff1731e47edff807b0c"
    })
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
    c["observation"]["system_partition"] = unadmitted_measurement_partition(
        "No selected Ward-consistent condensed finite-temperature state/material map; frozen normal calibration is not He-II",
        "He-II second-sound phase velocity, conditional on same-state longitudinal mode identification")
    c["next_action"] = "Specify one fixed Ward-consistent condensed finite-temperature completion and independent material state/current map; then derive its same-state longitudinal operator. Additional helium data or detector detail alone cannot repair the unselected model."
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
        commit=T13_COMMIT, unknown={"system_state": "Independent material mode/state and effective kernel correspondence missing; an absolute base-Phi scale is required only for claims that use that scale.",
        "drive_environment": "Acquire an eligible independently characterized drive/kernel package before physical scoring.",
        "detector": "Source/readout gain, phase, mode and units are not admitted.",
        "frame_time": "Lock physical frequency convention and coordinate conversion.",
        "propagation": "Instrument transfer and mode matching remain open."})
    c["claim_boundary"] = "No admitted physical kernel package. Reuse formal result without rerunning fixtures or treating a graphite inquiry as a helium prerequisite."
    c["observation"]["system_partition"] = unadmitted_measurement_partition(
        "Unadmitted material mode/state and invariant-kernel matching; no absolute Phi amplitude inferred",
        "Independently driven kernel response in an admitted instrument coordinate/time chart")
    c["next_action"] = "Admit one actual same-state source/kernel/readout operator with units, gain/phase, frequency convention and joint uncertainty; use identifiable combinations where justified. Do not demand an absolute Phi scale for a scale-invariant test, and do not substitute a different native forcing protocol."
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
        result.append((f"{folder}/calculation_contracts/observation_coverage.json", adopt_offline_product(c, topic)))
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
