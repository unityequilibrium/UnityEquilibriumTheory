"""Synchronize the Ding OA input-availability no-go into durable records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
UPDATE_LOG = TOPIC / "UPDATE_LOG.md"
DATA_MANIFEST = TOPIC / "DATA_MANIFEST.md"
LIMITATIONS = TOPIC / "LIMITATIONS.md"
VERIFICATION_SPEC = TOPIC / "VERIFICATION_SPEC.md"
WORK_LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-11.md"
PACKAGE = TOPIC / (
    "Data/03_Research/ding_2022_pbte_numeric_input_availability_package.json"
)
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_pbte_numeric_input_availability_audit.json"
INVENTORY = TOPIC / "Data/03_Research/raw/ding_2022_pmc_s3_inventory.xml"
MARKER = "### 2026-08-11 - Ding PBTE official-OA numeric-input no-go"


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
    marker = "| Ding 2022 PMC OA numeric-input availability |"
    if marker in text:
        return False
    anchor = "|:--|:--|:--|:--|--:|:--|:--|:--|" + newline
    if anchor not in text:
        raise RuntimeError("Data-manifest table header anchor not found")
    row = (
        "| Ding 2022 PMC OA numeric-input availability | "
        "`Data/03_Research/ding_2022_pbte_numeric_input_availability_package.json`; "
        "`Data/03_Research/raw/ding_2022_pmc_s3_inventory.xml`; "
        "`docs/core/07_artifacts/topic13/t13_ding_pbte_numeric_input_availability_audit.json` | "
        "PMC OA API, complete `PMC8755757.1/` S3 prefix, object metadata, and full text captured 2026-08-11 | "
        "source inventory only; required `C_src` units J m^-3 K^-1 | "
        f"{INVENTORY.stat().st_size} inventory bytes | inventory `{sha256(INVENTORY)}`; package `{sha256(PACKAGE)}`; audit `{sha256(AUDIT)}` | "
        "Source acquisition decision; no calibration consumed | "
        "`PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO`; official OA route lacks reproducible PBTE numeric inputs, while author request or independent reproduction remains open. |"
        + newline
    )
    updated = text.replace(anchor, anchor + row, 1)
    write_preserving_format(DATA_MANIFEST, updated, has_bom)
    return True


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    if audit["status"] != "PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO":
        raise RuntimeError("Ding OA availability audit must pass before docs sync")
    update_changed = append_once(
        UPDATE_LOG,
        MARKER,
        """
### 2026-08-11 - Ding PBTE official-OA numeric-input no-go

- Scope: determine whether the complete official PMC OA distribution directly exposes the phonon payload needed to reproduce numeric `C_src(T)`.
- Added or changed: archived OA API record, complete S3 prefix inventory, object metadata, and full text; added source-availability package/audit, gate/register integration, tests, and acquisition decision.
- Verified with: `PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO`; the prefix is complete with 11 objects and no force-constant, scattering-matrix, mode-heat-capacity, or Phonopy/ShengBTE payload; Xie 2026 remains unread.
- Result closed: `T13_DING_PBTE_OA_NUMERIC_INPUT_NO_GO` is `CLOSED_FOR_LANE`; further searching inside the same official OA package is no longer an open-ended action.
- Still open: corresponding-author request or an independently sourced graphite phonon reproduction package, numeric `C_src(T)`, uncertainty/convergence, `e0`, base `Phi -> Delta_u_ph`, and full thermodynamic closure.
- Claim impact: no upgrade; the no-go is scoped to the captured OA route and is not a claim that data do not exist elsewhere.
- Next controller: `ding_pbte_author_data_or_independent_reproduction_package_missing`.
""",
    )
    manifest_changed = insert_manifest_row()
    limitations_changed = append_once(
        LIMITATIONS,
        "## Ding 2022 OA Numeric-Input Availability (2026-08-11)",
        """
## Ding 2022 OA Numeric-Input Availability (2026-08-11)

The complete captured official `PMC8755757.1/` prefix has no force constants, Phonopy/ShengBTE inputs, scattering matrix, mode-resolved heat-capacity data, or numeric `C_src(T)`. The article gives computational grid/supercell details but routes supporting data to a corresponding-author request. This closes only the current official-OA search route. It does not show that author-held data are unavailable and does not permit reconstruction of `C_src(T)` from normalized TTG curves.
""",
    )
    verification_changed = append_once(
        VERIFICATION_SPEC,
        "## Ding PBTE Numeric-Input Availability Gate",
        r"""
## Ding PBTE Numeric-Input Availability Gate

Run:

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_ding_pbte_numeric_input_availability.py
```

Artifact:

- `docs/core/07_artifacts/topic13/t13_ding_pbte_numeric_input_availability_audit.json`

Acceptance requires archived hash/size parity, OA identity/license/retraction checks, a complete non-truncated 11-object prefix, media-role classification, absence of reproduction payload candidates, the author-request statement, published computational-detail locators, an explicit missing-input list, and holdout non-access. A pass closes only the captured official-OA source route.
""",
    )
    ledger_changed = append_once(
        WORK_LEDGER,
        "## Topic 13 Ding OA Numeric-Input No-Go",
        """
## Topic 13 Ding OA Numeric-Input No-Go

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` artifacts
- changed: archived official PMC OA inventory records and added scoped input-availability no-go, gate/register integration, tests, and source-acquisition decision
- verification: complete 11-object prefix; no reproducible PBTE numeric payload candidate; availability statement routes data to author request; holdout remains unread
- public-safety status: `partial`; OA source identities are safe, but author-held data and independent reproduction inputs remain open
- current claim boundary: `T13_DING_PBTE_OA_NUMERIC_INPUT_NO_GO` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13 files and artifacts remain in the worktree; unrelated Topic 0.22/0.25 work was not edited
- next action: author request or independent open graphite phonon reproduction package
""",
    )
    print(
        {
            "update_log_changed": update_changed,
            "data_manifest_changed": manifest_changed,
            "limitations_changed": limitations_changed,
            "verification_spec_changed": verification_changed,
            "work_ledger_changed": ledger_changed,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
