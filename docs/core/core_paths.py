"""Canonical path and import helpers for the UET core physical migration."""

from __future__ import annotations

import os
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_ROOT = REPO_ROOT / "docs" / "core"
LEGACY_ARTIFACT_ROOT = CORE_ROOT / "artifacts"
CANONICAL_ARTIFACT_ROOT = CORE_ROOT / "07_artifacts"

PROTECTED_CORE_ROOT_FILES = {
    "AGENTS.md",
    "README.md",
    "CORE_FILE_INDEX.md",
    "__init__.py",
    "core_paths.py",
    "core_compat.py",
}

_TOOLING_DIRS = {
    "Data": "data",
    "Legacy": "legacy",
    "Reporting": "reporting",
    "Runners": "runners",
}


def repo_root() -> Path:
    return REPO_ROOT


def core_root() -> Path:
    return CORE_ROOT


def normalize_relative(path: str | Path) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def is_markdown_redirect(path: str | Path) -> bool:
    value = Path(path)
    if value.suffix.lower() != ".md" or not value.exists():
        return False
    try:
        return value.read_text(encoding="utf-8").startswith("# Compatibility redirect")
    except (OSError, UnicodeDecodeError):
        return False


def is_python_shim(path: str | Path) -> bool:
    value = Path(path)
    if value.suffix.lower() != ".py" or not value.exists():
        return False
    try:
        text = value.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    # Match generated compatibility shims, not the helper implementation or its docs.
    forward_shim = re.search(r'(?m)^\s*_?forward_public_symbols\(globals\(\),\s*"docs\.core\.', text) is not None
    runpy_shim = re.search(r'(?m)^_CANONICAL_RELATIVE\s*=\s*"docs/', text) is not None and "runpy.run_path" in text
    return forward_shim or runpy_shim


def _artifact_domain(name: str) -> str:
    lower = name.lower()
    if lower.startswith(("t13_", "topic13_", "thermal_", "he4_")):
        return "topic13"
    if any(token in lower for token in ("gate", "foundation", "organization", "closure")):
        return "gates"
    if any(token in lower for token in ("provenance", "source", "manifest", "hash")):
        return "provenance"
    if any(token in lower for token in ("formula", "correspondence", "coarse", "ontology")):
        return "correspondence"
    if any(token in lower for token in ("verification", "validation", "audit", "proof")):
        return "verification"
    return "archive"


def _test_role(name: str, relative: str) -> str:
    lower = name.lower()
    if any(token in lower for token in ("formula", "derivative", "stationarity", "eos", "action", "noether")):
        return "equation"
    if any(token in lower for token in ("causal", "convergence", "stability", "numerical", "conservation", "energy")):
        return "numerical"
    if any(token in lower for token in ("artifact", "schema", "manifest", "registry", "organization")):
        return "artifact"
    if "validation" in relative.lower() or "parameter_engine" in relative.lower():
        return "regression"
    return "regression"


def _python_area(stem: str) -> str:
    lower = stem.lower()
    if lower.startswith(("uet_o2_", "standard_o2")):
        return "02_equations/o2"
    if lower.startswith(("uet_covariant", "covariant_")):
        return "02_equations/covariant"
    if lower.startswith(("uet_noether", "uet_lorentz")):
        return "02_equations/lorentz_noether"
    if lower.startswith("uet_matter_space_flux_"):
        return "02_equations/matter_space"
    if lower in {
        "uet_trace",
        "uet_matter_space",
        "uet_spatial",
        "uet_master_equation",
        "uet_matter_space_causal",
        "uet_matter_space_finite_cone",
        "uet_matter_space_characteristic",
        "uet_matter_space_split",
    }:
        return "02_equations/matter_space"
    if lower.startswith("mass_density"):
        return "03_lanes/mass_density"
    if lower.startswith(("photon", "quantum", "carrier", "impact", "observer", "relational")):
        return "03_lanes/carrier_observer"
    if lower.startswith(("persistence", "resource")):
        return "03_lanes/persistence"
    if lower.startswith(("thermal", "thermo", "he4", "uet_raman", "uet_reciprocal")):
        return "03_lanes/thermal"
    if lower.startswith("t13_"):
        return "03_lanes/topic13_support"
    return "99_review/unassigned_python"


def _markdown_area(name: str) -> str:
    lower = name.lower()
    if lower.startswith("t13_"):
        return "03_lanes/topic13_support"
    if lower.endswith("_update_log.md") or "update_log" in lower:
        return "08_history/update_logs"
    if any(token in lower for token in ("report", "audit", "thought_experiment", "note")):
        return "08_history/research_notes"
    if lower.startswith(("uet_research_dependency_graph", "uet_research_room", "core_file_", "core_research_")):
        return "00_governance"
    if lower.endswith(("_spec.md", "_contract.md")):
        return "01_contracts"
    return "01_contracts"


def canonical_path_for(legacy_path: str | Path) -> str:
    """Resolve one current path to its deterministic canonical target."""

    relative = normalize_relative(legacy_path)
    prefix = "docs/core/"
    if not relative.startswith(prefix):
        return relative
    tail = relative[len(prefix) :]
    if "/" not in tail and tail in PROTECTED_CORE_ROOT_FILES:
        return relative
    if tail.startswith((
        "00_governance/",
        "01_contracts/",
        "02_equations/",
        "03_lanes/",
        "04_proofs/",
        "05_tests/",
        "06_data/",
        "07_artifacts/",
        "08_history/",
        "99_review/",
    )):
        return relative
    if tail.startswith("02_Proof/"):
        if tail == "02_Proof/README.md":
            return relative
        return "docs/core/04_proofs/" + tail[len("02_Proof/") :]
    if tail.startswith("artifacts/"):
        name = Path(tail).name
        return f"docs/core/07_artifacts/{_artifact_domain(name)}/{name}"
    if tail == "data/scripts/README.md":
        return "docs/scripts/core/legacy/UET_SCRIPT_UTILITY_HUB.md"
    if tail.startswith("data/scripts/"):
        rest = Path(tail[len("data/scripts/") :])
        parts = list(rest.parts)
        if parts:
            parts[0] = _TOOLING_DIRS.get(parts[0], parts[0].lower())
        return "docs/scripts/core/" + "/".join(parts)
    if tail == "data/README.md":
        return relative
    if tail.startswith("data/external/"):
        return "docs/core/06_data/source_packages/" + tail[len("data/external/") :]
    if tail.startswith("data/"):
        rest = tail[len("data/") :]
        lower = rest.lower()
        if any(token in lower for token in ("derived", "input")):
            area = "derived_inputs"
        elif lower.endswith(("manifest.json", "provenance.json", "package.json", "audit.json")):
            area = "manifests"
        else:
            area = "source_packages"
        return f"docs/core/06_data/{area}/{rest}"
    if tail.startswith("test/"):
        rest = Path(tail[len("test/") :])
        role = _test_role(rest.name, str(rest))
        if rest.parts and rest.parts[0].lower() == "validation":
            return f"docs/core/05_tests/{role}/validation/{rest.name}"
        if len(rest.parts) == 1:
            return f"docs/core/05_tests/{role}/root/{rest.name}"
        return f"docs/core/05_tests/{role}/{rest.as_posix()}"
    path = Path(tail)
    if path.suffix.lower() == ".py":
        return f"docs/core/{_python_area(path.stem)}/{path.name}"
    if path.suffix.lower() == ".md":
        return f"docs/core/{_markdown_area(path.name)}/{path.name}"
    if path.suffix.lower() in {".json", ".npz", ".csv", ".tsv", ".sqlite", ".pdf", ".html"}:
        return f"docs/core/99_review/unresolved_assets/{path.name}"
    return f"docs/core/99_review/unresolved_assets/{path.name}"


def canonical_module_name(canonical_path: str | Path) -> str:
    relative = normalize_relative(canonical_path)
    if not relative.endswith(".py"):
        raise ValueError(f"not a Python module: {canonical_path}")
    return relative[:-3].replace("/", ".")


def canonical_module_path(legacy_path: str | Path) -> str:
    return canonical_module_name(canonical_path_for(legacy_path))


def canonical_artifact_path(name: str | Path, domain: str | None = None) -> Path:
    filename = Path(name).name
    return CANONICAL_ARTIFACT_ROOT / (domain or _artifact_domain(filename)) / filename


def canonical_data_path(relative: str | Path) -> Path:
    return REPO_ROOT / canonical_path_for(f"docs/core/data/{normalize_relative(relative)}")


def canonical_test_path(relative: str | Path) -> Path:
    return REPO_ROOT / canonical_path_for(f"docs/core/test/{normalize_relative(relative)}")


def relative_path(from_path: str | Path, to_path: str | Path) -> str:
    return Path(os.path.relpath(Path(to_path), start=Path(from_path).parent)).as_posix()
