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
OUTPUT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_krsw_normal_incidence_slab_cycle.json"


def _load_one_face_audit():
    spec = importlib.util.spec_from_file_location("krsw_one_face_slab_cycle_audit", ONE_FACE_AUDIT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load exact one-face audit: {ONE_FACE_AUDIT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load_one_face_audit()
ZERO = Fraction(0)


def _is_zero(matrix) -> bool:
    return all(value == ZERO for row in matrix for value in row)


def _matrix_strings(matrix) -> list[list[str]]:
    return AUDIT._matrix_strings(matrix)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _characteristic_coefficients(phase: str, normal_sign: int) -> tuple[int, int]:
    dx = -1 if phase == "F" else 1
    return 1 + normal_sign * dx, 1 - normal_sign * dx


def _phase_coefficients(phase: str, time_t: tuple[int, int], space_x: tuple[int, int]) -> tuple[int, int]:
    dx = -1 if phase == "F" else 1
    return tuple(time_t[i] + dx * space_x[i] for i in range(2))


def _projection_record(name: str, projection, weight) -> dict:
    identity = AUDIT._identity(10)
    weighted_adjoint = AUDIT._matmul(AUDIT._transpose(projection), weight)
    weighted_projection = AUDIT._matmul(weight, projection)
    weighted_norm_after = AUDIT._matmul(
        AUDIT._matmul(AUDIT._transpose(projection), weight), projection
    )
    energy_defect = AUDIT._difference(weight, weighted_norm_after)
    expected_defect = AUDIT._matmul(weight, AUDIT._difference(identity, projection))
    complement = AUDIT._difference(identity, projection)
    complement_gram = AUDIT._matmul(
        AUDIT._matmul(AUDIT._transpose(complement), weight), complement
    )
    checks = {
        "idempotent": _is_zero(AUDIT._difference(AUDIT._matmul(projection, projection), projection)),
        "weighted_self_adjoint": _is_zero(AUDIT._difference(weighted_adjoint, weighted_projection)),
        "energy_defect_is_weighted_complement": _is_zero(AUDIT._difference(energy_defect, expected_defect)),
        "complement_gram_equals_weighted_complement": _is_zero(AUDIT._difference(complement_gram, expected_defect)),
        "rank_four_projection": AUDIT._rank(projection) == 4,
        "rank_six_energy_defect": AUDIT._rank(energy_defect) == 6,
    }
    return {
        "composition": name,
        "rank": AUDIT._rank(projection),
        "energy_defect_rank": AUDIT._rank(energy_defect),
        "checks": checks,
        "matrix_exact": _matrix_strings(projection),
        "energy_defect_exact": _matrix_strings(energy_defect),
    }


def build_artifact() -> dict:
    weight = AUDIT._weighted_tensor_norm()
    m_right = AUDIT._face_maps(+1)[0]
    m_left = AUDIT._face_maps(-1)[0]
    left_after_right = AUDIT._matmul(m_left, m_right)
    right_after_left = AUDIT._matmul(m_right, m_left)
    right_cycle = _projection_record("M_left*M_right", left_after_right, weight)
    left_cycle = _projection_record("M_right*M_left", right_after_left, weight)

    # For a plane-front profile F(t-x), (a,b)=(0,2F') at the right face;
    # for G(t+x), (a,b)=(2G',0). The roles reverse at the left face.
    characteristic_checks = {
        "right_outgoing_F_has_a_zero_b_two": _characteristic_coefficients("F", +1) == (0, 2),
        "right_incoming_G_has_a_two_b_zero": _characteristic_coefficients("G", +1) == (2, 0),
        "left_outgoing_G_has_a_zero_b_two": _characteristic_coefficients("G", -1) == (0, 2),
        "left_incoming_F_has_a_two_b_zero": _characteristic_coefficients("F", -1) == (2, 0),
        "right_then_left_propagation_preserves_profile_phase": (
            _phase_coefficients("G", (1, 0), (0, 1))
            == _phase_coefficients("G", (1, 1), (0, 0))
        ),
        "left_then_right_propagation_preserves_profile_phase": (
            _phase_coefficients("F", (1, 0), (0, 0))
            == _phase_coefficients("F", (1, 1), (0, 1))
        ),
    }
    all_checks = {
        "one_face_source_audit_passes": all(AUDIT.build_artifact()["checks"].values()),
        "right_cycle_is_W_orthogonal_projection": all(right_cycle["checks"].values()),
        "left_cycle_is_W_orthogonal_projection": all(left_cycle["checks"].values()),
        **characteristic_checks,
    }
    source_hashes = {
        ONE_FACE_AUDIT.relative_to(ROOT).as_posix(): _sha256(ONE_FACE_AUDIT),
        ONE_FACE_ARTIFACT.relative_to(ROOT).as_posix(): _sha256(ONE_FACE_ARTIFACT),
        Path(__file__).resolve().relative_to(ROOT).as_posix(): _sha256(Path(__file__).resolve()),
    }
    source_url = "https://arxiv.org/html/0807.3207"
    return {
        "schema_version": "core-curved-3p1-gh-krsw-normal-incidence-slab-cycle-v1",
        "artifact": "curved_3p1_gh_krsw_normal_incidence_slab_cycle",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "PASS_EXACT_NORMAL_INCIDENCE_SLAB_CYCLE_NONAMPLIFICATION" if all(all_checks.values()) else "FAIL_NORMAL_INCIDENCE_SLAB_CYCLE",
        "major_result_id": "CORE_CURVED_3P1_GH_KRSW_NORMAL_INCIDENCE_SLAB_CYCLE",
        "major_result": {
            "major_result_id": "CORE_CURVED_3P1_GH_KRSW_NORMAL_INCIDENCE_SLAB_CYCLE",
            "topic": "core_curved_3p1",
            "closure_level": "CLOSED_FOR_LANE" if all(all_checks.values()) else "OPEN",
            "what_is_closed": [
                "For the source-free flat linearized wave system at normal incidence, characteristic amplitudes propagate unchanged between two parallel faces, up to travel-time delay.",
                "Both possible two-face reflection-cycle maps are exact rank-4 orthogonal projections in the Frobenius tensor weight W.",
                "The W-weighted pulse energy after a full round trip is no larger than before it; the exact loss is the squared W norm of the projected-out component.",
                "Since each cycle map is idempotent, repeated complete cycles have no cumulative amplitude or pulse-energy growth in this restricted lane.",
            ],
            "what_remains_open": [
                "This is the constrained second-order linear wave sector with gamma2=0, not the full first-order GH evolution or its SAT discretization.",
                "Tangential frequencies, glancing modes, complex-frequency uniform estimates, curved/variable-coefficient backgrounds, matter sources, nonlinear terms, and corners remain open.",
                "The result does not prove the full 3D Core parent or Gravity compatibility.",
            ],
            "equation_or_mapping": {
                "flat_wave_solution": "gamma(t,x)=F(t-x)+G(t+x), componentwise, with zero tangential derivatives",
                "characteristics": "a_s=(partial_t+s*partial_x)gamma; b_s=(partial_t-s*partial_x)gamma; q_s=-a_s; p_s=-b_s",
                "boundary_maps": "q_right=M_right*p_right; q_left=M_left*p_left",
                "propagation": "p_left(t+L)=q_right(t); p_right(t+2L)=q_left(t+L)=P_right*p_right(t), P_right=M_left*M_right; the reverse cycle uses P_left=M_right*M_left",
                "weighted_projector": "P^2=P; P^T W=W P; rank(P)=4; W=diag(1 for diagonal,2 for off-diagonal symmetric tensor slots)",
                "pulse_energy": "E[p]=(1/4)*integral(p(t)^T W p(t) dt); E[Pp]=E[p]-(1/4)*integral(((I-P)p)^T W((I-P)p) dt)<=E[p]",
                "physical_cycle_time": "2L/c; the audit uses geometric units c=1",
            },
            "units": "Geometric units c=1; tensor derivative amplitudes and W-weighted linear wave pulse flux. Physical round-trip time is 2L/c.",
            "derivation_class": "exact rational face-map algebra plus exact normal-incidence d'Alembert propagation",
            "observable": "positive componentwise wave-system flux in the declared symmetric-tensor norm; not a physical gravitational-energy observable",
            "data_role": "published standard-GR boundary hierarchy plus exact internal analytic construction; no empirical data, fitting, or holdout",
            "verification_status": "PASS_EXACT_NORMAL_INCIDENCE_SLAB_CYCLE_NONAMPLIFICATION" if all(all_checks.values()) else "FAIL_NORMAL_INCIDENCE_SLAB_CYCLE",
            "open_blockers": [
                "extend the cycle-energy argument to nonzero tangential Fourier modes and the full 4+2+4 first-order GH characteristic system",
                "prove an SBP-SAT energy estimate for the actual spatial discretization, including edges and corners",
            ],
            "dependency_unlocked": "none",
            "claim_boundary": "Exact non-amplification for source-free, flat, linearized, normal-incidence slab reflection cycles only; this is not Bondi/ADM energy, full GH stability, curved 3+1 closure, UET validation, or Gravity compatibility.",
        },
        "source": {
            "title": "Boundary conditions for coupled quasilinear wave equations with application to isolated systems",
            "authors": ["H.-O. Kreiss", "O. Reula", "O. Sarbach", "J. Winicour"],
            "locator": "Section IV.1, equations (55)-(67) and harmonic constraints immediately following equation (67)",
            "url": source_url,
            "role": "imported standard-GR linearized harmonic boundary hierarchy; the finite-slab propagation argument is the present exact specialization",
        },
        "scope": {
            "domain": "0<=x<=L, two plane faces, Minkowski background",
            "field_equation": "(partial_t^2-partial_x^2)gamma_ab=0, for ten symmetric tensor components",
            "boundary_conditions": "homogeneous KRSW plane hierarchy plus harmonic constraints, specialized to normal incidence",
            "characteristic_convention": "principal characteristic variables; lower-order gamma2*psi term omitted",
            "excluded": ["tangential derivatives", "curvature", "variable lapse or shift", "matter", "nonlinear terms", "discrete SAT evolution", "edge and corner conditions"],
        },
        "cycles": {"right_then_left": right_cycle, "left_then_right": left_cycle},
        "checks": all_checks,
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
