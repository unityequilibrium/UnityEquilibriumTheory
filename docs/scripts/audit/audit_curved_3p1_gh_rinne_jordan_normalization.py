from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
BASELINE_PATH = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_rinne_negative_shift_kreiss_symbol.py"
BASELINE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_jordan_normalization.json"
BETAS = (-0.1, -0.25, -0.5, -0.75, -0.9, -0.99)


def _load_baseline():
    spec = importlib.util.spec_from_file_location("_uet_rinne_negative_baseline", BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {BASELINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASELINE = _load_baseline()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _matrix(beta: float) -> np.ndarray:
    zeta = -beta
    g2 = 1.0 / (1.0 - beta * beta)
    return np.asarray([
        [-g2 * beta * zeta, -g2 * zeta, -1j * g2 * beta, 0.0j],
        [-g2 * zeta, -g2 * beta * zeta, -1j * g2, 0.0j],
        [1j / beta, 0.0j, zeta / beta, 0.0j],
        [0.0j, 0.0j, 0.0j, zeta / beta],
    ], dtype=complex)


def build_artifact() -> dict:
    row_map, column_map, _ = BASELINE._source_transforms()
    records = []
    for beta in BETAS:
        a = np.asarray([-beta, 0.0, 1.0j, 0.0j])
        b = np.asarray([0.0j, 1.0, -1.0j, 0.0j])
        c = np.asarray([0.0j, 0.0j, 0.0j, 1.0])
        ka, kb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
        m = _matrix(beta)
        source_residual = -a / ka + b / kb - m @ (a / ka)
        corrected_residual = -a / ka + b / ka - m @ (a / ka)
        printed = BASELINE._degenerate_case(beta, "printed_euclidean_norms", row_map, column_map)
        corrected = BASELINE._degenerate_case(beta, "source_ode_consistent", row_map, column_map)
        corrected_det = 4.0 / (abs(beta) ** 26 * (1.0 + beta * beta) ** 5)
        printed_det = (ka + kb) ** 10 / (8.0 * abs(beta) ** 26 * ka**10 * kb**20)
        ratio = (ka + kb) ** 10 / (32.0 * kb**20)
        records.append({
            "beta": beta,
            "jordan_identity_residuals": [
                float(np.linalg.norm(m @ a + a - b)),
                float(np.linalg.norm(m @ b + b)),
                float(np.linalg.norm(m @ c + c)),
            ],
            "K_A": ka,
            "K_B": kb,
            "printed_eq74_ode_residual": float(np.linalg.norm(source_residual)),
            "printed_residual_formula": float(abs(1.0 / kb - 1.0 / ka) * kb),
            "corrected_ode_residual": float(np.linalg.norm(corrected_residual)),
            "full_matrix_printed_eq124_log_offset": printed["source_eq_124_log_offset"],
            "full_matrix_corrected_det_log_offset": corrected["corrected_jordan_determinant_log_offset"],
            "full_matrix_printed_mode_residual": printed["maximum_principal_mode_residual"],
            "full_matrix_corrected_mode_residual": corrected["maximum_principal_mode_residual"],
            "corrected_det_formula": corrected_det,
            "printed_det_formula": printed_det,
            "printed_to_corrected_ratio": ratio,
            "full_matrix_ratio_log_offset": float(
                printed["basis_determinant_log_abs"]
                - corrected["basis_determinant_log_abs"]
                - np.log(ratio)
            ),
        })

    checks = {
        "exact_jordan_vector_identities": max(max(r["jordan_identity_residuals"]) for r in records) < 1e-9,
        "printed_eq74_residual_matches_norm_mismatch": all(
            abs(r["printed_eq74_ode_residual"] - r["printed_residual_formula"]) < 1e-9 for r in records
        ),
        "corrected_jordan_chain_satisfies_ode": max(
            max(r["corrected_ode_residual"], r["full_matrix_corrected_mode_residual"]) for r in records
        ) < 1e-9,
        "corrected_determinant_matches_full_30x30_matrix": max(
            abs(r["full_matrix_corrected_det_log_offset"]) for r in records
        ) < 2e-9,
        "source_to_corrected_determinant_ratio_matches_full_matrix": max(
            abs(r["full_matrix_ratio_log_offset"]) for r in records
        ) < 2e-9,
        "corrected_determinant_above_one_eighth_on_samples": all(
            r["corrected_det_formula"] > 0.125 for r in records
        ),
    }
    hashes = {
        _rel(Path(__file__)): _sha(Path(__file__)),
        _rel(BASELINE_PATH): _sha(BASELINE_PATH),
        _rel(BASELINE_ARTIFACT): _sha(BASELINE_ARTIFACT),
    }
    closed = [
        "At zeta=-beta, -1<beta<0, the exact Jordan identities are M*A=-A+B, M*B=-B, M*C=-C.",
        "For K_A=sqrt(1+beta^2), K_B=sqrt(2), the printed Eq. (74) generalized-mode coefficient has ODE residual exp(-xi)*sigma1*(1/K_B-1/K_A)*B.",
        "Replacing only xi*B/K_B by xi*B/K_A gives an ODE-consistent chain with exact 30x30 determinant 4/(abs(beta)^26*(1+beta^2)^5)>1/8 throughout -1<beta<0.",
        "The printed Eq. (90) determinant and corrected determinant have a closed-form ratio, reproduced independently by the registered full boundary matrix.",
    ]
    open_items = [
        "The source normalization/determinant discrepancy has no authoritative correction or independently confirmed alternate convention.",
        "A continuous complex-frequency transfer/inverse bound and imported Kreiss norm interface remain open.",
        "Variable-coefficient/nonlinear GH evolution, tangential/corner completion, dimensional-observable mapping, and Core curved 3+1 remain open.",
    ]
    claim = (
        "Exact Jordan-chain and determinant result only at zeta=-beta for the frozen-coefficient "
        "standard-GR GH boundary-symbol lane with -1<beta<0 and the declared Euclidean normalization. "
        "Not a full complex-frequency transfer estimate, nonlinear well-posedness proof, UET validation, "
        "or Core-parent closure."
    )
    equation = {
        "vectors": "A=(-beta,0,i,0), B=(0,1,-i,0), C=(0,0,0,1)",
        "jordan_identities": "M*A=-A+B; M*B=-B; M*C=-C",
        "printed_mode_residual": "exp(-xi)*sigma1*(1/K_B-1/K_A)*B",
        "corrected_mode": "exp(-xi)[sigma1*(A+xi*B)/K_A+sigma2*B/K_B+sigma3*C]",
        "corrected_determinant": "abs(det(C_boundary))=4/(abs(beta)^26*(1+beta^2)^5)>1/8 for -1<beta<0",
        "printed_to_corrected_ratio": "(K_A+K_B)^10/(32*K_B^20)<1 for -1<beta<0",
        "confluent_derivation": "lim(abs(det(C_generic))/abs(lambda_2-lambda_1)^10)=1/(8*abs(beta)^26); the normalized generalized mode tends to (A+B/2)/sqrt(2), while the companion mode tends to B/sqrt(2). Transforming this pair to (A/K_A,B/K_B) multiplies the determinant by (sqrt(2)/K_A)^10, giving 4/(abs(beta)^26*(1+beta^2)^5).",
        "strict_lower_bound": "For a=abs(beta) in (0,1), a^26*(1+a^2)^5<32, hence the corrected determinant is strictly greater than 1/8.",
    }
    status = "PASS_EXACT_NEGATIVE_SHIFT_JORDAN_DEGENERACY_LANE" if all(checks.values()) else "FAIL_OR_UNRESOLVED_JORDAN_DEGENERACY_AUDIT"
    major = {
        "major_result_id": "CORE_CURVED_3P1_GH_RINNE_NEGATIVE_SHIFT_JORDAN_DEGENERACY",
        "topic": "core_curved_3p1",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": closed,
        "equation_or_mapping": equation,
        "units": "Dimensionless frozen-coefficient Fourier-Laplace variables; no SI observable mapping.",
        "derivation_class": "Exact Jordan-chain algebra and confluent determinant, cross-checked against the registered 30x30 boundary matrix.",
        "observable": "Principal-ODE residual and absolute boundary-symbol determinant at zeta=-beta.",
        "data_role": "Primary-source formula audit and internal matrix cross-check; no empirical data or fitting.",
        "evidence_artifacts": [{"path": _rel(BASELINE_ARTIFACT), "sha256": hashes[_rel(BASELINE_ARTIFACT)]}],
        "verification_status": status,
        "open_blockers": open_items,
        "dependency_unlocked": "none; Core curved 3+1 remains PARTIAL and Gravity remains blocked",
        "claim_boundary": claim,
    }
    return {
        "schema_version": "core-curved-3p1-rinne-jordan-normalization-v1",
        "artifact": "curved_3p1_gh_rinne_jordan_normalization",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "major_result_id": major["major_result_id"],
        "major_result": major,
        "closure_level": major["closure_level"],
        "MAJOR_RESULT_CLOSURE": major["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": closed,
        "WHAT_REMAINS_OPEN": open_items,
        "DEPENDENCY_UNLOCKED": major["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Added an isolated exact audit of the negative-shift Jordan degeneracy; the source convention remains unchanged and visible.",
        "EQUATION_OR_MAPPING": equation,
        "VERIFICATION": {
            "checks": checks,
            "samples": records,
            "analytic_derivation": {
                "eigenvalue_gap": "lambda_2-lambda_1=(zeta+beta)/beta+O((zeta+beta)^2) as zeta approaches -beta",
                "generic_determinant_confluent_limit": "lim(abs(det(C_generic))/abs(lambda_2-lambda_1)^10)=1/(8*abs(beta)^26)",
                "normalized_confluent_basis": "g=(A+B/2)/sqrt(2), v=B/sqrt(2)",
                "basis_change_determinant_per_tensor_component": "sqrt(2)/K_A; adding a multiple of v to g does not change the determinant",
                "corrected_determinant": "1/(8*abs(beta)^26)*(sqrt(2)/K_A)^10=4/(abs(beta)^26*(1+beta^2)^5)",
                "uniform_pointwise_lower_bound": "a^26*(1+a^2)^5<32 for a=abs(beta) in (0,1), so determinant>1/8",
                "normalization_mismatch": "K_A=sqrt(1+beta^2)<sqrt(2)=K_B for every -1<beta<0",
            },
            "source_hashes": hashes,
            "primary_source": {
                "title": "Stable radiation-controlling boundary conditions for the generalized harmonic Einstein equations",
                "author": "Oliver Rinne",
                "publication": "Classical and Quantum Gravity 23 (2006), 6275-6300",
                "doi": "10.1088/0264-9381/23/22/013",
                "arxiv": "https://arxiv.org/abs/gr-qc/0606053",
                "scope": "Section 3.2, Eqs. (70)-(74), (89)-(90)",
            },
        },
        "CONTROLLING_BLOCKER": "complex_frequency_transfer_bound_and_imported_kreiss_norm_interface_missing",
        "NEXT_ACTION": "Extend the boundary-map inverse/transfer estimate over complex zeta and high-frequency compactification; keep this exact degenerate-point result separate.",
        "CLAIM_BOUNDARY": claim,
        "claim_promotion": False,
    }


def main() -> None:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": _rel(OUTPUT), "status": artifact["STATUS"], "checks": artifact["VERIFICATION"]["checks"]}, indent=2))


if __name__ == "__main__":
    main()
