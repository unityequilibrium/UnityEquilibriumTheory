"""He-II entropy source facts and ideal-reference coordinate covariance; no UET prediction."""
from __future__ import annotations
import argparse
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
CONTRACT = TOPIC / "Data/03_Research/he4_entropy_source_and_reference_contract.json"
CARD = TOPIC / "HE4_ENTROPY_SOURCE_AND_REFERENCE_CONTRACT.md"
REGISTRY = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_entropy_reference_addendum.json"
OUTPUT = TOPIC / "Result/artifacts/he4_entropy_source_reference_audit.json"
REFERENCE_PATH = TOPIC / "Code/03_Research/Research_Fluid_Two_Fluid_EOS_Reference.py"
spec = importlib.util.spec_from_file_location("standard_two_fluid_entropy_reference", REFERENCE_PATH)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


def shifted_state(base, a):
    """Chain rule for e*(rho,sigma*)=e(rho,sigma*-a*rho)."""
    return dict(base, sigma=base["sigma"] + a * base["rho"],
                A=base["A"] - 2 * a * base["B"] + a * a * base["D"],
                B=base["B"] - a * base["D"])


def assembled_operator(c, a, entropy_correction=True, phase_correction=True):
    """Explicit flux/force rows; independent of matrix similarity construction."""
    r, rs, sg = c["rho"], c["rho_s"], c["sigma"]
    rn = r - rs
    A, B, D = c["A"], c["B"], c["D"]
    M = np.array([[0, 0, 1, 0],
                  [0, 0, sg / rn, -sg * rs / rn],
                  [r * A + sg * B, r * B + sg * D, 0, 0],
                  [A, B, 0, 0]], float)
    if entropy_correction:
        M[1, 2] -= a * rs / rn
        M[1, 3] += a * rs * r / rn
    if phase_correction:
        M[3, 0] += a * B
        M[3, 1] += a * D
    H = np.zeros((4, 4))
    H[:2, :2] = [[A, B], [B, D]]
    H[2:, 2:] = [[1 / rn, -rs / rn], [-rs / rn, rs * r / rn]]
    return M, H


def audit(package, contract_path):
    rules = package["verification"]
    tol, floor = rules["identity_tolerance"], rules["negative_control_floor"]
    checks = {}

    def boolean(name, value):
        checks[name] = {"pass": bool(value)}

    def close(name, value):
        checks[name] = {"metric": float(value), "threshold": tol,
                        "pass": bool(np.isfinite(value) and value <= tol)}

    def greater(name, value, minimum=0.):
        checks[name] = {"metric": float(value), "minimum": minimum,
                        "pass": bool(np.isfinite(value) and value > minimum)}

    boolean("candidate_and_reference_role", package["record_role"] == "SOURCE_CANDIDATE_AND_STANDARD_REFERENCE_ONLY")
    boolean("review_pdf_identity", package["source"]["downloaded_pdf_sha256"] ==
            "c3e03d88b803d36628587638be98e0f3af1e6613b15f81e04eedcc17f3d5442e")
    boolean("two_distinct_source_branches", package["branches"]["fountain"]["table"] == "8.3" and
            package["branches"]["calorimetric"]["table"] == "8.5")
    boolean("calorimetric_branch_anchor_explicit", package["branches"]["calorimetric"]["anchor_status"] ==
            "ZERO_TEMPERATURE_INTEGRATION_CONVENTION_EXPLICIT_FOR_TABLE_8_5")
    boolean("calorimetric_input_not_independent", package["branches"]["calorimetric"]["independent_of_its_heat_capacity_input"] is False)
    boolean("fountain_primary_date_corrected", package["primary_fountain_source"]["publication_date"] == "1984-05-01" and
            package["primary_fountain_source"]["review_bibliography_year"] == 1983 and
            package["primary_fountain_source"]["doi"] == "10.1103/PhysRevB.29.4951")
    boolean("precision_not_row_uncertainty", package["primary_fountain_source"]["row_standard_uncertainty"] is None and
            package["primary_fountain_source"]["covariance"] is None)
    boolean("branch_covariance_unknown", all(b["covariance"] is None and b["per_row_uncertainty"] is None
            for b in package["branches"].values()))
    boolean("SI_multiplier_J_g_to_J_kg", package["source"]["SI_multiplier"] == "1000")
    comp = package["nominal_comparison"]
    boolean("nominal_comparison_only", comp["role"] == "DESCRIPTIVE_CENTRAL_DIFFERENCES_ONLY" and
            comp["same_physical_temperature_established"] is False and
            comp["temperature_interpolation_performed"] is False and comp["constant_offset_fitted"] is False and
            comp["physical_acceptance_threshold"] is None and comp["printing_intervals_are_physical_uncertainty"] is False)
    boolean("industrial_reference_not_transferred", package["reference_state_screen"]["TN1334_reference_identity_established"] is False and
            package["reference_state_screen"]["physical_entropy_offset_assigned"] is None)
    boolean("locked_contract", rules["locked_before_first_execution"] is True and
            tol == 1e-10 and floor == 1e-8 and rules["offsets"] == [-.3, 0, .4, 1.] and rules["periodic_grid"] == 32)
    for key in ("TN1334_entropy_anchor_resolved", "admitted_material_values_assigned",
                "independent_validation_admitted", "physical_uet_operator_admitted",
                "physical_prediction_executed", "physical_J05_executed", "physical_J06_executed",
                "claim_promotion", "dependency_unlock"):
        boolean("boundary_" + key, package[key] is False)

    prior = json.loads((ROOT / comp["prior_source"]).read_text(encoding="utf-8"))
    old_rows = {Decimal(row["raw_tokens"]["temperature_K"]): row for row in prior["rows"]}
    boolean("source_rows_three_by_two", len(package["rows"]) == 3)
    source_rows = []
    factor = Decimal(package["source"]["SI_multiplier"])
    for row in package["rows"]:
        T = Decimal(row["T90_raw"])
        old = old_rows[T]["raw_tokens"]
        fp = Decimal(row["fountain_entropy_raw"]) * factor
        cal = Decimal(row["calorimetric_entropy_raw"]) * factor
        tn = Decimal(old["entropy_J_gK"]) * 1000
        boolean(str(T) + "/source_positive", T > 0 and fp > 0 and cal > 0)
        source_rows.append({"nominal_T90_K": float(T), "fountain_s_J_kgK": float(fp),
                            "calorimetric_s_J_kgK": float(cal), "TN1334_nominal_s_J_kgK": float(tn),
                            "TN_minus_fountain_J_kgK": float(tn - fp), "TN_minus_calorimetric_J_kgK": float(tn - cal),
                            "role": "descriptive central differences; temperature/reference/physical covariance not reconciled"})
    # Unit control does not decide physical source compatibility.
    greater("J_per_g_as_J_per_kg_error_detected",
            abs(float(Decimal(package["rows"][1]["fountain_entropy_raw"]) * (1000 - 1))), floor)

    base = rules["base"]
    old_contract = json.loads((TOPIC / "Data/03_Research/fluid_two_fluid_eos_reference_contract.json").read_text(encoding="utf-8"))
    boolean("unchanged_standard_normalized_base", base == old_contract["verification"]["base"])
    M, H = reference.operator(base)
    th = reference.thermodynamics(base)
    n = rules["periodic_grid"]
    x = 2 * np.pi * np.arange(n) / n
    fields = np.array([.1 * np.sin(x) + .04 * np.cos(2*x), .08 * np.cos(x) + .03 * np.sin(3*x),
                       .12 * np.sin(2*x) + .07 * np.cos(x), .09 * np.cos(2*x) + .05 * np.sin(3*x)])
    kx = np.fft.fftfreq(n, 1 / n)

    def dx(f):
        return np.fft.ifft(1j * kx * np.fft.fft(f, axis=-1), axis=-1).real

    offsets = []
    for a in rules["offsets"]:
        prefix = str(a) + "/"
        new = shifted_state(base, a)
        L = np.eye(4)
        L[1, 0] = a
        Linv = np.eye(4)
        Linv[1, 0] = -a
        direct, work = assembled_operator(new, a)
        conjugated = L @ M @ Linv
        congruence = Linv.T @ H @ Linv
        close(prefix + "explicit_flux_force_equals_similarity", reference.relative(direct, conjugated))
        close(prefix + "Hessian_equals_congruence", reference.relative(work, congruence))
        greater(prefix + "positive_quadratic_availability", np.min(np.linalg.eigvalsh(work)))
        close(prefix + "reciprocal_work", reference.rms(work @ direct - (work @ direct).T))
        close(prefix + "characteristic_speeds_invariant", reference.match(np.linalg.eigvals(direct), np.linalg.eigvals(M)))
        new_th = reference.thermodynamics(new)
        for key in ("c_T_squared", "c_S_squared", "c_v", "c_p"):
            close(prefix + key + "_invariant", reference.relative(new_th[key], th[key]))
        physical_s = (new["sigma"] - a * new["rho"]) / new["rho"]
        corrected_v = new["rho_s"] / (new["rho"] - new["rho_s"]) * new["T"] * physical_s**2 / new_th["c_v"]
        close(prefix + "physical_entropy_speed_term_recovered", reference.relative(corrected_v, th["v_entropy_squared"]))
        # Non-equilibrium points test pressure and conjugates by the EOS chain rule.
        r, sg = base["rho"] + .02, base["sigma"] - .03
        e, mu, temperature, pressure = reference.potentials(r, sg, base)
        sg_star, mu_star = sg + a*r, mu - a*temperature
        close(prefix + "Gibbs_pressure_invariant", reference.relative(r*mu_star + sg_star*temperature - e, pressure))
        close(prefix + "chemical_potential_force_recovered", reference.relative(mu_star + a*temperature, mu))
        fstar = L @ fields
        rate = -direct @ dx(fstar)
        rn, rs = new["rho"] - new["rho_s"], new["rho_s"]
        vn = (fstar[2] - rs*fstar[3]) / rn
        entropy_flux = new["sigma"]*vn - a*rs*(vn - fstar[3])
        mu_perturbed = new["A"]*fstar[0] + new["B"]*fstar[1]
        T_perturbed = new["B"]*fstar[0] + new["D"]*fstar[1]
        close(prefix + "local_transformed_entropy_current", reference.rms(rate[1] + dx(entropy_flux)))
        close(prefix + "local_transformed_phase_force", reference.rms(rate[3] + dx(mu_perturbed + a*T_perturbed)))
        close(prefix + "quadratic_availability_invariant",
              reference.relative(np.einsum("in,ij,jn->n", fstar, work, fstar),
                                 np.einsum("in,ij,jn->n", fields, H, fields)))
        flux = .5*np.einsum("in,ij,jn->n", fstar, work @ direct, fstar)
        close(prefix + "local_quadratic_work_balance",
              reference.rms(np.einsum("in,ij,jn->n", fstar, work, rate) + dx(flux)))
        record = {"offset": a, "correct_characteristic_speeds": sorted(np.linalg.eigvals(direct).real.tolist()),
                  "correct_reciprocal_work_defect": reference.rms(work @ direct - (work @ direct).T)}
        if a != 0:
            wrong_entropy, _ = assembled_operator(new, a, entropy_correction=False)
            wrong_phase, _ = assembled_operator(new, a, phase_correction=False)
            naive, naive_work = reference.operator(new)
            entropy_defect = reference.rms((-wrong_entropy @ dx(fstar))[1] + dx(entropy_flux))
            phase_defect = reference.rms((-wrong_phase @ dx(fstar))[3] + dx(mu_perturbed + a*T_perturbed))
            speed_defect = reference.match(np.linalg.eigvals(naive), np.linalg.eigvals(M))
            greater(prefix + "omit_entropy_flux_correction_detected", entropy_defect, floor)
            greater(prefix + "omit_phase_force_correction_detected", phase_defect, floor)
            greater(prefix + "omit_both_characteristic_speeds_error_detected", speed_defect, floor)
            greater(prefix + "omit_both_operator_correspondence_error_detected", reference.relative(naive, conjugated), floor)
            # The wrong model still passes its own positive-work test.
            greater(prefix + "wrong_model_positive_availability", np.min(np.linalg.eigvalsh(naive_work)))
            close(prefix + "wrong_model_own_reciprocal_work_passes", reference.rms(naive_work @ naive - (naive_work @ naive).T))
            record["negative_controls"] = {"omit_entropy_flux_local_defect": entropy_defect,
                "omit_phase_force_local_defect": phase_defect,
                "omit_both_normalized_speed_error": speed_defect,
                "naive_characteristic_speeds": sorted(np.linalg.eigvals(naive).real.tolist()),
                "naive_own_work_defect": reference.rms(naive_work @ naive - (naive_work @ naive).T),
                "role": "different synthetic model can pass positive-work audit; not He-II prediction"}
        else:
            close(prefix + "zero_offset_returns_original", reference.relative(direct, M))
        offsets.append(record)

    # M,L,T unit exponents. a is specific entropy, not dimensionless physical entropy.
    dimensions = {"rho": (1,-3,0,0), "sigma": (1,-1,-2,-1), "a": (0,2,-2,-1),
                  "T": (0,0,0,1), "mu": (0,2,-2,0),
                  "A": (-1,5,-2,0), "B": (-1,3,0,1), "D": (-1,1,2,2)}
    add = lambda *names: tuple(sum(dimensions[name][i] for name in names) for i in range(4))
    for name, lhs, rhs in [("a_rho_is_sigma", ("a","rho"), "sigma"), ("a_T_is_mu", ("a","T"), "mu"),
                           ("a_B_is_A", ("a","B"), "A"), ("a_a_D_is_A", ("a","a","D"), "A"),
                           ("a_D_is_B", ("a","D"), "B")]:
        boolean("SI_dimension/" + name, add(*lhs) == dimensions[rhs])

    requirements = json.loads((TOPIC / "Data/03_Research/he4_two_fluid_thermodynamic_input_requirements.json").read_text(encoding="utf-8"))
    boolean("original_material_requirements_stay_null", all(i["value"] is None and i["uncertainty"] is None
            for i in requirements["required_inputs"]))
    paths = [contract_path, CARD, REGISTRY, Path(__file__).resolve()] + [ROOT / name for name in package["reused_inputs"]]
    hashes = {p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.name:
              hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    passed = all(c["pass"] for c in checks.values())
    return {"schema_version":"t010-he4-entropy-source-reference-audit-v1", "date": package["date"],
            "status":"PASS_SOURCE_AND_REFERENCE_COORDINATE_CHECKS_ONLY" if passed else "SOURCE_OR_REFERENCE_CHECK_FAIL",
            "scope":"source branch/units/nominal differences and normalized ideal two-fluid coordinate covariance",
            "check_count":len(checks), "passing_check_count":sum(c["pass"] for c in checks.values()),
            "checks": checks, "input_hashes":hashes, "source_rows":source_rows, "normalized_offset_controls":offsets,
            "locked_tolerances":{"identity_tolerance":tol, "negative_control_floor":floor},
            "source_acquisition_controller":package["source_acquisition_controller"],
            "parent_input_controller":package["parent_input_controller"], "physical_controller":package["physical_controller"],
            "remaining_blockers":package["remaining_blockers"],
            "calorimetric_branch_reference_known":True, "TN1334_entropy_anchor_resolved":False,
            "admitted_material_values_assigned":False, "independent_validation_admitted":False,
            "physical_uet_operator_admitted":False, "physical_prediction_executed":False,
            "physical_J05_executed":False,"physical_J06_executed":False,
            "claim_promotion":False,"dependency_unlock":False,"thresholds_relaxed":False,
            "physical_acceptance_threshold":None, "entropy_offset_fitted":False,
            "notes":["Offline checks do not independently re-read the source PDF; manual rendered-page review is separately documented.",
                     "Table 8.5 zero-temperature integration anchor is not TN1334 edition closure.",
                     "Nominal temperature differences are descriptive, without scale interpolation or uncertainty propagation.",
                     "Correct complete coordinate change preserves poles; partial constitutive replacement changes the synthetic model.",
                     "Positive reciprocal quadratic work alone cannot certify entropy-reference correspondence.",
                     "No physical He-II eigenvalues, UET parameter fit, trajectory, dissipative closure or external validation."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-json", type=Path, default=CONTRACT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    path = args.contract_json.resolve()
    result = audit(json.loads(path.read_text(encoding="utf-8")), path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(result["status"], result["passing_check_count"], "/", result["check_count"])
    if result["passing_check_count"] != result["check_count"]:
        print("FAIL:", [name for name,c in result["checks"].items() if not c["pass"]])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
