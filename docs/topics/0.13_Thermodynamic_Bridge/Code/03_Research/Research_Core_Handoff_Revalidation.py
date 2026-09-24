"""Read-only Core handoff revalidation; never refresh another room's evidence."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

TOPIC = Path(__file__).resolve().parents[2]
ROOT = TOPIC.parents[2]
sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_artifact_path
from docs.core.uet_curved_3p1_matter_wiring import curved_3p1_matter_wiring_contract
from docs.scripts.audit.audit_uet_curved_3p1_adm_evolution import build_artifacts

OUTPUT = TOPIC / "Result/artifacts/core_handoff_revalidation.json"
TEST_NAMES = (
    "constraints", "geometry", "adm_evolution", "generalized_harmonic",
    "gh_nonlinear_vacuum", "gh_time_evolution", "matter_wiring",
)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def differences(old, new, path=""):
    """Report all changed leaves; caller alone may remove top-level generated_at."""
    if type(old) is not type(new):
        return [dict(path=path, before=old, after=new)]
    if isinstance(old, dict):
        rows = []
        for key in sorted(set(old) | set(new)):
            child = path + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in old or key not in new:
                rows.append(dict(path=child, before=old.get(key), after=new.get(key),
                                 missing_from="before" if key not in old else "after"))
            else:
                rows.extend(differences(old[key], new[key], child))
        return rows
    if isinstance(old, list):
        if len(old) != len(new):
            return [dict(path=path, before=old, after=new)]
        return [row for i, (a, b) in enumerate(zip(old, new))
                for row in differences(a, b, f"{path}/{i}")]
    return [] if old == new else [dict(path=path, before=old, after=new)]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parent_path = canonical_artifact_path("core_curved_3p1_parent_gate.json")
    acceptance_path = canonical_artifact_path("t13_full_core_ready_acceptance_audit.json")
    parent = load(parent_path)
    acceptance = load(acceptance_path)
    tests = [ROOT / "docs/core/05_tests/regression/root" / f"test_uet_curved_3p1_{name}.py"
             for name in TEST_NAMES]
    evidence = [dict(**e, actual_sha256=digest(ROOT/e["path"]))
                for e in parent["evidence_artifacts"]]
    for row in evidence:
        row["hash_matches"] = row["sha256"] == row["actual_sha256"]
    inputs = [parent_path, acceptance_path, *tests,
              *(ROOT / e["path"] for e in evidence),
              ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_adm_evolution.py",
              ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_matter_wiring.py",
              ROOT / "docs/scripts/audit/audit_uet_curved_3p1_adm_evolution.py",
              Path(__file__), Path(__file__).with_name("test_core_handoff_revalidation.py")]
    before = {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs}
    command = [sys.executable, "-B", "-m", "pytest", *(str(p) for p in tests),
               "-q", "-p", "no:cacheprovider"]
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
    names = ("curved_3p1_adm_evolution_operator_verification.json",
             "curved_3p1_fixed_gauge_adm_hyperbolicity_no_go.json",
             "curved_3p1_adm_evolution_formula_audit.json",
             "curved_3p1_formulation_selection_gate.json")
    comparisons = []
    for name, live in zip(names, build_artifacts()):
        stored = load(canonical_artifact_path(name))
        stored.pop("generated_at", None)
        live.pop("generated_at", None)
        delta = differences(stored, live)
        comparisons.append(dict(artifact=name, differences=delta,
                                exact_payload_match_except_generated_at=not delta))

    # Inspect the known pre-migration module as text, never execute Git content.
    old_ref = "1fd96a48ed977a473688ae8301e6e6768b14c712^:docs/core/uet_curved_3p1_adm_evolution.py"
    historical = subprocess.run(["git", "show", old_ref], cwd=ROOT, capture_output=True, check=True).stdout
    current = (ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_adm_evolution.py").read_bytes()
    stored_verification = load(canonical_artifact_path(names[0]))
    expected_module_sha = stored_verification["source_hashes"][
        "docs/core/02_equations/covariant/uet_curved_3p1_adm_evolution.py"]
    history_comparison = dict(
        git_locator=old_ref, historical_sha256=sha256(historical).hexdigest(),
        stored_expected_sha256=expected_module_sha,
        historical_hash_matches_stored=sha256(historical).hexdigest() == expected_module_sha,
        current_sha256=sha256(current).hexdigest(),
        complete_ast_equal=ast.dump(ast.parse(historical.decode("utf-8-sig"))) ==
                           ast.dump(ast.parse(current.decode("utf-8-sig"))),
        scope="Text/AST comparison of one module, not proof of whole-program equivalence or license to ignore hashes")
    contract = curved_3p1_matter_wiring_contract()
    required_handoff_items = {
        "matter_state_time_evolution": "matter-state time evolution",
        "stress_energy_conservation_propagation": "stress-energy conservation propagation",
        "self_consistent_two_fluid_curved_transport": "self-consistent two-fluid curved transport",
        "numerical_si_einstein_coupling_provenance": "numerical SI Einstein coupling provenance",
    }
    coverage = [dict(requirement=key, explicitly_open_in_matter_contract=value in contract["not_implemented"],
                     explicit_parent_requirement=parent["requirements"].get(key, "NOT_LISTED"))
                for key, value in required_handoff_items.items()]
    after = {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs}
    if before != after:
        raise ValueError("Core inputs changed during revalidation; do not publish mixed-state conclusions")
    result = dict(
        schema_version="t13-core-handoff-revalidation-v1", generated_at=datetime.now(timezone.utc).isoformat(),
        major_result_id="T13_CORE_HANDOFF_REVALIDATION", topic="0.13", closure_level="PARTIAL",
        what_is_closed="Current focused test outcomes and stale evidence links measured; prescribed-matter scope separated from self-consistent evolution",
        equation_or_mapping="Prescribed T_ab -> ADM projections -> GH RHS; not an evolved conserved matter solution",
        units="Existing geometric/natural/SI-projection lanes unchanged", derivation_class="READ_ONLY_INTEGRATION_REVALIDATION",
        observable="numerical constraint/source diagnostics, not a detector observable", data_role="INTERNAL_NO_NEW_EXPERIMENTAL_INPUT",
        verification_status="BLOCKED_HANDOFF_REVALIDATION" if run.returncode or not all(e["hash_matches"] for e in evidence)
                            else "FOCUSED_CHECKS_PASS_WITH_PHYSICAL_SCOPE_OPEN",
        current_parent_status=parent["status"], current_parent_open_blockers=parent["major_result"]["open_blockers"],
        t13_acceptance_record_status=acceptance["status"], t13_acceptance_scope=acceptance["major_result"]["claim_boundary"],
        t13_acceptance_reverified=False, parent_evidence=evidence,
        focused_tests=dict(command=[p.replace(str(ROOT), "<REPO>") for p in command], returncode=run.returncode,
                           stdout=run.stdout, stderr=run.stderr),
        fresh_adm_comparisons=comparisons, adm_module_history=history_comparison,
        matter_contract_open_items=contract["not_implemented"], parent_requirement_coverage=coverage,
        controlling_blocker="stale_core_provenance_and_prescribed_vs_conserved_matter_handoff",
        open_blockers=["review and regenerate ADM/source provenance plus downstream parent links",
                       "make matter evolution/conservation requirements explicit in parent acceptance",
                       "constraint-preserving boundaries and dimensional observable mapping remain open"],
        next_action="Core owner reviews exact differences and refreshes evidence in dependency order; do not bypass hash checks or relabel prescribed matter as evolved matter",
        dependency_unlocked=[], full_core_unlock=False, global_claim_promotion=False,
        core_artifacts_modified=False, claim_boundary="Revalidates selected implementations and evidence links only. Does not withdraw the bounded He-4 record or certify full Core/GR/graphite readiness.",
        evidence_hashes=before)
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(dict(status=result["verification_status"], tests=run.stdout.splitlines()[-1:],
                         stale_parent_links=sum(not r["hash_matches"] for r in evidence),
                         adm_history=history_comparison, differences=comparisons)))
    return 1 if result["verification_status"].startswith("BLOCKED") else 0


if __name__ == "__main__":
    raise SystemExit(main())
