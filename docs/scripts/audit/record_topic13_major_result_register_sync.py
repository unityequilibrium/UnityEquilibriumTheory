from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FULL_GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-13.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, marker: str, content: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in text:
        print(f"skip existing section: {path}")
        return
    separator = "\n" if text.endswith("\n") else "\n\n"
    path.write_text(text + separator + content.rstrip() + "\n", encoding="utf-8")
    print(f"appended: {path}")


def main() -> int:
    register_hash = sha256(REGISTER)
    dependency_hash = sha256(DEPENDENCY)
    full_hash = sha256(FULL_GATE)
    content = f"""## Topic 13 major-result register synchronization wave

- area: `research-core` (secondary: `repo-ops`)
- workspace: `docs/core/artifacts` and `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: canonical major-result register; dependency unlock gate; Topic 13 full gate; register sync helper and regression test
- verifier: major-result/dependency tests passed (`5 passed`); Topic 13 regression passed (`174 passed, 625 deselected`)
- public-safety: `partial`
- result: Bosak, Hanfland, IHEP TPG, and official Nelson-Riley comparator lanes are exposed as `CLOSED_FOR_LANE` major results; every lane retains `full_core_unlock=false`
- hashes: full gate `{full_hash}`; register `{register_hash}`; dependency gate `{dependency_hash}`
- remains: `T13_FULL_THERMODYNAMIC_BRIDGE` is `PARTIAL/BLOCKED`; Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, physical EOS/transport/KMS/entropy, base-Phi SI mapping, and material/uncertainty closure remain open
- next action: acquire permitted Ding/independent PBTE payload and independent base-Phi anchor; no downstream dependency promotion
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(LEDGER, "## Topic 13 major-result register synchronization wave", content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
