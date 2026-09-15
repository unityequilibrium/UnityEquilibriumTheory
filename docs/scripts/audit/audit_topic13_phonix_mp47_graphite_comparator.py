"""Audit the source-locked Phonix mp-47 graphite comparator.

The Phonix summary row is useful for an independent graphite harmonic
comparator, but its DOS is reported in arbitrary units and it does not expose
the Ding PBTE C_src inputs or a standard uncertainty.  This audit therefore
locks provenance and field-level boundaries without emitting a volumetric
heat capacity, alpha_Phi_K, or a Ding-regime reproduction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
RAW = DATA / "raw/phonix_mp47_graphite_summary_row.json"
PACKAGE = DATA / "phonix_mp47_graphite_source_package.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_phonix_mp47_graphite_comparator_audit.json"

DATASET = "phonix-db/phonix-summary"
EXPECTED_REVISION = "284bddebbd144ae3e3f93474dc05e4658417d09f"
REVISION_URL = (
    "https://huggingface.co/api/datasets/phonix-db/phonix-summary/revision/main"
)
SEARCH_URL = (
    "https://datasets-server.huggingface.co/search?"
    + urllib.parse.urlencode(
        {
            "dataset": DATASET,
            "config": "default",
            "split": "train",
            "query": "mp-47",
            "offset": 0,
            "length": 100,
        }
    )
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "UET-Topic13-Source-Audit/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object from {url}")
    return payload


def parse_array(row: dict[str, Any], field: str) -> list[float]:
    value = row.get(field)
    if not isinstance(value, str):
        raise ValueError(f"{field} must remain the source string representation")
    parsed = json.loads(value)
    if not isinstance(parsed, list) or not parsed:
        raise ValueError(f"{field} must decode to a non-empty array")
    values = [float(item) for item in parsed]
    if not all(math.isfinite(item) for item in values):
        raise ValueError(f"{field} contains a non-finite value")
    return values


def trapezoid(values: list[float], x: list[float]) -> float:
    if len(values) != len(x) or len(values) < 2:
        raise ValueError("trapezoid input lengths are invalid")
    return sum(
        0.5 * (values[index] + values[index + 1]) * (x[index + 1] - x[index])
        for index in range(len(values) - 1)
    )


def refresh_snapshot() -> None:
    revision = fetch_json(REVISION_URL)
    revision_sha = revision.get("sha")
    if revision_sha != EXPECTED_REVISION:
        raise RuntimeError(
            f"Phonix revision drifted: expected {EXPECTED_REVISION}, got {revision_sha}"
        )
    search = fetch_json(SEARCH_URL)
    rows = [
        item.get("row")
        for item in search.get("rows", [])
        if isinstance(item, dict) and isinstance(item.get("row"), dict)
    ]
    matches = [row for row in rows if row.get("mp_id") == "mp-47"]
    if len(matches) != 1:
        raise RuntimeError(f"expected one mp-47 row, got {len(matches)}")
    snapshot = {
        "schema_version": "t13-phonix-mp47-raw-snapshot-v1",
        "source_identity": {
            "dataset": DATASET,
            "dataset_revision": EXPECTED_REVISION,
            "revision_url": REVISION_URL,
            "query_url": SEARCH_URL,
            "row_locator": {"split": "train", "row_key": "mp-47", "mp_id": "mp-47"},
        },
        "captured_at": date.today().isoformat(),
        "row": matches[0],
    }
    raw_bytes = json.dumps(snapshot, indent=2, ensure_ascii=True).encode("utf-8") + b"\n"
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_bytes(raw_bytes)
    package = build_package(snapshot, sha256_bytes(raw_bytes))
    PACKAGE.write_text(json.dumps(package, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_package(snapshot: dict[str, Any], raw_sha256: str) -> dict[str, Any]:
    row = snapshot["row"]
    return {
        "schema_version": "t13-phonix-mp47-graphite-source-package-v1",
        "artifact": "phonix_mp47_graphite_source_package",
        "status": "SOURCE_LOCKED_COMPARATOR_ONLY",
        "source": {
            "provider": "Phonix database",
            "dataset": DATASET,
            "dataset_revision": EXPECTED_REVISION,
            "revision_url": REVISION_URL,
            "query_url": SEARCH_URL,
            "row_locator": {
                "split": "train",
                "mp_id": "mp-47",
                "unique_id": row.get("unique_id"),
                "formula": row.get("formula"),
                "space_group_number": row.get("spg_number"),
            },
            "local_raw_path": RAW.relative_to(ROOT).as_posix(),
            "local_raw_sha256": raw_sha256,
            "row_payload_sha256": sha256_bytes(canonical_json(row)),
            "license": "CC BY 4.0",
        },
        "material": {
            "formula": row.get("formula"),
            "space_group": "P6_3/mmc (No. 194)",
            "primitive_atoms": row.get("natoms_prim"),
            "source_volume_A3": row.get("volume[A^3]"),
            "source_structure": json.loads(row["structure"]),
            "Ding_TTG_material_equivalence": "NOT_ESTABLISHED",
            "regime_boundary": "ideal periodic graphite database row; not Ding natural-graphite TTG specimen",
        },
        "fields": {
            "phfreq[cm^-1]": "source string encoding of frequency-bin centers",
            "phdos[a.u.]": "source arbitrary-unit DOS values; normalization to modes per cm^-1 is not declared",
            "volume[A^3]": "primitive-cell volume in cubic Angstrom",
            "qmesh": "dimensionless reciprocal mesh label",
            "fc2_error[%]": "force-constant fitting diagnostic percent, not a standard uncertainty",
            "fc3_error[%]": "third-order force-constant fitting diagnostic percent, not a standard uncertainty",
            "kappa[W/mK]": "reported thermal-conductivity output at the dataset declared temperature scope",
        },
        "preprocessing": {
            "source_values_changed": False,
            "row_selection": "select exact mp_id=mp-47 from the immutable source snapshot",
            "array_decode": "JSON-decode phfreq[cm^-1] and phdos[a.u.] source strings only",
            "derived_check": "trapezoid integration of the source DOS is reported in source units only",
            "interpolation": False,
            "curve_digitization": False,
            "target_fit": False,
            "alpha_fit": False,
        },
        "uncertainty": {
            "standard_uncertainty_available": False,
            "measurement_uncertainty_available": False,
            "reported_force_constant_fit_errors_are_uncertainty": False,
            "epistemic_boundary": "No standard uncertainty is invented for DOS normalization, derived c_v, or Ding material equivalence.",
        },
        "data_role": "TRAINING/COMPARISON",
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_used_for_fit": False,
            "xie_2026_used_for_tuning": False,
        },
        "claim_boundary": "Source-locked Phonix graphite harmonic comparator only; not Ding PBTE C_src, not a volumetric c_v uncertainty source, not UET transport, and not alpha_Phi_K calibration.",
    }


def audit() -> dict[str, Any]:
    if not RAW.is_file() or not PACKAGE.is_file():
        raise FileNotFoundError("run with --refresh once to create the Phonix source snapshot")
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    row = raw.get("row")
    if not isinstance(row, dict):
        raise ValueError("raw snapshot row is not an object")
    frequencies = parse_array(row, "phfreq[cm^-1]")
    dos = parse_array(row, "phdos[a.u.]")
    spacing = [frequencies[index + 1] - frequencies[index] for index in range(len(frequencies) - 1)]
    dos_integral = trapezoid(dos, frequencies)
    checks = {
        "raw_snapshot_present": RAW.is_file(),
        "package_present": PACKAGE.is_file(),
        "dataset_revision_locked": raw.get("source_identity", {}).get("dataset_revision") == EXPECTED_REVISION,
        "package_revision_locked": package.get("source", {}).get("dataset_revision") == EXPECTED_REVISION,
        "raw_hash_matches_package": package.get("source", {}).get("local_raw_sha256") == sha256_path(RAW),
        "row_identity_is_mp47": row.get("mp_id") == "mp-47" and row.get("unique_id") == "mp-47",
        "graphite_formula_and_space_group": row.get("formula") == "C" and row.get("spg_number") == 194,
        "primitive_cell_contract": row.get("natoms_prim") == 4.0 and float(row.get("volume[A^3]", 0.0)) > 0.0,
        "frequency_dos_lengths_match": len(frequencies) == len(dos) and len(frequencies) == 51,
        "frequency_grid_is_uniform": bool(spacing) and max(abs(value - spacing[0]) for value in spacing) <= 1.0e-9,
        "dos_values_are_nonnegative": all(value >= 0.0 for value in dos),
        "dos_integral_is_finite_positive": math.isfinite(dos_integral) and dos_integral > 0.0,
        "source_dos_units_remain_arbitrary": package.get("fields", {}).get("phdos[a.u.]", "").startswith("source arbitrary-unit"),
        "standard_uncertainty_not_invented": package.get("uncertainty", {}).get("standard_uncertainty_available") is False,
        "ding_equivalence_not_asserted": package.get("material", {}).get("Ding_TTG_material_equivalence") == "NOT_ESTABLISHED",
        "numeric_c_v_not_emitted": True,
        "numeric_c_src_not_emitted": True,
        "numeric_alpha_Phi_K_not_emitted": True,
        "holdout_not_accessed": package.get("holdout_policy", {}).get("xie_2026_accessed") is False,
        "target_fit_not_performed": package.get("preprocessing", {}).get("target_fit") is False,
        "alpha_fit_not_performed": package.get("preprocessing", {}).get("alpha_fit") is False,
    }
    passed = all(checks.values())
    result = {
        "schema_version": "t13-phonix-mp47-graphite-comparator-v1",
        "artifact": "t13_phonix_mp47_graphite_comparator_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_PHONIX_GRAPHITE_HARMONIC_COMPARATOR" if passed else "FAIL_PHONIX_GRAPHITE_COMPARATOR_AUDIT",
        "major_result": {
            "major_result_id": "T13_PHONIX_MP47_GRAPHITE_HARMONIC_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "an immutable Phonix summary snapshot identifies mp-47 as a P6_3/mmc graphite row with declared primitive volume, q-mesh, phonon frequency bins, DOS bins, and force-constant diagnostics",
                "the source row passes identity, array-shape, grid, sign, hash, and provenance checks",
                "the source boundary explicitly separates arbitrary-unit DOS and fit diagnostics from standard c_v uncertainty",
            ],
            "equation_or_mapping": {
                "harmonic_kernel_boundary": "c_mu(T) = k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2; x_mu=h*nu_mu/(k_B*T)",
                "source_dos_integral": "I_DOS = integral[phdos_source(nu) dnu] (source units only)",
                "Ding_boundary": "No C_src(T) = sum_mu c_mu(T) is emitted because phdos is reported in a.u. and no Ding PBTE mode/scattering payload is present.",
            },
            "units": {
                "frequency": "cm^-1",
                "DOS": "a.u. (source-declared; no mode-per-frequency normalization asserted)",
                "volume": "A^3",
                "reported_source_integral": "a.u.*cm^-1",
                "c_v": "not emitted",
            },
            "derivation_class": "source-locked first-principles summary comparator with standard-kernel boundary audit",
            "observable": "graphite harmonic phonon DOS/source metadata",
            "data_role": "TRAINING/COMPARISON",
            "evidence_artifacts": [
                {"path": RAW.relative_to(ROOT).as_posix(), "sha256": sha256_path(RAW)},
                {"path": PACKAGE.relative_to(ROOT).as_posix(), "sha256": sha256_path(PACKAGE)},
            ],
            "verification_status": "PASS_SCOPED_PHONIX_GRAPHITE_HARMONIC_COMPARATOR" if passed else "FAIL_PHONIX_GRAPHITE_COMPARATOR_AUDIT",
            "open_blockers": [
                "phonix_summary_dos_units_a_u_not_unitful_c_v",
                "phonix_summary_standard_uncertainty_not_available",
                "ding_material_morphology_and_pbte_C_src_equivalence_missing",
                "base_Phi_SI_anchor_and_independent_alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "Source-locked Phonix mp-47 graphite harmonic comparator only; no Ding, alpha, transport, Core, Gravity, or Galaxy unlock.",
            "claim_boundary": "This closes a provenance and standard-harmonic-comparator lane. It is not Ding PBTE C_src, not a volumetric c_v uncertainty source, not UET transport, and not an alpha_Phi_K calibration.",
        },
        "source": {
            "dataset": DATASET,
            "dataset_revision": EXPECTED_REVISION,
            "row_locator": raw.get("source_identity", {}).get("row_locator"),
            "local_raw_path": RAW.relative_to(ROOT).as_posix(),
            "local_raw_sha256": sha256_path(RAW),
            "row_payload_sha256": package.get("source", {}).get("row_payload_sha256"),
            "source_volume_A3": row.get("volume[A^3]"),
            "primitive_atoms": row.get("natoms_prim"),
            "space_group_number": row.get("spg_number"),
            "qmesh": row.get("qmesh"),
            "fc2_error_percent": row.get("fc2_error[%]"),
            "fc3_error_percent": row.get("fc3_error[%]"),
            "standard_uncertainty_available": False,
            "ding_material_equivalence": "NOT_ESTABLISHED",
        },
        "derived_summary": {
            "frequency_bin_count": len(frequencies),
            "frequency_min_cm1": min(frequencies),
            "frequency_max_cm1": max(frequencies),
            "frequency_spacing_cm1": spacing[0],
            "dos_integral_source_units": dos_integral,
            "dos_normalization_to_modes_per_cm1": "NOT_ASSERTED",
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "alpha_fit_performed": False,
        "numeric_c_v_emitted": False,
        "numeric_C_src_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "phonix_summary_dos_units_and_uncertainty_not_sufficient_for_volumetric_cv",
        "next_controller": "Use the locked row as a phase-matched harmonic comparator only; obtain a unitful uncertainty-grade c_v or Ding-compatible PBTE C_src payload/reproduction with material-state mapping.",
        "claim_boundary": "Comparator provenance closure only; Full Topic 13 remains blocked.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="fetch and archive the immutable source row")
    args = parser.parse_args()
    if args.refresh:
        refresh_snapshot()
    result = audit()
    print(
        json.dumps(
            {
                "status": result["status"],
                "closure_level": result["major_result"]["closure_level"],
                "dos_integral_source_units": result["derived_summary"]["dos_integral_source_units"],
                "controlling_blocker": result["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
