"""Conditional input-output gain ambiguity; no new UET dynamics accepted."""
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]


def transfer(omega, alpha, drive_gain, decay=2.):
    return alpha*drive_gain/(decay+1j*np.asarray(omega))


def main():
    omega=np.array([0.,.2,1.,3.,10.])
    base=transfer(omega,3.,.7)
    scales=[.1,2.,10.]
    rows=[dict(scale=s,relative_error=float(np.linalg.norm(transfer(omega,3./s,.7*s)-base)/np.linalg.norm(base))) for s in scales]
    # Each measured transfer amplitude constrains log|alpha|+log|drive_gain|.
    A=np.ones((len(omega),2))
    files=["docs/scripts/audit/audit_topic13_actuation_readout_identifiability.py",
           "docs/core/test/test_topic13_actuation_readout_identifiability.py",
           "docs/topics/0.13_Thermodynamic_Bridge/BASE_PHI_INDEPENDENT_CALIBRATION_PROTOCOL.md"]
    r=dict(major_result_id="T13_ACTUATION_READOUT_CALIBRATION_DESIGN",topic="0.13",closure_level="PARTIAL",
        what_is_closed="Absolute input-output gain alone cannot separate Phi actuation and temperature readout gains in the declared linear control",
        equation_or_mapping="D Phi=b U; DeltaT=alpha Phi; H_TU=alpha*b/D; b->s*b, alpha->alpha/s leaves H invariant",
        units="D has inverse-time dimension in this scalar control; b has Phi/(input*time); alpha has K/Phi",
        derivation_class="Conditional linear input-output invariance, not a UET action derivation",
        data_role="SYNTHETIC_IDENTIFIABILITY_CONTROL_NO_CALIBRATION",
        rows=rows,frequency_count=len(omega),gain_design_rank=int(np.linalg.matrix_rank(A)),
        rank_with_independent_actuation=int(np.linalg.matrix_rank(np.vstack([A,[0,1]]))),
        verification_status="ALGEBRAIC_AMBIGUITY_DEMONSTRATED",
        open_blockers=["operational_input_to_base_Phi_operator_and_gain","independent_gain_or_absolute_Phi_anchor","same_material_calibration_provenance"],
        dependency_unlocked=[],full_core_unlock=False,
        claim_boundary="Does not prove all nonlinear/source protocols unidentifiable. Applies when alpha and actuation enter only through their product; no numeric alpha or external source payload is inferred.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in files])
    (ROOT/"docs/core/07_artifacts/topic13/t13_actuation_readout_identifiability_audit.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(rows=rows,rank=r["gain_design_rank"],anchored_rank=r["rank_with_independent_actuation"])))


if __name__=="__main__":main()
