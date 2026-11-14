"""Verification tests for lane-specific UET coarse graining."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_coarse_graining import (
    CoarseGrainingRecord,
    coarse_grain,
    coarse_graining_consistency,
    coarse_graining_contract,
    refine_coarse_graining,
    scale_dependence_audit,
)


def _record(lane: str, cells: int = 4) -> CoarseGrainingRecord:
    input_types = {
        "phase": "microscopic_order_field",
        "charge": "coarse_o2_noether_charge_density",
        "density": "si_mass_density_field",
        "telegraph": "finite_cone_collective_field",
    }
    unit_lanes = {
        "phase": "normalized",
        "charge": "natural_to_normalized",
        "density": "si_mass_density",
        "telegraph": "normalized",
    }
    return CoarseGrainingRecord(
        lane_id=lane,
        microscopic_state_type=input_types[lane],
        kernel="uniform_block_average_v1",
        reference_frame="declared_lab_frame",
        spatial_scale=1.0 / cells,
        temporal_scale=0.25,
        boundary_rule="periodic",
        unit_lane=unit_lanes[lane],
        parameter_provenance="locked_test_fixture",
        information_lost=("within_cell_fluctuations", "microscopic_labels"),
        observable_target=f"{lane}_diagnostic",
        output_cells=cells,
        reference_value=0.0,
        coordinate_scale=2.0,
    )


@pytest.mark.parametrize("lane", ("phase", "charge", "density", "telegraph"))
def test_all_lanes_are_explicit_and_preserve_the_declared_mean(lane: str) -> None:
    field = np.arange(1.0, 9.0)
    result = coarse_grain(field, _record(lane))
    assert result.lane_id == lane
    assert result.C.shape == (4,)
    assert result.diagnostics["universal_C_identity"] is False
    assert result.diagnostics["map_invertible"] is False
    assert result.diagnostics["mean_preservation_error"] <= 1e-12


def test_many_to_one_map_is_demonstrated_not_only_declared() -> None:
    left = np.array([0.0, 2.0, 2.0, 4.0, 4.0, 6.0, 6.0, 8.0])
    right = np.array([1.0, 1.0, 3.0, 3.0, 5.0, 5.0, 7.0, 7.0])
    a = coarse_grain(left, _record("phase"))
    b = coarse_grain(right, _record("phase"))
    assert not np.array_equal(left, right)
    assert np.array_equal(a.C, b.C)


def test_refinement_reports_consistency_without_claiming_rg_closure() -> None:
    field = np.linspace(0.0, 1.0, 8)
    records = tuple(_record("telegraph", cells) for cells in (2, 4, 8))
    states = refine_coarse_graining(field, records)
    check = coarse_graining_consistency(states)
    assert check.status == "PASS_INTERNAL_CONSISTENCY"
    assert check.global_mean_drift <= 1e-12
    assert len(check.refinement_l2) == 2
    assert check.universal_identity_claimed is False


def test_invalid_physical_lane_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        coarse_grain(np.array([1.0, -1.0, 2.0, 3.0]), _record("density", 2))
    bad = _record("phase")
    with pytest.raises(NotImplementedError):
        CoarseGrainingRecord(**{**bad.__dict__, "kernel": "gaussian_unimplemented"})


def test_scale_audit_is_descriptive_and_not_an_rg_derivation() -> None:
    result = scale_dependence_audit(
        {
            1.0: {"a": 1.0, "kappa": 0.5},
            2.0: {"a": 1.2, "kappa": 0.4},
            4.0: {"a": 1.3, "kappa": 0.35},
        }
    )
    assert result.status == "DESCRIPTIVE_SCALE_AUDIT_ONLY"
    assert "not a beta function" in result.claim_boundary
    assert set(result.logarithmic_slopes) == {"a", "kappa"}


def test_contract_keeps_physical_closure_open_per_lane() -> None:
    contract = coarse_graining_contract()
    assert contract["many_to_one"] is True
    assert contract["universal_C_identity"] is False
    assert contract["scale_audit"] == "descriptive_not_RG_derivation"
    assert set(contract["physical_closure"]) == {
        "charge", "phase", "density", "telegraph"
    }
