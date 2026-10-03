"""Off-shell pair spectral matrix and tree h-to-Phi source dressing.

Acoustic intermediate states only. No principal-value/local real matching,
independent quantum Phi loops or physical detector/calibration is added.
"""

from datetime import datetime, timezone
from decimal import Decimal, localcontext
import json
from math import isfinite, pi, sqrt
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Acoustic_Modal_Cuts as MOD

TH, EFT, INT, PREFIX = MOD.TH, MOD.EFT, MOD.INT, MOD.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_acoustic_source_pair_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_acoustic_source_pair.json")
MU_GRID, Q_GRID, FREQUENCY_RATIOS = (1.05, 1.2), (.04, .02), (1.1, 1.5)
ORDERS, SOURCE_STEPS, RESIDUE_OFFSETS = (24, 48, 96), (1e-4, 5e-5, 2.5e-5), (.01, .001, .0001)
GATES = {"identity_relative": 1e-9, "static_derivative_relative": 1e-5,
         "pole_residue_relative": 1e-6, "modal_projection_relative": 1e-6,
         "quadrature_relative": 1e-6, "original_causal_leakage": 1e-6}


def source_schur(q, omega, state, action):
    MOD.kernel(q, omega, state, action)
    ell, s = q*q-omega*omega, state["s"]
    w = state["V_curvature"]+action["epsilon"]*action["response_kinetic"]*ell
    den = ell+2*action["u"]*s-action["gamma"]**2*s/w
    det = ell*den-4*state["mu"]**2*omega**2
    if w == 0 or det == 0:
        raise ValueError("tree poles require a separate retarded limiting prescription")
    return 1/w+action["gamma"]**2*s*ell/(w*w*det)


def static_source_derivative(state, action, step):
    plus = EFT.tree_state(state["mu"], h=state["h"]+step, action=action)
    minus = EFT.tree_state(state["mu"], h=state["h"]-step, action=action)
    actual = (plus["Phi"]-minus["Phi"])/(2*step)
    predicted = 1/(state["V_curvature"]-action["gamma"]**2/(2*action["u"]))
    return INT.relative(actual, predicted)


def pair_vector(p, r, state, action):
    # Positive-frequency internal polarizations give M_aaa* = u_k^dagger V.
    up = MOD.mode(p, state, action)["polarization"]
    ur = MOD.mode(r, state, action)["polarization"]
    return np.einsum("ijk,j,k->i", MOD.cubic_tensor(state, action), up, ur)


def decimal_gram_source(samples, dressed):
    """Reconstruct d^dagger R d without cancelling rounded matrix entries."""
    with localcontext() as context:
        context.prec = 50
        real = [[Decimal(0) for _ in range(3)] for _ in range(3)]
        imag = [[Decimal(0) for _ in range(3)] for _ in range(3)]
        for measure, vector in samples:
            weight = Decimal.from_float(float(measure))
            vr = [Decimal.from_float(float(z.real)) for z in vector]
            vi = [Decimal.from_float(float(z.imag)) for z in vector]
            for i in range(3):
                for j in range(3):
                    real[i][j] += weight*(vr[i]*vr[j]+vi[i]*vi[j])
                    imag[i][j] += weight*(vi[i]*vr[j]-vr[i]*vi[j])
        dr = [Decimal.from_float(float(z.real)) for z in dressed]
        di = [Decimal.from_float(float(z.imag)) for z in dressed]
        value = sum((dr[i]*dr[j]+di[i]*di[j])*real[i][j]
                    -(dr[i]*di[j]-di[i]*dr[j])*imag[i][j]
                    for i in range(3) for j in range(3))
        return float(value)


def pair_matrix(q, omega, temperature, state, action, order=48, on_shell=False):
    TH.validate(q, temperature, state, action, order)
    if not isfinite(omega) or omega <= 0:
        raise ValueError("positive finite real frequency required")
    energy = TH.energy_value(q, state, action)
    if on_shell:
        if INT.relative(omega, energy) > GATES["identity_relative"]:
            raise ValueError("on-shell flag must agree with unchanged acoustic energy")
        pmin = 0.
    else:
        if omega <= energy:
            raise ValueError("this off-shell support contract requires omega > E(q)")
        pmin = brentq(lambda p: TH.energy_value(p, state, action)+TH.energy_value(q+p, state, action)-omega,
                      0., omega, xtol=1e-14, rtol=1e-13)
    pmax = q+pmin
    nodes, weights = np.polynomial.legendre.leggauss(order)
    matrix, projected, source = np.zeros((3, 3), complex), 0., 0.
    unit = MOD.mode(q, state, action)["polarization"]
    dressed = None if on_shell else np.linalg.solve(MOD.kernel(q, omega, state, action), np.array([0., 0., 1.]))
    margins, residuals, samples, bose_errors = [], [], [], []
    for node, weight in zip(nodes, weights):
        p = pmin+(pmax-pmin)*(node+1)/2
        if on_shell:
            r, cosine = MOD.pair_root(q, p, state, action)
        else:
            ep = TH.energy_value(p, state, action)
            r = brentq(lambda r: TH.energy_value(r, state, action)-(omega-ep),
                       abs(q-p), q+p, xtol=1e-14, rtol=1e-13)
            cosine = (q*q+p*p-r*r)/(2*q*p)
        if not -1 < cosine < 1:
            raise ValueError("strict pair support required; no clipped cosine")
        ep, er = TH.energy_value(p, state, action), TH.energy_value(r, state, action)
        vector = pair_vector(p, r, state, action)
        thermal = TH.thermal_weights(ep, er, omega, temperature, "pair")
        bose_errors.append(max(thermal["KMS_ratio_error"], thermal["FDT_error"]))
        measure = weight*(pmax-pmin)/2*p*r*thermal["difference"]/(ep*er*INT.group_velocity(r, state, action))/(32*pi*q)
        matrix += measure*np.outer(vector, vector.conjugate())
        samples.append((measure, vector))
        projected += measure*abs(np.vdot(unit, vector))**2
        if dressed is not None:
            source += measure*abs(np.vdot(dressed, vector))**2
        margins.append(1-abs(cosine))
        residuals.append(abs(omega-ep-er)/omega)
    return {"matrix": matrix, "modal_projection": float(projected),
            "source_spectral_response": None if on_shell else float(source),
            "decimal_gram_source": None if on_shell else decimal_gram_source(samples, dressed),
            "p_support": [pmin, pmax], "strict_support_margin": min(margins),
            "energy_residual": max(residuals), "Bose_identity_error": max(bose_errors)}


def matrix_record(matrix):
    return {"real": matrix.real.tolist(), "imag": matrix.imag.tolist()}


def audit():
    action, examples = EFT.controls(), []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        cf = INT.dispersion_coefficients(state, action)
        rows, poles = [], []
        for q in Q_GRID:
            mode = MOD.mode(q, state, action)
            energy = mode["omega"]
            residue_errors = []
            for offset in RESIDUE_OFFSETS:
                residue = sum(-(z-energy**2)*np.linalg.inv(MOD.kernel(q, sqrt(z), state, action))[2, 2].real
                              for z in (energy**2*(1-offset), energy**2*(1+offset)))/2
                residue_errors.append(INT.relative(residue, mode["Z_pi"]*mode["B"]**2))
            cut = pair_matrix(q, energy, 0., state, action, ORDERS[-1], True)
            expected = 2*energy*MOD.cut_rate(q, 0., state, action, "pair", ORDERS[-1])["gamma_pole"]
            poles.append({"q": q, "source_pole_residue": mode["Z_pi"]*mode["B"]**2,
                          "matrix_residue_errors": residue_errors,
                          "optical_projection_error": INT.relative(cut["modal_projection"], expected)})
            for ratio in FREQUENCY_RATIOS:
                omega = ratio*energy
                direct = np.linalg.inv(MOD.kernel(q, omega, state, action))[2, 2]
                for temperature in (0., cf["c"]*cf["dispersion_scale"]/256):
                    runs = [pair_matrix(q, omega, temperature, state, action, order) for order in ORDERS]
                    item = runs[-1]
                    matrix = item["matrix"]
                    dressed = np.linalg.solve(MOD.kernel(q, omega, state, action), np.array([0., 0., 1.]))
                    eig = np.linalg.eigvalsh(matrix)
                    rows.append({"q": q, "omega": omega, "omega_over_Eq": ratio, "T": temperature,
                                 "tree_source_schur_error": INT.relative(direct, source_schur(q, omega, state, action)),
                                 "pair_spectral_matrix": matrix_record(matrix),
                                 "scaled_min_eigenvalue": float(eig[0]/max(eig[-1], 1e-30)),
                                 "hermitian_error": float(np.max(abs(matrix-matrix.conjugate().T))/np.max(abs(matrix))),
                                 "source_spectral_response": item["source_spectral_response"],
                                 "double_source_gram_cancellation_error": INT.relative(np.vdot(dressed, matrix@dressed).real, item["source_spectral_response"]),
                                 "source_gram_error": INT.relative(item["decimal_gram_source"], item["source_spectral_response"]),
                                 "quadrature_error": INT.relative(runs[-2]["source_spectral_response"], item["source_spectral_response"]),
                                 "support_margin": item["strict_support_margin"], "energy_residual": item["energy_residual"],
                                 "Bose_identity_error": item["Bose_identity_error"],
                                 "p_support": item["p_support"]})
        examples.append({"mu": mu, "static_source_derivative_errors": [static_source_derivative(state, action, step) for step in SOURCE_STEPS],
                         "pole_checks": poles, "off_shell_pair_rows": rows})
    checks = {
        "static_source_matches_stationary_derivative": all(max(e["static_source_derivative_errors"]) < GATES["static_derivative_relative"] for e in examples),
        "tree_source_schur_matches_matrix_inverse": all(r["tree_source_schur_error"] < GATES["identity_relative"] for e in examples for r in e["off_shell_pair_rows"]),
        "source_pole_residue_matches_independent_matrix": all(p["matrix_residue_errors"][-1] < GATES["pole_residue_relative"] for e in examples for p in e["pole_checks"]),
        "pair_matrix_projects_to_modal_attenuation": all(p["optical_projection_error"] < GATES["modal_projection_relative"] for e in examples for p in e["pole_checks"]),
        "positive_hermitian_pair_kernel_and_source": all(r["scaled_min_eigenvalue"] >= -GATES["identity_relative"] and r["hermitian_error"] < GATES["identity_relative"] and r["source_spectral_response"] > 0 for e in examples for r in e["off_shell_pair_rows"]),
        "source_dressing_gram_support_and_quadrature": all(max(r["source_gram_error"], r["energy_residual"], r["Bose_identity_error"]) < GATES["identity_relative"] and r["support_margin"] > 0 and r["quadrature_error"] < GATES["quadrature_relative"] for e in examples for r in e["off_shell_pair_rows"])}
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY,
             PREFIX+"Code/03_Research/test_t13_acoustic_source_pair.py"]
    protected = [PREFIX+"Result/artifacts/t13_acoustic_modal_cuts.json", PREFIX+"Code/03_Research/Research_T13_Acoustic_Modal_Cuts.py",
                 PREFIX+"Result/artifacts/t13_acoustic_source_pair_first_failure.json"]+list(EFT.ACTION_PATHS)
    record = {"major_result_id": "T13_ACOUSTIC_OFF_SHELL_PAIR_SOURCE_INTERFACE", "topic": "0.13_Thermodynamic_Bridge",
              "branch_id": EFT.BRANCH, "created_at": datetime.now(timezone.utc).isoformat(),
              "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "PARTIAL",
              "verification_status": "PASS_SCOPED_PAIR_SOURCE_INTERFACE" if all(checks.values()) else "FAIL_SCOPED_PAIR_SOURCE_INTERFACE",
              "what_is_closed": "Tree h-to-Phi Schur susceptibility and acoustic pair spectral Gram kernel/source dressing on the declared off-shell grid",
              "equation_or_mapping": "chi_hh=1/W+gamma2 s ell/[W2(ell den-4mu2 omega2)]; R_pair=integral V Vdagger; Im delta_chi_hh=(D^-1 ePhi)dagger R_pair(D^-1 ePhi)",
              "units": {"source_h": "E^3", "Phi": "E", "chi_hh_source_spectral_response": "E^-2", "R_pair": "E^2", "q_omega_T": "E"},
              "derivation_class": "TREE_SOURCE_SCHUR_AND_ACOUSTIC_PAIR_CUT",
              "observable": "Conditional response to declared action source h, not temperature/detector data",
              "data_role": "DERIVED_NOT_CALIBRATION", "action_controls": action,
              "equation_registry_ids": [e["id"] for e in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "checks": checks, "examples": examples, "thresholds": GATES,
              "precision_policy": "50-decimal-digit accumulation/contraction of the same binary64 quadrature samples; not full high-precision roots, vertices or physical uncertainty",
              "declared_grids": {"mu": MU_GRID, "q": Q_GRID, "omega_over_Eq": FREQUENCY_RATIOS,
                                 "orders": ORDERS, "T_divisor": 256, "source_steps": SOURCE_STEPS,
                                 "residue_offsets": RESIDUE_OFFSETS, "locked_before_first_audit": True},
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
              "controlling_blocker": "off_shell_Landau_local_real_source_contact_and_complete_thermal_sunset_open",
              "open_blockers": ["off_shell_Landau_and_complete_source_contact_matching", "principal_value_and_finite_local_real_matching",
                                "all_mode_quantum_heavy_and_complete_thermal_sunset_pressure", "physical_material_readout_scale_transport_uncertainty"],
              "dependency_unlocked": ["further_source_matching_research_only"],
              "full_off_shell_source_matching_closed": False, "full_real_self_energy_matched": False,
              "full_two_loop_pressure_computed": False, "all_parent_modes_and_quantum_Phi_loops_included": False,
              "physical_Kubo_emitted": False, "independent_alpha_Phi_K_admitted": False,
              "full_SK_KMS_matching_closed": False, "parameter_fitting": False,
              "clipping": False, "cone_padding": False, "core_composition_gate_overwritten": False,
              "full_core_unlock": False, "claim_promotion": False, "xie_2026_accessed": False,
              "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "claim_boundary": "Pair-source diagnostic only, not a full retarded response, Landau/contact/local real match, all-mode quantum Phi/heavy loop, interacting EOS, physical Kubo/Kelvin/detector map or Full Topic13/Core. C/R_gen/R_obs excluded; no fitting/clipping/threshold or owner change."}
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived pair/source interface from original parent", record["equation_or_mapping"], checks, record["controlling_blocker"], "Complete off-shell Landau/source/contact/local real and thermal consistency", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    record = audit()
    OUTPUT.write_bytes((json.dumps(record, indent=2, allow_nan=False)+"\n").encode("utf-8"))
    print(json.dumps({"status": record["verification_status"], "checks": record["checks"]}, indent=2))
    raise SystemExit(0 if all(record["checks"].values()) else 1)
