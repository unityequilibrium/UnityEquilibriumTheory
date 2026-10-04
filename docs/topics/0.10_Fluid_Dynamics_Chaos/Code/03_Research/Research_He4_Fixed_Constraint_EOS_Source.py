"""Offline source, SI conversion and printing diagnostics; no UET mode prediction."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
DEFAULT_SOURCE = TOPIC / "Data/03_Research/he4_tn1334_fixed_constraint_eos_source_candidate.json"
CARD = TOPIC / "HE4_FIXED_CONSTRAINT_EOS_SOURCE_CARD.md"
OUTPUT = TOPIC / "Result/artifacts/he4_tn1334_fixed_constraint_eos_source_audit.json"
PHYSICAL_CONTROLLER = "vector_momentum_constitutive_origin_and_material_frame_admission_open"
SOURCE_CONTROLLER = "he4_fixed_constraint_EOS_source_found_but_covariance_entropy_anchor_and_independence_open"


@dataclass(frozen=True)
class Box:
    lo: Decimal
    hi: Decimal

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    def __add__(self, other):
        return Box(self.lo + other.lo, self.hi + other.hi)

    def __neg__(self):
        return Box(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        ends = [a * b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return Box(min(ends), max(ends))

    def __truediv__(self, other):
        if other.lo <= 0 <= other.hi:
            raise ValueError("interval denominator includes zero")
        return self * Box(Decimal(1) / other.hi, Decimal(1) / other.lo)

    def square(self):
        ends = (self.lo * self.lo, self.hi * self.hi)
        return Box(Decimal(0) if self.lo <= 0 <= self.hi else min(ends), max(ends))

    def overlaps(self, other):
        return max(self.lo, other.lo) <= min(self.hi, other.hi)

    def record(self):
        return {"lo": str(self.lo), "hi": str(self.hi)}


def exact(value):
    x = Decimal(value)
    return Box(x, x)


def printed_box(token):
    """Assumed nearest-printing enclosure only, not source physical uncertainty."""
    x = Decimal(token)
    half_ulp = Decimal(10) ** x.as_tuple().exponent / 2
    return Box(x - half_ulp, x + half_ulp)


def convert(raw, pressure_multiplier="1000000", divide_alpha=True, divide_kappa=True):
    factors = {"pressure_MPa": pressure_multiplier, "entropy_J_gK": "1000",
               "cv_J_gK": "1000", "cp_J_gK": "1000"}
    renamed = {"temperature_K": "T_K", "density_kg_m3": "rho_kg_m3",
               "pressure_MPa": "P_Pa", "entropy_J_gK": "s_J_kgK",
               "cv_J_gK": "cv_J_kgK", "cp_J_gK": "cp_J_kgK",
               "adiabatic_sound_m_s": "adiabatic_sound_m_s", "gruneisen": "gruneisen"}
    point, box = {}, {}
    for name, dest in renamed.items():
        factor = Decimal(factors.get(name, "1"))
        point[dest] = Decimal(raw[name]) * factor
        box[dest] = printed_box(raw[name]) * exact(str(factor))
    point["alpha_p_per_K"] = Decimal(raw["alpha_times_T"])
    box["alpha_p_per_K"] = printed_box(raw["alpha_times_T"])
    if divide_alpha:
        point["alpha_p_per_K"] /= point["T_K"]
        box["alpha_p_per_K"] /= box["T_K"]
    point["kappa_T_per_Pa"] = Decimal(raw["pressure_times_kappa"])
    box["kappa_T_per_Pa"] = printed_box(raw["pressure_times_kappa"])
    if divide_kappa:
        point["kappa_T_per_Pa"] /= point["P_Pa"]
        box["kappa_T_per_Pa"] /= box["P_Pa"]
    return point, box


def compatibility(box):
    rho, temperature = box["rho_kg_m3"], box["T_K"]
    cv, cp = box["cv_J_kgK"], box["cp_J_kgK"]
    alpha, kappa = box["alpha_p_per_K"], box["kappa_T_per_Pa"]
    pairs = {
        "cp_minus_cv": (cp - cv, temperature * alpha.square() / (rho * kappa)),
        "adiabatic_sound_squared": (box["adiabatic_sound_m_s"].square(),
                                    cp / (cv * rho * kappa)),
        "gruneisen": (box["gruneisen"], alpha / (rho * cv * kappa)),
    }
    return {name: {"printed": lhs.record(), "derived": rhs.record(),
                   "printing_intervals_overlap": lhs.overlaps(rhs)}
            for name, (lhs, rhs) in pairs.items()}


def all_compatible(result):
    return all(row["printing_intervals_overlap"] for row in result.values())


def audit(package, source_path):
    checks = {}

    def check(name, passed, **detail):
        checks[name] = {"pass": bool(passed), **detail}

    check("candidate_role", package["record_role"] == "SOURCE_CANDIDATE_NOT_ADMITTED_MATERIAL_EOS")
    check("source_edition", package["source"]["edition"] ==
          "NIST Technical Note 1334 revised, September 1998 PDF imprint")
    check("original_pdf_identity", package["source"]["downloaded_pdf_sha256"] ==
          "1532e4c65e1d2bc29da10db9e9ffd57e48ed46070a583bd8019581b44dc81c22")
    check("fixed_constraint_not_path_replacement",
          package["column_contract"]["cp_J_gK"]["constraint"] == "T ds/dT at fixed pressure"
          and package["column_contract"]["cv_J_gK"]["constraint"] ==
          "T ds/dT at fixed specific volume")
    check("source_phi_not_uet_Phi", package["column_contract"]["gruneisen"]["UET_Phi_equivalence"] is False)
    check("no_physical_printing_uncertainty",
          package["uncertainty_contract"]["printing_intervals_are_physical_uncertainty"] is False)
    check("locked_half_display_rule",
          package["audit_contract"]["printing_rule"] ==
          "symmetric half of the last displayed decimal unit for every raw token, including T; assumption for diagnostic compatibility only; source rounding mode not asserted")
    check("no_physical_acceptance_threshold", package["audit_contract"]["physical_acceptance_threshold"] is None)
    check("independence_not_admitted", package["ancestry"]["independent_validation_admitted"] is False)
    check("entropy_anchor_open", package["uncertainty_contract"]["entropy_reference"] ==
          "UNRESOLVED_FOR_TN1334_REVISED_EDITION")
    check("covariance_unassigned", package["uncertainty_contract"]["covariance"] is None)
    check("modern_normal_EOS_excluded", len(package["excluded_sources"]) == 1 and
          "helium II" in package["excluded_sources"][0]["reason"])
    for key in ("admitted_material_values_assigned", "physical_uet_operator_admitted",
                "physical_prediction_executed", "physical_J05_executed", "physical_J06_executed",
                "claim_promotion", "dependency_unlock"):
        check("boundary_" + key, package[key] is False)
    check("source_rows_not_empty", len(package["rows"]) == 3)

    records = []
    for row in package["rows"]:
        raw = row["raw_tokens"]
        point, box = convert(raw)
        prefix = row["row_id"]
        check(prefix + "_liquid_phase", row["phase"] == "He II liquid" and
              row["pair_position"] == "first/liquid row, not following vapor row")
        check(prefix + "_SVP_equilibrium", row["equilibrium_path"] == "SVP")
        check(prefix + "_positive_state",
              all(box[k].lo > 0 for k in ("rho_kg_m3", "P_Pa", "T_K",
                                         "s_J_kgK", "cp_J_kgK", "cv_J_kgK", "kappa_T_per_Pa")))
        check(prefix + "_negative_expansivity", box["alpha_p_per_K"].hi < 0)
        rho = point["rho_kg_m3"]
        ta = Decimal("2.53") - Decimal(".0056") * (rho - 140) - \
            Decimal(".035") * max(Decimal(0), rho - 180)
        # Check the whole printing box is below the source branch boundary.
        rho_hi = box["rho_kg_m3"].hi
        ta_min = Decimal("2.53") - Decimal(".0056") * (rho_hi - 140) - \
            Decimal(".035") * max(Decimal(0), rho_hi - 180)
        check(prefix + "_HeII_EOS_branch", 140 < box["rho_kg_m3"].lo and
              rho_hi < 190 and box["T_K"].hi < ta_min,
              T_A_at_printed_density_K=float(ta))
        check(prefix + "_transport_unknown_not_zero", all(v is None for v in row["transport"].values()))
        check(prefix + "_physical_uncertainty_unknown",
              row["physical_uncertainties"] is None and row["covariance"] is None)
        diagnostic = compatibility(box)
        for name, value in diagnostic.items():
            check(prefix + "_" + name + "_printing_compatibility", value["printing_intervals_overlap"])
        records.append({"row_id": prefix, "SI_central_values": {k: float(v) for k, v in point.items()},
                        "SI_printing_intervals": {k: v.record() for k, v in box.items()},
                        "printing_diagnostics": diagnostic,
                        "role": "fitted EOS source candidate; not admitted UET input or physical uncertainty"})

    # These deliberately incorrect interpretations are defined before execution.
    central = package["rows"][1]["raw_tokens"]
    negative = {}
    configurations = {
        "MPa_as_Pa": {"pressure_multiplier": "1"},
        "alpha_times_T_as_alpha": {"divide_alpha": False},
        "P_kappa_as_kappa": {"divide_kappa": False},
    }
    for name, kwargs in configurations.items():
        _, box = convert(central, **kwargs)
        result = compatibility(box)
        detected = not all_compatible(result)
        negative[name] = {"detected": detected, "diagnostics": result}
        check(name + "_error_detected", detected)
    vapor = dict(central, density_kg_m3="0.3292")
    _, box = convert(vapor)
    result = compatibility(box)
    detected = not all_compatible(result)
    negative["vapor_density"] = {"detected": detected, "diagnostics": result,
                                 "source_vapor_density_kg_m3": 0.3292}
    check("vapor_density_error_detected", detected)
    transport_corruption = {k: 0 for k in package["rows"][1]["transport"]}
    detected = not all(v is None for v in transport_corruption.values())
    negative["blank_transport_as_zero"] = {"detected": detected, "corrupted_values": transport_corruption}
    check("blank_transport_as_zero_detected", detected)

    requirements_path = ROOT / package["reused_inputs"][0]
    requirements = json.loads(requirements_path.read_text(encoding="utf-8"))
    check("original_admitted_inputs_remain_unassigned",
          all(row["value"] is None and row["uncertainty"] is None
              for row in requirements["required_inputs"]))
    identities = [source_path, CARD, Path(__file__).resolve()]
    identities.extend(ROOT / name for name in package["reused_inputs"])
    hashes = {}
    for path in identities:
        key = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name
        hashes[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    passing = all(row["pass"] for row in checks.values())
    return {
        "schema_version": "t010-he4-fixed-constraint-source-audit-v1",
        "date": package["date"],
        "status": "PASS_SOURCE_CANDIDATE_PRINTING_COMPATIBILITY_ONLY" if passing else
                  "SOURCE_CANDIDATE_PRINTING_DIAGNOSTIC_FAIL",
        "scope": "offline transcription metadata, SI conversion, branch selection and assumed printing compatibility",
        "input_hashes": hashes, "checks": checks,
        "check_count": len(checks), "passing_check_count": sum(r["pass"] for r in checks.values()),
        "rows": records, "negative_controls": negative,
        "printing_rule": package["audit_contract"]["printing_rule"],
        "printing_intervals_are_physical_uncertainty": False,
        "physical_acceptance_threshold": None,
        "source_acquisition_controller": SOURCE_CONTROLLER,
        "parent_input_controller": package["parent_input_controller"],
        "physical_controller": PHYSICAL_CONTROLLER,
        "remaining_blockers": package["remaining_blockers"],
        "numerical_HeII_source_rows_ingested": True,
        "admitted_material_values_assigned": False,
        "independent_validation_admitted": False,
        "physical_uet_operator_admitted": False,
        "physical_prediction_executed": False,
        "physical_J05_executed": False, "physical_J06_executed": False,
        "claim_promotion": False, "dependency_unlock": False,
        "thresholds_relaxed": False,
        "notes": [
            "Rendered source pages were inspected manually; offline audit cannot recheck upstream PDF transcription.",
            "Each thermodynamic derivative has its own fixed-variable constraint at an SVP equilibrium state.",
            "Interval enclosures may overestimate due to shared input dependence; they are not probabilistic covariance.",
            "The source adiabatic speed is not identified with the full two-fluid fast mode.",
            "No rho_s, sound eigenvalue, attenuation, UET field mapping or new parameter fit is calculated.",
            "Unresolved physical uncertainty, entropy anchor, experimental ancestry and state/protocol prevent material admission.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-json", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    source = args.source_json.resolve()
    package = json.loads(source.read_text(encoding="utf-8"))
    with localcontext() as context:
        context.prec = 60
        result = audit(package, source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(result["status"], result["passing_check_count"], "/", result["check_count"])
    return 0 if all(row["pass"] for row in result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
