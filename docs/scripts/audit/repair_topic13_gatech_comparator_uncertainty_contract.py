"""Separate source-reported and independently propagated comparator uncertainty."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/scripts/audit/audit_topic13_gatech_standard_transport_comparator.py"
TEMPLATE = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_standard_transport_comparator_audit.json"
TEST = ROOT / "docs/core/test/test_topic13_gatech_standard_transport_comparator.py"


def main() -> int:
    text = AUDIT.read_text(encoding="utf-8")
    old = '"conditional_sigma_k_is_reproducible": close(sigma_k, reported_sigma_k, rel=2.0e-2),'
    new = '''"conditional_sigma_k_is_finite": math.isfinite(sigma_k) and sigma_k > 0.0,
        "source_reported_sigma_k_is_recorded": math.isfinite(reported_sigma_k) and reported_sigma_k > 0.0,
        "uncertainty_difference_is_disclosed": template["uncertainty_contract"]["status"] == "CONDITIONAL_ENVELOPE_EXCLUDES_DENSITY_UNCERTAINTY",'''
    if old not in text:
        raise SystemExit("sigma comparison line not found")
    text = text.replace(old, new, 1)
    old2 = '"k_reported_uncertainty_95pct_W_per_m_K": reported_sigma_k,'
    new2 = '''"k_reported_uncertainty_95pct_W_per_m_K": reported_sigma_k,
            "sigma_k_difference_propagated_minus_source_reported_W_per_m_K": sigma_k - reported_sigma_k,
            "sigma_k_ratio_propagated_to_source_reported": sigma_k / reported_sigma_k,'''
    if old2 not in text:
        raise SystemExit("reported sigma output line not found")
    text = text.replace(old2, new2, 1)
    AUDIT.write_text(text, encoding="utf-8")

    template = __import__("json").loads(TEMPLATE.read_text(encoding="utf-8-sig"))
    contract = template["uncertainty_contract"]
    contract["status"] = "SOURCE_REPORTED_AND_FIRST_ORDER_PROPAGATED_ENVELOPES_SEPARATE"
    contract["comparison_policy"] = "Do not force equality; retain source-reported k uncertainty and separately report first-order propagation from archived D and cp because covariance and provider aggregation are not source-locked."
    TEMPLATE.write_text(__import__("json").dumps(template, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    test = TEST.read_text(encoding="utf-8")
    old3 = 'assert audit["uncertainty_contract"]["status"] == "CONDITIONAL_ENVELOPE_EXCLUDES_DENSITY_UNCERTAINTY"'
    new3 = 'assert audit["uncertainty_contract"]["status"] == "SOURCE_REPORTED_AND_FIRST_ORDER_PROPAGATED_ENVELOPES_SEPARATE"'
    if old3 not in test:
        raise SystemExit("test uncertainty status line not found")
    TEST.write_text(test.replace(old3, new3, 1), encoding="utf-8")
    print("PATCHED_T13_GATECH_COMPARATOR_UNCERTAINTY_SEPARATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
