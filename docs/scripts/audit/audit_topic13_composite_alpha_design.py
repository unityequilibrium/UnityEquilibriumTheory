"""Measurement-design identifiability for the existing conditional alpha product.

Log absolute factors use fixed reference units and fixed nonzero signs.
This supplies no physical measurements and does not identify normalized Phi.
"""
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
TARGET=np.array([1.,1.,1.,-1.])


def design(rows):
    A=np.asarray(rows,dtype=float).reshape(-1,4)
    if not np.all(np.isfinite(A)): raise ValueError("finite design required")
    coefficients=np.linalg.lstsq(A.T,TARGET,rcond=None)[0]
    residual=TARGET-A.T@coefficients
    _,s,vh=np.linalg.svd(A,full_matrices=True)
    rank=int(np.sum(s>1e-12))
    null=vh[rank:]
    return dict(rank=rank,individual_factors_identifiable=rank==4,
                alpha_magnitude_identifiable=bool(np.linalg.norm(residual)<1e-12),
                target_rowspace_residual=float(np.linalg.norm(residual)),
                measurement_combination=coefficients.tolist(),
                null_directions=null.tolist(),target_null_overlaps=(null@TARGET).tolist())


def log_alpha_variance(coefficients,covariance):
    c=np.asarray(coefficients,dtype=float); S=np.asarray(covariance,dtype=float)
    if S.shape!=(len(c),len(c)) or not np.all(np.isfinite(S)):
        raise ValueError("finite matching covariance required")
    if not np.allclose(S,S.T) or np.linalg.eigvalsh(S).min() < -1e-14:
        raise ValueError("symmetric positive semidefinite covariance required")
    return float(c@S@c)


def main():
    matrices={
        "heat_capacity_only":[[0,0,0,1]],
        "heat_capacity_and_gZ":[[0,0,0,1],[0,1,1,0]],
        "heat_capacity_and_full_numerator":[[0,0,0,1],[1,1,1,0]],
        "heat_capacity_chi_and_gZ":[[0,0,0,1],[1,0,0,0],[0,1,1,0]],
        "all_factors":np.eye(4).tolist(),
        "normalized_shape_only":np.zeros((1,4)).tolist(),
    }
    rows={k:dict(matrix=v,**design(v)) for k,v in matrices.items()}
    paths=["docs/scripts/audit/audit_topic13_composite_alpha_design.py",
           "docs/core/test/test_topic13_composite_alpha_design.py",
           "docs/core/03_lanes/thermal/uet_material_interface_factor_resolution.py",
           "docs/core/03_lanes/thermal/uet_material_lattice_interface_contract.py"]
    artifact=dict(major_result_id="T13_COMPOSITE_ALPHA_MEASUREMENT_DESIGN",topic="0.13",closure_level="PARTIAL",
        equation_or_mapping="log|alpha|=log|chi|+log|g|+log|Z|-log|C_src|; identifiable iff target is in rowspace(A)",
        units="Logs of magnitudes relative to fixed unit references, not logs of dimensionful values",
        derivation_class="Conditional linear structural identifiability",observable="alpha magnitude, conditional on declared signs and normalized-Phi convention",
        data_role="HYPOTHETICAL_DESIGN_NO_MEASUREMENTS",factor_order=["chi_u_theta","g_Phi_theta","Z_Phi","C_src"],designs=rows,
        what_is_closed="Separate identification of every factor is sufficient but not necessary to identify their target product",
        verification_status="ALGEBRAIC_DESIGN_ONLY",open_blockers=["independent_source_backed_numerator_measurement","fixed_Phi_amplitude_and_units","admissible_material_operator","sign_and_covariance_provenance"],
        dependency_unlocked=[],full_core_unlock=False,alpha_value_emitted=False,
        claim_boundary="No source or calibration found; no physical gate relaxed. Composite calibration cannot close missing action/transport derivations or the entire topic.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths])
    (ROOT/"docs/core/07_artifacts/topic13/t13_composite_alpha_design_audit.json").write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    for k,r in rows.items():print(k,r["rank"],r["alpha_magnitude_identifiable"])


if __name__=="__main__":main()
