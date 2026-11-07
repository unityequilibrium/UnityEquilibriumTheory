"""Reconcile the two recorded evidence sources before reporting legacy closure."""

from math import isfinite


MASTER = "docs/core/02_equations/matter_space/uet_master_equation.py"
CLOSURE = "docs/core/07_artifacts/gates/uet_legacy_variational_closure.json"
PAIR = "legacy_potential_derivative_pair"
STATUS = "COMPATIBLE_CONDITIONAL"
LANE = "legacy_variational_v1"
BOUNDARY = (
    "Normalized legacy_variational_v1 only; legacy_local remains a quarantined "
    "non-variational comparator. No SI mapping or standard-theory special case established."
)


def finding(report, finding_id):
    matches = [item for item in report.get("findings", []) if item.get("finding_id") == finding_id]
    if len(matches) != 1 or matches[0].get("status") != STATUS:
        raise ValueError(f"Missing, duplicate or non-conditional legacy finding: {finding_id}")
    return matches[0]


def legacy_potential_finding(compatibility, closure):
    pair = finding(compatibility, PAIR)
    recorded = finding(closure, PAIR)
    comparator = recorded.get("legacy_comparator", {})
    if (
        compatibility.get("audit_status") != "PASS"
        or PAIR in compatibility.get("controlling_blockers", [])
        or closure.get("audit_status") != "PASS"
        or closure.get("closure_status") != "PASS_CONDITIONAL"
        or closure.get("controlling_blockers") != []
        or closure.get("unresolved_scope_conflicts") != []
        or closure.get("canonical_mode") != LANE
        or recorded.get("canonical_mode") != LANE
        or closure.get("legacy_default_mode") != "legacy_local"
        or comparator.get("status") != "QUARANTINED_COMPARATOR"
        or comparator.get("preserved") is not True
        or closure.get("evidence_inputs", {}).get("master_equation")
        not in {MASTER, "docs/core/uet_master_equation.py"}
        or pair.get("equation_family") != "uet.legacy.master_potential"
        or not any(
            item.get("path") == MASTER
            and item.get("details", {}).get("dynamics_selects_exact_derivative_in_canonical_mode") is True
            and item.get("details", {}).get("legacy_comparator_present") is True
            for item in pair.get("evidence", [])
        )
    ):
        raise ValueError("Legacy potential evidence does not agree on the implementation or modes")

    metrics = pair.get("metrics", {})
    reference = recorded.get("metrics", {})
    canonical = reference.get("canonical_finite_difference_max_absolute_residual")
    historical = reference.get("legacy_comparator_finite_difference_max_absolute_residual")
    threshold = reference.get("threshold")
    if (
        not all(type(x) in (int, float) and isfinite(x) for x in (canonical, historical, threshold))
        or not 0 <= canonical <= threshold < historical
        or metrics.get("canonical_max_absolute_residual") != canonical
        or metrics.get("legacy_comparator_max_absolute_residual") != historical
        or metrics.get("threshold") != threshold
        or not reference.get("samples")
        or metrics.get("sample_points") != reference["samples"]
        or not recorded.get("declared_relation")
        or pair.get("declared_relation") != recorded["declared_relation"]
        or not recorded.get("analytic_derivative")
        or metrics.get("analytic_derivative") != recorded["analytic_derivative"]
    ):
        raise ValueError("Legacy potential evidence disagrees on the relation, residuals or threshold")
    return pair


def legacy_family_status(compatibility, closure):
    pair = legacy_potential_finding(compatibility, closure)
    sign = finding(compatibility, "legacy_information_gradient_sign").get("metrics", {})
    sign_record = finding(closure, "legacy_information_gradient_sign")
    operator = finding(compatibility, "legacy_information_operator").get("metrics", {})
    operator_record = finding(closure, "legacy_information_operator").get("contract", {})
    beta = finding(compatibility, "legacy_beta_unit_semantics").get("metrics", {})
    if (
        sign_record.get("canonical_mode") != LANE
        or sign.get("canonical_source_sign") != -1
        or sign.get("expected_canonical_source_sign") != -1
        or sign.get("legacy_comparator_source_sign") != 1
        or sign.get("canonical_source_sign") != sign_record.get("canonical_source_sign")
        or sign.get("legacy_comparator_source_sign") != sign_record.get("legacy_comparator_source_sign")
        or sign_record.get("c_source_sign_matches") is not True
        or operator.get("canonical_operator_closed") is not True
        or operator.get("historical_box_is_comparator") is not True
        or not all(operator_record.get(key) is True for key in (
            "periodic_laplacian", "periodic_gradient_energy", "canonical_source",
            "first_order_update", "canonical_gradient_flow_declared", "historical_box_is_comparator",
        ))
        or beta.get("normalized_beta_contract_closed") is not True
        or beta.get("stale_beta_unit_label_count") != 0
    ):
        raise ValueError("Legacy C/I operator or normalized beta evidence does not agree")
    return pair["status"]
