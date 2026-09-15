"""Repair Topic 13 causal gate composition and preserve the named-lane boundary."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FULL_GATE = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"
NO_GO_SYNC = ROOT / "docs/scripts/audit/sync_topic13_no_go_gate.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def repair_full_gate() -> None:
    text = FULL_GATE.read_text(encoding="utf-8-sig")
    if "named_coupled_branch_pass =" not in text:
        text = replace_once(
            text,
            "    source_package_path, source_package = load(\n"
            "        \"docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json\"\n"
            "    )\n",
            "    source_package_path, source_package = load(\n"
            "        \"docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json\"\n"
            "    )\n"
            "    no_go_path, no_go = load(\"docs/core/07_artifacts/archive/conserved_c_finite_cone_no_go_assessment.json\")\n"
            "    telegraph_path, telegraph = load(\"docs/core/07_artifacts/verification/matter_space_conserved_flux_telegraph_verification.json\")\n"
            "    coupled_path, coupled = load(\"docs/core/07_artifacts/verification/matter_space_flux_phi_coupled_verification.json\")\n",
            "full-gate causal artifact inputs",
        )
        text = replace_once(
            text,
            "    full_candidate_pass = (\n",
            "    formal_no_go_recorded = no_go.get(\"status\") == \"NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS\"\n"
            "    named_finite_cone_branch_pass = (\n"
            "        telegraph.get(\"status\") == \"PASS\"\n"
            "        and telegraph.get(\"major_result\", {}).get(\"closure_level\") == \"CLOSED_FOR_LANE\"\n"
            "    )\n"
            "    named_coupled_branch_pass = (\n"
            "        coupled.get(\"status\") == \"PASS\"\n"
            "        and coupled.get(\"major_result\", {}).get(\"closure_level\") == \"CLOSED_FOR_LANE\"\n"
            "    )\n"
            "    causal_lane_pass = formal_no_go_recorded and named_finite_cone_branch_pass and named_coupled_branch_pass\n"
            "    full_candidate_pass = (\n",
            "full-gate causal state derivation",
        )
        old_causal = (
            '        "causal_full_candidate_or_formal_no_go_branch": {\n'
            '            "status": "PASS" if full_candidate_pass else "BLOCKED",\n'
            '            "full_candidate_pass": full_candidate_pass,\n'
            '            "selected_reference_pass": branch_pass,\n'
            '            "formal_no_go_recorded": False,\n'
            '            "structural_no_go_evidence_present": causal_no_go_evidence,\n'
            '            "threshold": 1.0e-6,\n'
            '            "no_clipping_or_padding": True,\n'
            '            "controlling_blocker": "formal_conserved_C_no_go_or_explicit_regularization_missing",\n'
            '        },\n'
        )
        new_causal = (
            '        "causal_full_candidate_or_formal_no_go_branch": {\n'
            '            "status": "PASS" if causal_lane_pass else "BLOCKED",\n'
            '            "full_candidate_pass": full_candidate_pass,\n'
            '            "selected_reference_pass": branch_pass,\n'
            '            "formal_no_go_recorded": formal_no_go_recorded,\n'
            '            "structural_no_go_evidence_present": causal_no_go_evidence and formal_no_go_recorded,\n'
            '            "threshold": 1.0e-6,\n'
            '            "no_clipping_or_padding": True,\n'
            '            "named_finite_cone_branch_pass": named_finite_cone_branch_pass,\n'
            '            "named_finite_cone_branch_closure_level": telegraph.get("major_result", {}).get("closure_level", "OPEN"),\n'
            '            "named_coupled_branch_pass": named_coupled_branch_pass,\n'
            '            "named_coupled_branch_closure_level": coupled.get("major_result", {}).get("closure_level", "OPEN"),\n'
            '            "no_go_scope": no_go.get("proof_scope"),\n'
            '            "no_go_artifact": {"path": rel(no_go_path), "sha256": sha256(no_go_path)},\n'
            '            "controlling_blocker": "original_conserved_c_gradient_baseline_blocked" if causal_lane_pass else "formal_conserved_C_no_go_or_explicit_regularization_missing",\n'
            '        },\n'
        )
        text = replace_once(text, old_causal, new_causal, "full-gate causal gate")
        text = replace_once(
            text,
            '            evidence(rel(source_package_path), source_package, {"status": source_package.get("status")}),\n',
            '            evidence(rel(source_package_path), source_package, {"status": source_package.get("status")}),\n'
            '            evidence(rel(no_go_path), no_go, {"status": no_go.get("status"), "proof_scope": no_go.get("proof_scope")}),\n'
            '            evidence(rel(telegraph_path), telegraph, {"status": telegraph.get("status"), "major_result_id": telegraph.get("major_result", {}).get("major_result_id")}),\n'
            '            evidence(rel(coupled_path), coupled, {"status": coupled.get("status"), "major_result_id": coupled.get("major_result", {}).get("major_result_id")}),\n',
            "full-gate causal evidence list",
        )

    if "primary_blocker =" not in text:
        text = replace_once(
            text,
            "    artifact = {\n",
            "    primary_blocker = (\n"
            "        \"dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing\"\n"
            "        if not alpha_ready\n"
            "        else (blockers[0] if blockers else None)\n"
            "    )\n"
            "    artifact = {\n",
            "full-gate primary blocker",
        )
        text = replace_once(
            text,
            '        "controlling_blocker": blockers[0] if blockers else None,\n',
            '        "controlling_blocker": primary_blocker,\n',
            "full-gate primary blocker field",
        )

    obsolete = (
        "{\n"
        '            "formal_conserved_C_no_go_or_explicit_regularization_missing",\n'
        '            "named finite-cone branch or explicit conserved-C regularization",\n'
        '            "named_finite_cone_branch_or_explicit_regularization_missing",\n'
        "        }"
    )
    if obsolete not in text:
        text = replace_once(
            text,
            '        *previous_major.get("what_remains_open", []),\n',
            '        *[\n'
            '            item\n'
            '            for item in previous_major.get("what_remains_open", [])\n'
            '            if item not in {\n'
            '                "formal_conserved_C_no_go_or_explicit_regularization_missing",\n'
            '                "named finite-cone branch or explicit conserved-C regularization",\n'
            '                "named_finite_cone_branch_or_explicit_regularization_missing",\n'
            '            }\n'
            '        ],\n',
            "full-gate stale causal blocker filter",
        )
    FULL_GATE.write_text(text, encoding="utf-8")


def repair_no_go_sync() -> None:
    text = NO_GO_SYNC.read_text(encoding="utf-8-sig")
    if "named_coupled_branch_pass" not in text:
        text = replace_once(
            text,
            "    no_go_hash = hashlib.sha256(NO_GO.read_bytes()).hexdigest()\n",
            "    no_go_hash = hashlib.sha256(NO_GO.read_bytes()).hexdigest()\n"
            "    telegraph_path = ROOT / \"docs/core/07_artifacts/verification/matter_space_conserved_flux_telegraph_verification.json\"\n"
            "    coupled_path = ROOT / \"docs/core/07_artifacts/verification/matter_space_flux_phi_coupled_verification.json\"\n"
            "    telegraph = json.loads(telegraph_path.read_text(encoding=\"utf-8-sig\"))\n"
            "    coupled = json.loads(coupled_path.read_text(encoding=\"utf-8-sig\"))\n"
            "    named_finite_cone_branch_pass = telegraph.get(\"status\") == \"PASS\" and telegraph.get(\"major_result\", {}).get(\"closure_level\") == \"CLOSED_FOR_LANE\"\n"
            "    named_coupled_branch_pass = coupled.get(\"status\") == \"PASS\" and coupled.get(\"major_result\", {}).get(\"closure_level\") == \"CLOSED_FOR_LANE\"\n",
            "no-go sync named branch inputs",
        )
        text = replace_once(
            text,
            '    causal["named_finite_cone_branch_pass"] = False\n'
            '    causal["controlling_blocker"] = "named_finite_cone_branch_or_explicit_regularization_missing"\n'
            '    gate["controlling_blocker"] = "named_finite_cone_branch_or_explicit_regularization_missing"\n',
            '    causal["named_finite_cone_branch_pass"] = named_finite_cone_branch_pass\n'
            '    causal["named_finite_cone_branch_closure_level"] = telegraph.get("major_result", {}).get("closure_level", "OPEN")\n'
            '    causal["named_coupled_branch_pass"] = named_coupled_branch_pass\n'
            '    causal["named_coupled_branch_closure_level"] = coupled.get("major_result", {}).get("closure_level", "OPEN")\n'
            '    causal["controlling_blocker"] = "original_conserved_c_gradient_baseline_blocked" if (causal["formal_no_go_recorded"] and named_finite_cone_branch_pass and named_coupled_branch_pass) else "named_finite_cone_branch_or_explicit_regularization_missing"\n'
            '    alpha_gate = gate["verification_status"].get("alpha_Phi_K", {})\n'
            '    gate["controlling_blocker"] = (\n'
            '        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"\n'
            '        if alpha_gate.get("status") == "BLOCKED"\n'
            '        else gate.get("controlling_blocker")\n'
            '    )\n',
            "no-go sync named branch contract",
        )
        text = replace_once(
            text,
            '    gate["major_result"]["what_is_closed"].append("scoped structural no-go assessment for the declared conserved-C local-gradient class")\n',
            '    closed_item = "scoped structural no-go assessment for the declared conserved-C local-gradient class"\n'
            '    if closed_item not in gate["major_result"]["what_is_closed"]:\n'
            '        gate["major_result"]["what_is_closed"].append(closed_item)\n',
            "no-go sync closed-result dedupe",
        )
        text = replace_once(
            text,
            '    gate["major_result"]["what_remains_open"] = [\n'
            '        "named finite-cone branch or explicit conserved-C regularization",\n'
            '        *[item for item in gate["major_result"]["what_remains_open"] if item != "formal_conserved_C_no_go_or_explicit_regularization_missing"],\n'
            '    ]\n',
            '    gate["major_result"]["what_remains_open"] = [\n'
            '        item\n'
            '        for item in gate["major_result"]["what_remains_open"]\n'
            '        if item not in {\n'
            '            "formal_conserved_C_no_go_or_explicit_regularization_missing",\n'
            '            "named finite-cone branch or explicit conserved-C regularization",\n'
            '            "named_finite_cone_branch_or_explicit_regularization_missing",\n'
            '        }\n'
            '    ]\n',
            "no-go sync stale blocker filter",
        )
    NO_GO_SYNC.write_text(text, encoding="utf-8")


def main() -> int:
    repair_full_gate()
    repair_no_go_sync()
    print("REPAIRED_TOPIC13_CAUSAL_GATE_CONTRACT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
