"""Synchronize the Ding PBTE mapping wave into Topic 13 durable records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
UPDATE_LOG = TOPIC / "UPDATE_LOG.md"
DATA_MANIFEST = TOPIC / "DATA_MANIFEST.md"
FORMULA_AUDIT = TOPIC / "FORMULA_AUDIT.md"
VERIFICATION_SPEC = TOPIC / "VERIFICATION_SPEC.md"
WORK_LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-11.md"
PACKAGE = TOPIC / (
    "Data/03_Research/ding_2022_pbte_energy_temperature_source_package.json"
)
PDF = TOPIC / "Data/03_Research/raw/ding_2022_supplementary_information.pdf"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_pbte_energy_temperature_mapping_audit.json"
MARKER = "### 2026-08-11 - Ding PBTE energy-temperature source mapping"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_preserving_newline(path: Path) -> tuple[str, str, bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, newline, has_bom


def write_preserving_format(path: Path, text: str, has_bom: bool) -> None:
    encoded = text.encode("utf-8")
    if has_bom:
        encoded = b"\xef\xbb\xbf" + encoded
    path.write_bytes(encoded)


def append_once(path: Path, marker: str, block: str) -> bool:
    text, newline, has_bom = read_preserving_newline(path)
    if marker in text:
        return False
    normalized = block.strip("\n").replace("\n", newline)
    updated = text.rstrip("\r\n") + newline * 2 + normalized + newline
    write_preserving_format(path, updated, has_bom)
    return True


def insert_manifest_row() -> bool:
    text, newline, has_bom = read_preserving_newline(DATA_MANIFEST)
    marker = "| Ding 2022 PBTE energy-temperature source mapping |"
    if marker in text:
        return False
    anchor = "|:--|:--|:--|:--|--:|:--|:--|:--|" + newline
    if anchor not in text:
        raise RuntimeError("Data-manifest table header anchor not found")
    row = (
        "| Ding 2022 PBTE energy-temperature source mapping | "
        "`Data/03_Research/ding_2022_pbte_energy_temperature_source_package.json`; "
        "`Data/03_Research/raw/ding_2022_supplementary_information.pdf`; "
        "`docs/core/07_artifacts/topic13/t13_ding_pbte_energy_temperature_mapping_audit.json` | "
        "Ding et al., Nature Communications 13, 285 (2022), Supplementary pp.3-5, Eqs. S1-S10; DOI `10.1038/s41467-021-27907-z`; PMC `PMC8755757` | "
        "`g_mu` and `Delta_u_ph` J m^-3; `C_src` J m^-3 K^-1; `Delta_Tq` K | "
        f"{PDF.stat().st_size} raw bytes | PDF `{sha256(PDF)}`; package `{sha256(PACKAGE)}`; audit `{sha256(AUDIT)}` | "
        "Derived standard-PBTE formula and TTG-observable mapping; no numeric calibration or holdout consumption | "
        "`PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN`; numeric `C_src(T)`, convergence/uncertainty, `e0`, and base `Phi` mapping remain open. |"
        + newline
    )
    updated = text.replace(anchor, anchor + row, 1)
    write_preserving_format(DATA_MANIFEST, updated, has_bom)
    return True


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    if audit["status"] != "PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN":
        raise RuntimeError("Ding PBTE audit must pass before docs are synchronized")
    update_changed = append_once(
        UPDATE_LOG,
        MARKER,
        """
### 2026-08-11 - Ding PBTE energy-temperature source mapping

- Scope: source-lock the standard Ding 2022 PBTE map from deviational phonon energy density to the TTG temperature-response observable without asserting a base-UET `Phi` identity.
- Added or changed: official Supplementary PDF archive and hashes, source/formula package, deterministic audit, `Phi_E`/full-gate/register integration, focused tests, formula/verification records, and major-result wave report.
- Verified with: `PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN`; all mapping checks passed; Wave 1 integrity remains dependency-conservative; Xie 2026 access and consumption remain false.
- Result closed: `T13_DING_PBTE_ENERGY_TEMPERATURE_MAPPING` is `CLOSED_FOR_LANE`; `Delta_Tq = sum_mu(g_mu)/C_src` is source-located and unit-closed, while `C_src` is explicitly distinct from UET `C`.
- Route decision: use Ding-compatible mode heat capacity/unit-cell inputs for the TTG source lane; preserve Georgia Tech as a separate c_p/source-dependency no-go rather than pooling material grades.
- Still open: numeric `C_src(T)` and convergence/uncertainty, `e0`, base `Phi -> Delta_u_ph`, independent `alpha_Phi_K`, and EOS/transport/KMS/entropy closure.
- Claim impact: no topic or global promotion; this is a standard-physics formula/source result, not a numeric calibration, prediction, or external validation.
- Next controller: `ding_pbte_numeric_C_src_and_uet_energy_anchor_missing`.
""",
    )
    manifest_changed = insert_manifest_row()
    formula_changed = append_once(
        FORMULA_AUDIT,
        "## Ding 2022 PBTE energy-temperature source mapping (2026-08-11)",
        """
## Ding 2022 PBTE energy-temperature source mapping (2026-08-11)

- Source locator: Ding 2022 Supplementary Information p.3 Eq. S4 and p.5 Eq. S10.
- Source mapping: `Delta_u_ph = sum_mu(g_mu)` and `Delta_Tq = Delta_u_ph/C_src`.
- Unit closure: `(J m^-3)/(J m^-3 K^-1) = K`.
- Conditional named branch: `Phi_E = Delta_u_ph/e0`, `alpha_Phi_E_K = e0/C_src`.
- Ontology boundary: source `C_src` is heat capacity per volume and is not UET `C`; `Phi_E` is not base `Phi`; `R_gen` remains a derived trace.
- Derivation class: source-backed standard linearized PBTE mapping; UET dimensional correspondence remains open.
- Numeric status: no `C_src(T)`, `e0`, or alpha value is emitted; Xie 2026 remains unread.
""",
    )
    verification_changed = append_once(
        VERIFICATION_SPEC,
        "## Ding PBTE Source-Formula Gate",
        r"""
## Ding PBTE Source-Formula Gate

Run:

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_ding_pbte_energy_temperature_mapping.py
```

Artifact:

- `docs/core/07_artifacts/topic13/t13_ding_pbte_energy_temperature_mapping_audit.json`

Acceptance requires the official PDF hash/size/MD5, source identity, Eq. S4/S10 locators, kelvin unit closure, source-`C`/UET-`C` separation, absent numeric calibration, material non-pooling, and Xie 2026 non-access checks to pass. `PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN` closes only the source-formula lane; it does not close numeric `C_src(T)`, base `Phi`, `e0`, `alpha_Phi_K`, or Full Topic 13.
""",
    )
    ledger_changed = append_once(
        WORK_LEDGER,
        "## Topic 13 Ding PBTE Source Mapping",
        """
## Topic 13 Ding PBTE Source Mapping

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` artifacts
- changed: archived official Ding Supplement, added source/formula audit, gate/register integration, tests, and synchronized formula/provenance records
- verification: Ding mapping audit passes; hash, units, ontology, material separation, and holdout checks pass; aggregate Wave 1 integrity remains conservative
- public-safety status: `partial`; CC BY source identity is recorded, but numeric `C_src(T)`, uncertainty/convergence, and UET dimensional inputs remain open
- current claim boundary: `T13_DING_PBTE_ENERGY_TEMPERATURE_MAPPING` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13 files and generated artifacts remain in the worktree; unrelated Topic 0.22/0.25 work was not edited
- next action: package or reproduce Ding-compatible mode heat capacity and unit-cell inputs, then derive `e0` and base `Phi -> Delta_u_ph`
""",
    )
    print(
        {
            "update_log_changed": update_changed,
            "data_manifest_changed": manifest_changed,
            "formula_audit_changed": formula_changed,
            "verification_spec_changed": verification_changed,
            "work_ledger_changed": ledger_changed,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
