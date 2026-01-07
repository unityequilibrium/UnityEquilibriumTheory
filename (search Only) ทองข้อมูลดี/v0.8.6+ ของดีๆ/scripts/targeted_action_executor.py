#!/usr/bin/env python
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

def now_tag() -> str:
    return time.strftime("%Y%m%d-%H%M%S")

def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def save_json(p: Path, obj: Any):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def is_path_locked(baseline_manifest: Any, target_path: str) -> bool:
    """
    Best-effort baseline lock detection.
    Accepts manifest shapes like:
    - {"files":[{"path":"..."}], ...}
    - {"locked_files":["..."], ...}
    - {"freeze_files":["..."], ...}
    - {"locked": true} (treat all as locked)
    """
    if baseline_manifest is None:
        return False
    try:
        if isinstance(baseline_manifest, dict) and bool(baseline_manifest.get("locked", False)):
            return True
        paths=set()
        if isinstance(baseline_manifest, dict):
            if "files" in baseline_manifest and isinstance(baseline_manifest["files"], list):
                for f in baseline_manifest["files"]:
                    if isinstance(f, dict) and "path" in f:
                        paths.add(str(f["path"]))
                    elif isinstance(f, str):
                        paths.add(f)
            for k in ["locked_files", "freeze_files", "frozen_files", "paths"]:
                if k in baseline_manifest and isinstance(baseline_manifest[k], list):
                    for x in baseline_manifest[k]:
                        if isinstance(x, str):
                            paths.add(x)
                        elif isinstance(x, dict) and "path" in x:
                            paths.add(str(x["path"]))
        return (str(target_path) in paths)
    except Exception:
        return False

def load_do_not_touch(p: Optional[Path]) -> Dict[str,Any]:
    if p is None or (not p.exists()):
        return {"files": [], "groups": []}
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return {"files": [], "groups": []}
        obj.setdefault("files", [])
        obj.setdefault("groups", [])
        return obj
    except Exception:
        return {"files": [], "groups": []}

def group_is_blocked(group_key: str, dnt: Dict[str,Any]) -> bool:
    try:
        return group_key in set(dnt.get("groups", []) or [])
    except Exception:
        return False

def file_is_blocked(path: str, dnt: Dict[str,Any]) -> bool:
    try:
        return str(path) in set(dnt.get("files", []) or [])
    except Exception:
        return False

def actions_by_type(actions: List[Dict[str,Any]], typ: str) -> List[Dict[str,Any]]:
    out=[]
    for a in actions or []:
        if str(a.get("type","")).upper() == typ.upper():
            out.append(a)
    return out

def parse_group(g: str) -> Tuple[str,str,str]:
    parts = [x.strip() for x in g.split("|")]
    if len(parts) < 3:
        raise ValueError(f"Bad group key: {g}")
    return parts[0], parts[1], parts[2]

def select_group_multiplier(actions: List[Dict[str,Any]]) -> Optional[float]:
    """
    Combine multiple DECREASE_DT_PRESET actions conservatively: take the minimum multiplier.
    """
    mults=[]
    for a in actions:
        if str(a.get("type","")).upper() == "DECREASE_DT_PRESET":
            try:
                mults.append(float(a.get("multiplier")))
            except Exception:
                pass
    if not mults:
        return None
    return min(mults)

def _mul_value(obj: Any, mult: float) -> Tuple[Any, bool]:
    """
    Multiply common preset shapes:
    - number -> number*mult
    - dict with dt/dt0/dt_max/dt_preset -> multiply those fields
    """
    changed=False
    if isinstance(obj, (int, float)):
        return float(obj)*mult, True
    if isinstance(obj, dict):
        out=dict(obj)
        for k in ["dt", "dt0", "dt_max", "dt_preset", "dt_nominal"]:
            if k in out and isinstance(out[k], (int,float)):
                out[k] = float(out[k]) * mult
                changed=True
        return out, changed
    return obj, False

def apply_to_band_presets(presets: Any, band: str, model: str, integrator: str, mult: float) -> Tuple[Any, List[Dict[str,Any]]]:
    """
    Best-effort apply multiplier to band_dt_presets across likely schemas.
    Returns (new_presets, change_log).
    """
    changes=[]
    # Case A: list of rows
    if isinstance(presets, list):
        new=[]
        for row in presets:
            if isinstance(row, dict) and str(row.get("band","")).strip()==band and str(row.get("model","")).strip()==model:
                # integrator field can be 'integrator' or within dict
                integ = str(row.get("integrator","") or row.get("name","") or "").strip()
                if integ == integrator or (not integ and integrator):
                    before=row
                    after=dict(row)
                    after, ch = _mul_value(after, mult)
                    if ch:
                        changes.append({"where":"band_list_row", "band":band, "model":model, "integrator":integrator, "before":before, "after":after})
                    new.append(after)
                else:
                    new.append(row)
            else:
                new.append(row)
        return new, changes

    # Case B: nested dict
    if isinstance(presets, dict):
        new = json.loads(json.dumps(presets))  # deep copy
        # try [band][model][integrator]
        if band in new and isinstance(new[band], dict):
            if model in new[band] and isinstance(new[band][model], dict):
                mnode = new[band][model]
                # direct integrator key
                if integrator in mnode:
                    before = mnode[integrator]
                    after, ch = _mul_value(before, mult)
                    if ch:
                        mnode[integrator] = after
                        changes.append({"where":"band_dict_direct", "path":[band,model,integrator], "before":before, "after":after})
                    return new, changes
                # sometimes a field 'integrators' dict
                if "integrators" in mnode and isinstance(mnode["integrators"], dict) and integrator in mnode["integrators"]:
                    before = mnode["integrators"][integrator]
                    after, ch = _mul_value(before, mult)
                    if ch:
                        mnode["integrators"][integrator] = after
                        changes.append({"where":"band_dict_integrators", "path":[band,model,"integrators",integrator], "before":before, "after":after})
                    return new, changes
                # sometimes 'default'
                if "default" in mnode:
                    before = mnode["default"]
                    after, ch = _mul_value(before, mult)
                    if ch:
                        mnode["default"] = after
                        changes.append({"where":"band_dict_default", "path":[band,model,"default"], "before":before, "after":after})
                    return new, changes

        # fallback: scan for dict entries that mention band/model/integrator
        def walk(node, path):
            nonlocal changes
            if isinstance(node, dict):
                # heuristic match
                b = str(node.get("band","")).strip()
                m = str(node.get("model","")).strip()
                i = str(node.get("integrator","")).strip()
                if b==band and m==model and (i==integrator or (not i and integrator)):
                    before=dict(node)
                    after, ch = _mul_value(node, mult)
                    if ch:
                        # apply in place
                        node.clear()
                        node.update(after if isinstance(after, dict) else {"value": after})
                        changes.append({"where":"band_dict_scan", "path":path, "before":before, "after":after})
                for k,v in list(node.items()):
                    walk(v, path+[k])
            elif isinstance(node, list):
                for idx,v in enumerate(node):
                    walk(v, path+[idx])
        walk(new, [])
        return new, changes

    return presets, changes

def apply_to_dt_presets(presets: Any, model: str, integrator: str, mult: float) -> Tuple[Any, List[Dict[str,Any]]]:
    """
    Best-effort apply multiplier to dt_presets (no band).
    """
    changes=[]
    if isinstance(presets, list):
        new=[]
        for row in presets:
            if isinstance(row, dict) and str(row.get("model","")).strip()==model:
                integ = str(row.get("integrator","") or row.get("name","") or "").strip()
                if integ == integrator or (not integ and integrator):
                    before=row
                    after=dict(row)
                    after, ch = _mul_value(after, mult)
                    if ch:
                        changes.append({"where":"dt_list_row", "model":model, "integrator":integrator, "before":before, "after":after})
                    new.append(after)
                else:
                    new.append(row)
            else:
                new.append(row)
        return new, changes

    if isinstance(presets, dict):
        new = json.loads(json.dumps(presets))
        if model in new and isinstance(new[model], dict):
            mnode = new[model]
            if integrator in mnode:
                before = mnode[integrator]
                after, ch = _mul_value(before, mult)
                if ch:
                    mnode[integrator]=after
                    changes.append({"where":"dt_dict_direct", "path":[model,integrator], "before":before, "after":after})
                return new, changes
            if "integrators" in mnode and isinstance(mnode["integrators"], dict) and integrator in mnode["integrators"]:
                before = mnode["integrators"][integrator]
                after, ch = _mul_value(before, mult)
                if ch:
                    mnode["integrators"][integrator]=after
                    changes.append({"where":"dt_dict_integrators", "path":[model,"integrators",integrator], "before":before, "after":after})
                return new, changes
            if "default" in mnode:
                before = mnode["default"]
                after, ch = _mul_value(before, mult)
                if ch:
                    mnode["default"]=after
                    changes.append({"where":"dt_dict_default", "path":[model,"default"], "before":before, "after":after})
                return new, changes

        # scan fallback
        def walk(node, path):
            nonlocal changes
            if isinstance(node, dict):
                m = str(node.get("model","")).strip()
                i = str(node.get("integrator","")).strip()
                if m==model and (i==integrator or (not i and integrator)):
                    before=dict(node)
                    after, ch = _mul_value(node, mult)
                    if ch:
                        node.clear()
                        node.update(after if isinstance(after, dict) else {"value": after})
                        changes.append({"where":"dt_dict_scan", "path":path, "before":before, "after":after})
                for k,v in list(node.items()):
                    walk(v, path+[k])
            elif isinstance(node, list):
                for idx,v in enumerate(node):
                    walk(v, path+[idx])
        walk(new, [])
        return new, changes

    return presets, changes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--action_plan_json", required=True)
    ap.add_argument("--band_dt_presets", default="")
    ap.add_argument("--dt_presets", default="")
    ap.add_argument("--out_json", default="targeted_actions_applied.json")
    ap.add_argument("--out_md", default="targeted_actions_applied.md")
    ap.add_argument("--baseline_manifest", default="")
    ap.add_argument("--do_not_touch_json", default="")
    ap.add_argument("--respect_lock", action="store_true")
    ap.add_argument("--allow_modify_locked", action="store_true")
    ap.add_argument("--min_multiplier", type=float, default=0.1, help="do not reduce dt below this factor per run")
    ap.add_argument("--apply", action="store_true", help="write updated preset files")
    args = ap.parse_args()

    plan = load_json(Path(args.action_plan_json))
    baseline_manifest = load_json(Path(args.baseline_manifest)) if args.baseline_manifest and Path(args.baseline_manifest).exists() else None
    dnt = load_do_not_touch(Path(args.do_not_touch_json)) if args.do_not_touch_json else {"files": [], "groups": []}
    groups = plan.get("groups", []) or []

    band_path = Path(args.band_dt_presets) if args.band_dt_presets else None
    dt_path = Path(args.dt_presets) if args.dt_presets else None

    band_presets = load_json(band_path) if (band_path and band_path.exists()) else None
    dt_presets = load_json(dt_path) if (dt_path and dt_path.exists()) else None

    applied=[]
    all_changes=[]
    hold_apply = bool(plan.get("global", {}).get("hold_apply", False))

    for g in groups:
        acts = g.get("recommended_actions", []) or []
        mult = select_group_multiplier(acts)
        if mult is None:
            continue
        mult = max(float(args.min_multiplier), float(mult))
        group_key = str(g.get("group","")).strip()
        try:
            band, model, integrator = parse_group(group_key)
        except Exception:
            continue

        entry = {"group": group_key, "band": band, "model": model, "integrator": integrator, "multiplier": mult, "changes": [], "skipped": False, "skip_reasons": [], "unapplied_actions": []}
        if group_is_blocked(group_key, dnt):
            entry["skipped"] = True
            entry["skip_reasons"].append("do_not_touch_group")

        # Track other action types (informational unless extended)
        for typ in ["TUNE_BACKTRACKING","ENABLE_NUMERIC_GUARDS","DETERMINISM_DIAGNOSE","INCREASE_EVIDENCE"]:
            for a in actions_by_type(acts, typ):
                entry["unapplied_actions"].append(a)

        if entry["skipped"]:
            applied.append(entry)
            continue

        if band_presets is not None:
            new_band, ch = apply_to_band_presets(band_presets, band, model, integrator, mult)
            if ch:
                entry["changes"].extend(ch)
                band_presets = new_band
        if dt_presets is not None:
            new_dt, ch2 = apply_to_dt_presets(dt_presets, model, integrator, mult)
            if ch2:
                entry["changes"].extend(ch2)
                dt_presets = new_dt

        if entry["changes"]:
            applied.append(entry)
            all_changes.extend(entry["changes"])

    # write backups + apply (respect baseline lock / do-not-touch)
    backups=[]
    if args.apply:
        tag = now_tag()
        # Decide if we are allowed to modify each file
        allow_band = True
        allow_dt = True
        if args.respect_lock and (not args.allow_modify_locked):
            if band_path and band_path.exists():
                if file_is_blocked(str(band_path), dnt) or is_path_locked(baseline_manifest, str(band_path)):
                    allow_band = False
            if dt_path and dt_path.exists():
                if file_is_blocked(str(dt_path), dnt) or is_path_locked(baseline_manifest, str(dt_path)):
                    allow_dt = False
        if band_path and band_path.exists() and band_presets is not None and allow_band:
            bak = band_path.with_suffix(band_path.suffix + f".bak.{tag}")
            bak.write_text(band_path.read_text(encoding="utf-8"), encoding="utf-8")
            save_json(band_path, band_presets)
            backups.append({"file": str(band_path), "backup": str(bak)})
        if dt_path and dt_path.exists() and dt_presets is not None and allow_dt:
            bak = dt_path.with_suffix(dt_path.suffix + f".bak.{tag}")
            bak.write_text(dt_path.read_text(encoding="utf-8"), encoding="utf-8")
            save_json(dt_path, dt_presets)
            backups.append({"file": str(dt_path), "backup": str(bak)})
        if (not allow_band) or (not allow_dt):
            # annotate report meta via backups list
            if not allow_band and band_path:
                backups.append({"file": str(band_path), "backup": "", "note": "SKIPPED_WRITE_LOCK_GUARD"})
            if not allow_dt and dt_path:
                backups.append({"file": str(dt_path), "backup": "", "note": "SKIPPED_WRITE_LOCK_GUARD"})

    report = {
        "meta": {
            "action_plan_json": str(Path(args.action_plan_json)),
            "applied_count": len(applied),
            "hold_apply_in_plan": hold_apply,
            "apply_flag": bool(args.apply),
            "backups": backups
        },
        "applied_groups": applied
    }

    out_json = Path(args.out_json)
    save_json(out_json, report)

    # Markdown
    md=[]
    md.append("# Targeted Actions Applied (R0-E26)\n\n")
    md.append(f"- applied_count: **{len(applied)}**\n")
    md.append(f"- apply_flag: **{bool(args.apply)}**\n")
    if backups:
        md.append(f"- backups: {backups}\n")
    md.append("\n---\n\n")
    for a in applied:
        md.append(f"## {a['group']}\n")
        md.append(f"- multiplier: **{a['multiplier']}**\n")
        md.append(f"- changes: {len(a['changes'])}\n")
        for ch in a["changes"][:20]:
            md.append(f"  - {ch.get('where')} path={ch.get('path','')} \n")
        if len(a["changes"]) > 20:
            md.append(f"  - ... ({len(a['changes'])-20} more)\n")
        md.append("\n")
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("".join(md), encoding="utf-8")

    print(f"Wrote {out_json} and {out_md} | applied_groups={len(applied)}")

if __name__ == "__main__":
    main()
