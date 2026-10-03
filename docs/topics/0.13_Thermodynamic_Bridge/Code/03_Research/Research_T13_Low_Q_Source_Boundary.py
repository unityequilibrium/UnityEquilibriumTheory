"""Versioned author tables and explicit omitted-basis estimator boundary.

Source interpolation estimates are exposed comparison controls, never a
native UET parameter calibration. Missing errors and ancestry remain open.
"""

from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import combinations
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
import mpmath as mp

LOCAL = Path(__file__).resolve().parent
sys.path.insert(0, str(LOCAL))
import Research_T13_Multi_Q_Estimator as M

ROOT, PREFIX, TH = M.ROOT, M.PREFIX, M.TH
REGISTRY = PREFIX+"Data/03_Research/t13_low_q_source_protocol.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_low_q_source_boundary.json")
FIRST_FAILURE = OUTPUT.with_name("t13_low_q_source_boundary_first_failure.json")
PREDECESSOR = PREFIX+"Result/artifacts/t13_multi_q_estimator.json"
PREDECESSOR_SHA = "56c9aa7ef469c51a30337bea9ea958c8d2459ed7e2316fbbe49644ad192c57b1"
POWERS, Q_GRID = (0, 2, 3, 4), (F(1, 50), F(1, 100), F(1, 200))
RATIOS, BETA = (F(1), F(1, 2), F(1, 3), F(1, 4)), (F(1), F(2), F(3), F(-1))
WINDOWS = ((F(4, 5), F(2, 5), F(1, 5)), (F(3, 5), F(3, 10), F(3, 20)), (F(2, 5), F(1, 5), F(1, 10)))
FOUR_WINDOW = (F(3, 5), F(3, 10), F(1, 5), F(3, 20))
GATES = {"independent_float_control_relative": 1e-8, "original_causal_leakage": 1e-6}
MP_DIGITS, MP_GATE = 80, 1e-45
FIRST_FAILURE_SHA = "ba1acb4929d07a222476f4c0b0b0ca0684e9da17a86f3a6ea8438ac31a42982d"


def cell(value):
    if value in ("NAN", "--"):
        return None
    return F(value)


def row_record(name, line_no, line, q, energy, error, pressure, ancestry):
    if q is not None and q < 0 or energy is not None and energy < 0 or error is not None and error < 0:
        raise ValueError("negative source q/energy/error")
    encoding = "utf-16-le" if name == "DispersionAllPressures.txt" else "latin-1"
    return {"row_id": f"{name}:L{line_no}:P{pressure}", "source_file": name,
            "line_number": line_no, "line_encoding": encoding,
            "line_sha256": hashlib.sha256(line.encode(encoding)).hexdigest(),
            "source_line_lexical": line,
            "q_lexical": q, "energy_lexical": energy, "error_lexical": error,
            "pressure_bar": str(pressure), "ancestry": ancestry}


def parse_all(raw, pressures):
    if not raw.startswith(b"\xff\xfe"):
        raise ValueError("author UTF-16-LE BOM required")
    lines = raw.decode("utf-16").splitlines()
    header = [line.split("\t") for line in lines[:3]]
    if len(header) != 3 or any(len(row) != 16 for row in header) or header[1][1] != "A-1" or set(header[1][2:]) != {"meV"}:
        raise ValueError("unrecognized all-pressures header/unit convention")
    labels = tuple(F(re.search(r"P=([0-9.]+)", text).group(1)) for text in header[2][2::2])
    if labels != tuple(pressures) or header[2][2::2] != header[2][3::2]:
        raise ValueError("pressure ordering or energy/error label mismatch")
    out = []
    for index, line in enumerate(lines[3:], start=4):
        values = line.split("\t")
        if len(values) != 16 or int(values[0]) != index-3:
            raise ValueError("row width or upstream index changed")
        q = cell(values[1])
        if q is None:
            raise ValueError("missing all-pressures wavevector")
        for i, pressure in enumerate(pressures):
            e, error = cell(values[2+2*i]), cell(values[3+2*i])
            if (e is None) != (error is None):
                raise ValueError("partial missing energy/error pair")
            out.append(row_record("DispersionAllPressures.txt", index, line, q, e, error, pressure,
                                  "NEUTRON_LOW_Q_SYSTEMATICS_FLAGGED" if q < F(1, 5) else "NEUTRON_AUTHOR_TABLE"))
    return out


def parse_p0(raw):
    lines = raw.decode("latin-1").splitlines()
    if lines[0].split("\t") != ["k", "e", "err(e)"] or lines[1].split("\t") != ["\xc5-1", "meV", "meV"]:
        raise ValueError("unrecognized P0 header/unit convention")
    out, separators = [], []
    for index, line in enumerate(lines[2:], start=3):
        parts = line.split("\t")
        if len(parts) != 3:
            raise ValueError("P0 row width changed")
        q, e, error = [cell(v) for v in parts]
        if q is None:
            if e is not None or error is not None:
                raise ValueError("partial separator")
            separators.append(index)
            continue
        ancestry = "ULTRASOUND" if q < F(3, 20) else "COMBINED_ULTRASOUND_NEUTRON" if q <= F(3, 10) else "NEUTRON"
        out.append(row_record("DispersionP0allRange.txt", index, line, q, e, error, F(0), ancestry))
    return out, separators


def invert(matrix):
    n = len(matrix)
    a = [list(row)+[F(int(i == j)) for j in range(n)] for i, row in enumerate(matrix)]
    determinant = F(1)
    for k in range(n):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            raise ValueError("singular coefficient design")
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            determinant = -determinant
        diagonal = a[k][k]
        determinant *= diagonal
        a[k] = [v/diagonal for v in a[k]]
        for i in range(n):
            if i != k:
                factor = a[i][k]
                a[i] = [v-factor*w for v, w in zip(a[i], a[k])]
    return [row[n:] for row in a], determinant


def four_weights(qs):
    if len(qs) != 4 or len(set(qs)) != 4 or any(q <= 0 for q in qs):
        raise ValueError("four distinct positive momenta required")
    return invert([[q**power for power in POWERS] for q in qs])


def four_estimate(qs, energies):
    if len(energies) != 4 or any(e <= 0 for e in energies):
        raise ValueError("four positive energies required")
    weights, _ = four_weights(qs)
    return [sum(w*e/q for w, e, q in zip(row, energies, qs)) for row in weights]


def determinant_formula(qs):
    vandermonde = F(1)
    for i, j in combinations(range(4), 2):
        vandermonde *= qs[j]-qs[i]
    return vandermonde*sum(a*b*c for a, b, c in combinations(qs, 3))


def control(maximum):
    qs4 = [maximum*r for r in RATIOS]
    energies = [q*sum(b*q**p for b, p in zip(BETA, POWERS)) for q in qs4]
    exact = four_estimate(qs4, energies)
    matrix = np.array([[float(q**p) for p in POWERS] for q in qs4])
    scaled = matrix*np.array([float(maximum**(-p)) for p in POWERS])
    floating = np.linalg.solve(scaled, np.array([float(e/q) for e, q in zip(energies, qs4)]))
    recovered = floating*np.array([float(maximum**(-p)) for p in POWERS])
    relative = float(max(abs(v-float(b))/abs(float(b)) for v, b in zip(recovered, BETA)))
    with mp.workdps(MP_DIGITS):
        def number(v):
            return mp.mpf(v.numerator)/v.denominator
        high_matrix = mp.matrix([[number((q/maximum)**p) for p in POWERS] for q in qs4])
        high = mp.lu_solve(high_matrix, mp.matrix([number(e/q) for e, q in zip(energies, qs4)]))
        high_error = float(max(abs(high[k]/number(maximum**p)-number(BETA[k]))/abs(number(BETA[k])) for k, p in enumerate(POWERS)))
    qs3 = [maximum, maximum/2, maximum/4]
    e3 = [q*sum(b*q**p for b, p in zip(BETA, POWERS)) for q in qs3]
    weights = M.weights(qs3)
    alias = [sum(w*q**3 for w, q in zip(row, qs3)) for row in weights]
    expected = [BETA[0], BETA[1], BETA[3]]
    observed = M.estimate(qs3, e3)
    _, det = four_weights(qs4)
    return {"q_max": float(maximum), "four_recovery_exact": exact == list(BETA),
            "four_determinant_identity_exact": det == determinant_formula(qs4) != 0,
            "independent_float_relative_error": relative,
            "independent_mp80_relative_error": high_error,
            "three_alias_identity_exact": observed == [v+BETA[2]*a for v, a in zip(expected, alias)],
            "alias_exact": [M.fraction_record(v) for v in alias],
            "alias_scaled_constants_exact": [M.fraction_record(alias[0]/maximum**3), M.fraction_record(alias[1]/maximum), M.fraction_record(alias[2]*maximum)]}


def source_window(rows, qs, four=False):
    lookup = {r["q_lexical"]: r for r in rows if r["pressure_bar"] == "0"}
    selected = [lookup.get(q) for q in qs]
    out = {"q_angstrom_inverse": [float(q) for q in qs], "source_rows": [encode_row(r) if r else None for r in selected],
           "classification": "ROW_PRESENT_EXPOSED_ESTIMATOR_NOT_UET_INFERENCE", "physical_I_estimate": None}
    if any(r is None or r["energy_lexical"] is None for r in selected):
        return out | {"classification": "MISSING_ROWS_NO_INTERPOLATION_OR_SUBSTITUTE", "coefficients": None}
    energies = [r["energy_lexical"] for r in selected]
    if any(e <= 0 for e in energies):
        return out | {"classification": "NONPOSITIVE_ENERGY_NOT_ESTIMATED", "coefficients": None}
    estimate = four_estimate(qs, energies) if four else M.estimate(qs, energies)
    return out | {"coefficients": [float(v) for v in estimate], "coefficients_exact": [M.fraction_record(v) for v in estimate],
                  "reported_errors_complete": all(r["error_lexical"] is not None for r in selected),
                  "joint_covariance_acquired": False, "theoretical_remainder_bounded": False,
                  "contains_low_q_or_hybrid_ancestry": any(r["ancestry"] not in ("NEUTRON", "NEUTRON_AUTHOR_TABLE") for r in selected)}


def encode_row(row):
    return {k.replace("_lexical", "_exact") if isinstance(v, F) or v is None else k:
            str(v) if isinstance(v, F) else v for k, v in row.items()}


def audit():
    previous = (ROOT/PREDECESSOR).read_bytes()
    if hashlib.sha256(previous).hexdigest() != PREDECESSOR_SHA:
        raise ValueError("estimator predecessor identity changed")
    manifest = json.loads((ROOT/REGISTRY).read_text())
    raw = []
    for item in manifest["raw_files"]:
        content = (ROOT/item["path"]).read_bytes()
        if hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise ValueError("raw source identity changed")
        raw.append(content)
    pressures = [F(str(p)) for p in manifest["protocol"]["pressures_bar"]]
    all_rows = parse_all(raw[0], pressures)
    p0_rows, separators = parse_p0(raw[1])
    controls = [control(q) for q in Q_GRID]
    summaries, windows = [], []
    for name, rows in (("all_pressures", all_rows), ("P0_hybrid", p0_rows)):
        summaries.append({"table": name, "row_cells_archived_including_missing": len(rows),
                          "energies_present": sum(r["energy_lexical"] is not None for r in rows),
                          "errors_missing": sum(r["error_lexical"] is None for r in rows),
                          "ancestry_counts": {a: sum(r["ancestry"] == a for r in rows) for a in sorted({r["ancestry"] for r in rows})},
                          "unique_row_ids": len({r["row_id"] for r in rows}) == len(rows)})
        windows.append({"table": name, "three_node": [source_window(rows, qs) for qs in WINDOWS], "four_node": source_window(rows, FOUR_WINDOW, four=True)})
    checks = {"source_hash_headers_units_and_row_identity": all(r["unique_row_ids"] for r in summaries),
              "missing_and_ancestry_retained": any(r["energy_lexical"] is None for r in all_rows) and any(r["error_lexical"] is None for r in p0_rows) and bool(separators),
              "three_node_omitted_q4_alias_exact": all(c["three_alias_identity_exact"] for c in controls),
              "alias_scaling_exact": all(c["alias_scaled_constants_exact"] == controls[0]["alias_scaled_constants_exact"] for c in controls),
              "four_node_rank_and_recovery_exact": all(c["four_recovery_exact"] and c["four_determinant_identity_exact"] for c in controls),
              "independent_scaled_float_control": all(c["independent_float_relative_error"] < GATES["independent_float_control_relative"] for c in controls),
              "missing_physical_window_not_filled": windows[0]["three_node"][2]["classification"] == "MISSING_ROWS_NO_INTERPOLATION_OR_SUBSTITUTE",
              "no_physical_inverse_from_source": all(w["physical_I_estimate"] is None for table in windows for w in table["three_node"]+[table["four_node"]])}
    passed = all(checks.values())
    paths = [REGISTRY, Path(__file__).relative_to(ROOT).as_posix(), PREFIX+"Code/03_Research/test_t13_low_q_source_boundary.py",
             PREFIX+"Data/03_Research/godfrin_2021_v1/.gitattributes"]+[r["path"] for r in manifest["raw_files"]]
    protected = [PREDECESSOR, M.REGISTRY, M.PREDECESSOR, M.Q.PREDECESSOR, M.Q.DENS.REM.PREDECESSOR,
                 PREFIX+"Result/artifacts/t13_gaussian_source_work_first_failure.json"]+list(M.Q.EFT.ACTION_PATHS)
    failure = FIRST_FAILURE.read_bytes()
    if hashlib.sha256(failure).hexdigest() != FIRST_FAILURE_SHA:
        raise ValueError("original float64 failure identity changed")
    protected.append(FIRST_FAILURE.relative_to(ROOT).as_posix())
    extended = {"independent_mp80_four_node_control": all(c["independent_mp80_relative_error"] < MP_GATE for c in controls),
                "original_float64_failure_not_relabelled": checks == json.loads(failure)["checks"] and not checks["independent_scaled_float_control"]}
    archived = checks["source_hash_headers_units_and_row_identity"] and checks["missing_and_ancestry_retained"]
    alias_verified = checks["three_node_omitted_q4_alias_exact"] and checks["alias_scaling_exact"]
    four_verified = checks["four_node_rank_and_recovery_exact"] and extended["independent_mp80_four_node_control"]
    result = {"major_result_id": "T13_LOW_Q_NUMERIC_SOURCE_AND_OMITTED_TERM_MEASUREMENT_BOUNDARY", "topic": "0.13_Thermodynamic_Bridge", "branch_id": M.Q.VIRT.BRANCH,
              "generated_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
              "verification_status": "PASS_SCOPED_LOW_Q_SOURCE_BOUNDARY" if passed else "FAIL_SCOPED_LOW_Q_SOURCE_BOUNDARY",
              "what_is_closed": "Versioned author numeric-source archive/row provenance with missing cells and mixed ancestry; exact q4 alias and four-node separation under the declared coefficient class",
              "equation_or_mapping": "delta_beta_k=b4*sum W_ki*q_i^3; quintic alias scales b4/q_max; four basis powers(0,2,3,4) have detV=Vandermonde(q)*e3(q)",
              "units": {"source_q": "angstrom^-1", "source_energy_error": "meV", "source_coefficients": "meV angstrom^(1,3,4,5)", "native_q4_coefficient": "E^-3"},
              "derivation_class": "SOURCE_ARCHIVE_AND_DERIVED_EXACT_MEASUREMENT_MODEL_DISCREPANCY", "observable": "exposed dispersion coefficient estimates, not native kinetic or Kelvin inference", "data_role": "LITERATURE_SOURCE_SCREEN_EXPOSED_COMPARISON_NOT_CALIBRATION_OR_HOLDOUT",
              "source_identity": manifest["source_identity"], "declared_protocol": manifest["protocol"], "thresholds": GATES,
              "checks": checks, "source_summaries": summaries, "p0_separator_line_numbers": separators, "controls": controls, "source_windows": windows,
              "extended_checks": extended, "precision_extension": manifest["precision_extension"],
              "subresults": [{"major_result_id": "T13_GODFRIN_V1_NUMERIC_SOURCE_ARCHIVE", "closure_level": "CLOSED_FOR_LANE" if archived else "OPEN"},
                             {"major_result_id": "T13_Q4_ALIAS_AND_FOUR_NODE_SEPARATION", "closure_level": "CLOSED_FOR_LANE" if alias_verified and four_verified else "OPEN"}],
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected), "equation_registry_ids": [r["id"] for r in manifest["equation_entries"]],
              "controlling_blocker": "native_material_map_joint_covariance_and_non_tree_remainder_not_admitted",
              "open_blockers": ["same_state_atomic_current_and_action_unit_map", "joint_q_energy_covariance_and_non_tree_remainder", "source_calibration_ancestry_and_version_parity", "independent_thermal_alpha_heat_entropy_KMS_parent"],
              "dependency_unlocked": ["source_backed_measurement_model_and_scale_route_research_only"] if archived and alias_verified and four_verified else [],
              "numeric_source_archive_acquired": archived, "q4_alias_verified": alias_verified, "four_node_separation_verified": four_verified,
              "source_tables_are_independent_of_each_other": False, "reported_errors_assumed_one_sigma": False, "source_is_blind_holdout": False,
              "four_term_basis_excludes_all_other_terms_as_physics": False,
              "physical_q5_measured": False, "physical_q4_detected_by_this_audit": False, "physical_I_inferred": False, "physical_joint_covariance_acquired": False,
              "physical_material_map_admitted": False, "physical_measurement_design_completed": False, "independent_alpha_Phi_K_admitted": False,
              "physical_Kubo_emitted": False, "full_SK_KMS_matching_closed": False, "nonlinear_parent_action_completed": False,
              "controlled_full_action_truncation_error_established": False, "external_numeric_rows_admitted_to_UET_comparison": 0,
              "full_core_unlock": False, "core_composition_gate_overwritten": False, "old_source_work_audit_promoted": False,
              "external_UET_parameter_fitting": False, "missing_row_or_uncertainty_imputation": False, "source_window_tuning": False,
              "clipping": False, "cone_padding": False, "claim_promotion": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "claim_boundary": "Source packaging and exact estimator-confounding/separation result, not physical q4 detection, q5/temperature calibration, necessary lab precision or global no-go. Archived source is exposed/mixed and lacks joint covariance; four points separate only four declared basis terms, not all higher remainders. Original tree results/causal FAIL and Core-owner scope unchanged."}
    names = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    result["report"] = dict(zip(names, (result["closure_level"], result["what_is_closed"], result["open_blockers"], result["dependency_unlocked"], result["verification_status"], "Acquired permitted numeric source and derived omitted-basis diagnostic", result["equation_or_mapping"], checks, result["controlling_blocker"], "Derive source-to-scale independent input and bound nuisance/remainder before physical inference; no target tuning", result["claim_boundary"])))
    return result


if __name__ == "__main__":
    result = audit()
    content = (json.dumps(result, indent=2, allow_nan=False)+"\n").encode()
    OUTPUT.write_bytes(content)
    if not all(result["checks"].values()) and not FIRST_FAILURE.exists():
        FIRST_FAILURE.write_bytes(content)
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"], "source_summaries": result["source_summaries"]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
