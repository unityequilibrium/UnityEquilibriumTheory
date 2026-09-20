"""Compare frozen local bridge results; inspect declared Core evidence edges.

Historical artifacts and calibration are never rewritten. This is not an
import-graph proof or a rerun of the full He-4 composition.
"""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import (
    action_natural_phi_thermal_bridge_state,
)
from docs.core.uet_o2_action_thermal_stiffness_beta import (
    action_thermal_stiffness_beta_state,
)

ART = "docs/core/artifacts/"
COMPOSITION = ART + "t13_he4_core_thermodynamic_bridge_composition_audit.json"


def declared_edges(value):
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            yield value["path"], value["sha256"]
        for child in value.values():
            yield from declared_edges(child)
    elif isinstance(value, list):
        for child in value:
            yield from declared_edges(child)


def allowed(path):
    p = Path(path)
    return (path.startswith("docs/core/") and ".." not in p.parts
            and p.suffix in (".json", ".py")
            and not any(word in path.lower() for word in ("xie", "holdout", "/raw/")))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def evidence_graph(root=COMPOSITION):
    pending, visited, edges = [root], set(), []
    while pending:
        parent = pending.pop()
        if parent in visited:
            continue
        visited.add(parent)
        document = json.loads((ROOT / parent).read_text(encoding="utf-8"))
        for path, expected in sorted(set(declared_edges(document))):
            row = {"parent": parent, "path": path, "expected_sha256": expected}
            if not allowed(path):
                row["status"] = "EXCLUDED_NOT_READ"
            elif not (ROOT / path).is_file():
                row["status"] = "MISSING"
            else:
                actual = digest(ROOT / path)
                row.update(actual_sha256=actual, status="MATCH" if actual == expected else "STALE")
                if path.startswith(ART) and path.endswith(".json"):
                    pending.append(path)
            edges.append(row)
    return {"documents_inspected": sorted(visited), "edges": edges,
            "scope": "Declared path/sha256 pairs only; not unrecorded imports or external sources. Stale JSON traversed as CURRENT contents, not reconstructed historical contents."}


def compare_states(old, current):
    rows = {}
    for key, value in old.items():
        if type(value) in (int, float) and type(current.get(key)) in (int, float):
            difference = current[key] - value
            rows[key] = {"historical": value, "current": current[key],
                         "absolute_difference": abs(difference),
                         "relative_difference": abs(difference / value) if value else None}
    return rows


def main():
    graph = evidence_graph()
    results = {}
    for name, function in (
        ("observable_bridge", action_natural_phi_thermal_bridge_state),
        ("stiffness_beta", action_thermal_stiffness_beta_state),
    ):
        suffix = "observable_bridge" if name == "observable_bridge" else "stiffness_beta"
        path = ART + "t13_uet_o2_action_thermal_" + suffix + "_audit.json"
        old = json.loads((ROOT / path).read_text(encoding="utf-8"))["state"]
        current = asdict(function())
        results[name] = {"historical_artifact": path, "historical_sha256": digest(ROOT / path),
                         "branch_historical": old["branch"], "branch_current": current["branch"],
                         "comparison": compare_states(old, current)}
    result = {
        "status": "REVISION_IMPACT_MEASURED_NOT_FULL_COMPOSITION_REVALIDATED",
        "major_result_id": "T13_LOCAL_EOS_REVISION_IMPACT", "closure_level": "PARTIAL",
        "configuration": "Unchanged bridge and beta default builders: T=.22, mu=.35, Phi=.15; quadrature=128. Historical generator scripts call these defaults. No calibration rematching.",
        "evidence_graph": graph, "local_recomputations": results,
        "claim_promotion": False, "dependency_unlocked": [],
        "holdout_policy": "No excluded file opened; no holdout payload, calibration or fitting. This does not erase prior context exposure.",
        "controlling_blocker": "Physical protocol correspondence and remaining dependent artifact revision review",
        "claim_boundary": "Two normal-reference calculations only. No condensed/nonunit-kinetic sweep, external validation, or historical gate replacement.",
        "evidence_artifacts": [{"path": p, "sha256": digest(ROOT / p)} for p in (
            "docs/scripts/audit/audit_topic13_eos_revision_impact.py",
            "docs/core/test/test_topic13_eos_revision_impact.py",
            "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py")],
    }
    target = ROOT / ART / "t13_eos_revision_impact_audit.json"
    target.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"edge_counts": {s: sum(e["status"] == s for e in graph["edges"])
                                     for s in ("MATCH", "STALE", "MISSING", "EXCLUDED_NOT_READ")},
                      "local_recomputations": results}, indent=2))


if __name__ == "__main__":
    main()
