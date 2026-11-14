"""
Allen-Dynes source-labeled smoke-test verifier.

This script is intentionally separate from Experiment_Superconductor_Data.py.
It does not change the raw McMillan gate; it writes a separate artifact for
source-labeled Allen-Dynes branch development.
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
    / "0_4_superconductivity_superfluids_allen_dynes_verification.json"
)
DESIGN_PACKET_PATH = Path(
    "docs/data/external/condensed_matter/superconductivity/row_resolution_targets/"
    "allen_dynes_verifier_branch_design_packet_20260515.json"
)
POLICY_REQUEST_PATH = Path(
    "docs/data/external/condensed_matter/superconductivity/row_resolution_targets/"
    "nb3sn_physrevb_27_1568_unified_non_mirrored_policy_request_20260515.json"
)
POLICY_RELEASE_PREVIEW_PATH = Path(
    "docs/data/external/condensed_matter/superconductivity/row_resolution_targets/"
    "nb3sn_allen_dynes_policy_release_preview_20260515.json"
)

AVERAGE_ERROR_GATE_PERCENT = 20.0
PER_ROW_ERROR_GATE_PERCENT = 20.0


def hash_file(path):
    path = Path(path)
    if not path.exists():
        return None
    return sha256(path.read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dotted_get(mapping, dotted_path):
    current = mapping
    for part in dotted_path.split("."):
        current = current[part]
    return current


def resolve_release_condition(condition):
    if not condition:
        return {
            "has_release_condition": False,
            "decision_state": None,
            "accepted": False,
        }
    policy_path = Path(condition["policy_request_path"])
    policy_record = load_json(policy_path)
    decision_state = dotted_get(policy_record, condition["decision_field"])
    accepted = decision_state in condition["accepted_decision_values"]
    return {
        "has_release_condition": True,
        "policy_request_path": str(policy_path),
        "policy_request_sha256": hash_file(policy_path),
        "decision_field": condition["decision_field"],
        "decision_state": decision_state,
        "accepted_decision_values": condition["accepted_decision_values"],
        "accepted": accepted,
    }


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
    strict_rows = []
    excluded_rows = []

    for row in input_table["rows"]:
        release_state = resolve_release_condition(row.get("strict_gate_release_condition"))
        effective_strict_gate_eligible = row["strict_gate_eligible"] or release_state["accepted"]
        strict_gate_exclusion_reason = None if effective_strict_gate_eligible else row.get(
            "strict_gate_exclusion_reason"
        )
        predicted_tc_K, f1, f2, omega_ratio = allen_dynes_tc(
            row["omega_log_K"],
            row["omega2_sqrt_K"],
            row["lambda_ep"],
            row["mu_star"],
        )
        signed_error_K = predicted_tc_K - row["tc_observed_K"]
        relative_error_percent = abs(signed_error_K) / row["tc_observed_K"] * 100
        evaluated = {
            "material": row["material"],
            "sample_label": row["sample_label"],
            "tc_observed_K": row["tc_observed_K"],
            "tc_observed_basis": row["tc_observed_basis"],
            "table_tc_K": row.get("table_tc_K"),
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
            "input_label": row["input_label"],
            "archive_policy_state": row["archive_policy_state"],
            "declared_strict_gate_eligible": row["strict_gate_eligible"],
            "effective_strict_gate_eligible": effective_strict_gate_eligible,
            "strict_gate_release_state": release_state,
            "strict_gate_exclusion_reason": strict_gate_exclusion_reason,
            "source_record_paths": row["source_record_paths"],
            "source_record_hashes": {
                source_path: hash_file(source_path)
                for source_path in row["source_record_paths"]
            },
        }
        rows.append(evaluated)
        if effective_strict_gate_eligible:
            strict_rows.append(evaluated)
        else:
            excluded_rows.append(
                {
                    "material": row["material"],
                    "sample_label": row["sample_label"],
                    "reason": strict_gate_exclusion_reason,
                    "archive_policy_state": row["archive_policy_state"],
                    "release_state": release_state,
                }
            )

    return rows, strict_rows, excluded_rows


def summarize(rows):
    if not rows:
        return {
            "row_count": 0,
            "average_relative_error_percent": None,
            "rows_within_20_percent": 0,
        }
    return {
        "row_count": len(rows),
        "average_relative_error_percent": sum(
            row["relative_error_percent"] for row in rows
        )
        / len(rows),
        "rows_within_20_percent": sum(
            1 for row in rows if row["per_row_gate_status"] == "PASS"
        ),
    }


def gate_status(strict_rows, excluded_rows):
    if not strict_rows:
        return "BLOCKED_PENDING_SOURCE_POLICY"
    summary = summarize(strict_rows)
    all_rows_pass = all(row["per_row_gate_status"] == "PASS" for row in strict_rows)
    average_pass = (
        summary["average_relative_error_percent"] <= AVERAGE_ERROR_GATE_PERCENT
    )
    return "PASS" if all_rows_pass and average_pass else "FAIL"


def interpret_status(status):
    if status == "BLOCKED_PENDING_SOURCE_POLICY":
        return {
            "interpretation": (
                "This artifact is a separate Allen-Dynes smoke test. The diagnostic rows "
                "fit Nb3Sn well, but no row enters the strict gate until archive/non-mirrored "
                "citation policy is accepted. The policy release preview is non-executing "
                "and does not change the current blocked gate. Strict eligibility is resolved "
                "from row release conditions and policy decision state."
            ),
            "limitations": [
                "This artifact does not replace the raw McMillan baseline artifact.",
                "The current smoke test covers only Nb3Sn same-source rows.",
                "Strict gate status is blocked because archive policy remains pending.",
                "No calibrated, inverse-fit, or heuristic UET rows are counted in the strict lane.",
            ],
            "next_actions": [
                "Resolve non-mirrored citation policy for PhysRevB.27.1568.",
                "Add additional source-labeled rows only after omega_log, omega2, lambda_ep, and mu_star evidence is captured.",
                "Keep raw McMillan and Allen-Dynes branch artifacts side by side in documentation.",
            ],
        }
    return {
        "interpretation": (
            "This artifact is a separate Allen-Dynes smoke test. The Nb3Sn same-source rows "
            "enter the strict gate because the PhysRevB.27.1568 non-mirrored citation route "
            "has been accepted for this source package and branch gate. This is not a "
            "topic-level PASS and does not replace the raw McMillan baseline artifact."
        ),
        "limitations": [
            "This artifact does not replace the raw McMillan baseline artifact.",
            "The current strict gate covers only the Nb3Sn same-source smoke-test rows.",
            "The accepted policy scope is limited to PhysRevB.27.1568 and this Allen-Dynes branch gate.",
            "No calibrated, inverse-fit, or heuristic UET rows are counted in the strict lane.",
        ],
        "next_actions": [
            "Add additional source-labeled rows only after omega_log, omega2, lambda_ep, and mu_star evidence is captured.",
            "Keep raw McMillan and Allen-Dynes branch artifacts side by side in documentation.",
            "Do not upgrade the full superconductivity topic claim until broader source-locked coverage exists.",
        ],
    }


def write_artifact():
    input_table = load_json(INPUT_PATH)
    design_packet = load_json(DESIGN_PACKET_PATH)
    policy_request = load_json(POLICY_REQUEST_PATH)
    policy_release_preview = load_json(POLICY_RELEASE_PREVIEW_PATH)
    rows, strict_rows, excluded_rows = evaluate_rows(input_table)
    strict_summary = summarize(strict_rows)
    diagnostic_summary = summarize(rows)
    status = gate_status(strict_rows, excluded_rows)
    status_text = interpret_status(status)

    artifact = {
        "schema_version": "1.0",
        "topic": "0.4_Superconductivity_Superfluids",
        "verifier_branch": "Allen-Dynes source-labeled smoke test",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": (
            "python docs/topics/0.4_Superconductivity_Superfluids/"
            "Code/03_Research/Experiment_Allen_Dynes_Data.py"
        ),
        "run_status": "PASS",
        "model_gate_status": status,
        "thresholds": {
            "strict_average_relative_error_percent": AVERAGE_ERROR_GATE_PERCENT,
            "strict_per_row_relative_error_percent": PER_ROW_ERROR_GATE_PERCENT,
        },
        "inputs": {
            "input_table": {
                "path": str(INPUT_PATH),
                "sha256": hash_file(INPUT_PATH),
            },
            "design_packet": {
                "path": str(DESIGN_PACKET_PATH),
                "sha256": hash_file(DESIGN_PACKET_PATH),
                "branch_contract": design_packet["branch_contract"],
            },
            "policy_request": {
                "path": str(POLICY_REQUEST_PATH),
                "sha256": hash_file(POLICY_REQUEST_PATH),
                "decision_state": policy_request["policy_decision_request"]["decision_state"],
            },
            "policy_release_preview": {
                "path": str(POLICY_RELEASE_PREVIEW_PATH),
                "sha256": hash_file(POLICY_RELEASE_PREVIEW_PATH),
                "would_be_branch_model_gate_status": policy_release_preview[
                    "preview_gate_metrics"
                ]["would_be_branch_model_gate_status"],
                "claim_boundary": policy_release_preview["claim_boundary"],
            },
        },
        "strict_source_locked_summary": strict_summary,
        "diagnostic_all_rows_summary": diagnostic_summary,
        "rows_excluded_from_strict_gate": excluded_rows,
        "results": rows,
        "interpretation": status_text["interpretation"],
        "limitations": status_text["limitations"],
        "next_actions": status_text["next_actions"],
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Allen-Dynes artifact saved to {ARTIFACT_PATH}")
    print(f"Branch gate: {status}")
    print(
        "Diagnostic average error: "
        f"{diagnostic_summary['average_relative_error_percent']:.6f}%"
    )


if __name__ == "__main__":
    write_artifact()
