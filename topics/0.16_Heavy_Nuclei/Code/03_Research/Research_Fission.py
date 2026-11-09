"""
UET Research: Nuclear Fission Simulation
========================================
Topic: 0.16 Heavy Nuclei

Diagnostic fission check for:
    n + U-235 -> Ba-141 + Kr-92 + 3n + Energy

The current verifier checks an exothermic fission sanity range and an AME2020
U-235 binding checkpoint. Fragment binding energies are still produced by the
SEMF/UET bridge, so the artifact is WARN rather than a calibrated fission Q-value PASS.
"""

import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path


def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None


root_path = _bootstrap()
if root_path is None:
    print("CRITICAL: UET docs root not found")
    sys.exit(1)
TOPIC_DIR = root_path / "docs" / "topics" / "0.16_Heavy_Nuclei"
AME_HEAVY_PATH = TOPIC_DIR / "Data" / "03_Research" / "ame2020_heavy_nuclei.json"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_16_heavy_nuclei_verification.json"


def load_engine():
    engine_file = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Heavy_Nuclei.py"
    spec = importlib.util.spec_from_file_location("Engine_Heavy_Nuclei", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "UETHeavyNucleiEngine")


def file_sha256(path):
    digest = sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_ame_heavy():
    if not AME_HEAVY_PATH.exists():
        return None
    with open(AME_HEAVY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_ame_binding_mev(data, z, a):
    if not data:
        return None
    for row in data.get("heavy_nuclei", []):
        if row.get("Z") == z and row.get("A") == a:
            return row["binding_energy_keV"] / 1000.0
    return None


def write_artifact(artifact):
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")


def run_fission_sim():
    print("=" * 60)
    print("UET RESEARCH: NUCLEAR FISSION DIAGNOSTIC (U-235)")
    print("=" * 60)

    engine_cls = load_engine()
    engine = engine_cls()

    z_parent, a_parent = 92, 235
    z_frag1, a_frag1 = 56, 141
    z_frag2, a_frag2 = 36, 92

    be_parent = engine.compute_binding_energy(z_parent, a_parent)
    be_frag1 = engine.compute_binding_energy(z_frag1, a_frag1)
    be_frag2 = engine.compute_binding_energy(z_frag2, a_frag2)
    total_be_products = be_frag1 + be_frag2
    energy_released = total_be_products - be_parent

    ame_data = load_ame_heavy()
    u235_ame_binding_mev = find_ame_binding_mev(ame_data, z_parent, a_parent)
    u235_error_percent = None
    if u235_ame_binding_mev:
        u235_error_percent = abs(be_parent - u235_ame_binding_mev) / u235_ame_binding_mev * 100

    threshold = {
        "energy_release_mev_min": 100.0,
        "energy_release_mev_max": 250.0,
        "u235_binding_error_percent_max": 2.0,
        "fragment_ame_required_for_pass": True,
    }
    exothermic_gate = threshold["energy_release_mev_min"] < energy_released < threshold["energy_release_mev_max"]
    u235_gate = u235_error_percent is not None and u235_error_percent <= threshold["u235_binding_error_percent_max"]
    fragment_ame_present = False
    status = "WARN" if exothermic_gate and u235_gate else "FAIL"
    failure_reason = (
        "Exothermic range and U-235 binding checkpoint pass, but Ba-141/Kr-92 fragment AME masses are not used by this verifier."
        if status == "WARN"
        else "Fission sanity check failed the energy-release or U-235 binding checkpoint gate."
    )

    print(f"  Parent U-235 bridge BE: {be_parent:.1f} MeV")
    if u235_ame_binding_mev is not None:
        print(f"  AME2020 U-235 BE:       {u235_ame_binding_mev:.1f} MeV")
        print(f"  U-235 error:            {u235_error_percent:.2f}%")
    print(f"  Products bridge BE:     {total_be_products:.1f} MeV")
    print(f"  Energy released:        {energy_released:.1f} MeV")
    print(f"  Artifact status:        {status}")

    artifact = {
        "schema_version": "1.1",
        "topic": "0.16_Heavy_Nuclei",
        "status": status,
        "claim_class": "C/D boundary - internal fission sanity check with missing fragment provenance",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.16_Heavy_Nuclei/Code/03_Research/Research_Fission.py",
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "inputs": [
            {
                "path": str(AME_HEAVY_PATH.relative_to(root_path)).replace("\\", "/"),
                "sha256": file_sha256(AME_HEAVY_PATH) if AME_HEAVY_PATH.exists() else None,
                "source": "AME2020 heavy-nuclei working copy",
                "doi": ame_data.get("publication", {}).get("doi") if ame_data else None,
            }
        ],
        "formula_ids": [
            "HN16-SEMF-BINDING",
            "HN16-UET-SEMF-BRIDGE",
            "HN16-FISSION-Q-SANITY",
        ],
        "threshold": threshold,
        "metrics": {
            "parent": {"Z": z_parent, "A": a_parent, "binding_energy_mev": be_parent},
            "fragments": [
                {"Z": z_frag1, "A": a_frag1, "binding_energy_mev": be_frag1},
                {"Z": z_frag2, "A": a_frag2, "binding_energy_mev": be_frag2},
            ],
            "energy_release_mev": energy_released,
            "u235_ame_binding_mev": u235_ame_binding_mev,
            "u235_binding_error_percent": u235_error_percent,
            "exothermic_gate": exothermic_gate,
            "u235_binding_gate": u235_gate,
            "fragment_ame_present": fragment_ame_present,
        },
        "failure_reason": failure_reason,
        "limitations": [
            "The verifier uses SEMF/UET-bridge fragment binding estimates, not source-locked AME fragment masses.",
            "The result supports an internal fission sanity check only.",
            "It does not validate the Island of Stability or a first-principles heavy-nuclei theory.",
        ],
    }
    write_artifact(artifact)
    print(f"  Artifact written: {ARTIFACT_PATH}")
    return status in {"PASS", "WARN"}


if __name__ == "__main__":
    success = run_fission_sim()
    sys.exit(0 if success else 1)
