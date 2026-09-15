"""Audit interpolation of psi versus the entropy coordinate z=sqrt(w)*psi."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_action_derived_transition_kernel import action_derived_transition_kernel_state
from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import energy_momentum_conserving_bs_state
from docs.core.uet_o2_continuum_collision_operator import _interpolation_matrix


def coordinate_rows(vectors, interpolation, exact_weights, basis_weights):
    """Rows act on z_basis; interpolation.T acts on unweighted psi_basis."""
    v, s = np.asarray(vectors), np.asarray(interpolation)
    we, wb = np.asarray(exact_weights), np.asarray(basis_weights)
    if we.ndim != 1 or wb.ndim != 1 or s.shape != (len(wb), len(we)) or v.ndim != 2 or v.shape[1] != len(we):
        raise ValueError("incompatible transition coordinate dimensions")
    if any(not np.all(np.isfinite(a)) for a in (v, s, we, wb)) or np.any(we <= 0) or np.any(wb <= 0):
        raise ValueError("finite arrays and positive susceptibility weights required")
    return ((v * np.sqrt(we)) @ s.T) / np.sqrt(wb)[None, :]


def manufactured_case():
    we, wb = np.array([1.,4.,9.,16.]), np.array([4.,9.,16.,25.])
    incidence = np.array([[1.,1.,-1.,-1.]])
    v, s = incidence / np.sqrt(we), np.eye(4)
    old, repaired = v @ s.T, coordinate_rows(v,s,we,wb)
    psi = np.array([1.,2.,4.,8.])
    z = np.sqrt(wb)*psi
    return dict(expected_channel_amplitude=float((incidence@psi)[0]),
        legacy_amplitude=float((old@z)[0]), coordinate_amplitude=float((repaired@z)[0]),
        legacy_constant_defect=float((old@np.sqrt(wb))[0]),
        coordinate_constant_defect=float((repaired@np.sqrt(wb))[0]))


def main():
    config=natural_bridge_config()
    exact=action_derived_transition_kernel_state(.22,.35,.15,config,
        quadrature_order=24,channel_count=64,cutoff_factor=48.)
    v=np.asarray(exact.transition_vectors)
    we=np.asarray(exact.state_weights)
    record=dict(major_result_id="T13_TRANSITION_COORDINATE_CORRESPONDENCE",topic="0.13",
        closure_level="PARTIAL",status="WEIGHTED_COORDINATE_MISMATCH_IDENTIFIED",
        what_is_closed="Counterexample distinguishes normalized interpolation of psi from weighted solver coordinates",
        equation_or_mapping="z_e=sqrt(W_e)*S.T*inv_sqrt(W_b)*z_b; U_b=V_e*sqrt(W_e)*S.T*inv_sqrt(W_b)",
        units="Susceptibility-weighted natural coordinates; S dimensionless",
        derivation_class="Change-of-coordinates identity conditional on psi interpolation",
        observable="Transition amplitude and quadratic collision form, not material transport",
        data_role="INTERNAL_MANUFACTURED_AND_EXISTING_MODEL",rows=[],manufactured=manufactured_case(),
        production_changed=False,full_core_unlock=False,dependency_unlocked=[],
        open_blockers=["production_coordinate_map_repair", "interpolation_consistency", "transition_and_angular_convergence", "material_mapping"],
        verification_status="COUNTEREXAMPLE_AND_ACTUAL_GRID_AUDIT",
        claim_boundary="Alternative mapping is not yet installed; positivity or projected conservation alone does not establish interpolation correspondence",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            "docs/scripts/audit/audit_topic13_transition_coordinate_map.py",
            "docs/core/test/test_topic13_transition_coordinate_map.py",
            "docs/core/uet_o2_continuum_collision_operator.py",
            "docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py",
            "docs/core/uet_o2_action_derived_transition_kernel.py",
            "docs/core/uet_o2_action_thermal_observable_bridge.py",
            "docs/core/uet_o2_action_thermal_stiffness_beta.py")])
    for rule in ("axis6","axis_cube14"):
        base=energy_momentum_conserving_bs_state(.22,.35,.15,config,radial_order=8,
            collision_integration_order=24,angular_order=24,cutoff_factor=48.,_direction_rule=rule)
        s=_interpolation_matrix(exact.state_species_signs,exact.state_momenta,exact.state_energies,
            base.state_species_signs,base.state_momenta,base.state_energies,cutoff=base.momentum_cutoff,support_order=40)
        wb=np.asarray(base.susceptibility_weights)
        old=v@s.T
        corrected=coordinate_rows(v,s,we,wb)
        target=np.sqrt(we)
        legacy_interpolated=s.T@np.sqrt(wb)
        expected_constant=(v*np.sqrt(we))@np.ones(len(we))
        row=dict(rule=rule,
            psi_constant_relative_error=float(np.max(np.abs(legacy_interpolated/target-1))),
            normalized_interpolation_constant_error=float(np.max(np.abs(s.sum(axis=0)-1))),
            legacy_channel_constant_error=float(np.max(np.abs(old@np.sqrt(wb)-expected_constant))),
            coordinate_channel_constant_error=float(np.max(np.abs(corrected@np.sqrt(wb)-expected_constant))),
            row_norm_legacy=float(np.linalg.norm(old)),row_norm_coordinate=float(np.linalg.norm(corrected)))
        record["rows"].append(row)
        print(json.dumps(row),flush=True)
    (ROOT/"docs/core/07_artifacts/topic13/t13_transition_coordinate_map_audit.json").write_text(
        json.dumps(record,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(record["manufactured"]))


if __name__=="__main__":
    main()
