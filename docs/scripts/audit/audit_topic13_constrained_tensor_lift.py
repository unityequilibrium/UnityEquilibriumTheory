"""Check a completed constrained tensor through the existing covariant lift."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
import mpmath as mp

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    _covariant_tensor_entropy_heat_flux,_boost_tensor_residual,DEFAULT_METRIC,DEFAULT_FOUR_VELOCITY,
)
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import finite_temperature_o2_state


def main():
    path="docs/core/07_artifacts/topic13/t13_constrained_tensor_audit.json"
    source=json.loads((ROOT/path).read_text())
    if not source["completed"] or len(source["rows"])!=4 or any(row["status"]!="EVALUATED" for row in source["rows"]):
        raise ValueError("complete four-case tensor evidence required")
    for entry in source["evidence_artifacts"]:
        if sha256((ROOT/entry["path"]).read_bytes()).hexdigest()!=entry["sha256"]:
            raise ValueError("tensor evidence input hash mismatch")
    eos=finite_temperature_o2_state(.22,.35,.15,natural_bridge_config())
    forces=[[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.],[0.,1.,-.5,.25]]
    rows=[]
    for row in source["rows"]:
        k=np.asarray(row["response"],float); d=np.asarray(row["dissipation"],float)
        tensor=np.zeros((4,4)); tensor[1:,1:]=k
        for force in forces:
            force=np.asarray(force)
            base=_covariant_tensor_entropy_heat_flux(DEFAULT_METRIC,DEFAULT_FOUR_VELOCITY,.22,eos.entropy_density,tensor,force)
            residual=abs(base["entropy_production"]-force[1:]@d@force[1:]/.22)
            boost=_boost_tensor_residual(DEFAULT_METRIC,DEFAULT_FOUR_VELOCITY,.22,eos.entropy_density,tensor,force,base)
            rows.append(dict(rule=row["rule"],dps=row["dps"],force=force.tolist(),
                entropy_balance_absolute=residual,boost_residual=boost,
                entropy_original_gate=bool(residual<=1e-7),boost_original_gate=bool(boost<=1e-10),
                isotropy_original_gate=float(row["isotropy_relative"])<=1e-8))
    precision_differences={}
    with mp.workdps(180):
        for rule in source["direction_rules"]:
            pair=[row for row in source["rows"] if row["rule"]==rule]
            a,b=(mp.matrix(row["response"]) for row in pair)
            precision_differences[rule]=mp.nstr(max(abs(x) for x in a-b)/max(max(abs(x) for x in a),1),12)
    record=dict(major_result_id="T13_CONSTRAINED_TENSOR_LIFT",topic="0.13",closure_level="PARTIAL",
        status="INTERNAL_TENSOR_LIFT_CHECKED",what_is_closed="Four tensors, four forces each tested through unchanged covariant lift",
        equation_or_mapping="q=K X; sigma=X.T K X/T; compare X.T D X/T and existing boost0.37",
        units="natural",derivation_class="Existing tensor lift applied to independent constrained response",
        reported_matrix_precision_difference=precision_differences,
        observable="Internal heat/entropy mapping",data_role="INTERNAL_NO_FIT",rows=rows,
        verification_status="ORIGINAL_THRESHOLDS_RETAINED",dependency_unlocked=[],full_core_unlock=False,
        open_blockers=["physical_interpolation","resolution_and_input_sensitivity","charged_frame_integration","material_mapping"],
        claim_boundary="Float64 lift of high-precision reference outputs; not full charged-frame state integration or physical validation",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in (
            path,"docs/scripts/audit/audit_topic13_constrained_tensor_lift.py",
            "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py")])
    (ROOT/"docs/core/07_artifacts/topic13/t13_constrained_tensor_lift_audit.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(cases=len(rows),max_entropy=max(r["entropy_balance_absolute"] for r in rows),
        max_boost=max(r["boost_residual"] for r in rows),all_gates=all(r["entropy_original_gate"] and r["boost_original_gate"] and r["isotropy_original_gate"] for r in rows))))
    return 0 if all(r["entropy_original_gate"] and r["boost_original_gate"] and r["isotropy_original_gate"] for r in rows) else 1


if __name__=="__main__": raise SystemExit(main())
