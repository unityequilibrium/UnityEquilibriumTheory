"""Synchronize the Topic 13 source-independence wave into durable logs."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
DATA_MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
WORK_LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-11.md"
MARKER = "### 2026-08-11 - Georgia Tech volumetric-property source-independence no-go"


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
    marker = "| Georgia Tech graphite c_p source and dependency no-go |"
    if marker in text:
        return False
    anchor = (
        "|:--|:--|:--|:--|--:|:--|:--|:--|" + newline
    )
    if anchor not in text:
        raise RuntimeError("Data-manifest table header anchor not found")
    row = (
        "| Georgia Tech graphite c_p source and dependency no-go | "
        "`Data/03_Research/gatech_gen3csp_graphite_source_package.json`; "
        "`docs/core/07_artifacts/topic13/t13_gatech_volumetric_cp_independence_audit.json` | "
        "Georgia Tech Gen3 CSP graphite page, uncertainty method, and archived `Graphite.xlsx` row A3:G3 | "
        "`c_p` J g^-1 K^-1; D mm^2 s^-1; k W m^-1 K^-1; assumed density g cm^-3 | "
        "11234 raw bytes | raw `baa7f6181fa3d5521fc594cb2c832308927bc77dbac89c43b373bc304eaa6900`; "
        "package `2635be1d91f35c9be6fd36d14a9e4d04384f158dd90340b59c5d7fa3f277bd51`; "
        "audit `7e9e858548cac1843c6bf5d405aeb192226ea79ef69a7dd5c3dc1e55d3cf8c6e` | "
        "Independent `c_p` source anchor and source-dependency audit; no calibration consumed | "
        "`PASS_SOURCE_CP_95CI_CV_OPEN` plus `PASS_SCOPED_SOURCE_INDEPENDENCE_NO_GO`; reported k is derived from D, c_p, and assumed density, so direct volumetric `c_v` or independent same-grade inputs remain required. |"
        + newline
    )
    updated = text.replace(anchor, anchor + row, 1)
    write_preserving_format(DATA_MANIFEST, updated, has_bom)
    return True


def main() -> int:
    update_changed = append_once(
        UPDATE_LOG,
        MARKER,
        """
### 2026-08-11 - Georgia Tech volumetric-property source-independence no-go

- Scope: test whether the archived Georgia Tech `k`, diffusivity, and `c_p` row can independently close density or volumetric heat capacity.
- Added or changed: disclosed publisher interpolation and property origins in the source package; added the deterministic source-independence audit, gate/register synchronization, focused tests, and the major-result wave record.
- Verified with: source audit `PASS_SOURCE_CP_95CI_CV_OPEN`; no-go audit `PASS_SCOPED_SOURCE_INDEPENDENCE_NO_GO`; focused Topic 13 suite `27 passed`; Wave 1 integrity `PASS_WITH_BLOCKED_LANES`.
- Result closed: `T13_GATECH_VOLUMETRIC_CP_INDEPENDENCE_NO_GO` is `CLOSED_FOR_LANE`; `k/(D c_p)` recovers the assumed `1780 kg m^-3`, and `k/D` recovers `rho_assumed c_p`, so neither is independent evidence.
- Blocker narrowed: the immediate source controller is now `independent_same_grade_density_or_direct_volumetric_heat_capacity_missing` rather than an ambiguous same-workbook conversion route.
- Still open: direct volumetric `c_v` or independent same-grade density uncertainty, same-regime `alpha_V` and `K_T`, material mapping, `e0`, base `Phi -> Phi_E`, independent `alpha_Phi_K`, and full thermodynamic closure.
- Claim impact: no upgrade; Full Topic 13 remains `PARTIAL / BLOCKED`, Xie 2026 remains untouched, and global claim promotion remains false.
""",
    )
    manifest_changed = insert_manifest_row()
    ledger_changed = append_once(
        WORK_LEDGER,
        "## Topic 13 Georgia Tech Source-Independence No-Go",
        """
## Topic 13 Georgia Tech Source-Independence No-Go

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` artifacts
- changed: disclosed property origins, added the scoped no-go verifier, gate/register integration, regression tests, and major-result report
- verification: source-independence wave exit `0`; focused Topic 13 suite `27 passed`; Wave 1 integrity `PASS_WITH_BLOCKED_LANES`; holdout access remains false
- public-safety status: `partial`; source reuse terms and direct same-grade thermophysical inputs remain open
- current claim boundary: `T13_GATECH_VOLUMETRIC_CP_INDEPENDENCE_NO_GO` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13 files and generated artifacts remain in the worktree; unrelated Topic 0.22 changes were not touched
- next action: acquire direct volumetric `c_v` or independent same-grade density with uncertainty plus same-regime `alpha_V` and `K_T`
""",
    )
    print(
        {
            "update_log_changed": update_changed,
            "data_manifest_changed": manifest_changed,
            "work_ledger_changed": ledger_changed,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
