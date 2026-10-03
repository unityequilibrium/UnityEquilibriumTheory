"""Author table identity and omitted-basis separation, not calibration."""

import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import Research_T13_Low_Q_Source_Boundary as S


@pytest.fixture(scope="module")
def artifact():
    return json.loads(S.OUTPUT.read_text())


def test_q4_alias_and_separation_exact():
    for maximum in S.Q_GRID:
        result = S.control(maximum)
        assert result["three_alias_identity_exact"]
        assert result["four_recovery_exact"] and result["four_determinant_identity_exact"]
    constants = [S.control(q)["alias_scaled_constants_exact"] for q in S.Q_GRID]
    assert constants[0] == constants[1] == constants[2]
    assert S.M.decode(constants[0][2]) != 0


@pytest.mark.parametrize("qs", [[S.F(1)]*4, [S.F(0), S.F(1), S.F(2), S.F(3)],
                                 [S.F(-1), S.F(1), S.F(2), S.F(3)], [S.F(1), S.F(2)]])
def test_invalid_geometry_rejected(qs):
    with pytest.raises(ValueError):
        S.four_weights(qs)


@pytest.mark.parametrize("qs", [(S.F(1), S.F(2), S.F(3), S.F(4)), tuple(reversed(S.RATIOS)), S.RATIOS])
def test_generalized_determinant_and_matrix_inverse(qs):
    weights, determinant = S.four_weights(qs)
    assert determinant == S.determinant_formula(qs) != 0
    for k, power in enumerate(S.POWERS):
        assert all(sum(weights[k][i]*qs[i]**p for i in range(4)) == int(p == power) for p in S.POWERS)


def test_numeric_source_parsing_preserves_missing_and_ancestry(artifact):
    registry = json.loads((S.ROOT/S.REGISTRY).read_text())
    rows = S.parse_all((S.ROOT/registry["raw_files"][0]["path"]).read_bytes(), [S.F(str(p)) for p in registry["protocol"]["pressures_bar"]])
    p0, separators = S.parse_p0((S.ROOT/registry["raw_files"][1]["path"]).read_bytes())
    assert len(rows) == 1050*7 and len({r["row_id"] for r in rows}) == len(rows)
    assert any(r["energy_lexical"] is None for r in rows)
    assert any(r["error_lexical"] is None for r in p0) and separators
    assert {"ULTRASOUND", "COMBINED_ULTRASOUND_NEUTRON", "NEUTRON"} == {r["ancestry"] for r in p0}
    r = next(r for r in p0 if r["q_lexical"] == 0)
    assert r["energy_lexical"] == 0 and r["error_lexical"] is None
    for row in rows+p0:
        assert hashlib.sha256(row["source_line_lexical"].encode(row["line_encoding"])).hexdigest() == row["line_sha256"]
    assert artifact["source_summaries"][0]["row_cells_archived_including_missing"] == len(rows)


def test_wrong_units_are_rejected():
    with pytest.raises(ValueError):
        S.parse_p0(b"k\te\terr(e)\ncm-1\tmeV\tmeV\n0\t0\t--\n")


def test_raw_byte_preservation_rules_are_declared():
    attributes = (S.ROOT/(S.PREFIX+"Data/03_Research/godfrin_2021_v1/.gitattributes")).read_text()
    assert "*.txt -text" in attributes and "*.tex -text" in attributes


def test_no_source_imputation_or_physical_inverse(artifact):
    windows = artifact["source_windows"]
    assert windows[0]["three_node"][2]["classification"] == "MISSING_ROWS_NO_INTERPOLATION_OR_SUBSTITUTE"
    assert any(w.get("contains_low_q_or_hybrid_ancestry") for table in windows for w in table["three_node"]+[table["four_node"]])
    assert all(w["physical_I_estimate"] is None for table in windows for w in table["three_node"]+[table["four_node"]])
    assert not artifact["source_is_blind_holdout"] and not artifact["reported_errors_assumed_one_sigma"]
    assert not artifact["four_term_basis_excludes_all_other_terms_as_physics"]
    assert artifact["external_numeric_rows_admitted_to_UET_comparison"] == 0


def test_registry_and_protocol_scope(artifact):
    registry = json.loads((S.ROOT/S.REGISTRY).read_text())
    p = registry["protocol"]
    assert p == artifact["declared_protocol"]
    assert registry["thresholds"] == artifact["thresholds"] == S.GATES
    assert tuple(S.F(str(q)) for q in p["q4_control_maxima"]) == S.Q_GRID
    assert tuple(S.F(v) for v in p["four_node_ratios"]) == S.RATIOS
    assert tuple(S.F(v) for v in p["q4_control_beta"]) == S.BETA
    assert tuple(tuple(S.F(str(q)) for q in row) for row in p["three_node_physical_windows_angstrom_inverse"]) == S.WINDOWS
    assert tuple(S.F(str(q)) for q in p["four_node_physical_window_angstrom_inverse"]) == S.FOUR_WINDOW
    assert p["source_inspected_before_protocol"]
    assert len(artifact["report"]) == 11 and artifact["prior_Xie_context_exposure_review"] == "REVIEW_REQUIRED"
    required = {"ontology", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary"}
    assert all(required <= set(e) for e in registry["equation_entries"])
    assert artifact["precision_extension"] == registry["precision_extension"]
    assert registry["precision_extension"]["digits"] == S.MP_DIGITS
    assert registry["precision_extension"]["relative_tolerance"] == S.MP_GATE


def test_float64_failure_and_new_precision_method_have_separate_status(artifact):
    assert artifact["closure_level"] == "PARTIAL" and artifact["verification_status"] == "FAIL_SCOPED_LOW_Q_SOURCE_BOUNDARY"
    assert not artifact["checks"]["independent_scaled_float_control"]
    assert all(artifact["extended_checks"].values())
    assert artifact["numeric_source_archive_acquired"] and artifact["q4_alias_verified"] and artifact["four_node_separation_verified"]
    assert all(s["closure_level"] == "CLOSED_FOR_LANE" for s in artifact["subresults"])
    assert hashlib.sha256(S.FIRST_FAILURE.read_bytes()).hexdigest() == S.FIRST_FAILURE_SHA
    assert json.loads(S.FIRST_FAILURE.read_text())["checks"] == artifact["checks"]


@pytest.mark.parametrize("flag", ["physical_q5_measured", "physical_q4_detected_by_this_audit", "physical_I_inferred",
    "physical_joint_covariance_acquired", "physical_material_map_admitted", "physical_measurement_design_completed",
    "independent_alpha_Phi_K_admitted", "physical_Kubo_emitted", "full_SK_KMS_matching_closed",
    "nonlinear_parent_action_completed", "controlled_full_action_truncation_error_established", "full_core_unlock",
    "core_composition_gate_overwritten", "old_source_work_audit_promoted", "external_UET_parameter_fitting",
    "missing_row_or_uncertainty_imputation", "source_window_tuning", "clipping", "cone_padding", "claim_promotion", "xie_2026_accessed"])
def test_no_physical_promotion(artifact, flag):
    assert artifact[flag] is False


def test_current_and_protected_hashes(artifact):
    for item in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]:
        assert hashlib.sha256((S.ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_runtime_path_read_allowlist(monkeypatch, artifact):
    allowed = {str((S.ROOT/item["path"]).resolve()).casefold() for item in artifact["evidence_artifacts"]+artifact["protected_evidence_hashes"]}
    old_bytes, old_text, observed = Path.read_bytes, Path.read_text, set()

    def guard(path):
        name = str(path.resolve()).casefold()
        assert name in allowed, f"undeclared data read: {path}"
        observed.add(name)

    def read_bytes(path):
        guard(path)
        return old_bytes(path)

    def read_text(path, *args, **kwargs):
        guard(path)
        return old_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    monkeypatch.setattr(Path, "read_text", read_text)
    result = S.audit()
    assert result["checks"] == artifact["checks"]
    assert observed and not result["xie_2026_accessed"]
