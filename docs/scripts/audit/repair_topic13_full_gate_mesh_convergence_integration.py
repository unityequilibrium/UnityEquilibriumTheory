"""Apply the scoped Topic 13 mesh-convergence lane integration."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/scripts/audit/audit_topic13_full_bridge_gate.py"


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise RuntimeError(f"integration anchor not found: {old[:120]}")
    return text.replace(old, new, 1)


def main() -> None:
    text = GATE.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "'T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION': 'mp48_force_constant_harmonic_reconstruction',",
        "'T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION': 'mp48_force_constant_harmonic_reconstruction', 'T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE': 'mp48_force_constant_csrc_mesh_convergence',",
    )
    text = replace_once(
        text,
        '    force_constant_path, force_constant = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json"\n    )\n',
        '    force_constant_path, force_constant = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json"\n    )\n    mesh_convergence_path, mesh_convergence = load(\n        "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"\n    )\n',
    )
    text = replace_once(
        text,
        '    nist_alpha_v_path, nist_alpha_v = load(\n',
        '    mesh_convergence_lane = discovered_lane_integrations.get(\n        "mp48_force_constant_csrc_mesh_convergence"\n    )\n    if mesh_convergence_lane:\n        artifact["verification_status"]["source_package"][\n            "mp48_force_constant_csrc_mesh_convergence"\n        ] = mesh_convergence_lane\n        artifact["verification_status"]["eos_transport_kms_entropy"].pop(\n            "mp48_force_constant_csrc_mesh_convergence", None\n        )\n    nist_alpha_v_path, nist_alpha_v = load(\n',
    )
    text = replace_once(
        text,
        '    tpg_alpha_v_rel = rel(tpg_alpha_v_path)\n',
        '    mesh_convergence_rel = rel(mesh_convergence_path)\n    if mesh_convergence_rel not in {\n        item.get("path") for item in artifact.get("evidence_artifacts", [])\n        if isinstance(item, dict)\n    }:\n        artifact["evidence_artifacts"].append(\n            evidence(\n                mesh_convergence_rel,\n                mesh_convergence,\n                {\n                    "status": mesh_convergence.get("status"),\n                    "closure_level": mesh_convergence.get("major_result", {}).get("closure_level"),\n                    "max_abs_relative_mesh_step": mesh_convergence.get("max_abs_relative_mesh_step"),\n                    "controlling_blocker": mesh_convergence.get("controlling_blocker"),\n                },\n            )\n        )\n    tpg_alpha_v_rel = rel(tpg_alpha_v_path)\n',
    )
    text = replace_once(
        text,
        '    if discovered_lane_integrations.get("mp48_force_constant_harmonic_reconstruction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 force-constant harmonic reconstruction is closed for lane without Ding-source, transport, or alpha promotion")\n',
        '    if discovered_lane_integrations.get("mp48_force_constant_harmonic_reconstruction", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 force-constant harmonic reconstruction is closed for lane without Ding-source, transport, or alpha promotion")\n    if discovered_lane_integrations.get("mp48_force_constant_csrc_mesh_convergence", {}).get("closure_level") == "CLOSED_FOR_LANE":\n        lane_closures.append("MP48 force-constant C_src mesh-convergence question is closed as a scoped no-go; the independent source remains unaccepted for Ding closure")\n',
    )
    GATE.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
