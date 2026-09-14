import numpy as np

from docs.core.uet_o2_formal_transverse_response import (
    formal_transverse_quasiparticle_response,
    formal_transverse_response_contract,
)


def test_formal_transverse_response_is_positive_and_branch_aware() -> None:
    normal = formal_transverse_quasiparticle_response(0.22, 0.35, 0.15)
    condensed = formal_transverse_quasiparticle_response(0.20, 1.28, 0.15)
    assert normal.branch == "normal"
    assert condensed.branch == "condensed"
    assert normal.normal_momentum_susceptibility >= 0.0
    assert condensed.normal_momentum_susceptibility >= 0.0
    assert normal.condensate_phase_stiffness == 0.0
    assert condensed.condensate_phase_stiffness > 0.0
    assert np.isfinite(normal.normal_momentum_susceptibility)
    assert np.isfinite(condensed.normal_momentum_susceptibility)


def test_formal_transverse_response_does_not_promote_kubo_or_landau_claims() -> None:
    contract = formal_transverse_response_contract()
    assert "retarded Kubo" in contract["excluded_scope"]
    assert "not Landau normal mass density" in contract["unit_contract"]["normal_density_label"]
    assert "alpha_Phi_K" in contract["excluded_scope"]
