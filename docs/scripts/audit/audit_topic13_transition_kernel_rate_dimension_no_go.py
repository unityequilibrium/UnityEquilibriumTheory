"""Dimension audit for the finite-channel transition-kernel operator."""
from __future__ import annotations
from dataclasses import asdict
from math import log
from pathlib import Path
import hashlib,json
import numpy as np
from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import FiniteTemperatureO2QuasiparticleConfig
from docs.core.uet_o2_action_derived_transition_kernel import action_derived_transition_kernel_state

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/core/artifacts/t13_transition_kernel_rate_dimension_no_go.json"
REGISTRY_OUT=ROOT/"docs/core/artifacts/uet_equation_correspondence_registry_topic13_transition_rate_dimension_addendum.json"
EQUATION_ID="uet.o2.thermal.transition_kernel_rate_dimension_no_go"

def config(scale=1.):
    return FiniteTemperatureO2QuasiparticleConfig(eos=O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(matter_mass_sq=scale*scale,matter_quartic=.1),
        response=CovariantResponseConfig(response_mass_sq=.5*scale*scale)))

def scale_witness(scale=2.):
    if scale<=0 or scale==1: raise ValueError("positive nonunit scale required")
    a=action_derived_transition_kernel_state(.25,.1,0.,config(),quadrature_order=24,channel_count=6)
    b=action_derived_transition_kernel_state(.25*scale,.1*scale,0.,config(scale),quadrature_order=24,channel_count=6)
    operator_a=np.asarray(a.collision_operator,float); operator_b=np.asarray(b.collision_operator,float)
    ratio=float(np.trace(operator_b)/np.trace(operator_a))
    reported_ratio=b.positive_mode_rate/a.positive_mode_rate
    return {"scale":scale,"base_rate":a.positive_mode_rate,"scaled_rate":b.positive_mode_rate,
        "operator_trace_ratio":ratio,"measured_energy_exponent":log(ratio)/log(scale),
        "reported_positive_mode_rate_ratio":reported_ratio,
        "reported_positive_mode_rate_exponent":log(reported_ratio)/log(scale),
        "expected_rate_ratio":scale,"current_formula_ratio":scale*scale,
        "dc_response_ratio":b.dc_response/a.dc_response}

def main():
    rows=[scale_witness(s) for s in (1.5,2.,3.)]
    dimensions={"quadrature_weight_dp":1,"p_squared_each":2,"two_radial_measures":6,
        "cross_section":-2,"channel_rate":4,"state_weight_dp_p2_over_T":2,
        "transition_vector":-1,"collision_operator":2,"required_frequency_rate":1}
    checks={"numeric_operator_scales_E2":all(abs(r["measured_energy_exponent"]-2)<1e-10 for r in rows),
        "symbolic_operator_dimension_E2":dimensions["channel_rate"]+2*dimensions["transition_vector"]==2,
        "required_rate_dimension_E1":dimensions["required_frequency_rate"]==1,
        "dimension_mismatch_is_nonzero":dimensions["collision_operator"]!=dimensions["required_frequency_rate"]}
    paths=["docs/scripts/audit/audit_topic13_transition_kernel_rate_dimension_no_go.py",
        "docs/core/test/test_topic13_transition_kernel_rate_dimension_no_go.py",
        "docs/core/uet_o2_action_derived_transition_kernel.py","docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py"]
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    prior="docs/core/artifacts/t13_dressed_ra_pair_microscopic_rung_boundary_audit.json"
    artifact={"schema_version":"t13-transition-rate-dimension-no-go-v1","major_result_id":"T13_TRANSITION_KERNEL_RATE_DIMENSION_NO_GO",
        "topic":"0.13_Thermodynamic_Bridge","closure_level":"CLOSED_FOR_LANE","closure_disposition":"CLOSED_AS_DIMENSIONAL_NO_GO",
        "verification_status":"PASS_TRANSITION_RATE_DIMENSION_NO_GO" if all(checks.values()) else "WARN_TRANSITION_RATE_DIMENSION",
        "what_is_closed":["The current finite-channel transition operator scales as energy squared, both symbolically and under independent whole-action energy rescaling.",
            "The operator is therefore dimensionally incompatible with L-i*omega*I when omega is an energy/inverse time; the absolute positive-eigenvalue cutoff adds a separate scale-covariance failure.",
            "Algebraic BS/KMS identities using this operator cannot establish a physical rate until invariant phase-space and state normalization are repaired."],
        "equation_registry_ids":[EQUATION_ID],"registration_status":"CANDIDATE_DIAGNOSTIC_NOT_CENTRAL_ACCEPTANCE",
        "equation_or_mapping":{"current":"W_c~(dp1*p1^2)(dp2*p2^2)*sigma gives E^4; v_c~1/sqrt(w) gives E^-1; L=sum W_c v_c v_c^T gives E^2",
            "required":"L_rate must have E^1 so (L_rate-i*omega I)^-1 is dimensionally defined",
            "repair":"derive the linearized single-particle operator from Lorentz-invariant dPi=d^3p/[(2pi)^3 2E], delta^4, symmetry factors and a declared Hilbert-space weight"},
        "ontology":{"C":"unchanged","Phi":"unchanged","R_gen":"excluded","R_obs":"excluded"},"unit_lane":"natural_units",
        "units":dimensions,"derivation_class":"dimensional_no_go_with_energy_covariance_witness",
        "observable":"Collision-operator rate dimension, not a transport coefficient","data_role":"DERIVED_SYNTHETIC_DIAGNOSTIC",
        "scale_witnesses":rows,"checks":checks,"open_blockers":["lorentz_invariant_linearized_collision_measure",
            "Hilbert_space_state_weight_normalization","charge_resolved_contact_plus_Phi_rung","self_consistent_width_and_ladder"],
        "controlling_blocker":"collision_operator_energy_dimension_and_invariant_measure_repair_missing",
        "source_hashes":{p:sha(p) for p in paths},"evidence_artifacts":[{"path":prior,"sha256":sha(prior)}],
        "dependency_unlocked":[],"full_core_unlock":False,"claim_promotion":False,"xie_2026_accessed":False,"parameter_fitting_performed":False,
        "claim_boundary":"Dimensional rejection of the current finite-channel rate operator only; not a repaired collision kernel, width, ladder, Kubo coefficient, SI transport or Full Topic 13 closure."}
    artifact["report"]={"MAJOR_RESULT_CLOSURE":"CLOSED_FOR_LANE/CLOSED_AS_NO_GO","WHAT_IS_ACTUALLY_CLOSED":artifact["what_is_closed"],
        "WHAT_REMAINS_OPEN":artifact["open_blockers"],"DEPENDENCY_UNLOCKED":[],"STATUS":artifact["verification_status"],
        "WHAT_CHANGED":"Added symbolic and whole-action energy-rescaling evidence that the existing transition operator has E^2 rather than rate dimension E.",
        "EQUATION_OR_MAPPING":artifact["equation_or_mapping"],"VERIFICATION":checks,"CONTROLLING_BLOCKER":artifact["controlling_blocker"],
        "NEXT_ACTION":"Re-derive the single-particle linearized collision operator with invariant phase space and a declared weighted inner product before inserting the production rung.",
        "CLAIM_BOUNDARY":artifact["claim_boundary"]}
    OUT.write_text(json.dumps(artifact,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    entry={k:artifact[k] for k in ("ontology","unit_lane","units","derivation_class","observable","data_role","verification_status","controlling_blocker","claim_boundary")}
    entry.update({"equation_id":EQUATION_ID,"version":"1","classification":"dimensional_no_go","relation_or_code_path":artifact["equation_or_mapping"],
        "standard_physics_counterpart":"Lorentz-invariant linearized Boltzmann collision rate","variables":{"L":"collision operator","omega":"real frequency"},
        "mathematical_role":"Dimensional compatibility gate","observable_mapping":artifact["observable"],"parameter_dimensions":dimensions,
        "source_or_origin":"Code formula audit and whole-action energy covariance","assumptions":{"natural_units":True,"all_energy_inputs_scaled_together":True},
        "symmetry_and_conservation":"Dimension gate precedes conservation claims","limiting_cases":["energy scale 1.5,2,3"],
        "implementation_paths":[paths[0]],"verifier_paths":[paths[1]],"evidence_class":"INTERNAL_STRUCTURAL_DIAGNOSTIC",
        "proof_status":"CURRENT_OPERATOR_REJECTED_AS_RATE","evidence_artifacts":[{"path":OUT.relative_to(ROOT).as_posix(),"sha256":sha(OUT)}],
        "downstream_dependencies":[],"dependency_role":"blocks_microscopic_ladder_reuse","physical_dependency_unlock":False,
        "failure_mode":artifact["open_blockers"],"next_hardening_step":artifact["report"]["NEXT_ACTION"]})
    REGISTRY_OUT.write_text(json.dumps({"schema_version":"uet-equation-registry-addendum-v1","status":"CANDIDATE_DIAGNOSTIC_NOT_MERGED",
        "extends":"docs/core/artifacts/uet_equation_correspondence_registry.json","equation_entries":[entry],"full_core_unlock":False,"claim_promotion":False},indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":artifact["verification_status"],"checks":checks,"scale_witnesses":rows},indent=2))
    return 0 if all(checks.values()) else 1

if __name__=="__main__": raise SystemExit(main())
