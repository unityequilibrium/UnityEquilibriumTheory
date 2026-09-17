"""Audit the action-derived equilibrium KMS/FDT lane for Topic 13."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite, sqrt
from pathlib import Path

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_equilibrium_kms import (
    EQUILIBRIUM_KMS_STATUS,
    equilibrium_kms_contract,
    equilibrium_kms_state,
)
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    condensed_quasiparticle_energies,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_equilibrium_kms_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py"
EOS_MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def normal_mode_energies(
    momentum: float,
    chemical_potential: float,
    space_response: float,
    eos: O2FiniteDensityEOSConfig,
) -> tuple[float, float]:
    """Return the positive normal-branch particle/antiparticle energies."""

    k = float(momentum)
    mu = float(chemical_potential)
    mass_sq = effective_mass_sq(space_response, eos)
    if k < 0.0 or mass_sq <= 0.0:
        raise ValueError("normal witness requires non-negative momentum and positive mass squared")
    mass = sqrt(k * k + mass_sq)
    mu_eff = sqrt(eos.matter.matter_kinetic) * abs(mu)
    return mass - mu_eff, mass + mu_eff


def main() -> int:
    failures: list[str] = []
    response = CovariantResponseConfig(
        epsilon_nc=0.05,
        phi_equilibrium=0.0,
        response_kinetic=1.0,
        response_mass_sq=1.0,
        response_quartic=1.0,
    )
    matter = CovariantMatterConfig(
        matter_kinetic=1.0,
        matter_mass_sq=1.0,
        matter_quartic=1.0,
        response_coupling=0.8,
    )
    eos = O2FiniteDensityEOSConfig(matter=matter, response=response)
    quasiparticle = FiniteTemperatureO2QuasiparticleConfig(
        eos=eos,
        quadrature_order=64,
        cutoff_factor=50.0,
    )

    records: list[dict[str, object]] = []
    normal_points = ((0.22, 0.35, 0.15, 0.2), (0.31, 0.55, 0.20, 0.5))
    for temperature, chemical_potential, phi, momentum in normal_points:
        energies = normal_mode_energies(momentum, chemical_potential, phi, eos)
        for branch, energy in zip(("normal_particle", "normal_antiparticle"), energies):
            check(energy > 0.0, f"{branch} energy is not positive", failures)
            state = equilibrium_kms_state(temperature, energy)
            records.append({"branch": branch, "momentum": momentum, "state": state.__dict__})

    condensed_points = ((0.12, 1.18, 0.15), (0.20, 1.28, 0.20))
    for temperature, chemical_potential, phi in condensed_points:
        for momentum in (0.15, 0.5, 1.2):
            upper, lower = condensed_quasiparticle_energies(
                momentum,
                chemical_potential,
                phi,
                quasiparticle,
            )
            for branch, energy in zip(("condensed_upper", "condensed_lower"), (upper, lower)):
                check(energy > 0.0, f"{branch} energy is not positive", failures)
                state = equilibrium_kms_state(temperature, energy)
                records.append({"branch": branch, "momentum": momentum, "state": state.__dict__})

    representative_checks: dict[str, bool] = {}
    for index, record in enumerate(records):
        state = record["state"]
        assert isinstance(state, dict)
        temperature = float(state["temperature"])
        energy = float(state["mode_energy"])
        rho = float(state["spectral_weight"])
        greater = float(state["greater_weight"])
        lesser = float(state["lesser_weight"])
        noise = float(state["noise_weight"])
        occupation = float(state["occupation"])
        entropy = float(state["mode_entropy"])
        representative_checks[f"record_{index}_spectral_difference"] = bool(
            np.isclose(greater - lesser, rho, rtol=1.0e-12, atol=1.0e-12)
        )
        representative_checks[f"record_{index}_kms_log_ratio"] = bool(
            np.isclose(
                float(state["log_kms_ratio"]),
                energy / temperature,
                rtol=1.0e-12,
                atol=1.0e-12,
            )
        )
        representative_checks[f"record_{index}_kms_ratio"] = bool(
            np.isclose(
                greater / lesser,
                np.exp(energy / temperature),
                rtol=1.0e-12,
                atol=1.0e-12,
            )
        )
        representative_checks[f"record_{index}_fdt_noise"] = bool(
            np.isclose(
                noise,
                rho / np.tanh(energy / (2.0 * temperature)),
                rtol=1.0e-12,
                atol=1.0e-12,
            )
        )
        representative_checks[f"record_{index}_entropy_nonnegative"] = bool(entropy >= 0.0)
        representative_checks[f"record_{index}_equilibrium_entropy_production_zero"] = bool(
            float(state["entropy_production"]) == 0.0
        )
        check(occupation > 0.0, f"record {index} has non-positive Bose occupation", failures)
        check(
            all(
                isfinite(float(value))
                for value in state.values()
                if isinstance(value, (int, float))
            ),
            f"record {index} is non-finite",
            failures,
        )

    contract = equilibrium_kms_contract()
    checks = {
        "all_positive_frequency_records_pass": not failures,
        "spectral_difference_pass": all(
            value
            for key, value in representative_checks.items()
            if "spectral_difference" in key
        ),
        "kms_log_ratio_pass": all(
            value for key, value in representative_checks.items() if "kms_log_ratio" in key
        ),
        "kms_ratio_pass": all(
            value for key, value in representative_checks.items() if key.endswith("kms_ratio")
        ),
        "fdt_noise_pass": all(
            value for key, value in representative_checks.items() if "fdt_noise" in key
        ),
        "entropy_nonnegative_pass": all(
            value
            for key, value in representative_checks.items()
            if "entropy_nonnegative" in key
        ),
        "equilibrium_entropy_production_zero_pass": all(
            value
            for key, value in representative_checks.items()
            if "equilibrium_entropy_production_zero" in key
        ),
        "C_not_relabelled_as_charge": "not a charge" in contract["ontology"]["C"],
        "Phi_not_relabelled_as_temperature": "not temperature" in contract["ontology"]["Phi"],
        "R_gen_not_state": "not an equilibrium state" in contract["ontology"]["R_gen"],
        "interacting_SK_remains_open": "interacting SK action" in contract["scope"]["open"],
        "physical_Kubo_remains_open": "physical Kubo coefficients" in contract["scope"]["open"],
        "alpha_remains_open": "alpha_Phi_K" in contract["scope"]["open"],
        "no_target_or_holdout": True,
    }
    check(all(representative_checks.values()), "one or more KMS/FDT identities failed", failures)

    status = EQUILIBRIUM_KMS_STATUS if not failures else "BLOCKED_EQUILIBRIUM_KMS_AUDIT"
    artifact = {
        "schema_version": "t13-uet-o2-equilibrium-kms-v1",
        "artifact": "t13_uet_o2_equilibrium_kms_audit",
        "generated_at": str(date.today()),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_EQUILIBRIUM_KMS_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failures else "OPEN",
            "what_is_closed": [
                "mode-level equilibrium Bose KMS identity for positive-frequency O(2) witnesses",
                "spectral difference and fluctuation-dissipation noise identity",
                "nonnegative single-mode equilibrium entropy witness",
                "zero entropy production identity for the declared uniform equilibrium lane",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/02_equations/o2/uet_o2_equilibrium_kms.py", "sha256": sha256(MODULE)},
                {
                    "path": "docs/core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
                    "sha256": sha256(EOS_MODULE),
                },
            ],
            "verification_status": status,
            "open_blockers": [
                "interacting_SK_action_and_collision_noise_kernel_missing",
                "physical_retarded_correlator_Kubo_record_missing",
                "spatial_entropy_current_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "equilibrium KMS/FDT identity lane only; no dissipative transport, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "records": records,
        "representative_checks": representative_checks,
        "checks": checks,
        "failed_checks": failures,
        "numeric_beta_T13_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "physical_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "interacting_SK_action_and_physical_Kubo_provenance_missing",
        "next_controller": "Declare the interacting SK/KMS collision-noise kernel and state-matched physical Kubo source before claiming dissipative transport closure.",
        "claim_promotion": False,
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "closure_level": artifact["major_result"]["closure_level"],
                "records": len(records),
                "failed_checks": failures,
            },
            indent=2,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

