"""
Allen-Dynes policy-release dry run.

This script does not edit the policy request. It simulates an accepted
non-mirrored policy state in memory and writes a separate dry-run artifact.
"""

import json
import math
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


TOPIC_DIR = Path("docs/topics/0.4_Superconductivity_Superfluids")
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
INPUT_PATH = DATA_DIR / "allen_dynes_source_labeled_inputs.json"
ARTIFACT_PATH = (
    TOPIC_DIR
    / "Result"
    / "artifacts"
    / "0_4_superconductivity_superfluids_allen_dynes_policy_dry_run.json"
)
POLICY_REQUEST_PATH = Path(
    "docs/data/external/condensed_matter/superconductivity/row_resolution_targets/"
    "nb3sn_physrevb_27_1568_unified_non_mirrored_policy_request_20260515.json"
)
TRANSITION_CHECKLIST_PATH = Path(
    "docs/data/external/condensed_matter/superconductivity/row_resolution_targets/"
    "nb3sn_allen_dynes_policy_transition_checklist_20260515.json"
)

ASSUMED_DECISION_STATE = "accepted_for_this_source_package_only"
AVERAGE_ERROR_GATE_PERCENT = 20.0
PER_ROW_ERROR_GATE_PERCENT = 20.0


def hash_file(path):
    path = Path(path)
    if not path.exists():
        return None
    return sha256(path.read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def allen_dynes_tc(omega_log_K, omega2_sqrt_K, lambda_ep, mu_star):
    exponent = -1.04 * (1 + lambda_ep) / (
        lambda_ep - mu_star * (1 + 0.62 * lambda_ep)
    )
    omega_ratio = omega2_sqrt_K / omega_log_K
    lambda_1 = 2.46 * (1 + 3.8 * mu_star)
    f1 = (1 + (lambda_ep / lambda_1) ** 1.5) ** (1 / 3)
    lambda_2 = 1.82 * (1 + 6.3 * mu_star) * omega_ratio
    f2 = 1 + ((omega_ratio - 1) * lambda_ep**2) / (lambda_ep**2 + lambda_2**2)
    tc_K = f1 * f2 * (omega_log_K / 1.2) * math.exp(exponent)
    return tc_K, f1, f2, omega_ratio


def evaluate_rows(input_table):
    rows = []
    for row in input_table["rows"]:
        release_condition = row.get("strict_gate_release_condition", {})
        assumed_accepted = ASSUMED_DECISION_STATE in release_condition.get(
            "accepted_decision_values", []
        )
        effective_strict_gate_eligible = row["strict_gate_eligible"] or assumed_accepted
        predicted_tc_K, f1, f2, omega_ratio = allen_dynes_tc(
            row["omega_log_K"],
            row["omega2_sqrt_K"],
            row["lambda_ep"],
            row["mu_star"],
        )
        signed_error_K = predicted_tc_K - row["tc_observed_K"]
        relative_error_percent = abs(signed_error_K) / row["tc_observed_K"] * 100
        rows.append(
            {
                "material": row["material"],
                "sample_label": row["sample_label"],
                "tc_observed_K": row["tc_observed_K"],
                "tc_observed_basis": row["tc_observed_basis"],
                "omega_log_K": row["omega_log_K"],
                "omega2_sqrt_K": row["omega2_sqrt_K"],
                "sqrt_omega2_over_omega_log": omega_ratio,
                "lambda_ep": row["lambda_ep"],
                "mu_star": row["mu_star"],
                "f1": f1,
                "f2": f2,
                "predicted_tc_K": predicted_tc_K,
                "signed_error_K": signed_error_K,
                "relative_error_percent": relative_error_percent,
                "per_row_gate_status": (
                    "PASS"
                    if relative_error_percent <= PER_ROW_ERROR_GATE_PERCENT
                    else "FAIL"
                ),
                "declared_strict_gate_eligible": row["strict_gate_eligible"],
                "dry_run_effective_strict_gate_eligible": effective_strict_gate_eligible,
                "dry_run_assumed_decision_state": ASSUMED_DECISION_STATE,
                "dry_run_release_condition_satisfied": assumed_accepted,
            }
        )
    return rows


def summarize(rows):
    strict_rows = [row for row in rows if row["dry_run_effective_strict_gate_eligible"]]
    if not strict_rows:
        return {
            "strict_row_count": 0,
            "strict_average_relative_error_percent": None,
            "strict_rows_within_20_percent": 0,
            "strict_gate_status": "BLOCKED_PENDING_SOURCE_POLICY",
        }
    average_error = sum(row["relative_error_percent"] for row in strict_rows) / len(strict_rows)
    rows_within_gate = sum(1 for row in strict_rows if row["per_row_gate_status"] == "PASS")
    strict_gate_status = (
        "PASS_FOR_NB3SN_SMOKE_TEST_ONLY"
        if average_error <= AVERAGE_ERROR_GATE_PERCENT and rows_within_gate == len(strict_rows)
        else "FAIL"
    )
    return {
        "strict_row_count": len(strict_rows),
        "strict_average_relative_error_percent": average_error,
        "strict_rows_within_20_percent": rows_within_gate,
        "strict_gate_status": strict_gate_status,
    }


def write_artifact():
    input_table = load_json(INPUT_PATH)
    policy_request = load_json(POLICY_REQUEST_PATH)
    transition_checklist = load_json(TRANSITION_CHECKLIST_PATH)
    rows = evaluate_rows(input_table)
    summary = summarize(rows)
    artifact = {
        "schema_version": "1.0",
        "topic": "0.4_Superconductivity_Superfluids",
        "verifier_branch": "Allen-Dynes policy-release dry run",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": (
            "python docs/topics/0.4_Superconductivity_Superfluids/"
            "Code/03_Research/Experiment_Allen_Dynes_Policy_Dry_Run.py"
        ),
        "run_status": "PASS",
        "model_gate_status": summary["strict_gate_status"],
        "dry_run": {
            "assumed_decision_state": ASSUMED_DECISION_STATE,
            "actual_policy_decision_state": policy_request["policy_decision_request"][
                "decision_state"
            ],
            "edits_policy_file": False,
            "claim_boundary": "This dry run does not edit or accept the policy request.",
        },
        "inputs": {
            "input_table": {
                "path": str(INPUT_PATH),
                "sha256": hash_file(INPUT_PATH),
            },
            "policy_request": {
                "path": str(POLICY_REQUEST_PATH),
                "sha256": hash_file(POLICY_REQUEST_PATH),
            },
            "transition_checklist": {
                "path": str(TRANSITION_CHECKLIST_PATH),
                "sha256": hash_file(TRANSITION_CHECKLIST_PATH),
                "allowed_acceptance_values": transition_checklist[
                    "allowed_acceptance_values"
                ],
            },
        },
        "dry_run_strict_summary": summary,
        "results": rows,
        "interpretation": (
            "This dry run verifies that the policy-aware strict-gate logic would release "
            "the Nb3Sn smoke-test rows if the policy decision were accepted. It is not "
            "the current model gate."
        ),
        "limitations": [
            "Does not edit the policy request.",
            "Does not replace the current Allen-Dynes artifact.",
            "Does not replace the raw McMillan artifact.",
            "Still covers only the Nb3Sn smoke-test row set.",
        ],
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Allen-Dynes policy dry-run artifact saved to {ARTIFACT_PATH}")
    print(f"Dry-run gate: {summary['strict_gate_status']}")
    print(
        "Dry-run strict average error: "
        f"{summary['strict_average_relative_error_percent']:.6f}%"
    )


if __name__ == "__main__":
    write_artifact()
