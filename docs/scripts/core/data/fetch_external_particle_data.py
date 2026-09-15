"""Fetch source-locked external data for particle-physics topics.

The script downloads upstream artifacts into docs/data/external/particle_physics
and writes a manifest with hashes. It intentionally distinguishes source-locked
raw artifacts from benchmark-ready parsed datasets.
"""

from __future__ import annotations

# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP

import hashlib
import json
import time
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


REPO_ROOT = _UET_REPO_ROOT / "docs"
OUT_ROOT = REPO_ROOT / "docs" / "data" / "external" / "particle_physics"
MANIFEST_PATH = OUT_ROOT / "external_particle_sources_manifest.json"


@dataclass(frozen=True)
class SourceSpec:
    dataset_id: str
    topic: str
    source_name: str
    url: str
    fallback_urls: tuple[str, ...]
    local_relpath: str
    expected_min_bytes: int
    source_type: str
    benchmark_ready: bool
    notes: str


SOURCES: tuple[SourceSpec, ...] = (
    SourceSpec(
        dataset_id="pdg_2025_sqlite",
        topic="0.5-0.8",
        source_name="Particle Data Group API SQLite database 2025",
        url="https://pdg.lbl.gov/2025/api/pdg-2025-v0.2.2.sqlite",
        fallback_urls=(),
        local_relpath="pdg/pdg-2025-v0.2.2.sqlite",
        expected_min_bytes=1_000_000,
        source_type="sqlite",
        benchmark_ready=True,
        notes="Machine-readable PDG database for particle properties and Standard Model constants.",
    ),
    SourceSpec(
        dataset_id="pdgall_2025_sqlite",
        topic="0.5-0.8",
        source_name="Particle Data Group API SQLite database 2025 with historical summary data",
        url="https://pdg.lbl.gov/2025/api/pdgall-2025-v0.2.2.sqlite",
        fallback_urls=(),
        local_relpath="pdg/pdgall-2025-v0.2.2.sqlite",
        expected_min_bytes=1_000_000,
        source_type="sqlite",
        benchmark_ready=True,
        notes="Machine-readable PDG database including historical Summary Table values.",
    ),
    SourceSpec(
        dataset_id="ame2020_mass_1",
        topic="0.5",
        source_name="AME2020 atomic mass table",
        url="https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20",
        fallback_urls=(
            "http://amdc.impcas.ac.cn/ame2020/mass_1.mas20",
            "https://people.physics.anu.edu.au/~ecs103/chart/mass_1.mas20",
        ),
        local_relpath="ame2020/mass_1.mas20",
        expected_min_bytes=100_000,
        source_type="fixed_width_text",
        benchmark_ready=False,
        notes="Raw AME mass table. Requires parser and binding-energy extraction before benchmark use.",
    ),
    SourceSpec(
        dataset_id="nufit_6_0_article_pdf",
        topic="0.7",
        source_name="NuFIT 6.0 JHEP article PDF",
        url="https://link.springer.com/content/pdf/10.1007/JHEP12(2024)216.pdf",
        fallback_urls=(),
        local_relpath="nufit/NuFIT_6_0_JHEP12_2024_216.pdf",
        expected_min_bytes=100_000,
        source_type="pdf",
        benchmark_ready=False,
        notes="Open-access paper source. Numeric tables must be extracted or replaced by official table files if available.",
    ),
    SourceSpec(
        dataset_id="fermilab_muon_g2_2025_press_release",
        topic="0.8",
        source_name="Fermilab Muon g-2 final 2025 press release",
        url="https://news.fnal.gov/2025/06/muon-g-2-most-precise-measurement-of-muon-magnetic-anomaly/",
        fallback_urls=(),
        local_relpath="muon_g2/fermilab_muon_g2_2025_press_release.html",
        expected_min_bytes=10_000,
        source_type="html",
        benchmark_ready=False,
        notes="Official final-result source document. Needs publication/table extraction for numerical benchmark update.",
    ),
    SourceSpec(
        dataset_id="doe_muon_g2_2025_press_release",
        topic="0.8",
        source_name="DOE Muon g-2 final 2025 press release mirror",
        url="https://www.energy.gov/science/articles/muon-g-2-announces-most-precise-measurement-magnetic-anomaly-muon-0",
        fallback_urls=(),
        local_relpath="muon_g2/doe_muon_g2_2025_press_release.html",
        expected_min_bytes=10_000,
        source_type="html",
        benchmark_ready=False,
        notes="DOE mirror of Fermilab final-result release, useful as redundant provenance.",
    ),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_source(spec: SourceSpec) -> dict:
    target = OUT_ROOT / spec.local_relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    status = "downloaded"
    error = None

    attempted_urls = []
    try:
        payload = None
        last_error = None
        for url in (spec.url, *spec.fallback_urls):
            attempted_urls.append(url)
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "UET research data audit/1.0 (source provenance checker)"},
            )
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    payload = response.read()
                break
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        if payload is None:
            raise last_error or RuntimeError("no payload downloaded")
        target.write_bytes(payload)
        size = target.stat().st_size
        if size < spec.expected_min_bytes:
            status = "downloaded_but_too_small"
    except Exception as exc:  # noqa: BLE001
        status = "failed"
        error = str(exc)
        size = target.stat().st_size if target.exists() else 0

    record = {
        **asdict(spec),
        "local_path": str(target.relative_to(REPO_ROOT)),
        "status": status,
        "bytes": size,
        "sha256": sha256_file(target) if target.exists() and size > 0 else None,
        "duration_seconds": round(time.time() - started, 3),
        "error": error,
        "attempted_urls": attempted_urls,
    }
    print(f"{spec.dataset_id}: {status} bytes={size}")
    if error:
        print(f"  error: {error}")
    return record


def write_manifest(records: Iterable[dict]) -> None:
    records = list(records)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "generated_by": "docs/scripts/data/fetch_external_particle_data.py",
        "policy": "Downloaded file plus hash is source-locked, not automatically benchmark-ready.",
        "records": records,
    }
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote manifest: {MANIFEST_PATH}")


def main() -> int:
    records = [fetch_source(spec) for spec in SOURCES]
    write_manifest(records)
    failures = [record for record in records if record["status"] == "failed"]
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
