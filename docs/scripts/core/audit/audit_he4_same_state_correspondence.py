"""Read-only input audit; emit a conditional Core-to-Topic13 handoff.

No scientific verifier rerun or parameter fit. --topic13-root selects the
declared checkout containing the new source and low-temperature branch.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CORE = "docs/core/07_artifacts/topic13/"
T13 = "docs/topics/0.13_Thermodynamic_Bridge/"


def build(topic_root):
    inputs = []
    def read(base, path, checkout):
        raw = (base / path).read_bytes()
        inputs.append({"path": path, "checkout_role": checkout,
                       "sha256": hashlib.sha256(raw).hexdigest()})
        return json.loads(raw)
    cal = read(ROOT, CORE+"t13_he4_o2_response_calibration_audit.json", "core")
    si = read(ROOT, CORE+"t13_he4_o2_si_beta_mapping_audit.json", "core")
    natural = read(ROOT, CORE+"t13_uet_o2_action_thermal_observable_bridge_audit.json", "core")
    read(ROOT, CORE+"t13_he4_matching_independence_audit.json", "core")
    source = read(topic_root, T13+"Data/03_Research/t13_low_q_source_protocol.json", "topic13")
    low = read(topic_root, T13+"Result/artifacts/t13_low_T_phase_eft.json", "topic13")
    boundary = read(topic_root, T13+"Result/artifacts/t13_low_q_source_boundary.json", "topic13")
    for path in ["docs/core/03_lanes/thermal/he4_svp_reference.py",
                 "docs/core/03_lanes/thermal/he4_o2_response_calibration.py",
                 "docs/core/03_lanes/thermal/he4_o2_si_beta_mapping.py",
                 "docs/core/03_lanes/thermal/he4_normal_viscosity_kubo.py"]:
        raw=(ROOT/path).read_bytes()
        inputs.append({"path":path,"checkout_role":"core", "sha256":hashlib.sha256(raw).hexdigest()})
    c, s, n = cal["record"], si["record"], natural["state"]
    alpha_return = c["theta_T_K_per_natural_temperature"] * n["alpha_phi_temperature_natural"] / c["Z_Phi_normalized_per_natural_Phi"]
    # Conditional thermodynamic chain rule, not admitted atomic charge matching.
    energy_unit = 1.380649e-23*c["theta_T_K_per_natural_temperature"]
    charge_unit = s["energy_density_scale_J_m3"]/energy_unit
    return {
        "schema_version":"core-he4-same-state-correspondence-v1",
        "owner_id":"FOUNDATION", "evidence_status":"INTERNAL",
        "organization_status":"REVIEW_REQUIRED",
        "organization_next_action":"ORG register this opt-in audit and handoff without changing existing physics gates",
        "disposition":"SPECIFIC_ADDITIONAL_INPUTS_REQUIRED",
        "controlling_blocker":"same_state_atomic_current_action_measure_and_low_T_remainder_not_admitted",
        "physical_transfer_admitted":False, "claim_promotion":False,
        "core_state": {
            "phase":"He II external material; action anchor is the normal quasiparticle branch",
            "temperature_K":c["temperature_K"], "derivative_rows_K":[1.6,1.7,1.8],
            "pressure":"SVP path; absolute pressure value not locked by this calibration",
            "density_kg_m3":s["total_density_kg_m3"],
            "number_density_m3":s["number_density_m3"],
            "source":"Donnelly-Barenghi 1998 DOI 10.1063/1.556028; source-evaluated rows",
            "source_snapshot_sha256":cal["source_identity"]["interactive_snapshot_sha256"],
            "action_anchor":{k:n[k] for k in ["temperature","chemical_potential","space_response","branch"]},
            "normalization":{k:c[k] for k in ["alpha_Phi_K","alpha_uncertainty_K_per_normalized_base_Phi","theta_T_K_per_natural_temperature","Z_Phi_normalized_per_natural_Phi","Z_Phi_uncertainty_bound"]},
            "energy_density_scale_J_m3":s["energy_density_scale_J_m3"],
            "derivation_class":"EXTERNAL_CALIBRATION_AND_SCALE_CONVENTION_WITH_LOCAL_ACTION_DERIVATIVES",
            "independence":"External to UET target fitting; calibration reconstruction itself is not independent validation or a blind response dataset"
        },
        "low_T_state": {
            "phase":"declared condensed tree/phase EFT; atomic material identification open",
            "source_temperature":"Godfrin primary low-T source documents T<100mK; hybrid rows also require component-specific temperature/ancestry, not a 1.7K row",
            "source_pressure":"seven source pressures; SVP hybrid has mixed ultrasound/neutron ancestry",
            "density_kg_m3":None, "physical_chemical_potential":None,
            "action_chemical_potentials":[x["state_tree_not_Hartree"]["mu"] for x in low["examples"]],
            "tree_states":[{k:x["state_tree_not_Hartree"].get(k) for k in ["mu","xi","h","Phi","s"]} for x in low["examples"]],
            "units":"action natural E; source meV and angstrom^-1; conversion unadmitted",
            "source_identity":source["source_identity"],
            "source_limitations":source["source_limitations"],
            "original_source_audit_status":boundary["verification_status"],
            "derivation_class":low["derivation_class"]
        },
        "chemical_potential_current_normalization": {
            "core_action":"phase theta=-mu*t; charge is d p/d mu with declared natural measure",
            "transport_reference":"delta_mu=0 relative to SVP; not absolute atom chemical potential or action mu=0",
            "conditional_relation":"if mu_phys=E_unit*mu_nat+constant and p_phys=e0*p_nat+constant, n_Q_phys=(e0/E_unit)*n_Q_nat",
            "energy_unit_J":energy_unit, "conditional_charge_unit_m3":charge_unit,
            "normal_anchor_charge_fraction_of_atom_density":charge_unit*n["charge_density"]/s["number_density_m3"],
            "interpretation":"diagnostic under stated chain rule; charge-to-atom/normal-component matching not derived; no material no-go"
        },
        "action_measure_normalization": {
            "thermal_integral":"d^3k/(2pi)^3; radial k^2 dk/(2pi^2), natural action variables",
            "conditional_relation":"ell=hbar*c_star/E_unit; S_phys/hbar=A integral d4x_nat L_nat; e0=A*E_unit/ell^3",
            "c_star_m_s":None,"ell_m":None,"A":None,
            "status":"MISSING_SPACETIME_AND_ACTION_NORMALIZATION",
            "field_rescaling_is_action_measure":False
        },
        "constraints_and_checks": {
            "calibration_alpha_reconstruction_relative_error":abs(alpha_return/c["alpha_Phi_K"]-1),
            "calibration_identity_only":True, "temperature_domains_overlap":False,
            "SVP_derivative_equals_fixed_mu_derivative":False,
            "normal_branch_equals_full_HeII":False, "source_covariance_supplied":False,
            "new_model_solve_or_fit":False,"Xie_numeric_read":False
        },
        "checks_scope":"Metadata/source audit and conditional dimensional chain rule; existing physical models were not rerun",
        "required_inputs": [
            "same-state T/pressure/density rows and their covariance, not transfer of 1.7K values",
            "atomic U(1) charge assignment/current unit and chemical-potential zero/rest-energy convention",
            "length/time/energy scale and action prefactor from independent input; response Z_Phi alone is insufficient",
            "thermodynamic path Jacobian linking SVP equilibrium derivatives to fixed-(mu,Phi) action derivatives",
            "same-state independent scale or pressure/compressibility/density-current observable not used in matching, with source ancestry review",
            "bound interaction/finite-T and omitted dispersion terms before selecting q3/q5 inference"
        ],
        "claim_boundary":"Existing bounded Core composition preserved. Transfer to the low-T material is not admitted; no global no-go or empirical validation.",
        "inputs":inputs,
        "reproduce":"py -3.14 docs/scripts/core/audit/audit_he4_same_state_correspondence.py --topic13-root <checkout-with-low-T-source>"
    }


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--topic13-root",type=Path,default=ROOT)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    result=build(args.topic13_root.resolve())
    if result["constraints_and_checks"]["calibration_alpha_reconstruction_relative_error"] > 1e-12:
        raise SystemExit("matching identity drift; existing matching-audit tolerance is 1e-12")
    output=ROOT/(CORE+"core_he4_same_state_correspondence_2026_10_04.json")
    if args.check:
        if json.loads(output.read_text(encoding="utf-8")) != result:
            raise SystemExit("handoff drift: inspect source changes before regeneration")
        print("PASS: saved handoff matches current declared inputs; physical transfer remains open")
    else:
        output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
        print(output.relative_to(ROOT))
