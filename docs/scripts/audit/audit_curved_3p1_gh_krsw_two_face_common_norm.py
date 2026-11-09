from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ONE_FACE_AUDIT = ROOT / "docs/scripts/audit/audit_curved_3p1_gh_krsw_normal_incidence_energy.py"
ONE_FACE_ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_krsw_normal_incidence_energy.json"
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_krsw_two_face_common_norm.json"


def _load_audit():
    spec = importlib.util.spec_from_file_location("krsw_one_face_exact_audit", ONE_FACE_AUDIT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load exact one-face audit: {ONE_FACE_AUDIT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load_audit()
F = Fraction
ZERO = F(0)


def _matmul(left, right):
    return AUDIT._matmul(left, right)


def _transpose(matrix):
    return AUDIT._transpose(matrix)


def _subtract(left, right):
    return AUDIT._difference(left, right)


def _matvec(matrix, vector):
    return [sum((row[j] * vector[j] for j in range(len(vector))), ZERO) for row in matrix]


def _quadratic_form(matrix, vector):
    return sum((vector[i] * matrix[i][j] * vector[j] for i in range(len(vector)) for j in range(len(vector))), ZERO)


def _quadratic_form_for_face(matrix, chi, weight):
    matrix2 = _matmul(matrix, matrix)
    ratio = (1 - chi) / (1 + chi)
    return AUDIT._add(
        AUDIT._add(
            weight,
            AUDIT._scale(1 / ratio, _matmul(_matmul(_transpose(matrix), weight), matrix)),
        ),
        AUDIT._scale(1 / (ratio * ratio), _matmul(_matmul(_transpose(matrix2), weight), matrix2)),
    )


def build_artifact() -> dict:
    chi = F(1, 4)
    weight = AUDIT._weighted_tensor_norm()
    right, left = AUDIT._face_maps(+1)[0], AUDIT._face_maps(-1)[0]
    vector = [ZERO for _ in AUDIT.PAIRS]
    vector[AUDIT.INDEX[(0, 2)]] = F(1)
    vector[AUDIT.INDEX[(1, 2)]] = F(1)
    right_image = _matvec(right, vector)
    round_trip = _matvec(left, right_image)
    product = _matmul(left, right)

    h_right = _quadratic_form_for_face(right, chi, weight)
    h_left = _quadratic_form_for_face(left, chi, weight)
    h_average = AUDIT._scale(F(1, 2), AUDIT._add(h_right, h_left))
    candidates = {
        "right_face_form": h_right,
        "left_face_form": h_left,
        "arithmetic_mean_of_face_forms": h_average,
    }

    checks = {
        "one_face_source_artifact_passes": all(AUDIT.build_artifact()["checks"].values()),
        "round_trip_fixed_vector_exact": round_trip == vector,
        "right_face_intermediate_nonzero": any(right_image),
        "both_faces_are_nonzero_maps": any(any(row) for row in right) and any(any(row) for row in left),
        "strict_common_contraction_contradiction_exact": round_trip == vector and any(vector) and any(right_image),
    }

    exact_candidates = {}
    for name, h in candidates.items():
        exact_candidates[name] = {
            "same_form_for_both_faces": name == "arithmetic_mean_of_face_forms",
            "right_defect_is_zero": all(
                value == ZERO
                for row in _subtract(h, _matmul(_matmul(_transpose(right), h), right))
                for value in row
            ),
            "left_defect_is_zero": all(
                value == ZERO
                for row in _subtract(h, _matmul(_matmul(_transpose(left), h), left))
                for value in row
            ),
            "form_on_fixed_vector": str(_quadratic_form(h, vector)),
            "form_on_right_image": str(_quadratic_form(h, right_image)),
        }

    one_face_payload = json.loads(ONE_FACE_ARTIFACT.read_text(encoding="utf-8"))
    source_hashes = {
        ONE_FACE_AUDIT.relative_to(ROOT).as_posix(): hashlib.sha256(ONE_FACE_AUDIT.read_bytes()).hexdigest(),
        ONE_FACE_ARTIFACT.relative_to(ROOT).as_posix(): hashlib.sha256(ONE_FACE_ARTIFACT.read_bytes()).hexdigest(),
    }
    source_url = "https://arxiv.org/html/0807.3207"
    return {
        "schema_version": "core-curved-3p1-gh-krsw-two-face-common-norm-v1",
        "artifact": "curved_3p1_gh_krsw_two_face_common_norm",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "PASS_EXACT_NO_STRICT_COMMON_FACE_CONTRACTION; WEAK_COMMON_NORM_OPEN" if all(checks.values()) else "FAIL_TWO_FACE_COMMON_NORM_AUDIT",
        "major_result_id": "CORE_CURVED_3P1_GH_KRSW_NO_STRICT_COMMON_TWO_FACE_CONTRACTION",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_KRSW_NO_STRICT_COMMON_TWO_FACE_CONTRACTION",
            "topic": "core_curved_3p1",
            "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
            "what_is_closed": [
                "The exact normal-incidence two-face boundary-map composition has a nonzero fixed amplitude.",
                "Therefore no single positive-definite quadratic norm can make both face maps strict contractions on every nonzero amplitude.",
                "This rules out strict per-face contraction in a common norm as a proof route for this algebraic lane.",
            ],
            "what_remains_open": [
                "Existence of a common positive-definite nonincreasing form with semidefinite defects is not decided.",
                "The face-map composition is not a spatial propagation operator and does not establish a slab eigenmode or instability.",
                "An evolution energy estimate for the full first-order GH system, tangential frequencies, variable coefficients, and corners remains open.",
            ],
            "equation_or_mapping": {
                "maps": "q=M_right p at the +x face; q=M_left p at the -x face, using the exact KRSW normal-incidence maps",
                "fixed_vector": "M_left*M_right*v=v, with v_(t,y)=v_(x,y)=1 and all other components zero",
                "strict_contraction_no_go": "If H is common and positive definite and both M_s^T H M_s < H, then v^T H v > (M_right*v)^T H(M_right*v) > (M_left*M_right*v)^T H(M_left*M_right*v)=v^T H v, a contradiction.",
                "weak_form_obligation": "For H>0 and defects D_s=H-M_s^T H M_s >=0, the fixed cycle requires D_right*v=0 and D_left*(M_right*v)=0; these neutral-subspace equalities do not by themselves decide feasibility.",
            },
            "units": "Dimensionless amplitudes in the flat-background linearized standard-GR normal-incidence lane.",
            "derivation_class": "exact rational matrix composition and quadratic-form contradiction",
            "observable": "spectral contraction property of the declared algebraic face maps; not a physical observable",
            "data_role": "internal exact algebra based on a published standard-GR boundary comparator; no empirical data, fitting, or holdout",
            "verification_status": "PASS_EXACT_NO_STRICT_COMMON_FACE_CONTRACTION" if all(checks.values()) else "FAIL_TWO_FACE_COMMON_NORM_AUDIT",
            "open_blockers": [
                "common semidefinite quadratic-form feasibility or a full two-sided discrete energy estimate",
                "mapping the one-face algebra to a spatially evolved GH slab with compatible corners",
            ],
            "dependency_unlocked": "none",
            "claim_boundary": "No-go only for strict common contraction of these exact normal-incidence face maps; not a no-go for nonincreasing energy, slab stability, full GH CPBC, UET, or Gravity.",
        },
        "source": {
            "title": "Boundary conditions for coupled quasilinear wave equations with application to isolated systems",
            "authors": ["H.-O. Kreiss", "O. Reula", "O. Sarbach", "J. Winicour"],
            "locator": "Section IV.1, equations (55)-(67) and the harmonic constraints immediately following equation (67)",
            "url": source_url,
        },
        "scope": {
            "assumptions": [
                "The two maps are the exact normal-incidence maps in the source-hashed one-face artifact.",
                "A common norm means the same positive-definite H is used for both oriented faces.",
                "Strict contraction is required for every nonzero input vector at each face.",
            ],
            "not_assumed_or_proved": [
                "No composition of face maps is identified with propagation through a finite-width slab.",
                "No result is asserted for a common nonincreasing norm or the full evolved GH equations.",
            ],
        },
        "composition": {
            "rank": AUDIT._rank(product),
            "fixed_vector_components": {"h_02": "1", "h_12": "1"},
            "fixed_vector_exact": round_trip == vector,
            "intermediate_nonzero": any(right_image),
            "strict_common_contraction_is_impossible": checks["strict_common_contraction_contradiction_exact"],
        },
        "tested_candidate_forms": exact_candidates,
        "checks": checks,
        "claim_promotion": False,
        "full_core_unlock": False,
        "gravity_unlock": False,
        "source_hashes": source_hashes,
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": artifact["status"], "checks": artifact["checks"], "artifact": OUTPUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if all(artifact["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
