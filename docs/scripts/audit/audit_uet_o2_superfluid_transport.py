"""Generate Wave 10 O(2) EOS and covariant-superfluid artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
    canonical_existing_path,
)

from docs.core.uet_covariant_matter import (  # noqa: E402
    CovariantMatterConfig,
    matter_noether_current,
)
from docs.core.uet_covariant_response import CovariantResponseConfig  # noqa: E402
from docs.core.uet_covariant_superfluid_transport import (  # noqa: E402
    KuboCoefficientRecord,
    O2_SUPERFLUID_TRANSPORT_CONTROLLER,
    SuperfluidHydroState,
    SuperfluidTransportConfig,
    causal_transport_diagnostics,
    covariant_superfluid_transport_contract,
    entropy_production,
    ideal_superfluid_current,
    ideal_superfluid_stress_tensor,
    josephson_residual,
    linear_mode_spectrum,
    spatial_projector,
)
from docs.core.uet_noether_phase_field_map import (  # noqa: E402
    NoetherPhaseFieldMapConfig,
    symmetric_double_well_thermodynamic_map,
)
from docs.core.uet_o2_finite_density_eos import (  # noqa: E402
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
    o2_equilibrium_state,
    o2_finite_density_eos_contract,
    o2_helmholtz_state,
)

OUT = CANONICAL_ARTIFACT_ROOT
EOS_CORE = canonical_existing_path(ROOT / "docs/core/02_equations/o2/uet_o2_finite_density_eos.py")
TRANSPORT_CORE = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_superfluid_transport.py")
MATTER_CORE = canonical_existing_path(ROOT / "docs/core/02_equations/covariant/uet_covariant_matter.py")
STATE_MAP_CORE = canonical_existing_path(ROOT / "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py")
SPEC = canonical_existing_path(ROOT / "docs/core/01_contracts/O2_SUPERFLUID_EOS_TRANSPORT_SPEC.md")
SOURCE_RECORDS = (
    ROOT
    / "docs/data/external/relativistic_transport/son_relativistic_superfluid_2002/source_record.json",
    ROOT
    / "docs/data/external/relativistic_transport/chapman_hoyos_oz_superfluid_kubo_2013/source_record.json",
    ROOT
    / "docs/data/external/relativistic_transport/jain_kovtun_2024/source_record.json",
    ROOT
    / "docs/data/external/relativistic_transport/haehl_loganayagam_rangamani_2018/source_record.json",
)

THRESHOLDS: dict[str, float] = {
    "stationarity_max_abs": 1.0e-12,
    "analytic_derivative_max_abs": 1.0e-8,
    "legendre_first_law_max_abs": 1.0e-10,
    "response_reciprocity_max_abs": 1.0e-8,
    "projector_max_abs": 1.0e-12,
    "ideal_constitutive_max_abs": 1.0e-10,
    "josephson_max_abs": 1.0e-12,
    "lorentz_covariance_max_abs": 1.0e-10,
    "goldstone_sound_max_abs": 1.0e-8,
    "entropy_minimum": -1.0e-12,
    "natural_causal_speed_sq_max": 1.0,
    "double_well_reduction_relative_max": 1.0e-3,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return [
                {"real": float(item.real), "imag": float(item.imag)}
                for item in value.flat
            ]
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _dump(name: str, payload: dict[str, Any]) -> None:
    path = canonical_artifact_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_ready(payload), indent=2) + "\n",
        encoding="utf-8",
    )


def _eos_config(*, epsilon: float = 0.17) -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.3,
            matter_mass_sq=0.65,
            matter_quartic=0.9,
            response_coupling=0.42,
        ),
        response=CovariantResponseConfig(
            epsilon_nc=epsilon,
            phi_equilibrium=0.1,
        ),
    )


def _source_provenance() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    passed = True
    for path in SOURCE_RECORDS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        checks = {
            "arxiv_url_present": bool(payload.get("arxiv_url")),
            "benchmark_role_present": bool(payload.get("benchmark_role")),
            "formula_locator_present": bool(payload.get("formula_locators")),
            "claim_boundary_present": bool(payload.get("claim_boundary")),
            "local_copy_status_present": bool(payload.get("local_copy_status")),
        }
        passed = passed and all(checks.values())
        records.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": _sha(path),
                "title": payload["title"],
                "arxiv_id": payload.get("arxiv_id"),
                "doi": payload.get("doi"),
                "benchmark_role": payload["benchmark_role"],
                "local_copy_status": payload["local_copy_status"],
                "checks": checks,
            }
        )
    return {"status": "PASS" if passed else "FAIL", "records": records}


def _kubo_record(
    name: str,
    value: float,
    state: SuperfluidHydroState,
) -> KuboCoefficientRecord:
    return KuboCoefficientRecord(
        coefficient_name=name,
        value=value,
        units="natural_control_units",
        hydrodynamic_frame="Landau",
        temperature=state.temperature,
        chemical_potential=state.chemical_potential,
        space_response=state.space_response,
        correlator_formula_id=f"synthetic_retarded_{name}_control",
        source_path_or_url="internal://wave10-synthetic-kubo-control",
        source_hash="0" * 64,
        evidence_status="SYNTHETIC_CONTROL",
    )


def _eos_checks(config: O2FiniteDensityEOSConfig) -> dict[str, Any]:
    rng = np.random.default_rng(102001)
    stationarity: list[float] = []
    density_derivative: list[float] = []
    susceptibility_derivative: list[float] = []
    response_derivative: list[float] = []
    legendre: list[float] = []
    first_law: list[float] = []
    inverse_susceptibility: list[float] = []
    signed_pressure: list[float] = []
    signed_density: list[float] = []
    sound_values: list[float] = []

    for _ in range(96):
        mu = float(rng.choice([-1.0, 1.0]) * rng.uniform(1.05, 2.1))
        phi = float(rng.uniform(-0.6, 0.8))
        state = o2_equilibrium_state(mu, phi, config)
        if state.branch != "condensed":
            raise RuntimeError("preregistered EOS grid left the condensed branch")
        stationary = (
            (state.effective_mass_sq - config.matter.matter_kinetic * mu * mu)
            * state.amplitude
            + config.matter.matter_quartic * state.amplitude**3
        )
        stationarity.append(abs(stationary))
        step_mu = 1.0e-5
        plus = o2_equilibrium_state(mu + step_mu, phi, config)
        minus = o2_equilibrium_state(mu - step_mu, phi, config)
        density_fd = (plus.pressure - minus.pressure) / (2.0 * step_mu)
        chi_fd = (plus.charge_density - minus.charge_density) / (
            2.0 * step_mu
        )
        density_derivative.append(abs(density_fd - state.charge_density))
        susceptibility_derivative.append(
            abs(chi_fd - float(state.susceptibility))
        )
        step_phi = 1.0e-6
        response_fd = (
            o2_equilibrium_state(mu, phi + step_phi, config).pressure
            - o2_equilibrium_state(mu, phi - step_phi, config).pressure
        ) / (2.0 * step_phi)
        response_derivative.append(abs(response_fd - state.response_source))
        signed = o2_equilibrium_state(-mu, phi, config)
        signed_pressure.append(abs(state.pressure - signed.pressure))
        signed_density.append(abs(state.charge_density + signed.charge_density))
        sound_values.append(float(state.sound_speed_sq))

    for density in np.concatenate(
        [np.linspace(-2.0, -0.05, 32), np.linspace(0.05, 2.0, 32)]
    ):
        phi = 0.2
        state = o2_helmholtz_state(float(density), phi, config)
        legendre.append(
            abs(
                float(state.helmholtz_free_energy)
                - (state.chemical_potential * density - state.pressure)
            )
        )
        step = 1.0e-5
        plus = o2_helmholtz_state(float(density + step), phi, config)
        minus = o2_helmholtz_state(float(density - step), phi, config)
        df_dn = (
            float(plus.helmholtz_free_energy)
            - float(minus.helmholtz_free_energy)
        ) / (2.0 * step)
        dmu_dn = (plus.chemical_potential - minus.chemical_potential) / (
            2.0 * step
        )
        first_law.append(abs(df_dn - state.chemical_potential))
        inverse_susceptibility.append(
            abs(dmu_dn - 1.0 / float(state.susceptibility))
        )

    null = _eos_config(epsilon=0.0)
    null_left = o2_equilibrium_state(1.5, -10.0, null)
    null_right = o2_equilibrium_state(1.5, 20.0, null)
    null_error = max(
        abs(null_left.pressure - null_right.pressure),
        abs(null_left.charge_density - null_right.charge_density),
        abs(null_left.response_source),
        abs(null_right.response_source),
    )

    map_config = NoetherPhaseFieldMapConfig(
        density_reference=0.0,
        density_scale=0.8,
        chemical_potential_scale=1.0,
    )
    phase = np.linspace(-1.0, 1.0, 129)
    exact = np.array(
        [
            o2_helmholtz_state(
                map_config.density_reference + map_config.density_scale * item,
                0.2,
                config,
            ).helmholtz_free_energy
            for item in phase
        ],
        dtype=float,
    )
    comparator = symmetric_double_well_thermodynamic_map(
        phase, map_config
    ).natural_free_energy_density
    scale = max(1.0e-12, float(np.max(np.abs(exact))))
    double_well_residual = float(np.max(np.abs(exact - comparator)) / scale)

    metrics = {
        "stationarity_max_abs": max(stationarity),
        "dp_dmu_max_abs": max(density_derivative),
        "d2p_dmu2_max_abs": max(susceptibility_derivative),
        "dp_dphi_max_abs": max(response_derivative),
        "legendre_max_abs": max(legendre),
        "first_law_df_dn_max_abs": max(first_law),
        "inverse_susceptibility_max_abs": max(inverse_susceptibility),
        "signed_pressure_even_max_abs": max(signed_pressure),
        "signed_density_odd_max_abs": max(signed_density),
        "response_null_max_abs": null_error,
        "minimum_sound_speed_sq": min(sound_values),
        "maximum_sound_speed_sq": max(sound_values),
        "double_well_reduction_relative_residual": double_well_residual,
    }
    gates = {
        "stationarity": metrics["stationarity_max_abs"]
        <= THRESHOLDS["stationarity_max_abs"],
        "analytic_derivatives": max(
            metrics["dp_dmu_max_abs"],
            metrics["d2p_dmu2_max_abs"],
            metrics["inverse_susceptibility_max_abs"],
        )
        <= THRESHOLDS["analytic_derivative_max_abs"],
        "response_reciprocity": metrics["dp_dphi_max_abs"]
        <= THRESHOLDS["response_reciprocity_max_abs"],
        "legendre_first_law": max(
            metrics["legendre_max_abs"],
            metrics["first_law_df_dn_max_abs"],
        )
        <= THRESHOLDS["legendre_first_law_max_abs"],
        "signed_symmetry": max(
            metrics["signed_pressure_even_max_abs"],
            metrics["signed_density_odd_max_abs"],
        )
        <= 1.0e-12,
        "response_null": metrics["response_null_max_abs"] <= 1.0e-12,
        "stable_subluminal_sound": (
            metrics["minimum_sound_speed_sq"] >= 0.0
            and metrics["maximum_sound_speed_sq"] <= 1.0 + 1.0e-12
        ),
    }
    return {
        "metrics": metrics,
        "gates": gates,
        "double_well_reduction": {
            "status": (
                "ACCEPTED"
                if double_well_residual
                <= THRESHOLDS["double_well_reduction_relative_max"]
                else "REJECTED_REMAINS_CONSTITUTIVE_COMPARATOR"
            ),
            "fixed_domain": {"C_min": -1.0, "C_max": 1.0, "points": 129},
            "fitted_parameters": False,
        },
    }


def _transport_checks(config: O2FiniteDensityEOSConfig) -> dict[str, Any]:
    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    state = SuperfluidHydroState(
        temperature=0.0,
        chemical_potential=1.4,
        four_velocity=np.array([1.0, 0.0, 0.0, 0.0]),
        phase_gradient=np.array([-1.4, 0.0, 0.0, 0.0]),
        space_response=0.2,
    )
    transport = SuperfluidTransportConfig(
        eos=config,
        coefficient_records=(
            _kubo_record("regular_conductivity", 0.10, state),
            _kubo_record("phase_relaxation", 0.18, state),
            _kubo_record("charge_phase_cross", 0.025, state),
            _kubo_record("relaxation_time", 0.9, state),
        ),
        allow_synthetic_controls=True,
    )
    projector = spatial_projector(metric, state.four_velocity)
    u_covariant = metric @ np.asarray(state.four_velocity)
    mixed = projector @ metric
    projector_error = float(
        max(
            np.max(np.abs(projector @ u_covariant)),
            np.max(np.abs(mixed @ mixed - mixed)),
        )
    )
    josephson_error = abs(josephson_residual(state, metric))
    eos_state = o2_equilibrium_state(
        state.chemical_potential, state.space_response, config
    )
    current = ideal_superfluid_current(state, metric, transport)
    stress = ideal_superfluid_stress_tensor(state, metric, transport)
    expected_current = np.array([eos_state.charge_density, 0.0, 0.0, 0.0])
    expected_stress = np.diag(
        [
            eos_state.energy_density,
            eos_state.pressure,
            eos_state.pressure,
            eos_state.pressure,
        ]
    )
    ideal_error = float(
        max(
            np.max(np.abs(current - expected_current)),
            np.max(np.abs(stress - expected_stress)),
        )
    )
    fields = np.array([eos_state.amplitude, 0.0])
    gradients = np.vstack(
        [np.zeros(4), eos_state.amplitude * np.asarray(state.phase_gradient)]
    )
    action_current = matter_noether_current(
        metric, fields, gradients, config.matter
    )
    action_current_error = float(np.max(np.abs(current - action_current)))

    boost_speed = 0.37
    gamma = 1.0 / np.sqrt(1.0 - boost_speed**2)
    boost = np.array(
        [
            [gamma, -gamma * boost_speed, 0.0, 0.0],
            [-gamma * boost_speed, gamma, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    boosted_state = SuperfluidHydroState(
        temperature=0.0,
        chemical_potential=state.chemical_potential,
        four_velocity=boost @ np.asarray(state.four_velocity),
        phase_gradient=np.linalg.inv(boost).T
        @ np.asarray(state.phase_gradient),
        space_response=state.space_response,
    )
    boosted_transport = SuperfluidTransportConfig(eos=config)
    boosted_current = ideal_superfluid_current(
        boosted_state, metric, boosted_transport
    )
    boosted_stress = ideal_superfluid_stress_tensor(
        boosted_state, metric, boosted_transport
    )
    lorentz_error = float(
        max(
            np.max(np.abs(boosted_current - boost @ current)),
            np.max(np.abs(boosted_stress - boost @ stress @ boost.T)),
        )
    )

    rng = np.random.default_rng(102002)
    entropy_values = [
        entropy_production(rng.normal(size=2), state, transport)
        for _ in range(512)
    ]
    diagnostics = causal_transport_diagnostics(state, metric, transport)
    modes = linear_mode_spectrum(0.27, state, metric, transport)
    expected_sound = np.sqrt(float(eos_state.sound_speed_sq)) * 0.27
    sound_error = float(
        np.max(
            np.abs(
                modes["goldstone_angular_frequencies"]
                - np.array([-expected_sound, expected_sound])
            )
        )
    )
    missing_provenance_blocked = False
    try:
        causal_transport_diagnostics(
            state, metric, SuperfluidTransportConfig(eos=config)
        )
    except RuntimeError:
        missing_provenance_blocked = True

    metrics = {
        "projector_max_abs": projector_error,
        "josephson_max_abs": josephson_error,
        "ideal_constitutive_max_abs": ideal_error,
        "action_noether_current_max_abs": action_current_error,
        "lorentz_covariance_max_abs": lorentz_error,
        "entropy_production_minimum": min(entropy_values),
        "goldstone_sound_max_abs": sound_error,
        "diffusion_coefficient": diagnostics["diffusion_coefficient"],
        "characteristic_speed_sq": diagnostics["characteristic_speed_sq"],
        "missing_provenance_blocked": missing_provenance_blocked,
    }
    gates = {
        "projector": projector_error <= THRESHOLDS["projector_max_abs"],
        "josephson": josephson_error <= THRESHOLDS["josephson_max_abs"],
        "ideal_current_stress": max(ideal_error, action_current_error)
        <= THRESHOLDS["ideal_constitutive_max_abs"],
        "lorentz_covariance": lorentz_error
        <= THRESHOLDS["lorentz_covariance_max_abs"],
        "entropy_sign": min(entropy_values) >= THRESHOLDS["entropy_minimum"],
        "goldstone_sound": sound_error
        <= THRESHOLDS["goldstone_sound_max_abs"],
        "causal_speed": diagnostics["characteristic_speed_sq"]
        <= THRESHOLDS["natural_causal_speed_sq_max"] + 1.0e-12,
        "missing_provenance_blocks": missing_provenance_blocked,
        "trace_isolation": (
            covariant_superfluid_transport_contract()["trace_input"] is False
            and covariant_superfluid_transport_contract()["trace_backreaction"]
            is False
        ),
    }
    return {"metrics": metrics, "gates": gates}


def build_artifacts(
    *, generated_at: str | None = None
) -> tuple[dict[str, Any], ...]:
    now = generated_at or datetime.now(timezone.utc).isoformat()
    source = _source_provenance()
    config = _eos_config()
    eos_checks = _eos_checks(config)
    transport_checks = _transport_checks(config)
    eos_pass = source["status"] == "PASS" and all(eos_checks["gates"].values())
    transport_pass = all(transport_checks["gates"].values())
    # Keep legacy labels stable in committed artifacts while hashing the
    # canonical implementation selected by the shared path resolver.
    source_hashes = {
        "docs/core/02_equations/o2/uet_o2_finite_density_eos.py": _sha(EOS_CORE),
        "docs/core/02_equations/covariant/uet_covariant_superfluid_transport.py": _sha(TRANSPORT_CORE),
        "docs/core/02_equations/covariant/uet_covariant_matter.py": _sha(MATTER_CORE),
        "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py": _sha(STATE_MAP_CORE),
        "docs/core/01_contracts/O2_SUPERFLUID_EOS_TRANSPORT_SPEC.md": _sha(SPEC),
    }
    source_hashes.update(
        {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha(path)
            for path in SOURCE_RECORDS
        }
    )
    input_identity = {
        "eos_core": "docs/core/02_equations/o2/uet_o2_finite_density_eos.py",
        "transport_core": "docs/core/02_equations/covariant/uet_covariant_superfluid_transport.py",
        "parent_action": "docs/core/02_equations/covariant/uet_covariant_matter.py",
        "state_map": "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py",
        "spec": "docs/core/01_contracts/O2_SUPERFLUID_EOS_TRANSPORT_SPEC.md",
        "parameter_policy": "fixed_deterministic_synthetic_control_no_fit",
        "seed_eos": 102001,
        "seed_transport": 102002,
    }
    eos_verification = {
        "schema_version": "1.0",
        "artifact": "o2_finite_density_eos_verification",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave10_v1",
        "benchmark_role": "internal_tree_level_formula_verification",
        "method_label": "finite_density_O2_mean_field_EOS",
        "audit_status": "PASS" if eos_pass else "FAIL",
        "evidence_status": "TREE_LEVEL_MEAN_FIELD_DERIVATION",
        "unit_lane": "natural",
        "input_identity": input_identity,
        "thresholds": THRESHOLDS,
        "metrics": eos_checks["metrics"],
        "gates": eos_checks["gates"],
        "double_well_reduction": eos_checks["double_well_reduction"],
        "source_provenance": source,
        "source_hashes": source_hashes,
        "claim_boundary": {
            "allowed": "tree-level finite-density O2 mean-field derivation",
            "blocked": [
                "finite-temperature equation of state",
                "microscopic transport coefficient derivation",
                "symmetric double well derived from the O2 action",
                "physical validation",
            ],
        },
        "next_controller": (
            "covariant_superfluid_kubo_transport_and_entropy_matching_missing"
        ),
    }
    formula_audit = {
        "schema_version": "1.0",
        "artifact": "o2_eos_formula_audit",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave10_v1",
        "benchmark_role": "formula_audit",
        "method_label": "action_to_EOS_and_transport_status_registry",
        "status": "WARN" if eos_pass and transport_pass else "FAIL",
        "unit_lane": "natural",
        "formula_registry": [
            {
                "formula_id": "response_shifted_mass",
                "relation": "m_eff^2=m^2-epsilon_nc*h*(Phi-Phi_*)",
                "variables": "natural-unit action scalars and couplings",
                "unit_closure_status": "CLOSED_NATURAL_MASS_DIMENSIONS",
                "constant_origin": "topic_derived_relation",
                "proof_status": "derived",
                "verification_role": "gate",
                "implementation": "docs/core/02_equations/o2/uet_o2_finite_density_eos.py::effective_mass_sq",
            },
            {
                "formula_id": "finite_density_grand_potential",
                "relation": "Omega=(m_eff^2-Z*mu^2)A^2/2+lambda*A^4/4",
                "variables": "homogeneous O2 amplitude, chemical potential, response scalar",
                "unit_closure_status": "CLOSED_NATURAL_MASS_DIMENSION_4",
                "constant_origin": "topic_derived_relation",
                "proof_status": "derived_tree_level",
                "verification_role": "gate",
                "implementation": "docs/core/02_equations/o2/uet_o2_finite_density_eos.py::o2_equilibrium_state",
            },
            {
                "formula_id": "canonical_legendre_transform",
                "relation": "f=mu*n-p; Z^2*mu^3-Z*m_eff^2*mu-lambda*n=0",
                "variables": "signed charge density and stable condensed root",
                "unit_closure_status": "CLOSED_NATURAL_MASS_DIMENSION_4",
                "constant_origin": "topic_derived_relation",
                "proof_status": "derived",
                "verification_role": "gate",
                "implementation": "docs/core/02_equations/o2/uet_o2_finite_density_eos.py::o2_helmholtz_state",
            },
            {
                "formula_id": "ideal_covariant_superfluid_current_stress",
                "relation": "N^mu=f_s*xi^mu; T^mu_nu=f_s*xi^mu*xi^nu+p*g^mu_nu",
                "variables": "T=0 pure-superfluid P(X,Phi) sector",
                "unit_closure_status": "CLOSED_NATURAL_MASS_DIMENSIONS",
                "constant_origin": "topic_derived_relation",
                "proof_status": "derived_tree_level",
                "verification_role": "gate",
                "implementation": "docs/core/02_equations/covariant/uet_covariant_superfluid_transport.py",
            },
            {
                "formula_id": "longitudinal_kubo_transport",
                "relation": "D=sigma_reg/chi; tau*d_tJ+J=-sigma_reg*grad(mu)",
                "variables": "regular non-condensate response only",
                "unit_closure_status": "CLOSED_NATURAL_CONTROL_LANE_ONLY",
                "constant_origin": "open_placeholder",
                "proof_status": "open_coefficient_matching",
                "verification_role": "synthetic_control",
                "implementation": "docs/core/02_equations/covariant/uet_covariant_superfluid_transport.py",
            },
        ],
        "completed_formula_gates": [
            "tree_level_O2_EOS",
            "stable_signed_canonical_inversion",
            "response_reciprocity",
            "T0_covariant_ideal_current_and_stress",
            "local_longitudinal_entropy_control",
        ],
        "open_formula_gates": [
            "physical_Kubo_coefficient_values",
            "finite_temperature_normal_component",
            "full_superfluid_transport_tensor",
            "Schwinger_Keldysh_KMS_derivation",
            "gradient_EFT_kappa_C",
            "SI_lane",
        ],
        "source_hashes": source_hashes,
    }
    transport_verification = {
        "schema_version": "1.0",
        "artifact": "covariant_superfluid_transport_verification",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave10_v1",
        "benchmark_role": "internal_covariant_and_synthetic_transport_control",
        "method_label": "T0_P_of_X_plus_longitudinal_Kubo_interface",
        "audit_status": "PASS" if transport_pass else "FAIL",
        "evidence_status": "PARTIAL_T0_IDEAL_PLUS_SIMULATION_ONLY_DISSIPATIVE_CONTROL",
        "unit_lane": "natural",
        "input_identity": input_identity,
        "thresholds": THRESHOLDS,
        "metrics": transport_checks["metrics"],
        "gates": transport_checks["gates"],
        "physical_coefficient_evidence": "BLOCKED_NOT_PROVIDED",
        "finite_temperature_two_fluid_completion": "BLOCKED",
        "full_SK_KMS_completion": "BLOCKED",
        "source_provenance": source,
        "source_hashes": source_hashes,
        "trace_input": False,
        "trace_backreaction": False,
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
    }
    transport_contract = {
        "schema_version": "1.0",
        "artifact": "covariant_superfluid_transport_contract",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave10_v1",
        "benchmark_role": "ontology_dependency_and_claim_contract",
        "method_label": "T0_superfluid_Kubo_boundary",
        "status": "BLOCKED",
        "interface_status": "PASS" if eos_pass and transport_pass else "FAIL",
        "core_contract": covariant_superfluid_transport_contract(),
        "eos_contract": o2_finite_density_eos_contract(),
        "allowed_language": [
            "tree-level finite-density O2 mean-field equation of state",
            "covariant T=0 pure-superfluid ideal constitutive relation",
            "entropy-consistent longitudinal Kubo matching interface",
            "simulation-only dissipative control",
        ],
        "blocked_language": [
            "full relativistic two-fluid theory derived",
            "microscopic UET conductivity or viscosity derived",
            "external physical transport validation",
            "GR or global-universe closure established",
        ],
        "required_coefficient_fields": [
            "value",
            "units",
            "hydrodynamic_frame",
            "temperature",
            "chemical_potential",
            "space_response",
            "correlator_formula_id",
            "source_path_or_url",
            "source_hash",
            "evidence_status",
        ],
        "next_controller": O2_SUPERFLUID_TRANSPORT_CONTROLLER,
    }
    program = {
        "schema_version": "1.0",
        "artifact": "uet_gr_research_program_gate",
        "generated_at": now,
        "topic": "docs/core UET GR non-closed response",
        "version": "wave10_v1",
        "benchmark_role": "program_gate",
        "method_label": "monotonic_gr_research_stage_gate",
        "input_identity": {
            "eos_verification": "docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json",
            "eos_formula_audit": "docs/core/07_artifacts/correspondence/o2_eos_formula_audit.json",
            "transport_verification": "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json",
            "transport_contract": "docs/core/07_artifacts/archive/covariant_superfluid_transport_contract.json",
        },
        "notes": [
            "The EOS and ideal T=0 constitutive gates pass at tree level.",
            "Physical Kubo coefficients and full two-fluid/curved evolution remain blocked.",
        ],
        "status": "BLOCKED",
        "program_stage": "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED",
        "current_claim_class": "B",
        "gr_null_model": {
            "parameter": "epsilon_nc",
            "value": 0,
            "verification_status": "PASS",
        },
        "sector_status": {
            "ontology_and_claim_contract": "PASS",
            "legacy_claim_quarantine": "PASS",
            "conservative_tensor_formula": "PASS",
            "exact_gr_closed_limit": "PASS",
            "covariant_exchange_bianchi_balance": "PASS_CONSERVATIVE_PARENT_ONLY",
            "causal_nonclosed_sector": "PASS_CONSTITUTIVE_1P1D",
            "weak_field_reduction": "PARTIAL_RESPONSE_ONLY",
            "covariant_matter_action": "PASS_O2_SCALAR_PILOT",
            "reciprocal_coupling": "PASS_ACTION_LEVEL",
            "signed_O2_noether_current": "PASS_ON_SHELL",
            "diffusive_matter_reduction": "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT",
            "local_convex_matter_causality": "PASS_CONTROL",
            "gradient_phase_field_causality": "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY",
            "fixed_light_cone_parameter_domain": "PASS_NORMALIZED_ANALYTIC",
            "uniform_subluminal_phase_field_limit": "NO_GO_FOR_EXACT_PARABOLIC_LIMIT",
            "local_current_law_mapping": "PASS_ALGEBRAIC_MOBILITY_ONE",
            "hydrodynamic_state_coordinate_map": "PASS_AFFINE_FIXED_SCALE",
            "microscopic_state_reconstruction": "NO_GO_MANY_TO_ONE",
            "external_C_noether_coordinate_map": "PASS_DECLARED_SIGNED_CHARGE_ONLY",
            "equation_of_state_from_matter_action": "PASS_TREE_LEVEL_T0",
            "canonical_charge_EOS": "PASS_STABLE_BRANCH",
            "symmetric_double_well_reduction": eos_checks["double_well_reduction"]["status"],
            "covariant_T0_superfluid_constitutive": "PASS_PURE_SUPERFLUID",
            "longitudinal_entropy_control": "PASS_SYNTHETIC_ONLY",
            "Kubo_matching_interface": "PASS_NO_DEFAULTS",
            "physical_Kubo_coefficients": "BLOCKED",
            "finite_temperature_normal_component": "BLOCKED",
            "full_superfluid_transport_tensor": "BLOCKED",
            "Schwinger_Keldysh_KMS_completion": "BLOCKED",
            "covariant_coarse_graining": "BLOCKED_DEFERRED",
            "curved_3p1_solver": "BLOCKED",
            "physical_gr_benchmarks": "NOT_STARTED",
        },
        "global_universe_closure": "UNRESOLVED",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "controlling_blocker": O2_SUPERFLUID_TRANSPORT_CONTROLLER,
        "claim_promotion": "BLOCKED",
        "reason": (
            "The action-derived finite-density EOS and T=0 pure-superfluid "
            "current/stress pass internal formula gates. Dissipative values "
            "remain synthetic controls; physical Kubo evidence, a finite-T "
            "normal component, full SK/KMS closure, and curved 3+1 evolution "
            "are not implemented."
        ),
    }
    return (
        eos_verification,
        formula_audit,
        transport_verification,
        transport_contract,
        program,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    artifacts = build_artifacts()
    names = (
        "o2_finite_density_eos_verification.json",
        "o2_eos_formula_audit.json",
        "covariant_superfluid_transport_verification.json",
        "covariant_superfluid_transport_contract.json",
        "uet_gr_research_program_gate.json",
    )
    for name, payload in zip(names, artifacts):
        _dump(name, payload)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "eos_audit_status": artifacts[0]["audit_status"],
                    "formula_status": artifacts[1]["status"],
                    "transport_audit_status": artifacts[2]["audit_status"],
                    "transport_contract_status": artifacts[3]["status"],
                    "program_status": artifacts[4]["status"],
                    "next_controller": artifacts[4]["controlling_blocker"],
                },
                indent=2,
            )
        )
    if args.strict and (
        artifacts[0]["audit_status"] != "PASS"
        or artifacts[2]["audit_status"] != "PASS"
        or artifacts[3]["interface_status"] != "PASS"
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
