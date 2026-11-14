"""
Wave 29 structure-factor calibration source-support gate.

Wave 28 showed that the structure-factor / axis-estimator ratio is stable
enough to study, but still uncalibrated. This verifier checks whether the
current local 0.11 source package can support that calibration, or whether the
next work must first package source-backed estimator theory or repair the
simulation window/dynamics.

This is source triage only. It does not download papers, accept a calibration
factor, rescale any estimator, or promote exponent/universality claims.
"""

from __future__ import annotations

import json
import platform
import re
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET docs root not found")


ROOT = _bootstrap()
TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
REF_DIR = TOPIC_DIR / "Ref"
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_calibration_source_support_gate.json"

WAVE28_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_estimator_reconciliation_gate.json"

LOCAL_SOURCE_TEXT_GLOBS = ("*.md", "*.py", "*.json", "*.txt")
REQUIRED_ESTIMATOR_PATTERNS = {
    "structure_factor": re.compile(r"structure[-_\s]?factor", re.IGNORECASE),
    "second_moment_correlation_length": re.compile(
        r"second[-\s]?moment.{0,80}correlation[-\s]?length|correlation[-\s]?length.{0,80}second[-\s]?moment",
        re.IGNORECASE,
    ),
    "fourier_estimator": re.compile(r"Fourier|S\(k\)|S\(q\)|k_min|wave[-\s]?vector", re.IGNORECASE),
    "finite_size_admissibility": re.compile(
        r"finite[-\s]?size.{0,80}(admiss|scal|correlation)|L\s*/\s*xi|xi\s*/\s*L",
        re.IGNORECASE,
    ),
}

EXTERNAL_PRIMARY_SOURCE_CANDIDATES = [
    {
        "id": "hasenbusch_2010_3d_ising_fss",
        "title": "A Finite Size Scaling Study of Lattice Models in the three-dimensional Ising Universality Class",
        "url": "https://arxiv.org/abs/1004.4486",
        "role": "primary finite-size-scaling and 3D Ising correlation-length benchmark candidate",
        "local_packaged": False,
        "support_boundary": "Supports finite-size scaling with correlation length as an observable; does not source the UET empirical calibration factor.",
    },
    {
        "id": "lundow_campbell_2017_ising_corrections",
        "title": "The Ising universality class in dimension three: corrections to scaling",
        "url": "https://arxiv.org/abs/1710.03574",
        "role": "primary 3D Ising corrections-to-scaling and reduced second-moment correlation-length candidate",
        "local_packaged": False,
        "support_boundary": "Supports reduced second-moment correlation-length usage; does not accept the current RMS inverse-k proxy or calibration factor.",
    },
    {
        "id": "jones_young_2004_fss_correlation_length",
        "title": "Finite size scaling of the correlation length above the upper critical dimension",
        "url": "https://arxiv.org/abs/cond-mat/0412150",
        "role": "finite-size correlation-length cautionary benchmark candidate",
        "local_packaged": False,
        "support_boundary": "Supports caution that correlation-length finite-size scaling can change with regime; not a calibration source for this estimator.",
    },
]


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_record(path: Path, role: str) -> dict[str, Any]:
    exists = path.exists()
    data = load_json(path) if exists else {}
    return {
        "path": relpath(path),
        "role": role,
        "exists": exists,
        "sha256": hash_file(path) if exists else None,
        "status": data.get("status"),
        "blocker_label": data.get("blocker_label"),
        "claim_class": data.get("claim_class"),
    }


def iter_local_source_text_files() -> list[Path]:
    files: list[Path] = []
    for pattern in LOCAL_SOURCE_TEXT_GLOBS:
        files.extend(REF_DIR.rglob(pattern))
    return sorted(path for path in files if path.is_file())


def scan_local_sources() -> dict[str, Any]:
    source_files = iter_local_source_text_files()
    matches: dict[str, list[dict[str, Any]]] = {key: [] for key in REQUIRED_ESTIMATOR_PATTERNS}
    for path in source_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for key, pattern in REQUIRED_ESTIMATOR_PATTERNS.items():
            found = pattern.search(text)
            if found:
                start = max(found.start() - 80, 0)
                end = min(found.end() + 80, len(text))
                matches[key].append(
                    {
                        "path": relpath(path),
                        "sha256": hash_file(path),
                        "snippet": " ".join(text[start:end].split()),
                    }
                )
    pdfs = sorted(REF_DIR.rglob("*.pdf"))
    return {
        "text_source_count": len(source_files),
        "pdf_source_count": len(pdfs),
        "text_sources": [
            {
                "path": relpath(path),
                "sha256": hash_file(path),
                "bytes": path.stat().st_size,
            }
            for path in source_files
        ],
        "pdf_sources": [
            {
                "path": relpath(path),
                "sha256": hash_file(path),
                "bytes": path.stat().st_size,
            }
            for path in pdfs
        ],
        "matches": matches,
    }


def run_source_support_gate() -> dict[str, Any]:
    wave28 = load_json(WAVE28_ARTIFACT_PATH) if WAVE28_ARTIFACT_PATH.exists() else {}
    local_scan = scan_local_sources()
    wave28_metrics = wave28.get("metrics", {})
    candidate_factor = wave28_metrics.get("candidate_calibration_factor")

    local_required_match_counts = {
        key: len(value) for key, value in local_scan["matches"].items()
    }
    local_has_all_required = all(count > 0 for count in local_required_match_counts.values())
    local_has_any_estimator_support = any(count > 0 for count in local_required_match_counts.values())

    wave28_chain_gate = {
        "status": (
            "PASS"
            if wave28.get("blocker_label")
            == "structure_factor_estimator_ratio_stable_but_uncalibrated_and_lengths_decline"
            else "BLOCKED"
        ),
        "required_condition": "Wave 29 must start from the Wave 28 stable-but-uncalibrated estimator blocker.",
        "wave28_status": wave28.get("status"),
        "wave28_blocker_label": wave28.get("blocker_label"),
    }
    local_source_packaging_gate = {
        "status": "PASS" if local_has_all_required else "BLOCKED",
        "required_condition": "Local refs must contain text-source support for structure factor, second-moment correlation length, Fourier estimator definition, and finite-size admissibility before accepting calibration.",
        "required_match_counts": local_required_match_counts,
        "text_source_count": local_scan["text_source_count"],
        "pdf_source_count": local_scan["pdf_source_count"],
        "claim_boundary": "PDF presence alone is not source support unless the relevant estimator relation is extracted or cited in a manifest.",
    }
    external_candidate_gate = {
        "status": "WARN",
        "required_condition": "External primary candidates may guide the next source-packaging pass, but they are not accepted until stored or manifest-linked with role, DOI/URL, and formula boundary.",
        "candidate_count": len(EXTERNAL_PRIMARY_SOURCE_CANDIDATES),
        "candidates": EXTERNAL_PRIMARY_SOURCE_CANDIDATES,
    }
    empirical_calibration_factor_gate = {
        "status": "BLOCKED",
        "required_condition": "The observed calibration factor may not be used unless a source-backed benchmark or derivation justifies it.",
        "candidate_calibration_factor": candidate_factor,
        "source_support": None,
        "claim_boundary": "A stable observed ratio is not an accepted calibration constant.",
    }
    formula_alignment_gate = {
        "status": "BLOCKED",
        "required_condition": "The current RMS inverse-k proxy must be mapped to a source-backed second-moment or finite-size estimator before exponent fitting.",
        "current_formula": "xi_sf = 2*pi / sqrt(sum(S(k)*k^2)/sum(S(k))) over nonzero FFT modes",
        "source_backed_formula_available_locally": local_has_any_estimator_support and local_has_all_required,
        "mismatch_boundary": "Local sources do not yet justify the current RMS inverse-k proxy as an accepted critical correlation length.",
    }
    next_path_decision_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until either source packaging accepts a correlation-length estimator or the simulation window/dynamics repairs absolute-length growth.",
        "next_controller": (
            "package_primary_second_moment_estimator_sources_before_calibration"
            if not local_has_all_required
            else "derive_formula_mapping_or_repair_absolute_length_growth"
        ),
        "recommended_paths": [
            "Package primary sources for second-moment/finite-size correlation-length estimators with DOI/URL and formula boundary.",
            "Derive a mapping from the current RMS inverse-k proxy to a source-backed estimator, if possible.",
            "If no mapping is defensible, repair the simulation window/dynamics so both estimator families show nondecreasing absolute lengths.",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Source support triage cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 29 only shows that local source packaging is insufficient for calibration acceptance.",
    }

    if wave28_chain_gate["status"] != "PASS":
        blocker_label = "structure_factor_source_support_chain_missing"
    elif local_source_packaging_gate["status"] != "PASS":
        blocker_label = "structure_factor_calibration_source_support_missing_locally"
    else:
        blocker_label = "structure_factor_calibration_source_support_formula_mapping_open"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 29 structure-factor calibration source-support gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Calibration_Source_Support_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "source_support_triage_only",
        "inputs": [
            artifact_record(WAVE28_ARTIFACT_PATH, "Wave 28 stable-but-uncalibrated estimator controller"),
            {
                "path": relpath(REF_DIR),
                "role": "local 0.11 reference package scanned for estimator support",
                "exists": REF_DIR.exists(),
            },
        ],
        "metrics": {
            "candidate_calibration_factor": candidate_factor,
            "local_required_match_counts": local_required_match_counts,
            "local_matches": local_scan["matches"],
            "text_source_count": local_scan["text_source_count"],
            "pdf_source_count": local_scan["pdf_source_count"],
        },
        "local_sources": {
            "text_sources": local_scan["text_sources"],
            "pdf_sources": local_scan["pdf_sources"],
        },
        "external_primary_source_candidates": EXTERNAL_PRIMARY_SOURCE_CANDIDATES,
        "gates": {
            "wave28_chain_gate": wave28_chain_gate,
            "local_source_packaging_gate": local_source_packaging_gate,
            "external_candidate_gate": external_candidate_gate,
            "empirical_calibration_factor_gate": empirical_calibration_factor_gate,
            "formula_alignment_gate": formula_alignment_gate,
            "next_path_decision_gate": next_path_decision_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This verifier scans local text metadata and records PDF hashes; it does not parse or validate every PDF formula.",
            "External primary-source candidates are recorded as candidates only until they are packaged with formula roles and claim boundaries.",
            "No calibration factor, estimator formula, exponent, material, RG, or universality claim is accepted by this source triage.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims. Wave 29 keeps the next controller at source packaging or window/dynamics repair.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_source_support_gate()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "artifact": relpath(ARTIFACT_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )
