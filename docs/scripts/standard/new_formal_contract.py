"""Write a minimal FORMAL calculation contract (standard 30) for a derivation module.

Research Standard v2 keeps calculation contracts in force (docs/STANDARD.md
section 15), but a full PHYSICAL_COMPARISON contract runs to hundreds of
lines. Formal code (equations, mappings, derivation helpers) that is checked
by physics tests needs only the FORMAL profile, where the observation chain is
not applicable. This tool fills that boilerplate from a few arguments and
computes the identity hashes with the same CRLF normalization as
docs/scripts/audit/audit_calculation_completeness.py.

Example:
  python docs/scripts/standard/new_formal_contract.py \
    --contract-id CORE_DEF_MAPPING_FORMAL_V1 \
    --question "Does the DEF map follow from the Jordan-frame action?" \
    --quantity "DEF alpha and beta" --formula-id UET_DEF_MAP \
    --code docs/core/02_equations/covariant/uet_scalar_tensor_mapping.py \
    --test docs/core/05_tests/physics/test_def_mapping.py \
    --out docs/core/00_governance/calculation_contracts/def_mapping_formal.json

Then run: python docs/scripts/audit/audit_calculation_completeness.py --changed origin/main --check

Comparisons with observations (Test Cards) still need a PHYSICAL_COMPARISON
contract; see docs/core/00_governance/calculation_contracts/t001_binary_pulsar_def_constraint.json
as the reference template.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TEXT_SUFFIXES = {".py", ".md", ".json", ".csv", ".tsv", ".txt", ".tex", ".yml", ".yaml"}
GROUPS = ("system_state", "drive_environment", "propagation", "frame_time", "detector", "processing", "numerics")
NOT_FORMAL = "not applicable to this formal derivation"


def identity_sha256(root: Path, rel: str) -> str:
    data = (root / rel).read_bytes()
    if Path(rel).suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def build_contract(root: Path, contract_id: str, question: str, quantity: str,
                   formula_ids: list[str], code: list[str], tests: list[str], unit: str = "dimensionless") -> dict:
    evidence = code + tests
    components = []
    for group in GROUPS:
        if group in ("system_state", "processing"):
            components.append({"id": group, "group": group, "disposition": "MODELED",
                               "reason": "Declared formal expressions in the code under contract.", "evidence": list(code)})
        elif group == "numerics":
            components.append({"id": group, "group": group, "disposition": "MODELED",
                               "reason": "Checked by the listed physics tests (docs/STANDARD.md section 6).",
                               "evidence": list(tests or code)})
        else:
            components.append({"id": group, "group": group, "disposition": "NOT_APPLICABLE",
                               "reason": "Formal derivation; no physical measurement chain.", "evidence": []})
    return {
        "schema_version": "uet-calculation-contract-v1",
        "contract_id": contract_id,
        "profile": "FORMAL",
        "review": {"status": "INCOMPLETE", "reviewer": "tool:new_formal_contract",
                   "rationale": "Formal coverage generated from Standard v2 records; evidence level is set in docs/standard, not here."},
        "question": question,
        "output": {"quantity": quantity, "unit": unit, "domain": "declared formal domain of the code",
                   "accuracy": "exact or as asserted by the listed physics tests", "claim_intent": "FORMAL_RESULT"},
        "model": {"formula_ids": formula_ids, "assumptions": "as declared in the code and Theory Card",
                  "approximation": "none beyond the code", "initial_boundary": "algebraic",
                  "drive_environment": "not relevant to a formal derivation", "parameters": "symbolic or test-sampled"},
        "data_policy": {"uses_observations": False, "calibration_ids": [], "comparison_ids": [],
                        "independent_validation": False, "holdout_policy": "none"},
        "observation": {**{k: NOT_FORMAL for k in ("source_state", "generated_trace", "carrier", "observer_state",
                                                    "readout", "backaction", "frame", "time_convention", "product_level")},
                        "corrections": []},
        "components": components,
        "error_budget": {"unit": unit, "numerical": "test tolerances", "approximation": "none declared",
                         "measurement": "not applicable", "systematic": "not applicable", "omissions": "none declared",
                         "dependence": "not applicable", "acceptance": "formal coverage only", "omission_limit": None},
        "identities": [{"path": p, "kind": "working_file", "role": "code", "sha256": identity_sha256(root, p),
                        "availability": "REQUIRED"} for p in evidence],
        "entrypoints": list(code),
        "evidence": evidence,
        "claim_boundary": "Formal coverage only; no physical acceptance or status change.",
        "next_action": "Refresh identities with this tool when the code or tests change.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--contract-id", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--quantity", required=True)
    parser.add_argument("--formula-id", action="append", required=True)
    parser.add_argument("--code", action="append", required=True)
    parser.add_argument("--test", action="append", default=[])
    parser.add_argument("--unit", default="dimensionless")
    parser.add_argument("--out", required=True)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    contract = build_contract(args.root, args.contract_id, args.question, args.quantity,
                              args.formula_id, args.code, args.test, args.unit)
    out = args.root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(contract, indent=2, ensure_ascii=False) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
