"""
UET Golden Result Migrator (v1.0)
=================================
Restructures the messy Result system into the Paper-Ready Architecture:
- Root/Result/* -> topics/[Topic]/_Archive/*
- topics/[Topic]/Result/[Pillar]/* -> topics/[Topic]/Result/* (Flattened)
- Sets latest successful run as the 'Stable' result.

Author: Antigravity AI
Date: 2026-01-24
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

import os
import shutil
import time
from pathlib import Path

# --- CONFIG ---
# Script is in docs/scripts/
SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parent.parent.parent  # Move up to PROJECT ROOT
TOPICS_DIR = ROOT / "docs" / "topics"
GLOBAL_RESULT_DIR = ROOT / "docs" / "Result"

# Canonical Mapping (Same as UETPathManager)
TOPIC_MAP = {
    "0.1": "0.1_Galaxy_Rotation_Problem",
    "0.2": "0.2_Black_Hole_Physics",
    "0.3": "0.3_Cosmology_Hubble_Tension",
    "0.4": "0.4_Superconductivity_Superfluids",
    "0.5": "0.5_Nuclear_Binding_Hadrons",
    "0.6": "0.6_Electroweak_Physics",
    "0.7": "0.7_Neutrino_Physics",
    "0.8": "0.8_Muon_g2_Anomaly",
    "0.9": "0.9_Quantum_Nonlocality",
    "0.10": "0.10_Fluid_Dynamics_Chaos",
    "0.11": "0.11_Phase_Transitions",
    "0.12": "0.12_Vacuum_Energy_Casimir",
    "0.13": "0.13_Thermodynamic_Bridge",
    "0.14": "0.14_Complex_Systems",
    "0.15": "0.15_Cluster_Dynamics",
    "0.16": "0.16_Heavy_Nuclei",
    "0.17": "0.17_Mass_Generation",
    "0.18": "0.18_Quantum_Computing",
    "0.19": "0.19_Gravity_GR",
    "0.20": "0.20_Atomic_Physics",
    "0.21": "0.21_Yang_Mills_Mass_Gap",
    "0.22": "0.22_Biophysics_Origin_of_Life",
    "0.23": "0.23_Unity_Scale_Link",
    "0.24": "0.24_Artificial_Intelligence",
    "0.25": "0.25_Strategy_Power_Economics",
}


def get_topic_from_name(name):
    """Infors Topic ID from folder name (e.g. '123_Galaxy_Solver' -> '0.1')."""
    mapping = {
        "Galaxy": "0.1",
        "BlackHole": "0.2",
        "Cosmo": "0.3",
        "Super_Conductivity": "0.4",
        "Superfluid": "0.4",
        "Nuclear": "0.5",
        "Electroweak": "0.6",
        "Neutrino": "0.7",
        "Muon": "0.8",
        "Nonlocality": "0.9",
        "Quantum": "0.9",
        "Fluid": "0.10",
        "Phase": "0.11",
        "Casimir": "0.12",
        "Thermo": "0.13",
        "Econ": "0.14",
        "Cluster": "0.15",
        "Higgs": "0.6",
        "CCBH": "0.2",
        "Mixing": "0.7",
        "Atomic": "0.20",
        "MassGap": "0.21",
        "Neural": "0.22",
        "Quantum": "0.18",
        "Robot": "0.25",
        "Strat": "0.25",
    }
    for key, tid in mapping.items():
        if key in name:
            return tid
    return None


def migrate_global_results():
    print("🧹 Phase 1: Migrating GLOBAL results to topic archives...")
    if not GLOBAL_RESULT_DIR.exists():
        print("  - Global Result folder not found. Skipping.")
        return

    for item in GLOBAL_RESULT_DIR.iterdir():
        if item.name in [".", "..", "General", "General_Logs"]:
            continue

        # Determine Topic
        topic_id = None
        if item.name in TOPIC_MAP:
            topic_id = item.name
        else:
            topic_id = get_topic_from_name(item.name)

        if not topic_id:
            print(f"  ? Unknown result type: {item.name}")
            continue

        full_topic_name = TOPIC_MAP.get(topic_id)
        if not full_topic_name:
            continue

        dest_archive = TOPICS_DIR / full_topic_name / "_Archive"
        dest_archive.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(str(item), str(dest_archive / item.name))
            print(f"  -> Moved {item.name} to {full_topic_name}/_Archive")
        except Exception as e:
            print(f"  ! Error moving {item.name}: {e}")


def flatten_topic_results():
    print("\n🏢 Phase 2: Flattening TOPIC-LOCAL results (Removing Pillar folders)...")
    for topic_folder in TOPICS_DIR.iterdir():
        if not topic_folder.is_dir() or not (topic_folder / "Result").exists():
            continue

        result_root = topic_folder / "Result"

        # Pillars to check: 01_Engine, 02_Proof, 03_Research, 04_Competitor
        for pillar in ["01_Engine", "02_Proof", "03_Research", "04_Competitor"]:
            pillar_path = result_root / pillar
            if not pillar_path.exists():
                continue

            # Move all content from Pillar/RunID to Result/
            for run_item in pillar_path.iterdir():
                if run_item.is_dir():
                    # Move files from inside the run folder to root Result
                    # and move the whole run folder to _Archive
                    dest_archive = topic_folder / "_Archive"
                    dest_archive.mkdir(parents=True, exist_ok=True)

                    # 1. Promote summary and plots to main Result
                    for f in run_item.iterdir():
                        if f.suffix in [".png", ".json", ".csv"]:
                            new_name = f"{pillar}_{f.name}"
                            shutil.copy2(str(f), str(result_root / new_name))

                    # 2. Move original logs to archive
                    try:
                        shutil.move(str(run_item), str(dest_archive / run_item.name))
                    except:
                        pass
                else:
                    # Move single file
                    shutil.move(str(run_item), str(result_root / run_item.name))

            # Delete empty pillar folder
            try:
                shutil.rmtree(str(pillar_path))
            except:
                pass

        print(f"  - Flattened {topic_folder.name}")


def main():
    print("🚀 STARTING UET RESULT REFORMATION")
    print("=" * 40)
    migrate_global_results()
    flatten_topic_results()

    # Cleanup empty global Result
    if GLOBAL_RESULT_DIR.exists() and not os.listdir(GLOBAL_RESULT_DIR):
        GLOBAL_RESULT_DIR.rmdir()
        print("\n✨ Cleaned up empty global Result folder.")

    print("\n✅ REFORMATION COMPLETE. WORKSPACE IS NOW TIDY.")


if __name__ == "__main__":
    main()
