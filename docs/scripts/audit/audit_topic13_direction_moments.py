"""Exact angular-moment requirements versus the production six-axis basis."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import _DIRECTIONS


def candidate14():
    axes=np.asarray(_DIRECTIONS,dtype=float)
    corners=np.asarray(list(product((-1.,1.),repeat=3)))/np.sqrt(3)
    return np.vstack((axes,corners)),np.r_[np.full(6,1/15),np.full(8,3/40)]


def moments(directions,weights):
    d=np.asarray(directions,dtype=float); w=np.asarray(weights,dtype=float)
    if d.shape!=(len(w),3) or not np.all(np.isfinite(d)) or not np.all(np.isfinite(w)):
        raise ValueError("finite directions and matching weights required")
    if np.any(w<=0) or not np.isclose(w.sum(),1.) or not np.allclose(np.linalg.norm(d,axis=1),1.):
        raise ValueError("positive normalized sphere measure required")
    x,y,z=d.T
    q=np.column_stack((x*x-y*y,(x*x+y*y-2*z*z)/np.sqrt(3),2*x*y,2*x*z,2*y*z))
    gram=q.T@(w[:,None]*q)
    return {"direction_count":len(w),"weight_sum":float(w.sum()),
        "second_moment":(d.T@(w[:,None]*d)).tolist(),
        "x4":float(w@(x**4)),"x2y2":float(w@(x*x*y*y)),"x6":float(w@(x**6)),
        "quadrupole_gram":gram.tolist(),"quadrupole_rank":int(np.linalg.matrix_rank(gram,tol=1.e-12)),
        "shear_xy_source_norm":float(np.sqrt(w@((x*y)**2))),
        "fourth_order_gram_error":float(np.linalg.norm(gram-4/15*np.eye(5)))}


def main():
    axes=np.asarray(_DIRECTIONS,dtype=float)
    candidate,weights=candidate14()
    result={
        "major_result_id":"T13_ANGULAR_MOMENT_COVERAGE_BOUNDARY", "topic":"0.13_Thermodynamic_Bridge",
        "closure_level":"PARTIAL", "status":"SIX_AXIS_QUADRUPOLE_DEFICIT_IDENTIFIED",
        "what_is_closed":"Production six-axis rule loses three quadrupole channels; a positive 14-direction candidate restores degree-four moments but not all higher moments",
        "equation_or_mapping":"Sphere E[n_i n_j]=delta_ij/3; E[n_i^4]=1/5; E[n_i^2 n_j^2]=1/15; E[n_i^6]=1/7",
        "units":"dimensionless angular quadrature", "derivation_class":"Sphere integral and moment matching",
        "observable":"Angular source representability, not material viscosity/heat conductivity",
        "data_role":"INTERNAL_ANALYTIC_CONTROL",
        "sphere_reference":{"second_moment":(np.eye(3)/3).tolist(),"x4":1/5,"x2y2":1/15,"x6":1/7,"quadrupole_rank":5},
        "production_six_axis":moments(axes,np.full(6,1/6)),
        "candidate14":moments(candidate,weights),
        "candidate_directions":candidate.tolist(),"candidate_weights":weights.tolist(),
        "derivation":"Sign symmetry cancels odd powers. Normalization 6a+8b=1 and cross moment 8b/9=1/15 give b=3/40,a=1/15; diagonal fourth moment follows. Sphere E[x^(2m)]=1/(2m+1).",
        "verification_status":"ANGULAR_MOMENTS_ONLY_NO_TRANSPORT_RERUN",
        "open_blockers":["production_weighted_direction_interface", "directional_transport_convergence", "transition_discretization", "physical_material_mapping"],
        "dependency_unlocked":[],"claim_promotion":False,
        "claim_boundary":"Six-axis degree-four failure does not alone disprove its degree-two heat response. Candidate14 is not a full angular convergence proof and is not installed into production.",
        "evidence_artifacts":[{"path":p,"sha256":sha256((ROOT/p).read_bytes()).hexdigest()} for p in (
            "docs/scripts/audit/audit_topic13_direction_moments.py","docs/core/test/test_topic13_direction_moments.py",
            "docs/core/02_equations/o2/uet_o2_energy_momentum_conserving_bethe_salpeter.py")],
    }
    (ROOT/"docs/core/07_artifacts/topic13/t13_direction_moments_audit.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","production_six_axis","candidate14")},indent=2))


if __name__=="__main__":
    main()
