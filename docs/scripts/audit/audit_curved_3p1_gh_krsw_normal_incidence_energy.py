from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_krsw_normal_incidence_energy.json"
PROJECTOR_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_gh_boundary_projectors.py"
GH_SOURCE = ROOT / "docs/core/02_equations/covariant/uet_curved_3p1_generalized_harmonic.py"
PAIRS = tuple((i, j) for i in range(4) for j in range(i, 4))
INDEX = {pair: index for index, pair in enumerate(PAIRS)}
ZERO = Fraction(0)
ONE = Fraction(1)

Matrix = list[list[Fraction]]


def _zeros(rows: int, columns: int) -> Matrix:
    return [[ZERO for _ in range(columns)] for _ in range(rows)]


def _identity(size: int) -> Matrix:
    result = _zeros(size, size)
    for index in range(size):
        result[index][index] = ONE
    return result


def _transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def _matmul(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), ZERO) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def _scale(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * item for item in row] for row in matrix]


def _inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    work = [row[:] + identity_row[:] for row, identity_row in zip(matrix, _identity(size))]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular exact matrix")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [item / divisor for item in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [a - factor * b for a, b in zip(work[row], work[column])]
    return [row[size:] for row in work]


def _rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [item / divisor for item in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [a - factor * b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def _row(entries: dict[tuple[int, int], Fraction | int]) -> list[Fraction]:
    result = [ZERO for _ in PAIRS]
    for pair, value in entries.items():
        result[INDEX[tuple(sorted(pair))]] += Fraction(value)
    return result


def _trace_reversal() -> Matrix:
    signature = (-1, 1, 1, 1)
    result = _zeros(10, 10)
    for column, pair in enumerate(PAIRS):
        result[column][column] = -ONE
        if pair[0] == pair[1]:
            trace = Fraction(signature[pair[0]])
            for row, (a, b) in enumerate(PAIRS):
                if a == b:
                    result[row][column] += Fraction(signature[a], 2) * trace
    return result


def _boundary_rows(normal_sign: int) -> list[list[Fraction]]:
    s = Fraction(normal_sign)
    return [
        _row({(0, 0): 1, (0, 1): 2 * s, (1, 1): 1}),
        _row({(2, 2): 1, (3, 3): -1}),
        _row({(2, 3): 2}),
        _row({(2, 2): 1, (3, 3): 1}),
        _row({(0, 2): 1, (1, 2): s}),
        _row({(0, 3): 1, (1, 3): s}),
    ]


def _face_maps(normal_sign: int) -> tuple[Matrix, Matrix, Matrix]:
    """Return exact incoming/outgoing map, the boundary matrix, and trace reversal."""
    a_rows = _boundary_rows(normal_sign)
    b_rows = [_zeros(1, 10)[0] for _ in range(6)]
    for rho in range(4):
        a_rows.append(_row({(0, rho): Fraction(1, 2), (1, rho): Fraction(-normal_sign, 2)}))
        b_rows.append(_row({(0, rho): Fraction(1, 2), (1, rho): Fraction(normal_sign, 2)}))

    trace = _trace_reversal()
    a_gamma = _matmul(a_rows, trace)
    b_gamma = _matmul(b_rows, trace)
    m_gamma = _scale(Fraction(-1), _matmul(_inverse(a_rows), b_rows))
    # Trace reversal is an involution: gamma = U h and U^-1 = U.
    m_metric = _matmul(_matmul(trace, m_gamma), trace)
    return m_metric, a_gamma, trace


def _exact_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _matrix_strings(matrix: Matrix) -> list[list[str]]:
    return [[_exact_string(item) for item in row] for row in matrix]


def _is_zero(matrix: Matrix) -> bool:
    return all(item == ZERO for row in matrix for item in row)


def _difference(left: Matrix, right: Matrix) -> Matrix:
    return [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def _weighted_tensor_norm() -> Matrix:
    result = _zeros(10, 10)
    for index, (i, j) in enumerate(PAIRS):
        result[index][index] = Fraction(1 if i == j else 2)
    return result


def _face_certificate(normal_sign: int, chi: Fraction, weight: Matrix) -> dict:
    m, a_gamma, trace = _face_maps(normal_sign)
    m2 = _matmul(m, m)
    m3 = _matmul(m2, m)
    ratio = (1 - chi) / (1 + chi)
    h = _add(
        _add(weight, _scale(1 / ratio, _matmul(_matmul(_transpose(m), weight), m))),
        _scale(1 / (ratio * ratio), _matmul(_matmul(_transpose(m2), weight), m2)),
    )
    left_identity = _matmul(_matmul(_transpose(m), h), m)
    right_identity = _scale(ratio, _difference(h, weight))
    flux_form = _add(
        _scale((chi - 1) / 2, h),
        _scale((chi + 1) / 2, _matmul(_matmul(_transpose(m), h), m)),
    )
    target_flux = _scale(-(1 - chi) / 2, weight)
    return {
        "normal_sign": normal_sign,
        "boundary_matrix_rank": _rank(a_gamma),
        "trace_reversal_involution_exact": _is_zero(_difference(_matmul(trace, trace), _identity(10))),
        "map_rank": _rank(m),
        "map_squared_rank": _rank(m2),
        "map_cubed_is_exactly_zero": _is_zero(m3),
        "incoming_from_outgoing_map": _matrix_strings(m),
        "quadratic_form_identity_exact": _is_zero(_difference(left_identity, right_identity)),
        "quadratic_flux_identity_exact": _is_zero(_difference(flux_form, target_flux)),
    }, m


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict:
    chi = Fraction(1, 4)
    ratio = (1 - chi) / (1 + chi)
    weight = _weighted_tensor_norm()
    right_certificate, m_right = _face_certificate(+1, chi, weight)
    left_certificate, m_left = _face_certificate(-1, chi, weight)
    two_face = _matmul(m_left, m_right)
    fixed_vector = [ZERO for _ in PAIRS]
    fixed_vector[INDEX[(0, 2)]] = ONE
    fixed_vector[INDEX[(1, 2)]] = ONE
    fixed_result = [sum((two_face[i][j] * fixed_vector[j] for j in range(10)), ZERO) for i in range(10)]
    fixed_vector_is_exact = fixed_result == fixed_vector
    checks = {
        "component_order_matches_core_symmetric_pairs": PAIRS == tuple((i, j) for i in range(4) for j in range(i, 4)),
        "right_boundary_map_is_full_rank": right_certificate["boundary_matrix_rank"] == 10,
        "left_boundary_map_is_full_rank": left_certificate["boundary_matrix_rank"] == 10,
        "right_map_is_nilpotent_index_three": right_certificate["map_rank"] == 4 and right_certificate["map_squared_rank"] == 1 and right_certificate["map_cubed_is_exactly_zero"],
        "left_map_is_nilpotent_index_three": left_certificate["map_rank"] == 4 and left_certificate["map_squared_rank"] == 1 and left_certificate["map_cubed_is_exactly_zero"],
        "right_quadratic_identities_exact": right_certificate["quadratic_form_identity_exact"] and right_certificate["quadratic_flux_identity_exact"],
        "left_quadratic_identities_exact": left_certificate["quadratic_form_identity_exact"] and left_certificate["quadratic_flux_identity_exact"],
        "two_face_composition_has_exact_neutral_amplitude": fixed_vector_is_exact and _rank(two_face) == 4,
    }
    script = Path(__file__).resolve()
    source_hashes = {
        script.relative_to(ROOT).as_posix(): _sha256(script),
        PROJECTOR_SOURCE.relative_to(ROOT).as_posix(): _sha256(PROJECTOR_SOURCE),
        GH_SOURCE.relative_to(ROOT).as_posix(): _sha256(GH_SOURCE),
    }
    source_url = "https://arxiv.org/html/0807.3207"
    artifact = {
        "schema_version": "core-curved-3p1-gh-krsw-normal-incidence-energy-v1",
        "artifact": "curved_3p1_gh_krsw_normal_incidence_energy",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "PASS_EXACT_ONE_FACE_NORMAL_INCIDENCE_BOUNDARY_FORM_IDENTITY" if all(checks.values()) else "FAIL_KRSW_NORMAL_INCIDENCE_AUDIT",
        "major_result_id": "CORE_CURVED_3P1_GH_KRSW_NORMAL_INCIDENCE_BOUNDARY_ENERGY_IDENTITY",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_KRSW_NORMAL_INCIDENCE_BOUNDARY_ENERGY_IDENTITY",
            "topic": "core_curved_3p1",
            "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
            "what_is_closed": [
                "Exact rational reconstruction of the KRSW linearized harmonic plane-boundary hierarchy at normal incidence for each face orientation.",
                "For each one-face map q=M p, an explicitly constructed positive quadratic form H satisfies the declared characteristic-form identity exactly.",
                "The two-face algebraic composition has an exact fixed amplitude; this is a boundary-map composition result, not a slab evolution mode.",
            ],
            "what_remains_open": [
                "Tangential-frequency, glancing, imaginary/general complex-frequency and high-frequency domains are not covered.",
                "The constructed H and chi-weighted quadratic form are an algebraic certificate, not yet identified with the energy norm of the evolving Core GH discretization.",
                "No two-face slab evolution, corner treatment, variable-coefficient or nonlinear GH CPBC estimate is established.",
                "The exact neutral boundary-map amplitude means the one-face estimate does not prove strict two-face dissipation.",
            ],
            "equation_or_mapping": {
                "linear_characteristics": "q=Pi-Phi_n=-a; p=Pi+Phi_n=-b; a=(partial_t+s partial_x)gamma; b=(partial_t-s partial_x)gamma",
                "boundary_map": "A_s a + B_s b=0; q=M_s p; M_s=-A_s^{-1}B_s after exact trace reversal gamma_ab=-h_ab+(1/2)eta_ab eta^cd h_cd",
                "quadratic_form": "H=W+r^-1 M^T W M+r^-2 (M^2)^T W M^2; W=diag(1 for diagonal, 2 for off-diagonal symmetric tensor slots); chi=1/4; r=(1-chi)/(1+chi)=3/5",
                "exact_form_identity": "M^T H M=r(H-W)",
                "declared_characteristic_flux_form": "F=(chi-1)p^T H p/2+(chi+1)q^T H q/2=-(1-chi)p^T W p/2=-3 p^T W p/8 for q=M p",
                "two_face_composition": "M_left M_right v=v, v_(t,y)=v_(x,y)=1 and all other symmetric components zero",
            },
            "units": "Dimensionless amplitudes in a flat-background linearized standard-GR normal-incidence lane; no SI observable map.",
            "derivation_class": "exact rational linear algebra over the published KRSW plane-boundary hierarchy",
            "observable": "declared quadratic characteristic boundary form, not a physical detector observable",
            "data_role": "published standard-GR equation comparator plus exact internal algebra; no empirical data, fit, or holdout",
            "verification_status": "PASS_EXACT_ONE_FACE_NORMAL_INCIDENCE_BOUNDARY_FORM_IDENTITY" if all(checks.values()) else "FAIL_KRSW_NORMAL_INCIDENCE_AUDIT",
            "open_blockers": [
                "identify a compatible energy norm and prove a two-face discrete slab estimate for the full GH evolution",
                "extend the frequency analysis beyond normal incidence and connect the imported boundary theorem hypotheses to the Core GH system",
            ],
            "dependency_unlocked": "none",
            "claim_boundary": "A CLOSED_FOR_LANE exact algebraic comparator only; not a Core curved 3+1 closure, full GH well-posedness proof, UET validation, Gravity compatibility, or evidence for Topic 13.",
        },
        "source": {
            "title": "Boundary conditions for coupled quasilinear wave equations with application to isolated systems",
            "authors": ["H.-O. Kreiss", "O. Reula", "O. Sarbach", "J. Winicour"],
            "locator": "Section IV.1, equations (55)-(67) and the harmonic constraints immediately following equation (67)",
            "url": source_url,
            "role": "imported standard-GR boundary hierarchy; not a UET derivation",
        },
        "scope": {
            "background": "Minkowski",
            "equations": "linearized vacuum Einstein in harmonic coordinates with four harmonic constraints",
            "incidence": "normal only; tangential derivatives set to zero",
            "faces": ["outward normal +x", "outward normal -x"],
            "omitted_terms": ["lower-order GH gamma2 contribution", "curvature", "variable coefficients", "matter source", "finite tangential frequency"],
            "two_face_interpretation": "composition of algebraic face maps only; no spatial propagation or slab time evolution",
        },
        "component_order": [list(pair) for pair in PAIRS],
        "face_maps": {"right": right_certificate, "left": left_certificate},
        "two_face": {
            "composition_rank": _rank(two_face),
            "fixed_vector_components": {"h_02": "1", "h_12": "1"},
            "fixed_vector_residual_exact": "0" if fixed_vector_is_exact else "nonzero",
            "interpretation": "neutral algebraic boundary-map amplitude; not a physical eigenmode or slab-instability proof",
        },
        "checks": checks,
        "claim_promotion": False,
        "dependency_unlocked": [],
        "source_hashes": source_hashes,
    }
    return artifact


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": artifact["status"], "checks": artifact["checks"], "artifact": OUTPUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if all(artifact["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
