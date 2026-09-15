"""Rerun the locked resolution grid to a NEW tensor-repair artifact."""
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit import audit_topic13_transport_resolution as experiment


def main():
    baseline=ROOT/"docs/core/07_artifacts/topic13/t13_transport_resolution_audit.json"
    baseline_hash=sha256(baseline.read_bytes()).hexdigest()
    if baseline_hash!="28bc408cdc624f33c503c38727c85cff14de104d3c4409ed35cd496a8bda666f":
        raise ValueError("Frozen scalar baseline changed")
    # Override only the output destination; reuse every locked experiment case.
    experiment.OUT="docs/core/07_artifacts/topic13/t13_tensor_lift_repair_audit.json"
    code=experiment.main()
    path=ROOT/experiment.OUT
    record=json.loads(path.read_text())
    passed=code==0 and all(r.get("entropy_original_gate",False) and r.get("lorentz_residual",float("inf"))<=1.e-10 for r in record["rows"])
    record.update(major_result_id="T13_FULL_TENSOR_HEAT_ENTROPY_LIFT",
        closure_level="CLOSED_FOR_LANE" if passed else "OPEN",
        status="TENSOR_BALANCE_REPAIRED_TRANSPORT_UNRESOLVED" if passed else "TENSOR_REPAIR_CHECK_FAILED",
        what_is_closed="Full transverse response replaces isotropic scalar lift for flux and entropy; transport convergence remains open",
        baseline={"path":str(baseline.relative_to(ROOT)).replace("\\","/"),"sha256":baseline_hash},
        diagnostic_extension="Same locked ten cases rerun after full-tensor implementation. Historical scalar failures preserved in baseline; no threshold changes.")
    old={r["id"]:r for r in json.loads(baseline.read_text())["rows"]}
    for row in record["rows"]:
        row["historical_scalar_entropy_residual"]=old[row["id"]].get("entropy_residual")
        if "kappa" in row:
            row["kappa_change_from_same_case_before_repair"]=row["kappa"]-old[row["id"]]["kappa"]
    for p in ("docs/scripts/audit/audit_topic13_tensor_lift_repair.py","docs/core/test/test_topic13_tensor_heat_lift.py"):
        record["evidence_artifacts"].append({"path":p,"sha256":sha256((ROOT/p).read_bytes()).hexdigest()})
    path.write_text(json.dumps(record,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    assert sha256(baseline.read_bytes()).hexdigest()==baseline_hash
    print(record["status"],flush=True)
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
