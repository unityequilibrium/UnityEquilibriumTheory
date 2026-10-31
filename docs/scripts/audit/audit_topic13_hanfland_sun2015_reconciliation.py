"""Reconcile a published graphite DFT strain model with Hanfland source rows."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOPIC_DATA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_hanfland_sun2015_reconciliation.json"
FULL_GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
TEST_FILE = ROOT / (
    "docs/core/05_tests/regression/root/"
    "test_topic13_hanfland_sun2015_reconciliation.py"
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_row(package, name):
    rows = package.get("rows")
    if isinstance(rows, dict) and name in rows:
        return rows[name]
    if isinstance(rows, list):
        for row in rows:
            if row.get("row_id") == name:
                return row
    raise ValueError("missing source row identity: " + name)


def _row(package, name):
    try:
        value = float(_source_row(package, name)["value"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("missing or invalid source row: " + name) from exc
    if not (value == value and abs(value) != float("inf")):
        raise ValueError("non-finite source row: " + name)
    return value


def _uncertainty(package, name):
    try:
        value = float(_source_row(package, name)["uncertainty"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("missing or invalid source uncertainty: " + name) from exc
    if value < 0 or not (value == value and abs(value) != float("inf")):
        raise ValueError("invalid source uncertainty: " + name)
    return value


def _bounds(value, uncertainty):
    return value - uncertainty, value + uncertainty


def _envelope(function, *bounds):
    values = [function(*point) for point in itertools.product(*bounds)]
    return [min(values), max(values)]


def _overlap(left, right):
    return max(left[0], right[0]) <= min(left[1], right[1])


def _gamma(slope_gpa_inverse, gamma_prime, bulk_a_gpa, bulk_c_gpa):
    if bulk_a_gpa <= 0 or bulk_c_gpa <= 0:
        raise ValueError("compressional moduli must be positive")
    return (slope_gpa_inverse - gamma_prime / bulk_c_gpa) * bulk_a_gpa / 2.0


def _pressure_slope(gamma, gamma_prime, bulk_a_gpa, bulk_c_gpa):
    if bulk_a_gpa <= 0 or bulk_c_gpa <= 0:
        raise ValueError("compressional moduli must be positive")
    return 2.0 * gamma / bulk_a_gpa + gamma_prime / bulk_c_gpa


def assess(hanfland, sun):
    gamma_prime = _row(sun, "e2g2_axial_gruneisen_prime")
    shift_percent = _row(sun, "e2g2_axial_frequency_shift_per_percent_strain")
    sun_frequency = _row(sun, "e2g2_unstrained_frequency")
    sun_gamma = _row(sun, "e2g2_refined_hydrostatic_gruneisen")
    sun_pressure_shift = _row(sun, "e2g2_hydrostatic_frequency_shift")
    if sun["data_role"] != "PUBLISHED_DFT_MODEL_COMPARISON_NOT_EXPERIMENTAL_CALIBRATION":
        raise ValueError("Sun source is not labelled as a DFT model comparator")
    if sun["source_relationship"]["independent_experimental_row"] is not False:
        raise ValueError("DFT model must not be admitted as an independent measured row")

    table_slope = _row(hanfland, "E2g2_pressure_log_slope")
    table_error = _uncertainty(hanfland, "E2g2_pressure_log_slope")
    absolute_slope = _row(hanfland, "E2g2_absolute_pressure_slope")
    absolute_error = _uncertainty(hanfland, "E2g2_absolute_pressure_slope")
    frequency = _row(hanfland, "E2g2_frequency")
    frequency_error = _uncertainty(hanfland, "E2g2_frequency")
    bulk_a = _row(hanfland, "axial_modulus_a")
    bulk_a_error = _uncertainty(hanfland, "axial_modulus_a")
    bulk_c = _row(hanfland, "axial_modulus_c")
    bulk_c_error = _uncertainty(hanfland, "axial_modulus_c")

    table_bounds = _bounds(table_slope, table_error)
    absolute_bounds = (
        (absolute_slope - absolute_error) / (frequency + frequency_error),
        (absolute_slope + absolute_error) / (frequency - frequency_error),
    )
    ba_bounds = _bounds(bulk_a, bulk_a_error)
    bc_bounds = _bounds(bulk_c, bulk_c_error)
    if min(
        table_bounds[0],
        absolute_bounds[0],
        frequency - frequency_error,
        ba_bounds[0],
        bc_bounds[0],
        sun_frequency,
    ) <= 0:
        raise ValueError("source intervals must remain positive")

    table_gamma = _gamma(table_slope, gamma_prime, bulk_a, bulk_c)
    table_gamma_bounds = _envelope(
        lambda slope, ba, bc: _gamma(slope, gamma_prime, ba, bc),
        table_bounds,
        ba_bounds,
        bc_bounds,
    )
    absolute_gamma = _gamma(
        absolute_slope / frequency, gamma_prime, bulk_a, bulk_c
    )
    absolute_gamma_bounds = _envelope(
        lambda slope, ba, bc: _gamma(slope, gamma_prime, ba, bc),
        absolute_bounds,
        ba_bounds,
        bc_bounds,
    )
    model_slope = _pressure_slope(sun_gamma, gamma_prime, bulk_a, bulk_c)
    model_slope_bounds = _envelope(
        lambda ba, bc: _pressure_slope(sun_gamma, gamma_prime, ba, bc),
        ba_bounds,
        bc_bounds,
    )
    gamma_prime_from_shift = -100.0 * shift_percent / sun_frequency

    return {
        "source_roles": {
            "hanfland": "MEASURED_300K_HYDROSTATIC_GRAPHITE",
            "sun": "PUBLISHED_0K_DFT_MODEL",
            "independent_experimental_axial_row": False,
            "source_relationship": sun["source_relationship"]["relationship"],
            "temperature_match": False,
            "mode_match": "E2g(2) family comparison only; UET mode identity is not established",
        },
        "conditional_decomposition": {
            "equation": "dln(nu)/dP = 2*gamma/B_a + gamma_prime/B_c",
            "gamma_prime_DFT": gamma_prime,
            "gamma_prime_from_reported_shift": gamma_prime_from_shift,
            "gamma_prime_rounding_residual": abs(gamma_prime_from_shift - gamma_prime),
            "D_c_over_x": -2.0 * gamma_prime,
            "table_log_slope": {
                "input_GPa_inverse": table_slope,
                "input_parenthetic_error_GPa_inverse": table_error,
                "conditional_gamma_nominal": table_gamma,
                "conditional_gamma_rectangular_sensitivity": table_gamma_bounds,
                "conditional_D_ab_over_x_rectangular_sensitivity": [
                    -2.0 * table_gamma_bounds[1],
                    -2.0 * table_gamma_bounds[0],
                ],
            },
            "abstract_absolute_slope": {
                "input_cm_inverse_GPa": absolute_slope,
                "input_parenthetic_error_cm_inverse_GPa": absolute_error,
                "normalized_slope_nominal_GPa_inverse": absolute_slope / frequency,
                "normalized_slope_rectangular_sensitivity_GPa_inverse": absolute_bounds,
                "conditional_gamma_nominal": absolute_gamma,
                "conditional_gamma_rectangular_sensitivity": absolute_gamma_bounds,
            },
            "uncertainty_interpretation": (
                "Hanfland parenthetic errors are propagated as endpoint rectangles "
                "with rounded DFT gamma_prime fixed. They are not confidence "
                "intervals and omit DFT model uncertainty and covariance."
            ),
        },
        "cross_source_reconciliation": {
            "Sun_reported_hydrostatic_gamma": sun_gamma,
            "pressure_slope_from_Sun_gamma_and_Hanfland_moduli_GPa_inverse": model_slope,
            "model_slope_rectangular_sensitivity_GPa_inverse": model_slope_bounds,
            "Hanfland_table_log_slope_interval_GPa_inverse": table_bounds,
            "overlap_with_table_interval": _overlap(model_slope_bounds, table_bounds),
            "Hanfland_abstract_normalized_slope_interval_GPa_inverse": absolute_bounds,
            "overlap_with_abstract_interval": _overlap(model_slope_bounds, absolute_bounds),
            "Sun_DFT_hydrostatic_slope_cm_inverse_GPa": sun_pressure_shift,
            "Hanfland_abstract_absolute_slope_interval_cm_inverse_GPa": [
                absolute_slope - absolute_error,
                absolute_slope + absolute_error,
            ],
            "direct_DFT_slope_inside_Hanfland_abstract_interval": (
                absolute_slope - absolute_error
                <= sun_pressure_shift
                <= absolute_slope + absolute_error
            ),
            "DFT_vs_measured_unstrained_frequency_relative_difference_percent": (
                100.0 * (sun_frequency - frequency) / frequency
            ),
            "interpretation": (
                "The conditional comparison is route-sensitive. The narrow table "
                "slope rectangle does not overlap the prediction from Sun's "
                "reported gamma, while the broader abstract-slope rectangle does. "
                "Different fit ranges, 0 K versus 300 K, and unreported DFT model "
                "uncertainty prevent rejecting the model."
            ),
        },
        "identifiability": {
            "single_mode_observational_rank": 1,
            "unknown_strain_components_per_mode": 2,
            "observational_nullity": 1,
            "DFT_gamma_prime_is_an_observation": False,
            "empirical_rank_gain": 0,
            "conditional_solution_if_gamma_prime_fixed": True,
        },
        "claim_boundary": {
            "physical_D_tensor": None,
            "alpha_Phi_K": None,
            "TTG_validation": False,
            "full_topic13_closure": False,
            "dependency_unlocked": [],
            "claim_promotion": False,
            "holdout_access": "NOT_ACCESSED",
        },
    }


def main():
    hanfland_path = TOPIC_DATA / "hanfland_1989_raman_deformation_source_package.json"
    sun_path = TOPIC_DATA / "sun_2015_graphite_raman_strain_model_source_package.json"
    hanfland = json.loads(hanfland_path.read_text(encoding="utf-8"))
    sun = json.loads(sun_path.read_text(encoding="utf-8"))
    full_gate = json.loads(FULL_GATE.read_text(encoding="utf-8"))
    if full_gate.get("status") != "BLOCKED_OPEN_T13_FULL_BRIDGE":
        raise ValueError("unexpected Topic 13 full-gate state")
    if full_gate.get("claim_promotion") is not False:
        raise ValueError("Topic 13 claim-promotion boundary changed")
    raw_hanfland = ROOT / hanfland["source"]["local_path"]
    if digest(raw_hanfland) != hanfland["source"]["sha256"]:
        raise ValueError("Hanfland source PDF hash mismatch")

    result = assess(hanfland, sun)
    evidence_paths = [
        hanfland_path, sun_path, raw_hanfland, Path(__file__), TEST_FILE, FULL_GATE,
    ]
    artifact = {
        "schema_version": "t13-hanfland-sun2015-conditional-reconciliation-v1",
        "major_result_id": "T13_HANFLAND_SUN2015_CONDITIONAL_RAMAN_RECONCILIATION",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "The sign and units of the Sun DFT out-of-plane coefficient reconcile with its reported E2g(2) frequency shift at printed precision.",
            "The conditional in-plane coefficient implied by Hanfland's separate hydrostatic-slope routes is calculated with explicit rectangular sensitivity envelopes.",
            "The DFT source is a model condition, not an independent experimental row or empirical rank increase."
        ],
        "equation_or_mapping": (
            "dln(nu)/dP = 2*gamma/B_a + gamma_prime/B_c; "
            "gamma=(dln(nu)/dP-gamma_prime/B_c)*B_a/2; "
            "D_ab/x=-2*gamma; D_c/x=-2*gamma_prime"
        ),
        "units": {
            "pressure_slope": "GPa^-1",
            "compressional_moduli": "GPa",
            "gamma_and_gamma_prime": "dimensionless",
            "strain": "dimensionless",
            "D_over_x": "dimensionless per unit strain",
            "frequency": "cm^-1"
        },
        "derivation_class": "conditional_source_model_substitution_not_UET_derivation",
        "observable": "Gamma-point graphite E2g(2) Raman frequency strain response",
        "data_role": "MEASURED_SOURCE_ROWS_PLUS_PUBLISHED_DFT_MODEL_COMPARISON",
        "verification_status": "PASS_CONDITIONAL_SOURCE_MODEL_RECONCILIATION",
        "result": result,
        "open_blockers": [
            "same_state_independent_experimental_axial_strain_row_missing",
            "Sun_DFT_gamma_prime_model_error_and_uncertainty_unreported",
            "0K_DFT_to_300K_measurement_transfer_unestablished",
            "Raman_mode_to_UET_observable_and_Phi_normalization_missing",
            "independent_graphite_alpha_Phi_K_missing"
        ],
        "controlling_blocker": "independent_same_state_axial_strain_evidence_and_Phi_energy_anchor_missing",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_promotion": False,
        "full_topic13_gate_status": full_gate["status"],
        "full_topic13_gate_sha256": digest(FULL_GATE),
        "source_row_hashes": {
            "hanfland_" + key: hashlib.sha256(
                json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            for key, value in (
                (row["row_id"], row) for row in hanfland["rows"]
            )
        } | {
            "sun_" + key: hashlib.sha256(
                json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            for key, value in sun["rows"].items()
        },
        "evidence_hashes": {
            str(path.relative_to(ROOT)).replace("\\", "/"): digest(path)
            for path in evidence_paths
        },
        "claim_boundary": (
            "Conditional Raman strain decomposition only. The DFT value does not "
            "supply an independent measurement, identify a physical UET D tensor "
            "or alpha_Phi_K, or close Topic 13."
        ),
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(
        json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(artifact, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
