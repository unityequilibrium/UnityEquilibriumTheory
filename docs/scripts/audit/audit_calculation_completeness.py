"""Read-only contract validation and compact gradual-adoption inventory.

Only --emit-report writes, and only the requested methodological report. No
scientific artifact, threshold, gate, data or source file is regenerated here.
The stdlib schema interpreter implements exactly the keywords used by v1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SCHEMA = "docs/meta/schemas/calculation_contract_v1.schema.json"
BASELINE = "docs/meta/calculation_completeness_baseline.json"
REPORT = "docs/meta/calculation_completeness_inventory.json"
REGISTRY = "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
MIGRATION_MAP = "docs/core/07_artifacts/archive/uet_core_file_migration_map.json"
GROUPS = {"system_state", "drive_environment", "propagation", "frame_time", "detector", "processing", "numerics"}
TEXT = {".py", ".md", ".json", ".yaml", ".yml", ".csv", ".tsv", ".txt", ".toml"}
SUPPORT = {
    "docs/scripts/audit/audit_calculation_completeness.py",
    "docs/scripts/audit/build_calculation_contract_pilots.py",
    "docs/scripts/audit/audit_topic_standards.py",
}


def load_json(path: Path):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError(f"duplicate JSON key: {k}")
            result[k] = v
        return result
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(root), *args],
                            capture_output=True, check=False)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def repo_path(root: Path, path: str) -> Path:
    if not path or "\\" in path or Path(path).is_absolute() or re.match(r"^[A-Za-z]:", path):
        raise ValueError(f"not a repository-relative POSIX path: {path}")
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes repository: {path}")
    return target


def identity_bytes(root: Path, item: dict) -> bytes:
    path = item["path"]
    repo_path(root, path)
    if item["kind"] == "git_blob":
        commit = item.get("commit", "")
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("git_blob needs an immutable 40-character commit")
        data = git(root, "show", f"{commit}:{path}")
    else:
        data = repo_path(root, path).read_bytes()
    if Path(path).suffix.lower() in TEXT:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data


def identity_hash(root: Path, item: dict) -> str:
    return hashlib.sha256(identity_bytes(root, item)).hexdigest()


def contract_hash(contract: dict) -> str:
    return hashlib.sha256(json.dumps(contract, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def review_payload_hash(contract: dict) -> str:
    """Bind explicit review to the model, scope, parameters and observation policy."""
    return contract_hash({k: v for k, v in contract.items() if k != "review"})


def schema_errors(value, schema: dict, loc: str = "contract") -> list[str]:
    supported = {"$schema", "$id", "title", "description", "$comment", "type", "const", "enum",
                 "required", "properties", "items", "minItems", "minLength", "pattern", "minimum"}
    if set(schema) - supported:
        return [f"{loc}: unsupported schema keywords: {sorted(set(schema) - supported)}"]
    errors = []
    types = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
             "string": lambda x: isinstance(x, str), "boolean": lambda x: isinstance(x, bool),
             "number": lambda x: type(x) in (int, float) and math.isfinite(x),
             "null": lambda x: x is None}
    expected = schema.get("type")
    if expected and not any(types[t](value) for t in ([expected] if isinstance(expected, str) else expected)):
        return [f"{loc}: expected {expected}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{loc}: invalid constant")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{loc}: outside enum")
    if isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            errors.append(f"{loc}: empty value")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{loc}: invalid pattern")
    if type(value) in (int, float) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{loc}: below minimum")
    if isinstance(value, dict):
        errors += [f"{loc}: missing {k}" for k in schema.get("required", []) if k not in value]
        for k, sub in schema.get("properties", {}).items():
            if k in value:
                errors += schema_errors(value[k], sub, f"{loc}.{k}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{loc}: insufficient items")
        if "items" in schema:
            for i, item in enumerate(value):
                errors += schema_errors(item, schema["items"], f"{loc}[{i}]")
    return errors


def relational_accounting_errors(graph: dict, systems: dict, components: dict) -> list[str]:
    """Validate declared ownership; semantic state/energy equivalence still needs review."""
    errors = []
    accounting = components.get(graph.get("accounting_component_id"))
    if accounting is None or accounting["group"] != "system_state":
        errors.append("RELATIONAL partition needs system_state accounting_component_id")
    elif accounting["disposition"] in {"NOT_APPLICABLE", "BOUNDED_OMISSION"}:
        errors.append("declared state accounting cannot be absent or omitted")
    owners = {}
    for sid, system in systems.items():
        if "role" in system:
            errors.append(f"{sid}: RELATIONAL roles belong to relationships, not system.role")
        a = system.get("state_accounting")
        if a is None:
            errors.append(f"{sid}: RELATIONAL system needs state_accounting")
            continue
        for field in ("state_ids", "owner_ids"):
            if len(a[field]) != len(set(a[field])):
                errors.append(f"{sid}: duplicate {field}")
        if a["kind"] == "INDEPENDENT":
            if not a["state_ids"] or a["owner_ids"]:
                errors.append(f"{sid}: independent state needs state_ids and no owner_ids")
            for state in a["state_ids"]:
                if state in owners:
                    errors.append(f"{sid}: duplicate independent state {state} owned by {owners[state]}")
                owners[state] = sid
        else:
            if a["state_ids"] or not a["owner_ids"]:
                errors.append(f"{sid}: aggregate/view references owners, not new independent states")
            for owner in a["owner_ids"]:
                if systems.get(owner, {}).get("state_accounting", {}).get("kind") != "INDEPENDENT":
                    errors.append(f"{sid}: state owner {owner} must be an independent system")
        parent = system.get("parent_id")
        if parent is not None:
            if systems.get(parent, {}).get("state_accounting", {}).get("kind") != "AGGREGATE":
                errors.append(f"{sid}: parent must be an aggregate system")
            parent_owners = set(systems.get(parent, {}).get("state_accounting", {}).get("owner_ids", []))
            child_owners = {sid} if a["kind"] == "INDEPENDENT" else set(a["owner_ids"])
            if not child_owners <= parent_owners:
                errors.append(f"{sid}: parent accounting omits child owners")
        seen = {sid}
        while parent in systems:
            if parent in seen:
                errors.append(f"{sid}: cyclic subsystem containment")
                break
            seen.add(parent)
            parent = systems[parent].get("parent_id")
    change = graph.get("boundary_change")
    if change:
        component = components.get(change["component_id"])
        if component is None:
            errors.append("boundary change needs an identified mapping component")
        elif change["outcome"] == "EQUIVALENT" and component["disposition"] not in {"MODELED", "UPSTREAM_CORRECTED"}:
            errors.append("boundary equivalence needs admitted mapping evidence, not an omission or unknown")
        elif component["disposition"] == "NOT_APPLICABLE":
            errors.append("boundary change mapping cannot be not applicable")
        if change["outcome"] == "UNRESOLVED" and component and component["disposition"] != "UNKNOWN":
            errors.append("unresolved boundary change needs UNKNOWN mapping component")
    return errors


def partition_errors(contract: dict) -> list[str]:
    """Check declared interaction topology, not completeness or physical validity."""
    graph = contract["observation"].get("system_partition")
    if graph is None:
        return []
    errors = []
    systems = {s["id"]: s for s in graph["systems"]}
    components = {c["id"]: c for c in contract["components"]}
    relational = graph.get("role_mode", "LEGACY_FIXED") == "RELATIONAL"
    if relational:
        errors.extend(relational_accounting_errors(graph, systems, components))
    else:
        for sid, system in systems.items():
            if "role" not in system:
                errors.append(f"{sid}: legacy system needs role; choose RELATIONAL explicitly to change semantics")
            if any(k in system for k in ("parent_id", "state_accounting", "categories")):
                errors.append(f"{sid}: relational fields require explicit RELATIONAL role_mode")
        if "boundary_change" in graph or "accounting_component_id" in graph:
            errors.append("relational accounting fields require explicit RELATIONAL role_mode")
    for label, rows in (("system", graph["systems"]), ("coupling", graph["couplings"]),
                        ("observable", graph["observables"])):
        ids = [r["id"] for r in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"system_partition: duplicate {label} IDs")
    for edge in graph["couplings"]:
        if edge["source"] not in systems or edge["target"] not in systems:
            errors.append(f"{edge['id']}: unknown coupling endpoint")
        if edge["component_id"] not in components:
            errors.append(f"{edge['id']}: unknown coupling component")
        if not relational and edge["kind"] == "DETECTION" and systems.get(edge["target"], {}).get("role") != "DETECTOR":
            errors.append(f"{edge['id']}: detection must target a detector system")
        if not relational and edge["kind"] == "BACKACTION" and systems.get(edge["source"], {}).get("role") != "DETECTOR":
            errors.append(f"{edge['id']}: backaction must originate at a detector system")
    if not graph["observables"] and not graph.get("no_detector_reason"):
        errors.append("system_partition: no observables needs a scoped no_detector_reason")
    for observable in graph["observables"]:
        detector = observable["detector_id"]
        if observable["id"] in systems:
            errors.append(f"{observable['id']}: observable ID must differ from system IDs")
        receiver_exists = detector in systems if relational else systems.get(detector, {}).get("role") == "DETECTOR"
        if not receiver_exists:
            errors.append(f"{observable['id']}: observable is not a detector system")
        readout = components.get(observable["component_id"])
        if readout is None:
            errors.append(f"{observable['id']}: unknown readout component")
        elif readout["group"] not in {"detector", "processing"}:
            errors.append(f"{observable['id']}: readout needs detector/processing component")
        elif readout["disposition"] in {"NOT_APPLICABLE", "BOUNDED_OMISSION"}:
            errors.append(f"{observable['id']}: claimed readout cannot be absent or omitted")
        # Non-NA edges may be provisional UNKNOWN routes, which remain gaps in the
        # component ledger. Do not invent a reverse edge from an observed signal.
        active = [e for e in graph["couplings"] if e["kind"] != "BACKACTION"
                  and components.get(e["component_id"], {}).get("disposition")
                  in {"MODELED", "UPSTREAM_CORRECTED", "UNKNOWN"}]
        for target in observable["target_systems"]:
            if target not in systems:
                errors.append(f"{observable['id']}: unknown observable target")
                continue
            reachable = {target}
            for _ in systems:
                reachable |= {e["target"] for e in active if e["source"] in reachable
                              and e["kind"] != "RECEIVER_DYNAMICS"}
            incoming = any(e["kind"] == "DETECTION" and e["target"] == detector
                           and e["source"] in reachable for e in active)
            if not incoming:
                errors.append(f"{observable['id']}: no declared detection path from {target}")
        # Legacy graphs retain their fixed source scope. Relational graphs explicitly
        # declare the assessment scope, including observed targets and any other
        # coupled owners justified by review. No category implies isolation.
        if relational:
            targets = observable.get("backaction_targets", [])
            if "backaction_targets" not in observable or not observable.get("backaction_scope_reason"):
                errors.append(f"{observable['id']}: relational observable needs backaction targets and scope reason")
            if len(targets) != len(set(targets)):
                errors.append(f"{observable['id']}: duplicate backaction targets")
            if not (set(observable["target_systems"]) - {detector}) <= set(targets):
                errors.append(f"{observable['id']}: backaction scope omits an observed target")
            if any(t not in systems or t == detector for t in targets):
                errors.append(f"{observable['id']}: invalid backaction target")
        else:
            if "backaction_targets" in observable or "backaction_scope_reason" in observable:
                errors.append(f"{observable['id']}: relational scope fields require RELATIONAL role_mode")
            targets = [s for s, item in systems.items() if item.get("role") == "SOURCE"]
        for source in targets:
            if not any(
                    e["kind"] == "BACKACTION" and e["source"] == detector
                    and e["target"] == source for e in graph["couplings"]):
                errors.append(f"{observable['id']}: missing backaction assessment {detector}->{source}")
    return errors


def validate_contract(contract: dict, root: Path = ROOT, schema: dict | None = None) -> dict:
    errors = schema_errors(contract, schema or load_json(root / SCHEMA))
    gaps = []
    result = {"contract_id": contract.get("contract_id", "UNKNOWN"), "errors": errors,
              "gaps": gaps, "effective_status": "INCOMPLETE"}
    if errors:
        return result
    errors.extend(partition_errors(contract))
    if contract["profile"] != "FORMAL" and "system_partition" not in contract["observation"]:
        gaps.append("system_partition:legacy_unreviewed")
    stale = False
    if contract["review"]["status"] == "COMPLETE_FOR_SCOPE":
        if contract["review"].get("scope_sha256") != review_payload_hash(contract):
            stale = True
            errors.append("STALE scope/model/config review: explicit renewed scope_sha256 required")
    identity_keys = set()
    for item in contract["identities"]:
        key = (item["kind"], item.get("commit"), item["path"])
        if key in identity_keys:
            errors.append(f"duplicate identity: {key}")
        identity_keys.add(key)
        try:
            if identity_hash(root, item) != item["sha256"]:
                stale = True
                errors.append(f"STALE identity: {item['path']}")
        except (OSError, ValueError) as exc:
            if (item.get("availability") == "LOCAL_ONLY" and contract["review"]["status"] == "INCOMPLETE"
                    and contract["output"]["claim_intent"] != "PHYSICAL_ACCEPTANCE"):
                gaps.append(f"unavailable-local-evidence:{item['path']}")
            else:
                errors.append(f"identity unavailable: {item['path']}: {exc}")
    identity_paths = {x["path"] for x in contract["identities"]}
    known_locators = identity_paths | {f"git:{x['commit']}:{x['path']}" for x in contract["identities"] if x.get("commit")}
    change = contract["observation"].get("system_partition", {}).get("boundary_change")
    if change:
        matches = [i for i in contract["identities"] if
                   (f"git:{i['commit']}:{i['path']}" if i.get("commit") else i["path"]) == change["baseline_identity"]]
        if len(matches) != 1:
            errors.append("boundary change baseline must resolve to one identified contract")
        else:
            try:
                baseline = json.loads(identity_bytes(root, matches[0]).decode("utf-8-sig"))
                if not isinstance(baseline, dict) or baseline.get("contract_id") != change["baseline_contract_id"] or contract_hash(baseline) != change["baseline_contract_sha256"]:
                    errors.append("boundary change baseline contract ID/hash mismatch")
            except (OSError, ValueError, TypeError) as exc:
                errors.append(f"boundary change baseline unavailable/invalid: {exc}")
    refs = list(contract["evidence"]) + list(contract["review"].get("coverage_evidence", []))
    refs += [ref for c in contract["components"] for ref in c["evidence"]]
    refs += [c["evidence"] for c in contract["observation"]["corrections"]]
    refs += [contract["observation"][k] for k in ("unit_conversion_evidence", "frame_transform_evidence") if contract["observation"].get(k)]
    if contract["error_budget"].get("acceptance_evidence"):
        refs.append(contract["error_budget"]["acceptance_evidence"])
    if contract["data_policy"].get("independence_evidence"):
        refs.append(contract["data_policy"]["independence_evidence"])
    for ref in refs:
        if not isinstance(ref, str) or (ref.split("#")[0] not in known_locators and not ref.startswith(("https://", "http://"))):
            errors.append(f"unidentified evidence locator: {ref}")
    for path in contract["entrypoints"]:
        try:
            repo_path(root, path)
        except ValueError as exc:
            errors.append(str(exc))
        if path not in identity_paths:
            errors.append(f"entrypoint has no code/evidence identity: {path}")
    ids = [c["id"] for c in contract["components"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate component IDs")
    missing_groups = GROUPS - {c["group"] for c in contract["components"]}
    if missing_groups:
        errors.append(f"missing component groups: {sorted(missing_groups)}")
    bounds = {}
    for c in contract["components"]:
        d = c["disposition"]
        if d == "UNKNOWN":
            gaps.append(c["id"])
            if not c.get("owner") or not c.get("next_action"):
                errors.append(f"{c['id']}: UNKNOWN needs owner and next_action")
        elif d != "NOT_APPLICABLE" and not c["evidence"]:
            errors.append(f"{c['id']}: evidence required")
        if d == "BOUNDED_OMISSION":
            bound = c.get("bound")
            if type(bound) not in (int, float) or not math.isfinite(bound) or bound < 0:
                errors.append(f"{c['id']}: finite nonnegative omission bound required")
            elif c.get("unit") != contract["output"]["unit"]:
                errors.append(f"{c['id']}: omission bound must use output unit")
            elif not c.get("joint_group"):
                errors.append(f"{c['id']}: joint_group required")
            else:
                # A shared group denotes one joint bound, not independent errors.
                group = c["joint_group"]
                if group in bounds and bounds[group] != bound:
                    errors.append(f"{group}: inconsistent joint omission bound")
                bounds[group] = bound
    budget = contract["error_budget"]
    if budget["unit"] != contract["output"]["unit"]:
        errors.append("error budget/output unit mismatch")
    if bounds and (budget["omission_limit"] is None or sum(bounds.values()) > budget["omission_limit"]):
        errors.append("joint omission bounds exceed declared omission budget")
    corrections = {}
    for c in contract["observation"]["corrections"]:
        if c["id"] in corrections:
            errors.append(f"duplicate/reapplied correction: {c['id']}")
        corrections[c["id"]] = c["state"]
        if c["state"] == "UNKNOWN":
            gaps.append(f"correction:{c['id']}")
    if any(c["disposition"] == "UPSTREAM_CORRECTED" for c in contract["components"]):
        if "APPLIED_UPSTREAM" not in corrections.values():
            errors.append("upstream-corrected component lacks applied correction provenance")
    data = contract["data_policy"]
    observation = contract["observation"]
    if observation.get("comparison_unit", contract["output"]["unit"]) != contract["output"]["unit"] and not observation.get("unit_conversion_evidence"):
        errors.append("comparison/output unit mismatch without conversion evidence")
    if observation.get("comparison_frame", observation["frame"]) != observation["frame"] and not observation.get("frame_transform_evidence"):
        errors.append("comparison/model frame mismatch without transformation evidence")
    if observation.get("trace_scope") == "dissipation_history" and observation.get("trace_used_as_complete_state"):
        errors.append("dissipation trace cannot stand for complete observable state")
    if data["uses_observations"] and contract["profile"] != "PHYSICAL_COMPARISON":
        errors.append("observational inference cannot be labeled FORMAL/SYNTHETIC")
    if data["independent_validation"]:
        if set(data["calibration_ids"]) & set(data["comparison_ids"]):
            errors.append("calibration data reused as independent validation")
        if not data["comparison_ids"]:
            errors.append("independent validation has no named comparison data")
        if not data.get("independence_evidence"):
            errors.append("independent validation requires ancestry/independence evidence")
    status = contract["review"]["status"]
    if status == "COMPLETE_FOR_SCOPE" and gaps:
        errors.append("COMPLETE_FOR_SCOPE contradicts unresolved components/corrections")
    if status == "COMPLETE_FOR_SCOPE" and not contract["review"].get("coverage_evidence"):
        errors.append("COMPLETE_FOR_SCOPE requires substantive coverage review evidence")
    physical = contract["output"]["claim_intent"] == "PHYSICAL_ACCEPTANCE"
    if physical:
        if not data["uses_observations"] or not data["comparison_ids"]:
            errors.append("physical acceptance requires named actual comparison observations")
        if contract["profile"] != "PHYSICAL_COMPARISON" or status != "COMPLETE_FOR_SCOPE" or gaps:
            errors.append("physical acceptance requires complete physical contract")
        if budget.get("omission_limit") is None or not budget.get("acceptance_evidence"):
            errors.append("physical acceptance requires sourced quantitative error criterion")
        limit = budget.get("acceptance_limit")
        if type(limit) not in (int, float) or not math.isfinite(limit) or limit < 0:
            errors.append("physical acceptance requires finite output-unit acceptance_limit")
        elif budget.get("omission_limit") is not None and budget["omission_limit"] > limit:
            errors.append("omission allocation exceeds total acceptance limit")
        if not contract.get("physical_gates"):
            errors.append("physical acceptance requires existing physics gates")
        for gate in contract.get("physical_gates", []):
            try:
                if any(v not in {"PASS", "EXTERNAL_COMPARISON", "EXTERNALLY_VALIDATED"} for v in gate["accepted"]):
                    errors.append(f"non-accepting physics gate state cannot be whitelisted: {gate['path']}")
                obj = load_json(repo_path(root, gate["path"]))
                for key in gate["field"].split("."):
                    obj = obj[key]
                if obj not in gate["accepted"]:
                    errors.append(f"physical gate blocks acceptance: {gate['path']}")
                if gate["path"] not in identity_paths:
                    errors.append(f"physical gate lacks identity: {gate['path']}")
            except (OSError, ValueError, KeyError, TypeError) as exc:
                errors.append(f"physical gate unavailable: {exc}")
    result["effective_status"] = "STALE" if stale else (
        "INCOMPLETE" if errors or gaps else status)
    return result


def artifact_metadata(contract: dict, root: Path = ROOT) -> dict:
    """Additive producer interface; does not rewrite or promote saved results."""
    review = validate_contract(contract, root)
    if review["errors"]:
        raise ValueError("; ".join(review["errors"]))
    return {"contract_id": contract["contract_id"], "contract_sha256": contract_hash(contract),
            "contract_review_status": review["effective_status"],
            "identities": contract["identities"]}


def result_path(path: str) -> bool:
    return path.endswith(".json") and ("/Result/artifacts/" in path or path.startswith("docs/core/07_artifacts/"))


def scientific_path(path: str) -> bool:
    p = Path(path)
    if p.suffix not in {".py", ".json", ".csv", ".tsv", ".npy", ".npz", ".h5", ".hdf5", ".dat"} or path in SUPPORT:
        return False
    if p.name.startswith("test_") or "05_tests" in p.parts or "test" in p.parts or p.name == "__init__.py":
        return False
    data_input = (path.startswith("docs/data/external/") or path.startswith("docs/core/06_data/")
                  or (path.startswith("docs/topics/0.") and "/Data/" in path))
    if p.suffix != ".py":
        return result_path(path) or data_input
    return (path.startswith("docs/core/") or path.startswith("docs/scripts/audit/")
            or (path.startswith("docs/topics/0.") and "/Code/" in path) or data_input)


def discover_contracts(root: Path) -> list[tuple[str, dict]]:
    result = []
    # Bounded to research workspaces; do not walk caches, media, .git or books.
    for base in (root / "docs/core", root / "docs/topics"):
        paths = set(base.rglob("CALCULATION_CONTRACT.json"))
        paths.update(p for d in base.rglob("calculation_contracts") if d.is_dir() for p in d.glob("*.json"))
        for path in sorted(paths):
            result.append((path.relative_to(root).as_posix(), load_json(path)))
    # Existing manifests may embed the same contract; no competing duplicate IDs.
    baseline = load_json(root / BASELINE) if (root / BASELINE).exists() else {}
    for locator in baseline.get("embedded_contracts", []):
        result.append((locator, load_json(repo_path(root, locator))["calculation_contract"]))
    return result


def adoption_inventory(root: Path, baseline: dict, contracts: list, reviews: list,
                       current: set[str]) -> tuple[list, dict, list[str]]:
    """Triage declared routes, not individual files as experiments or scientific grades."""
    aliases, errors, sources, ambiguous = {}, [], [], set()
    for path in (BASELINE, REGISTRY, MIGRATION_MAP, SCHEMA, "docs/scripts/audit/audit_calculation_completeness.py"):
        if repo_path(root, path).is_file():
            sources.append({"path": path, "sha256": identity_hash(root, {"path": path, "kind": "working_file"})})
    if repo_path(root, MIGRATION_MAP).is_file():
        for row in load_json(repo_path(root, MIGRATION_MAP)).get("files", []):
            target = row["canonical_path"]
            for alias in [target, row.get("current_path", target), *row.get("legacy_paths", [])]:
                if alias in ambiguous:
                    continue
                if alias in aliases and aliases[alias] != target:
                    errors.append(f"ambiguous migration alias: {alias}")
                    ambiguous.add(alias)
                    aliases.pop(alias)
                    continue
                aliases[alias] = target

    resolved_cache, existence = {}, {p: True for p in current}

    def resolve(path):
        if path in resolved_cache:
            return resolved_cache[path]
        target = aliases.get(path, path)
        # Never guess by basename or accept a mapping outside this repository.
        repo_path(root, target)
        resolved_cache[path] = target
        return target

    def exists(path):
        if path not in existence:
            existence[path] = repo_path(root, path).is_file()
        return existence[path]

    seeds = {}
    for route in baseline.get("routes", []):
        rid = route["route_id"]
        if rid in seeds:
            errors.append(f"duplicate baseline route_id: {rid}")
        seeds[rid] = {**route, "kind": "EQUATION_FAMILY" if route["owner"] == "CORE" else "TOPIC_PACKAGE",
                      "baseline_paths": route["paths"], "discovery": [BASELINE]}
    if repo_path(root, REGISTRY).is_file():
        for entry in load_json(repo_path(root, REGISTRY)).get("entries", []):
            rid = entry["equation_id"]
            route = seeds.setdefault(rid, {"route_id": rid, "owner": "CORE", "kind": "EQUATION_FAMILY", "paths": [], "discovery": []})
            route["paths"] = sorted(set(route["paths"] + entry.get("implementation_paths", []) + entry.get("verifier_paths", [])))
            route.update(claim_boundary=entry.get("claim_boundary", "Unreviewed"),
                         registry_classification=entry.get("classification"),
                         downstream_dependencies=entry.get("downstream_dependencies", []))
            route["discovery"].append(REGISTRY)
    topics = sorted(p for p in (root / "docs/topics").glob("0.*") if p.is_dir() and re.match(r"^0\.\d+_", p.name))
    for folder in topics:
        owner = folder.name
        prefix = folder.relative_to(root).as_posix() + "/"
        route = seeds.setdefault(owner, {"route_id": owner, "owner": owner, "kind": "TOPIC_PACKAGE", "paths": [],
            "claim_boundary": "Unreviewed topic package, not accepted from folder presence", "discovery": []})
        docs = [prefix + name for name in ("README.md", "METHOD.md", "LIMITATIONS.md", "FORMULA_AUDIT.md", "DATA_MANIFEST.md")
                if repo_path(root, prefix + name).is_file()]
        # A missing verification spec remains a named gap, not a reason to omit a topic.
        route["paths"] = sorted(set(route["paths"] + docs + [prefix + "VERIFICATION_SPEC.md"]
                                    + [p for p in current if p.startswith(prefix)]))
        route["discovery"].append(prefix)
    contract_by_id = {c["contract_id"]: (locator, c) for locator, c in contracts}
    review_by_id = {r["contract_id"]: r for r in reviews}
    coverage = {}
    for locator, contract in contracts:
        cid = contract["contract_id"]
        paths = sorted({i["path"] for i in contract["identities"] if i["kind"] == "working_file"})
        for path in paths:
            coverage.setdefault(resolve(path), set()).add(cid)
        owner = locator.split("/")[2] if locator.startswith("docs/topics/") else "CORE"
        seeds["contract:" + cid] = {"route_id": "contract:" + cid, "owner": owner,
            "kind": "CONTRACT_PATH", "paths": paths, "contract_id": cid,
            "claim_boundary": contract["claim_boundary"], "discovery": [locator]}
    named = {resolve(p) for r in seeds.values() for p in r["paths"]}
    # Loose sources/results are classification candidates, not one experiment per file.
    loose = sorted(current - named)
    groups = {}
    for path in loose:
        canonical = resolve(path)
        if canonical in named:
            continue
        bucket = "CORE" if path.startswith("docs/core/") else "AUDIT_TOOLS" if path.startswith("docs/scripts/") else "OTHER_RESEARCH"
        groups.setdefault(bucket, set()).add(canonical)
    for owner, paths in sorted(groups.items()):
        seeds["unassigned:" + owner] = {"route_id": "unassigned:" + owner, "owner": owner,
            "kind": "SURFACE_GROUP", "paths": sorted(paths), "discovery": ["current research-surface discovery"],
            "claim_boundary": "Unassigned scientific-looking surfaces; classify before treating them as independent studies or evidence"}
    routes = []
    for rid, seed in sorted(seeds.items()):
        paths = sorted({resolve(p) for p in seed["paths"]})
        ids = {cid for p in paths for cid in coverage.get(p, [])}
        formula_ids = {c["contract_id"] for _, c in contracts if rid in c["model"]["formula_ids"]}
        ids |= formula_ids
        if seed["kind"] == "TOPIC_PACKAGE":
            ids |= {cid for cid, (loc, _) in contract_by_id.items() if loc.startswith(f"docs/topics/{seed['owner']}/")}
        if seed.get("contract_id"):
            ids = {seed["contract_id"]}
        missing = [p for p in paths if not exists(p)]
        uncovered = [p for p in paths if p not in coverage]
        linked = [review_by_id[cid] for cid in sorted(ids)]
        priority = 1 if seed["kind"] in {"EQUATION_FAMILY", "TOPIC_PACKAGE", "SURFACE_GROUP"} else (
            2 if contract_by_id[seed["contract_id"]][1]["profile"] == "PHYSICAL_COMPARISON" else 3)
        if seed["kind"] == "CONTRACT_PATH":
            review = linked[0]
            contract = contract_by_id[seed["contract_id"]][1]
            if review["errors"] or review["effective_status"] == "STALE":
                action, reason = "REVIEW_MODEL_OR_CODE", "Contract identities/structure are invalid or stale; inspect errors before reuse, do not automatically rerun physics."
            elif (review["gaps"] and contract["profile"] == "FORMAL"
                  and set(review["gaps"]) <= {"processing"}
                  and any(c["id"] == "processing" and c["reason"] == "Clean public lineage integration of the pinned research commit remains open."
                          for c in contract["components"])):
                action, reason = "UPDATE_METADATA", "Only the explicitly recorded public-lineage integration gap remains; retain the old conditional formal evidence locally without fresh certification or public promotion."
            elif review["gaps"]:
                action, reason = "WAIT_FOR_PREREQUISITE", "Scoped prerequisites remain: " + "; ".join(review["gaps"])
            elif review["effective_status"] == "COMPLETE_FOR_SCOPE":
                action, reason = "REUSE_SCOPED_EVIDENCE", "Identity-matched reviewed contract only; no parent-topic or physical-claim promotion."
            else:
                action, reason = "UPDATE_METADATA", "Explicit scope review is not complete; no evidence-producing change is established that would justify a rerun."
            next_action = contract["next_action"]
        else:
            action = "REVIEW_MODEL_OR_CODE"
            reason = (f"Package/family scope is not certified by {len(ids)} related contract(s); "
                      f"{len(uncovered)} declared paths lack working-file coverage and {len(missing)} resolved paths are unavailable. "
                      "Overlap is a navigation link, not full-route acceptance or a demonstrated code defect.")
            next_action = "Review the named claim/model and its current gate, classify uncovered inputs/results and attach scoped evidence; reuse unchanged results and do not rerun merely for coverage."
        routes.append({**seed, "resolved_paths": paths, "missing_paths": missing,
            "uncovered_paths": uncovered, "contract_ids": sorted(ids), "exact_formula_contract_ids": sorted(formula_ids),
            "review_status": linked[0]["effective_status"] if seed["kind"] == "CONTRACT_PATH" else "UNREVIEWED",
            "coverage_scope": "SCOPED_CONTRACT" if seed["kind"] == "CONTRACT_PATH" else "RELATED_ONLY_NOT_PACKAGE_COVERAGE",
            "adoption": {"action": action, "reason": reason, "priority": priority,
                         "priority_basis": "possible public/dependency surface" if priority == 1 else "physical-comparison contract" if priority == 2 else "scoped formal/synthetic contract",
                         "next_action": next_action, "claim_promotion": False}})
    routes.sort(key=lambda r: (r["adoption"]["priority"], r["owner"], r["route_id"]))
    scope = {"sources": sources, "numbered_topic_packages": len(topics),
             "route_unit": "declared equation family, topic package, scoped contract or unassigned surface group; overlapping units are not independent experiments",
             "limitations": ["No exhaustive recovery of equations/claims hidden in historical prose, external chats, books or private raw archives",
                            "Public/dependency priority is conservative triage, not a verified claim audit or a scientific evidence grade",
                            "All discovered routes have a reasoned next disposition, not completed scientific review; history is not declared inactive by its directory name"],
             "claim_promotion": False}
    return routes, scope, sorted(set(errors))


def build_report(root: Path, changed: list[str] | None = None) -> dict:
    contracts = discover_contracts(root)
    errors, reviews, coverage, seen = [], [], {}, set()
    schema = load_json(root / SCHEMA)
    for locator, contract in contracts:
        review = validate_contract(contract, root, schema)
        if (locator in (changed or []) and contract.get("profile") != "FORMAL"
                and "system_partition" not in contract.get("observation", {})):
            review["errors"].append("changed non-FORMAL contract requires observation.system_partition")
            review["effective_status"] = "INCOMPLETE"
        elif (locator in (changed or []) and contract.get("profile") != "FORMAL"
              and contract["observation"]["system_partition"].get("role_mode") != "RELATIONAL"):
            review["errors"].append("changed non-FORMAL contract requires explicit RELATIONAL role_mode")
            review["effective_status"] = "INCOMPLETE"
        review["path"] = locator
        review["contract_sha256"] = contract_hash(contract)
        reviews.append(review)
        if review["contract_id"] in seen:
            errors.append(f"duplicate contract_id: {review['contract_id']}")
        seen.add(review["contract_id"])
        errors.extend(f"{locator}: {e}" for e in review["errors"])
        for identity in contract.get("identities", []):
            if identity.get("kind") == "working_file":
                coverage.setdefault(identity["path"], []).append(review["contract_id"])
    baseline = load_json(root / BASELINE) if (root / BASELINE).exists() else {"routes": [], "legacy_paths": []}
    # Explicit legacy path queue prevents registry seed coverage being mistaken for completeness.
    try:
        discovered = git(root, "ls-files", "--cached", "--others", "--exclude-standard").decode().splitlines()
    except ValueError:
        # Non-Git fixture/workspace support, without treating missing Git history as evidence.
        discovered = [p.relative_to(root).as_posix() for p in (root / "docs").rglob("*") if p.is_file()]
    current = {p for p in discovered if scientific_path(p) and (root / p).is_file()}
    formal_roots = ("docs/core/01_contracts/", "docs/core/03_lanes/", "docs/core/04_proofs/",
                    "docs/core/08_history/research_notes/")
    formal_documents = {p for p in discovered if p.startswith(formal_roots)
                        and Path(p).suffix in {".md", ".tex"} and repo_path(root, p).is_file()}
    current |= formal_documents
    routes, inventory_scope, inventory_errors = adoption_inventory(root, baseline, contracts, reviews, current)
    inventory_scope["formal_document_surfaces"] = len(formal_documents)
    errors.extend(inventory_errors)
    unreviewed = sorted(p for p in current if p not in coverage)
    missing = sorted(p for p in baseline["legacy_paths"] if not (root / p).is_file())
    changed = sorted(set(changed or []))
    for p in changed:
        covered = p in coverage or p in baseline.get("support_paths", [])
        if result_path(p) and (root / p).is_file():
            try:
                obj = load_json(root / p)
                matched = next((c for _, c in contracts if isinstance(obj, dict) and c["contract_id"] == obj.get("contract_id")), None)
                if matched is None or obj.get("contract_sha256") != contract_hash(matched) or obj.get("identities") != matched["identities"]:
                    errors.append(f"changed result lacks exact contract hash/input lineage: {p}")
                else:
                    covered = True
            except (OSError, ValueError) as exc:
                errors.append(f"invalid changed result {p}: {exc}")
        if scientific_path(p) and (root / p).is_file() and not covered:
            errors.append(f"changed scientific path needs classification/contract: {p}")
    return {"schema_version": "uet-calculation-coverage-v1", "kind": "METHODOLOGICAL_NOT_PHYSICS_GATE",
            "baseline_lineage": baseline.get("lineage", {}),
            "summary": {"contracts": len(reviews), "legacy_routes": len(baseline["routes"]),
                        "discovered_routes": len(routes), "numbered_topic_packages": inventory_scope["numbered_topic_packages"],
                        "partition_declared": sum("system_partition" in c.get("observation", {}) for _, c in contracts),
                        "partition_unreviewed": sum("system_partition:legacy_unreviewed" in r["gaps"] for r in reviews),
                        "unreviewed_current_paths": len(unreviewed), "missing_or_relocated_baseline_paths": len(missing), "errors": len(errors)},
            "contracts": reviews, "routes": routes, "inventory_scope": inventory_scope, "unreviewed_current_paths": unreviewed,
            "missing_or_relocated_baseline_paths": missing,
            "changed_paths": changed, "errors": errors, "claim_promotion": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--changed", metavar="BASE_REF")
    parser.add_argument("--emit-report", action="store_true")
    parser.add_argument("--output", default=REPORT)
    args = parser.parse_args(argv)
    if args.check and args.emit_report:
        parser.error("--check is read-only and cannot be combined with --emit-report")
    try:
        changed = git(ROOT, "diff", "--name-only", "--diff-filter=ACMR", args.changed, "HEAD").decode().splitlines() if args.changed else []
        report = build_report(ROOT, changed)
        if args.emit_report:
            target = repo_path(ROOT, args.output)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(report["summary"], sort_keys=True))
        for error in report["errors"]:
            print(error, file=sys.stderr)
        return int(bool(report["errors"]))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"calculation completeness audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
