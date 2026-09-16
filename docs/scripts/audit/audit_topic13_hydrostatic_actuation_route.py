"""Source-backed directional spectral actuation; not an O(2) mass calibration."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from docs.core.uet_raman_deformation_constraint import spectral_constraint,absolute_slope_constraint,hydrostatic_row
SOURCE="docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/hanfland_1989_raman_deformation_source_package.json"


def directional_witness(a,c):
    row=hydrostatic_row(a,c)
    null=np.array([-row[1],row[0]])
    base=np.array([.3,-.7])
    return max(abs(row@(base+t*null)-row@base) for t in (-100.,-1.,1.,100.))


def main():
    package=json.loads((ROOT/SOURCE).read_text(encoding="utf-8-sig"))
    raw=package["source"]
    if sha256((ROOT/raw["local_path"]).read_bytes()).hexdigest()!=raw["sha256"]:
        raise ValueError("primary source hash mismatch")
    rows={r["row_id"]:r for r in package["rows"]}
    modes={}
    for mode in ("E2g1","E2g2"):
        f,s,d=[rows[mode+suffix] for suffix in ("_frequency","_pressure_log_slope","_absolute_pressure_slope")]
        table=spectral_constraint(f["value"],s["value"],frequency_error=f["uncertainty"],slope_error=s["uncertainty"])
        abstract=absolute_slope_constraint(f["value"],d["value"],frequency_error=f["uncertainty"],slope_error=d["uncertainty"])
        intervals=[r["pressure_derivative_sensitivity_envelope_J2_per_Pa"] for r in (table,abstract)]
        modes[mode]=dict(source_row_ids=[f["row_id"],s["row_id"],d["row_id"]],
            spectral_mass_source_gain_J2_per_Pa=table["squared_gap_pressure_derivative_J2_per_Pa"],
            fractional_squared_gap_gain_per_Pa=table["log_squared_gap_pressure_derivative_per_Pa"],
            union_sensitivity_envelope_J2_per_Pa=[min(i[0] for i in intervals),max(i[1] for i in intervals)],
            physical_O2_mass_source_gain=None)
    paths=[SOURCE,"docs/core/03_lanes/thermal/uet_raman_deformation_constraint.py",
           "docs/scripts/audit/audit_topic13_hydrostatic_actuation_route.py"]
    r=dict(major_result_id="T13_HYDROSTATIC_SPECTRAL_ACTUATION_ROUTE",topic="0.13",closure_level="PARTIAL",
        what_is_closed="Hydrostatic spectral mass-source projection is source-constrained without identifying the full deformation tensor",
        equation_or_mapping="u_mode=(dE_mode^2/dP)*deltaP; dE_mode^2/dP=2*E_mode^2*dln(nu)/dP",
        units="u_mode J^2; pressure Pa; not UET source units until mode/scale matching",
        derivation_class="Local derivative of source-reported pressure-frequency relation",
        data_role="EXTERNAL_SPECTRAL_CONSTRAINT_NOT_ALPHA_CALIBRATION",modes=modes,
        tensor_null_direction_projection_error=float(directional_witness(rows["axial_modulus_a"]["value"],rows["axial_modulus_c"]["value"])),
        source_state="Graphite 300 K; source-fitted zero-pressure derivatives; low mode measured in pressure cell above about4.5 GPa plus separate ambient frequency",
        uncertainty="Union of source table and abstract endpoint sensitivity envelopes; not confidence interval; covariance absent",
        verification_status="PRIMARY_HASH_CHECKED_DIRECTIONAL_PROJECTION_ONLY",
        open_blockers=["phonon_mode_to_O2_operator_matching","TTG_state_equivalence","source_uncertainty_covariance","pressure_actuation_protocol"],
        full_core_unlock=False,dependency_unlocked=[],alpha_Phi_K=None,
        claim_boundary="No prescribed pressure amplitude or temperature curve fitted; hydrostatic projection does not identify arbitrary-direction tensor or base Phi. Local derivative is not a validated finite-pressure drive model.",
        evidence_artifacts=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
        primary_source=dict(doi=raw["doi"],sha256=raw["sha256"],raw_redistribution=False))
    (ROOT/"docs/core/07_artifacts/topic13/t13_hydrostatic_actuation_route_audit.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(dict(modes=modes,null_error=r["tensor_null_direction_projection_error"])))


if __name__=="__main__":main()
