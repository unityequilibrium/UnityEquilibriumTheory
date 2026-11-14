"""Three source-bound physical screens; not a parent fit or physical admission.

Only the committed extracted subset is read. No network, roots, old producer,
trajectories or hidden material constants. Curated source verdicts and exact
diagnostic witnesses are distinguished in the artifact.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys

import sympy as s

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import (
    artifact_metadata, contract_hash, load_json, validate_contract,
)

TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
STEM = "physical_platform_correspondence_screen"
CONTRACT = f"{TOPIC}/calculation_contracts/{STEM}.json"
INPUT = f"{TOPIC}/Data/03_Research/{STEM}_sources.json"
OUTPUT = f"{TOPIC}/Result/artifacts/t13_{STEM}.json"
BASELINE = "d9a1a2833d62b026c390506ec77230359bb20798"
PLATFORMS = ("Mn_CuN", "Fe_Neel", "Pt_junction")
RELATIONS = {"EQUIVALENT", "APPROXIMATE", "DIFFERENT", "UNRESOLVED"}
ORIGINS = {"SI_DEFINITION", "OFFICIAL_STANDARD", "OBSERVED_REPORTED",
           "FIT_FROM_SOURCE_MODEL", "MODEL_CHOICE", "THEORETICAL_SOURCE_MODEL"}
UNCERTAINTIES = {"UNKNOWN", "NOT_APPLICABLE_MODEL_CHOICE", "EXACT_DEFINITION",
                 "REPORTED_STANDARD_UNCERTAINTY", "REPORTED_ERRORBAR_CONFIDENCE_UNKNOWN",
                 "REPORTED_PARENTHETICAL_NOT_HARD_BOUND"}


class CorrespondenceMissing(ValueError):
    pass


def rational(value):
    if type(value) not in (str, int, F):
        raise ValueError("exact decimal/rational string required, not bool/float")
    return F(value)


def validate_subset(data):
    if data["schema_version"] != "uet-physical-platform-source-subset-v1" or data["baseline_commit"] != BASELINE:
        raise ValueError("source-subset schema/baseline changed")
    if tuple(p["id"] for p in data["platforms"]) != PLATFORMS:
        raise ValueError("only the three approved platforms in fixed order")
    sources = {a["id"]: a for a in data["sources"]}
    if len(sources) != len(data["sources"]):
        raise ValueError("duplicate source")
    if len(set(sources)-{"si", "ciaaw", "nist"}) > 9:
        raise ValueError("bounded scientific-source budget exceeded")
    for src in sources.values():
        for key in ("url", "version", "read_scope", "access", "terms", "role"):
            if not src.get(key):
                raise ValueError("source provenance incomplete: "+key)
        if src.get("upstream_sha256") is not None:
            raise ValueError("this subset did not archive remote bytes; no invented upstream hash")
    facts = {a["id"]: a for a in data["facts"]}
    if len(facts) != len(data["facts"]):
        raise ValueError("duplicate fact")
    for fact in data["facts"]+data["constants"]:
        if fact["source"] not in sources or fact["origin"] not in ORIGINS or not fact.get("locator"):
            raise ValueError("fact source/origin/locator incomplete")
        if sources[fact["source"]]["access"] == "METADATA_ONLY":
            raise ValueError("abstract/metadata is not parameter evidence")
        rational(fact["value"])
        u = fact["uncertainty"]
        if u["kind"] not in UNCERTAINTIES:
            raise ValueError("unreviewed uncertainty convention")
        if u["kind"] in ("UNKNOWN", "NOT_APPLICABLE_MODEL_CHOICE") and u["value"] is not None:
            raise ValueError("unknown uncertainty must not become zero or a guessed error")
        if u["kind"] == "EXACT_DEFINITION":
            if fact["origin"] != "SI_DEFINITION" or fact["source"] != "si" or rational(u["value"]) != 0:
                raise ValueError("only declared SI defining values have zero uncertainty here")
        elif u["value"] is not None and rational(u["value"]) <= 0:
            raise ValueError("reported source uncertainty must remain nonzero")
    for p in data["platforms"]:
        if len(p["sources"]) > 3 or any(a not in sources for a in p["sources"]):
            raise ValueError("seed plus at most two source follow-ups")
        for rel in p["relations"]:
            if rel["outcome"] not in RELATIONS or not rel["reason"] or not rel["evidence"]:
                raise ValueError("scoped verdict needs reason/evidence")
            if any(a not in facts for a in rel["evidence"]):
                raise ValueError("unknown verdict evidence")
    return sources, facts


def constants(data):
    out = {v["id"]: rational(v["value"]) for v in data["constants"]}
    if min(out[k] for k in ("h", "e", "k_B", "u")) <= 0:
        raise ValueError("positive constants required")
    return out


def si_factor(unit, c):
    factors = {"J": (F(1), "J"), "eV": (c["e"], "J"), "meV": (c["e"]/1000, "J"),
               "m": (F(1), "m"), "nm": (F(1, 10**9), "m"),
               "angstrom": (F(1, 10**10), "m"), "s": (F(1), "s"),
               "ns": (F(1, 10**9), "s"), "K": (F(1), "K"),
               "T": (F(1), "T"), "kg": (F(1), "kg"), "1": (F(1), "1")}
    if unit not in factors:
        raise ValueError("unit needs an explicit convention: "+unit)
    return factors[unit]


def convert_fact(fact, c):
    factor, unit = si_factor(fact["unit"], c)
    u = deepcopy(fact["uncertainty"])
    if u["value"] is not None:
        if u.get("unit", fact["unit"]) != fact["unit"]:
            raise ValueError("uncertainty/source unit mismatch")
        u["value"] = str(rational(u["value"])*abs(factor))
        u["unit"] = unit
    return {"fact_id": fact["id"], "source_id": fact["source"], "context": fact["context"],
            "source_value": fact["value"], "source_unit": fact["unit"],
            "value_SI": str(rational(fact["value"])*factor), "unit_SI": unit,
            "origin": fact["origin"], "uncertainty_SI": u,
            "parent_parameter": False, "is_hard_interval": False}


def frequency_energy(value, unit, c):
    value = s.Rational(str(rational(value)))
    if value < 0:
        raise ValueError("positive frequency magnitude required")
    h = s.Rational(str(c["h"]))
    if unit == "Hz":
        return h*value
    if unit == "rad/s":
        return h*value/(2*s.pi)
    raise ValueError("cyclic versus angular convention required")


def same_context(*facts):
    if not facts or len({f["context"] for f in facts}) != 1:
        raise ValueError("cross-geometry/preparation/source tuple is not admitted")
    return True


def require_parent_dictionary(p):
    reasons = [f"{r['component']}:{r['outcome']}" for r in p["relations"]
               if r["outcome"] != "EQUIVALENT"]
    if p["native_binary_projection"] != "EQUIVALENT":
        reasons.append("closed two-state projection not established")
    if p["mechanical_boundary"] != "FREE_OPEN_N4":
        reasons.append("source support/leads not the free parent boundary")
    if p["readout_kind"] != "CALIBRATED_PHI":
        reasons.append("source readout is not calibrated Phi")
    if p["frozen_sector_preparation"] != "EQUIVALENT":
        reasons.append("source frozen sector not established")
    d = p["physical_scale_dictionary"]
    if any(d[k] is None for k in ("mu", "d_ref", "J_ref")):
        reasons.append("mu,d_ref,J_ref dictionary missing")
    if reasons:
        raise CorrespondenceMissing("; ".join(reasons))
    if any(rational(d[k]) <= 0 for k in ("mu", "d_ref", "J_ref")):
        raise ValueError("positive physical scales required")
    return d


def spin_matrices(spin):
    S = s.Rational(str(rational(spin)))
    if S < s.Rational(1, 2) or not (2*S).is_integer:
        raise ValueError("positive integer/half-integer quantum spin required")
    dim = int(2*S+1)
    plus = s.zeros(dim)
    for i in range(1, dim):
        m = S-i
        plus[i-1, i] = s.sqrt(S*(S+1)-m*(m+1))
    return s.diag(*[S-i for i in range(dim)]), plus, plus.T


def spin_witness(spin):
    S = rational(spin)
    sz, sp, sm = spin_matrices(S)
    d = sz.rows
    H = s.kronecker_product(sz, sz)+(s.kronecker_product(sp, sm)+s.kronecker_product(sm, sp))/2
    source, leaked = d-1, 2*d-2  # |S,-S> -> |S-1,-S+1>
    leakage = H[leaked, source]
    return {"source_spin": str(S), "single_site_quantum_dimension": d,
            "conditional_four_site_dimension": d**4,
            "four_site_dimension_is_model_comparison_not_reported_sample_size": True,
            "parent_four_binary_label_count": 16,
            "collinear_coefficient_over_positive_source_J": str(S*S),
            "required_parent_bond_prefactor_over_source_J": str(-4*S*S),
            "negative_prefactor_is_sign_witness_not_Jref_mapping": True,
            "off_projected_doublet_matrix_element_over_J": str(leakage),
            "projected_doublet_not_invariant": bool(S > F(1, 2) and leakage != 0)}


def symbolic_checks():
    J, Jr, S, f = s.symbols("J Jr S f", positive=True)
    h = s.Matrix([1/s.sqrt(5), 0, 0])
    endpoint = s.Matrix([-3/s.sqrt(5), 0, -1/s.sqrt(5)])
    null = s.Matrix([1, 0, -3])
    labels = tuple(product((-1, 1), repeat=4))
    stagger = lambda a: tuple((-1)**i*v for i, v in enumerate(a))
    bonds = lambda a: sum(a[i]*a[i+1] for i in range(3))
    C = lambda a: F(sum(a), 4)
    return {
        "native_gap_order_reversed": s.simplify((2*J*S**2)-(-Jr*f/2)) == 2*J*S**2+Jr*f/2,
        "matching_native_bond_requires_negative_parent_prefactor": s.solve(s.Eq(J*S**2, -Jr/4, evaluate=False), Jr, check=False) == [-4*J*S**2],
        "spin_half_factor4": s.Rational(1, 2)**2 == s.Rational(1, 4),
        "spin2_projection_factor16_not4": 4*s.Integer(2)**2 == 16,
        "staggering_is_involution": all(stagger(stagger(a)) == a for a in labels),
        "staggering_reverses_only_collinear_bond_sign": all(bonds(stagger(a)) == -bonds(a) for a in labels),
        "staggering_changes_C": any(C(stagger(a)) != C(a) for a in labels),
        "Neel_pair_same_population_C": C((-1, 1, -1, 1)) == C((1, -1, 1, -1)) == 0,
        "Neel_pair_distinct_staggered_readout": C(stagger((-1, 1, -1, 1))) != C(stagger((1, -1, 1, -1))),
        "Neel_maps_to_uniform_parent_labels": len(set(stagger((-1, 1, -1, 1)))) == 1,
        "parent_alternating_maps_to_physical_uniform": len(set(stagger((1, -1, 1, -1)))) == 1,
        "endpoint_null_direction": endpoint.dot(null) == 0 and h.dot(null) != 0,
        "Phi_not_endpoint_only": h.cross(endpoint) != s.zeros(3, 1),
        "open_N4_bonds": len(tuple(zip(range(4), range(1, 4)))) == 3,
        "total_vs_per_site_factor4": s.Rational(1, 4)*4 == 1,
        "Mn_doublet_leakage": spin_witness(F(5, 2))["projected_doublet_not_invariant"],
        "Fe_doublet_leakage": spin_witness(2)["projected_doublet_not_invariant"],
    }


def inherited_evidence():
    summaries = {}
    for stem in ("parent_static_reference_audit", "phi_variance_static_admissibility"):
        path = f"{TOPIC}/calculation_contracts/{stem}.json"
        contract = load_json(ROOT/path)
        check = validate_contract(contract, ROOT)
        if check["errors"]:
            raise ValueError("inherited source identity changed: "+"; ".join(check["errors"]))
        artifact = load_json(ROOT/f"{TOPIC}/Result/artifacts/t13_{stem}.json")
        if artifact["contract_sha256"] != contract_hash(contract) or artifact["identities"] != contract["identities"]:
            raise ValueError("inherited artifact/contract binding changed")
        summaries[stem] = {"contract_sha256": contract_hash(contract), "identities": len(contract["identities"])}
    return summaries


def scope_check(record):
    if record["physical_acceptance"] or record["quantum_parent_validated"] or record["candidate_selected"]:
        raise ValueError("diagnostic source screen cannot promote a physical candidate or quantum parent")
    if any(p["theta"] is not None or p["chi"] is not None or p["Var_Phi"] is not None for p in record["platforms"]):
        raise ValueError("no admitted source-to-parent dictionary: physical scale/variance substitution forbidden")
    return True


def negative_controls(data):
    def rejected(call):
        try:
            call()
        except ValueError:
            return True
        return False
    b = deepcopy(data)
    b["facts"][0]["uncertainty"] = {"kind":"UNKNOWN", "value":"0"}
    bad_metadata = deepcopy(data)
    bad_metadata["facts"][0]["source"] = "fe2012"
    filled = deepcopy(data["platforms"][0])
    filled["physical_scale_dictionary"].update(mu="1e-25", d_ref="3.6e-10", J_ref="1e-21")
    facts = {f["id"]:f for f in data["facts"]}
    stub = {"physical_acceptance":False, "quantum_parent_validated":False, "candidate_selected":False,
            "platforms":[{"theta":None, "chi":None, "Var_Phi":None}]}
    guessed = deepcopy(stub)
    guessed["platforms"][0]["Var_Phi"] = "0"
    c = constants(data)
    return {
        "unknown_uncertainty_to_zero_rejected": rejected(lambda:validate_subset(b)),
        "abstract_parameter_evidence_rejected": rejected(lambda:validate_subset(bad_metadata)),
        "cross_paper_tuple_rejected": rejected(lambda:same_context(facts["fe_J"],facts["fe_deltaT1"])),
        "base_temperature_substitution_rejected": rejected(lambda:same_context(facts["pt_T"],facts["pt_baseT"])),
        "scales_without_correspondence_rejected": rejected(lambda:require_parent_dictionary(filled)),
        "quantum_parent_promotion_rejected": rejected(lambda:scope_check(dict(stub,quantum_parent_validated=True))),
        "guessed_Phi_variance_rejected": rejected(lambda:scope_check(guessed)),
        "Hz_angular_confusion_distinguished": frequency_energy(1,"Hz",c) != frequency_energy(1,"rad/s",c),
    }


def calculate():
    data = load_json(ROOT/INPUT)
    sources, facts = validate_subset(data)
    c = constants(data)
    checks, controls = symbolic_checks(), negative_controls(data)
    if not all(checks.values()) or not all(controls.values()):
        raise ValueError("correspondence witness failed")
    rows = []
    for p in data["platforms"]:
        try:
            require_parent_dictionary(p)
        except CorrespondenceMissing as exc:
            reason = str(exc)
        else:
            raise ValueError("unexpected admitted platform: new review needed before any scale calculation")
        rows.append({"id": p["id"], "curated_relations": p["relations"],
                     "verdict_scope": "native inspected source description versus unchanged parent; not all realizations in nature",
                     "full_native_correspondence": "DIFFERENT" if any(r["outcome"] == "DIFFERENT" for r in p["relations"]) else "UNRESOLVED",
                     "physical_scale_omission_reason": reason,
                     "spin_witness": spin_witness(facts[p["spin_fact"]]["value"]) if p["spin_fact"] else None,
                     "theta": None, "chi": None, "Var_Phi": None,
                     "physical_acceptance": False, "source_ids": p["sources"]})
    result = {"source_baseline_commit": BASELINE, "completed_sections": ["S0", "S1", "S2", "S3", "S4"],
              "inherited_evidence": inherited_evidence(), "input_product_level": data["product_level"],
              "source_access": [{k: src[k] for k in ("id", "access", "read_scope", "version", "url")} for src in sources.values()],
              "facts_SI": [convert_fact(f, c) for f in data["facts"]], "platforms": rows,
              "checks": checks, "negative_controls":controls,
              "interpretation": {"curated_verdicts": "Human-inspectable source judgments, not learned automatically from platform names or a new physics gate.",
                   "spin_sign": "Native collinear matching would require negative parent bond prefactor; classical staggering changes C/readout/prepared sector and does not give quantum Heisenberg equivalence.",
                   "readout": "Endpoint null direction (1,0,-3) leaves endpoint unchanged but changes Phi; conductance/spectroscopy need an independent operator.",
                   "mass": "CIAAW atomic weights/u are context, never the collective modal mass.",
                   "access": "Original Fe2012 main text unresolved.2013 theory and partially accessed2017 experiment remain distinct source contexts."},
              "physical_acceptance": False, "quantum_parent_validated": False, "candidate_selected": False,
              "budgets_selected": False, "old_producers_rerun": False, "trajectories": 0,
              "parameter_sweeps": 0, "new_parent_terms": 0, "additional_platforms_beyond_approved": 0,
              "source_physics_disproved": False, "UET_disproved_or_validated": False,
              "next_controller": "physical-parent-preparation: native state/energy/boundary/readout correspondence is missing before scale substitution. Review the free-chain/frozen-sector premise; no model revision or new platform automatically.",
              "quantum_parent_controller": "UNCHANGED: separate actual quantum-parent state/operator/anharmonic bound absent"}
    scope_check(result)
    return result


def record():
    return {**artifact_metadata(load_json(ROOT/CONTRACT), ROOT), **calculate()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only source/identity/artifact check")
    mode.add_argument("--emit-report", action="store_true", help="write only the new screening artifact")
    args = parser.parse_args(argv)
    result = record()
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+"\n"
    if args.emit_report:
        (ROOT/OUTPUT).write_text(payload, encoding="utf-8", newline="\n")
    elif not (ROOT/OUTPUT).is_file() or (ROOT/OUTPUT).read_bytes() != payload.encode("utf-8"):
        raise ValueError("artifact missing/stale; inspect before explicit --emit-report")
    print(json.dumps(dict(platforms=len(result["platforms"]), checks=len(result["checks"]), negative_controls=len(result["negative_controls"]),
                          physical_acceptance=False, review=result["contract_review_status"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
