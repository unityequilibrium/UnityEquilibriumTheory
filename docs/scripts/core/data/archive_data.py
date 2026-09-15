"""
Copy archived data to topics folders
=====================================
Since network download failed, copy from local archive.
"""

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

import shutil
from pathlib import Path

# scripts/Maintenance -> docs -> root
current_file = Path(__file__).resolve()
PROJECT_ROOT = _UET_REPO_ROOT / "docs"
# (search Only) ทองข้อมูลดี is at root
ARCHIVE = PROJECT_ROOT / "(search Only) ทองข้อมูลดี" / "v0.9.0+" / "data"

# Destination
# docs/topics
TOPICS = _UET_REPO_ROOT / "docs" / "topics"

# Mapping: archive folder -> topic folder
COPY_MAP = [
    # Astrophysics
    (
        "02_astrophysics/cosmology/NGC6503_rotmod.dat",
        "0.1_Galaxy_Rotation_Problem/Real data source/galaxy_rotation_175/NGC6503_rotmod.dat",
    ),
    (
        "02_astrophysics/cosmology/planck2018_parameters.json",
        "0.3_Cosmology_Hubble_Tension/Data/hubble_tension/planck2018_parameters.json",
    ),
    (
        "02_astrophysics/cosmology/farrah_highz_sample.csv",
        "0.3_Cosmology_Hubble_Tension/Data/hubble_tension/farrah_highz_sample.csv",
    ),
    (
        "02_astrophysics/little_things_data.py",
        "0.1_Galaxy_Rotation_Problem/Data/little_things/little_things_data.py",
    ),
    (
        "02_astrophysics/black_hole_data.py",
        "0.2_Black_Hole_Physics/Data/black_holes/black_hole_data.py",
    ),
    # Condensed Matter
    (
        "03_condensed_matter/real_superconductor_data.json",
        "0.4_Superconductivity_Superfluids/Data/superconductivity_tc/real_superconductor_data.json",
    ),
    (
        "03_condensed_matter/casimir_force_data.json",
        "0.12_Vacuum_Energy_Casimir/Data/casimir_effect/casimir_force_data.json",
    ),
    (
        "03_condensed_matter/superfluid_data.py",
        "0.4_Superconductivity_Superfluids/Data/superfluids/superfluid_data.py",
    ),
    # Particle Physics
    (
        "01_particle_physics/particle_masses.py",
        "0.6_Electroweak_Physics/Data/particles/particle_masses.py",
    ),
    (
        "01_particle_physics/qcd_strong_force_data.py",
        "0.5_Nuclear_Binding_Hadrons/Data/qcd/qcd_strong_force_data.py",
    ),
    (
        "01_particle_physics/weak_force_data.py",
        "0.6_Electroweak_Physics/Data/weak_force/weak_force_data.py",
    ),
    (
        "01_particle_physics/neutrino_extended_data.py",
        "0.7_Neutrino_Physics/Data/neutrino/neutrino_extended_data.py",
    ),
    # Quantum
    ("04_quantum", "0.9_Quantum_Nonlocality/Data/quantum"),
]


def copy_data():
    """Copy data from archive to topics."""
    print("=" * 60)
    print("COPYING DATA FROM ARCHIVE TO TOPICS")
    print("=" * 60)
    print(f"\nSource: {ARCHIVE}")
    print(f"Destination: {TOPICS}")
    print()

    copied = 0
    skipped = 0

    for src_rel, dst_rel in COPY_MAP:
        src = ARCHIVE / src_rel
        dst = TOPICS / dst_rel

        if not src.exists():
            print(f"⚠️  Source not found: {src_rel}")
            skipped += 1
            continue

        # Create parent dirs
        dst.parent.mkdir(parents=True, exist_ok=True)

        try:
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"✅ {src_rel} -> {dst_rel}")
            copied += 1
        except Exception as e:
            print(f"❌ {src_rel}: {e}")
            skipped += 1

    print()
    print("=" * 60)
    print(f"SUMMARY: Copied {copied}, Skipped {skipped}")
    print("=" * 60)


if __name__ == "__main__":
    copy_data()
