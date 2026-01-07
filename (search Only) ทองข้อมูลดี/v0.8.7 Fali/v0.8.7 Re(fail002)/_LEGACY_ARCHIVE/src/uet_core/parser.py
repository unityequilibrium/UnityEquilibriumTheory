"""
Parse the 'params' field from the test matrix CSV into JSON-serializable config dicts.
Strict rule: configs written to disk must be JSON-friendly (no Python objects).

We use quartic Landau potentials:
V(u) = (a/2) u^2 + (delta/4) u^4 - s u
V'(u) = a u + delta u^3 - s
"""
from __future__ import annotations
import re
from typing import Dict, Any

def _parse_kv_list(s: str) -> Dict[str, str]:
    # split by commas but keep parentheses intact
    parts = []
    buf = []
    depth = 0
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(0, depth-1)
        if ch == ',' and depth == 0:
            part = ''.join(buf).strip()
            if part:
                parts.append(part)
            buf = []
        else:
            buf.append(ch)
    last = ''.join(buf).strip()
    if last:
        parts.append(last)
    out = {}
    for p in parts:
        if '=' in p and not p.strip().startswith(("V=","VC=","VI=")):
            k,v = p.split('=',1)
            out[k.strip()] = v.strip()
    return out

def parse_quartic(spec: str) -> Dict[str, float]:
    # spec like "quartic(a=1,delta=1,s=0)" or "quartic(aC=1,deltaC=1,sC=0)" etc.
    m = re.search(r'quartic\((.*)\)', spec.replace(' ', ''))
    if not m:
        raise ValueError(f"Cannot parse quartic potential from: {spec}")
    inside = m.group(1)
    kv: Dict[str,float] = {}
    for part in inside.split(','):
        if not part:
            continue
        k,v = part.split('=')
        kv[k]=float(v)
    # Support both standard (a,delta,s) and suffixed (aC,deltaC,sC or aI,deltaI,sI) formats
    a = float(kv.get('a', kv.get('aC', kv.get('aI', 0.0))))
    delta = float(kv.get('delta', kv.get('deltaC', kv.get('deltaI', 1.0))))
    s = float(kv.get('s', kv.get('sC', kv.get('sI', 0.0))))
    return {"type":"quartic", "a": a, "delta": delta, "s": s}

def parse_case_params(model: str, params_str: str) -> Dict[str, Any]:
    s = params_str.strip()
    # Normalize for regex scans
    s2 = re.sub(r'\s+', '', s)
    # Accept legacy aliases (older matrices / notes) like V_quartic(...), V-quartic(...), VC_quartic(...), VI_quartic(...).
    # Normalize them into the canonical V=quartic(...) / VC=quartic(...) / VI=quartic(...).
    _alias_pairs = [
        ('V_quartic(',  'V=quartic('),
        ('V-quartic(',  'V=quartic('),
        ('VC_quartic(', 'VC=quartic('),
        ('VC-quartic(', 'VC=quartic('),
        ('VI_quartic(', 'VI=quartic('),
        ('VI-quartic(', 'VI=quartic('),
    ]
    for _a, _b in _alias_pairs:
        if _a in s:
            s = s.replace(_a, _b)
    s2 = re.sub(r'\s+', '', s)

    if model == "C_only":
        kv = _parse_kv_list(s)
        kappa = float(kv.get("kappa", "1"))
        M = float(kv.get("M", "1"))
        Vm = re.search(r'V=quartic\([^\)]*\)', s2)
        if not Vm:
            raise ValueError(f"Missing V=quartic(...) in params: {params_str}")
        pot = parse_quartic(Vm.group(0).split("=",1)[1])
        return {"kappa": kappa, "M": M, "pot": pot}
    elif model == "C_I":
        kv = _parse_kv_list(s)
        kC = float(kv.get("kC", "1"))
        kI = float(kv.get("kI", "1"))
        MC = float(kv.get("MC", "1"))
        MI = float(kv.get("MI", "1"))

        # --- Mr mapping (Mr := MI/MC) ---
        Mr_in = kv.get("Mr", kv.get("M_ratio", None))
        if Mr_in is not None:
            Mr = float(Mr_in)
            if Mr <= 0:
                raise ValueError(f"Mr must be > 0, got {Mr}")

            has_MC = "MC" in kv
            has_MI = "MI" in kv

            if has_MC and (not has_MI):
                MI = Mr * MC
            elif has_MI and (not has_MC):
                MC = MI / Mr
            elif (not has_MC) and (not has_MI):
                MC = 1.0
                MI = Mr

            # push back to kv so downstream sees mapped values too
            kv["MC"] = str(MC)
            kv["MI"] = str(MI)
            kv["Mr_effective"] = str(MI / MC)

        beta = float(kv.get("beta", "0.5"))
        VCm = re.search(r'VC=quartic\([^\)]*\)', s2)
        VIm = re.search(r'VI=quartic\([^\)]*\)', s2)
        if not VCm or not VIm:
            raise ValueError(f"Missing VC/VI quartic in params: {params_str}")
        potC = parse_quartic(VCm.group(0).split("=",1)[1])
        potI = parse_quartic(VIm.group(0).split("=",1)[1])
        return {"kC": kC, "kI": kI, "MC": MC, "MI": MI, "Mr_effective": MI/MC, "beta": beta, "potC": potC, "potI": potI}
    else:
        raise ValueError(f"Unknown model: {model}")
