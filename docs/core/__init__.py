"""
UET Core Module
===============
Central module for UET theory, parameters, and equations.

Usage:
    from docs.core import get_params, UETParams, HBAR, C, G

    # Get parameters for a scale
    params = get_params("electroweak")
    print(f"κ = {params.kappa}, β = {params.beta}")

    # Or by topic number
    params = get_params("0.1")  # Galaxy rotation

Author: UET Research Team
Version: 0.9.0
"""

from .uet_parameters import (
    # Main API
    get_params,
    get_kappa_beta,
    UETParameters,
    # Physical constants
    HBAR,
    C,
    G,
    K_B,
    ALPHA_EM,
    L_PLANCK,
    M_PLANCK,
    T_PLANCK,
    # Policy
    PARAMETER_POLICY,
)
from .uet_trace import TraceKernelConfig, UETStepResult
from .uet_matter_space import (
    MATTER_SPACE_OPERATOR_MODE,
    MatterSpaceConfig,
    MatterSpaceState,
    MatterSpaceStabilityError,
    causal_linear_space_step,
    matter_space_step,
)
from .uet_covariant_response import (
    COVARIANT_RESPONSE_MODEL_STATUS,
    CovariantResponseConfig,
    conservative_action_density,
    einstein_gr_residual,
    response_scalar_equation_residual,
    uet_metric_residual,
)
from .uet_covariant_balance import (
    COVARIANT_BALANCE_STATUS,
    CovariantExchangeLedger,
    balance_contract,
    evaluate_balance_identity,
    exchange_completed_ledger,
)
from .uet_covariant_nonclosed import (
    CAUSAL_NONCLOSED_STATUS,
    CausalInfluenceConfig,
    CausalSourceEvent,
    causal_exchange_from_events,
    covariant_retarded_kernel_value,
    retarded_influence_from_events,
    retarded_telegraph_kernel_1p1,
)
from .uet_covariant_reduction import (
    COVARIANT_REDUCTION_STATUS,
    ReducedResponseCoefficients,
    WeakFieldReductionConfig,
    compare_response_reduction,
    derive_response_coefficients,
    matter_space_config_from_reduction,
)
from .uet_covariant_matter import (
    COVARIANT_MATTER_STATUS,
    CovariantMatterConfig,
    coupled_conservative_action_density,
    coupled_matter_stress_tensor,
    coupled_metric_residual,
    coupled_response_scalar_equation_residual,
    matter_action_contract,
    matter_current_divergence,
    matter_eom_residual,
    matter_noether_current,
    reciprocal_interaction_derivatives,
)
from .uet_covariant_diffusion import (
    COVARIANT_DIFFUSION_STATUS,
    ConservedCurrentBridgeConfig,
    ConservedCurrentState,
    CurrentDecomposition,
    causal_current_rhs,
    compare_adiabatic_limit,
    compare_matter_space_conserved_rhs,
    conditioned_matter_chemical_potential,
    conditioned_matter_free_energy,
    current_bridge_contract,
    current_energy_balance,
    current_extended_energy,
    decompose_noether_current,
    matter_equation_config_from_current_bridge,
    model_b_rhs,
    normalize_local_charge_and_current,
    principal_symbol_diagnostics,
)
from .uet_hyperbolic_phase_field import (
    HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV,
    HYPERBOLIC_PHASE_FIELD_SOURCE_DOI,
    HYPERBOLIC_PHASE_FIELD_STATUS,
    HyperbolicPhaseFieldConfig,
    HyperbolicPhaseFieldRates,
    HyperbolicPhaseFieldState,
    analytic_characteristic_speeds,
    augmented_chemical_potential,
    compare_augmented_to_cahn_hilliard_chemical,
    double_well_curvature,
    double_well_derivative,
    double_well_potential,
    gradient_constraint_rate_residual,
    gradient_constraint_residual,
    hyperbolic_phase_field_contract,
    hyperbolic_phase_field_energy,
    hyperbolic_phase_field_energy_balance,
    hyperbolic_phase_field_rhs,
    hyperbolicity_diagnostics,
    paper_asymptotic_scaling_diagnostics,
    periodic_central_derivative,
    principal_matrix,
    quasistatic_auxiliary_phase,
)
from .uet_hyperbolic_phase_field_bridge import (
    HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER,
    HYPERBOLIC_PHASE_FIELD_BRIDGE_STATUS,
    LocalCurrentLawMap,
    evaluate_parameter_sequence,
    fixed_cone_parabolic_limit_no_go,
    fixed_light_cone_feasibility,
    hyperbolic_phase_field_bridge_contract,
    map_external_flux_law_to_current,
    shifted_curvature_domain_bounds,
    subluminal_parameter_bounds,
)
from .uet_noether_phase_field_map import (
    NOETHER_PHASE_FIELD_MAP_CONTROLLER,
    NOETHER_PHASE_FIELD_MAP_STATUS,
    ConstitutiveScaleMap,
    ContinuityMap,
    DoubleWellThermodynamicMap,
    ExternalComparatorStateMap,
    NoetherPhaseFieldCoordinates,
    NoetherPhaseFieldMapConfig,
    denormalize_phase_field_coordinates,
    local_cell_average_1d,
    map_continuity_terms,
    map_external_comparator_state,
    map_normalized_constitutive_scales,
    noether_phase_field_map_contract,
    normalize_noether_hydrodynamic_state,
    symmetric_double_well_equilibrium_contract,
    symmetric_double_well_thermodynamic_map,
)
from .uet_o2_finite_density_eos import (
    O2_FINITE_DENSITY_EOS_CONTROLLER,
    O2_FINITE_DENSITY_EOS_STATUS,
    O2EOSState,
    O2FiniteDensityEOSConfig,
    chemical_potential_from_charge_density,
    condensate_control,
    effective_mass_sq,
    o2_eos_derivatives,
    o2_equilibrium_state,
    o2_finite_density_eos_contract,
    o2_helmholtz_state,
)
from .thermal_observable_bridge import (
    THERMAL_BRIDGE_STATUS,
    THERMAL_MAPPING_STATUS,
    ThermalObservableBridgeConfig,
    ThermalObservableBridgeResult,
    run_thermal_observable_bridge,
)
from .thermal_source_observable_map import (
    NORMALIZED_TTG_OBSERVABLE,
    THERMAL_SOURCE_MAP_SCHEMA_VERSION,
    THERMAL_CALIBRATION_SCHEMA_VERSION,
    THERMAL_CALIBRATION_STATUSES,
    ThermalPhiCalibration,
    normalized_ttg_signal,
    quasi_temperature_difference_from_phi,
    quasi_temperature_difference_from_calibration,
    ttg_wave_speed,
    ttg_wavevector,
    ttg_propagation_length,
)
from .persistence_energy_diagnostic import (
    PATH_COST_ORIGIN,
    PERSISTENCE_ENERGY_STATUS,
    PERSISTENCE_PRINCIPLE_ID,
    PERSISTENCE_PRINCIPLE_NAME_EN,
    PERSISTENCE_PRINCIPLE_NAME_TH,
    PERSISTENCE_PRINCIPLE_STATUS,
    PersistenceEnergyConfig,
    PersistenceEnergyResult,
    simulate_persistence_energy,
)
from .matter_interaction_forward import (
    FORWARD_MAPPING_STATUS,
    UET_EXTRA_RESPONSE_STATUS,
    MatterInteractionForwardConfig,
    MatterInteractionForwardResult,
    MatterSource,
    matter_to_interaction_forward,
)
from .uet_covariant_superfluid_transport import (
    O2_SUPERFLUID_TRANSPORT_CONTROLLER,
    O2_SUPERFLUID_TRANSPORT_OPERATOR_MODE,
    O2_SUPERFLUID_TRANSPORT_STATUS,
    KuboCoefficientRecord,
    SuperfluidHydroState,
    SuperfluidTransportConfig,
    causal_longitudinal_current_rate,
    causal_transport_diagnostics,
    covariant_superfluid_transport_contract,
    entropy_production,
    ideal_superfluid_coefficients,
    ideal_superfluid_current,
    ideal_superfluid_stress_tensor,
    josephson_residual,
    linear_mode_spectrum,
    longitudinal_onsager_matrix,
    spatial_projector,
    superfluid_invariants,
)


__all__ = [
    # Parameters
    "get_params",
    "get_kappa_beta",
    "UETParameters",
    # Constants
    "HBAR",
    "C",
    "G",
    "K_B",
    "ALPHA_EM",
    "L_PLANCK",
    "M_PLANCK",
    "T_PLANCK",
    # Policy
    "PARAMETER_POLICY",
    "TraceKernelConfig",
    "UETStepResult",
    "MATTER_SPACE_OPERATOR_MODE",
    "MatterSpaceConfig",
    "MatterSpaceState",
    "MatterSpaceStabilityError",
    "matter_space_step",
    "COVARIANT_RESPONSE_MODEL_STATUS",
    "CovariantResponseConfig",
    "conservative_action_density",
    "einstein_gr_residual",
    "response_scalar_equation_residual",
    "uet_metric_residual",
    "COVARIANT_BALANCE_STATUS",
    "CovariantExchangeLedger",
    "balance_contract",
    "evaluate_balance_identity",
    "exchange_completed_ledger",
    "CAUSAL_NONCLOSED_STATUS",
    "CausalInfluenceConfig",
    "CausalSourceEvent",
    "causal_exchange_from_events",
    "covariant_retarded_kernel_value",
    "retarded_influence_from_events",
    "retarded_telegraph_kernel_1p1",
    "COVARIANT_REDUCTION_STATUS",
    "ReducedResponseCoefficients",
    "WeakFieldReductionConfig",
    "compare_response_reduction",
    "derive_response_coefficients",
    "matter_space_config_from_reduction",
    "COVARIANT_MATTER_STATUS",
    "CovariantMatterConfig",
    "coupled_conservative_action_density",
    "coupled_matter_stress_tensor",
    "coupled_metric_residual",
    "coupled_response_scalar_equation_residual",
    "matter_action_contract",
    "matter_current_divergence",
    "matter_eom_residual",
    "matter_noether_current",
    "reciprocal_interaction_derivatives",
    "COVARIANT_DIFFUSION_STATUS",
    "ConservedCurrentBridgeConfig",
    "ConservedCurrentState",
    "CurrentDecomposition",
    "causal_current_rhs",
    "compare_adiabatic_limit",
    "compare_matter_space_conserved_rhs",
    "conditioned_matter_chemical_potential",
    "conditioned_matter_free_energy",
    "current_bridge_contract",
    "current_energy_balance",
    "current_extended_energy",
    "decompose_noether_current",
    "matter_equation_config_from_current_bridge",
    "model_b_rhs",
    "normalize_local_charge_and_current",
    "principal_symbol_diagnostics",
    "HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV",
    "HYPERBOLIC_PHASE_FIELD_SOURCE_DOI",
    "HYPERBOLIC_PHASE_FIELD_STATUS",
    "HyperbolicPhaseFieldConfig",
    "HyperbolicPhaseFieldRates",
    "HyperbolicPhaseFieldState",
    "analytic_characteristic_speeds",
    "augmented_chemical_potential",
    "compare_augmented_to_cahn_hilliard_chemical",
    "double_well_curvature",
    "double_well_derivative",
    "double_well_potential",
    "gradient_constraint_rate_residual",
    "gradient_constraint_residual",
    "hyperbolic_phase_field_contract",
    "hyperbolic_phase_field_energy",
    "hyperbolic_phase_field_energy_balance",
    "hyperbolic_phase_field_rhs",
    "hyperbolicity_diagnostics",
    "paper_asymptotic_scaling_diagnostics",
    "periodic_central_derivative",
    "principal_matrix",
    "quasistatic_auxiliary_phase",
    "HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER",
    "HYPERBOLIC_PHASE_FIELD_BRIDGE_STATUS",
    "LocalCurrentLawMap",
    "evaluate_parameter_sequence",
    "fixed_cone_parabolic_limit_no_go",
    "fixed_light_cone_feasibility",
    "hyperbolic_phase_field_bridge_contract",
    "map_external_flux_law_to_current",
    "shifted_curvature_domain_bounds",
    "subluminal_parameter_bounds",
    "NOETHER_PHASE_FIELD_MAP_CONTROLLER",
    "NOETHER_PHASE_FIELD_MAP_STATUS",
    "ConstitutiveScaleMap",
    "ContinuityMap",
    "DoubleWellThermodynamicMap",
    "ExternalComparatorStateMap",
    "NoetherPhaseFieldCoordinates",
    "NoetherPhaseFieldMapConfig",
    "denormalize_phase_field_coordinates",
    "local_cell_average_1d",
    "map_continuity_terms",
    "map_external_comparator_state",
    "map_normalized_constitutive_scales",
    "noether_phase_field_map_contract",
    "normalize_noether_hydrodynamic_state",
    "symmetric_double_well_equilibrium_contract",
    "symmetric_double_well_thermodynamic_map",
    "O2_FINITE_DENSITY_EOS_CONTROLLER",
    "O2_FINITE_DENSITY_EOS_STATUS",
    "O2EOSState",
    "O2FiniteDensityEOSConfig",
    "chemical_potential_from_charge_density",
    "condensate_control",
    "effective_mass_sq",
    "o2_eos_derivatives",
    "o2_equilibrium_state",
    "o2_finite_density_eos_contract",
    "o2_helmholtz_state",
    "O2_SUPERFLUID_TRANSPORT_CONTROLLER",
    "O2_SUPERFLUID_TRANSPORT_OPERATOR_MODE",
    "O2_SUPERFLUID_TRANSPORT_STATUS",
    "KuboCoefficientRecord",
    "SuperfluidHydroState",
    "SuperfluidTransportConfig",
    "causal_longitudinal_current_rate",
    "causal_transport_diagnostics",
    "covariant_superfluid_transport_contract",
    "entropy_production",
    "ideal_superfluid_coefficients",
    "ideal_superfluid_current",
    "ideal_superfluid_stress_tensor",
    "josephson_residual",
    "linear_mode_spectrum",
    "longitudinal_onsager_matrix",
    "spatial_projector",
    "superfluid_invariants",
    "THERMAL_BRIDGE_STATUS",
    "THERMAL_MAPPING_STATUS",
    "ThermalObservableBridgeConfig",
    "ThermalObservableBridgeResult",
    "run_thermal_observable_bridge",
    "NORMALIZED_TTG_OBSERVABLE",
    "THERMAL_SOURCE_MAP_SCHEMA_VERSION",
    "THERMAL_CALIBRATION_SCHEMA_VERSION",
    "THERMAL_CALIBRATION_STATUSES",
    "ThermalPhiCalibration",
    "normalized_ttg_signal",
    "quasi_temperature_difference_from_phi",
    "quasi_temperature_difference_from_calibration",
    "ttg_wave_speed",
    "ttg_wavevector",
    "ttg_propagation_length",
    "PATH_COST_ORIGIN",
    "PERSISTENCE_ENERGY_STATUS",
    "PERSISTENCE_PRINCIPLE_ID",
    "PERSISTENCE_PRINCIPLE_NAME_EN",
    "PERSISTENCE_PRINCIPLE_NAME_TH",
    "PERSISTENCE_PRINCIPLE_STATUS",
    "PersistenceEnergyConfig",
    "PersistenceEnergyResult",
    "simulate_persistence_energy",
    "FORWARD_MAPPING_STATUS",
    "UET_EXTRA_RESPONSE_STATUS",
    "MatterInteractionForwardConfig",
    "MatterInteractionForwardResult",
    "MatterSource",
    "matter_to_interaction_forward",

]
from .mass_density_3d import (
    MassDensity3DSource,
    gaussian_shape_3d,
    integrated_density_3d,
    mass_from_si_volume_density,
    normalized_shape_3d,
    si_volume_density_from_shape,
)

__all__ += [
    "MassDensity3DSource",
    "gaussian_shape_3d",
    "integrated_density_3d",
    "mass_from_si_volume_density",
    "normalized_shape_3d",
    "si_volume_density_from_shape",
]

__version__ = "0.9.0"
from .uet_impact_effect import (
    IMPACT_EFFECT_OPERATOR_MODE,
    TRACE_ONLY_MODE,
    COUPLED_RECEIVER_MODE,
    SUPPORTED_EFFECT_MODES,
    ImpactRecord,
    CarrierRecord,
    EffectRecord,
    ReceiverDynamics,
    ReceiverUpdate,
    impact_to_effect,
    apply_receiver_effect,
    impact_effect_contract,
)

__all__ += [
    "IMPACT_EFFECT_OPERATOR_MODE",
    "TRACE_ONLY_MODE",
    "COUPLED_RECEIVER_MODE",
    "SUPPORTED_EFFECT_MODES",
    "ImpactRecord",
    "CarrierRecord",
    "EffectRecord",
    "ReceiverDynamics",
    "ReceiverUpdate",
    "impact_to_effect",
    "apply_receiver_effect",
    "impact_effect_contract",
]
from .uet_matter_space_causal import (
    CAUSAL_DISCRETE_GRADIENT_OPERATOR_MODE,
    causal_space_discrete_energy,
    causal_space_discrete_gradient_step,
)

__all__ += [
    "CAUSAL_DISCRETE_GRADIENT_OPERATOR_MODE",
    "causal_space_discrete_energy",
    "causal_space_discrete_gradient_step",
]
from .uet_matter_space_split import (
    MATTER_SPACE_CAUSAL_SPLIT_OPERATOR_MODE,
    causal_matter_space_split_step,
    causal_split_energy,
)

__all__ += [
    "MATTER_SPACE_CAUSAL_SPLIT_OPERATOR_MODE",
    "causal_matter_space_split_step",
    "causal_split_energy",
]

from .uet_matter_space_finite_cone import (
    FINITE_CONE_C_OPERATOR_MODE,
    FiniteConeCConfig,
    FiniteConeCState,
    FiniteConeCStabilityError,
    finite_cone_c_chemical_potentials,
    finite_cone_c_contract,
    finite_cone_c_extended_energy,
    finite_cone_c_free_energy,
    finite_cone_c_stability_limit,
    finite_cone_c_step,
)

__all__ += [
    "FINITE_CONE_C_OPERATOR_MODE",
    "FiniteConeCConfig",
    "FiniteConeCState",
    "FiniteConeCStabilityError",
    "finite_cone_c_chemical_potentials",
    "finite_cone_c_contract",
    "finite_cone_c_extended_energy",
    "finite_cone_c_free_energy",
    "finite_cone_c_stability_limit",
    "finite_cone_c_step",
]
from .uet_resource_selection import (
    RESOURCE_SELECTION_OPERATOR_MODE,
    RESOURCE_SELECTION_STATUS,
    ResourceSelectionConfig,
    ResourceSelectionResult,
    ResourceSelectionStabilityError,
    simulate_resource_selection,
)

__all__ += [
    "RESOURCE_SELECTION_OPERATOR_MODE",
    "RESOURCE_SELECTION_STATUS",
    "ResourceSelectionConfig",
    "ResourceSelectionResult",
    "ResourceSelectionStabilityError",
    "simulate_resource_selection",
]

from .uet_matter_space_characteristic import (
    CHARACTERISTIC_CONE_OPERATOR_MODE,
    CharacteristicConeStabilityError,
    characteristic_cone_contract,
    characteristic_cone_dt,
    characteristic_cone_speed,
    characteristic_cone_step,
)

__all__ += [
    "CHARACTERISTIC_CONE_OPERATOR_MODE",
    "CharacteristicConeStabilityError",
    "characteristic_cone_contract",
    "characteristic_cone_dt",
    "characteristic_cone_speed",
    "characteristic_cone_step",
]

from .resource_selection_thermal_bridge import (
    RESOURCE_THERMAL_BRIDGE_MODE,
    RESOURCE_THERMAL_BRIDGE_STATUS,
    ResourceThermalBridgeConfig,
    ResourceThermalSummary,
    ResourceThermalBridgeResult,
    summarize_resource_thermal_ledger,
    run_resource_selection_thermal_bridge,
)

__all__ += [
    "RESOURCE_THERMAL_BRIDGE_MODE",
    "RESOURCE_THERMAL_BRIDGE_STATUS",
    "ResourceThermalBridgeConfig",
    "ResourceThermalSummary",
    "ResourceThermalBridgeResult",
    "summarize_resource_thermal_ledger",
    "run_resource_selection_thermal_bridge",
]

from .uet_matter_space_observable import (
    MATTER_SPACE_OBSERVABLE_OPERATOR_MODE,
    matter_space_observable_contract,
    normalized_matter_space_observable,
)

__all__ += [
    "MATTER_SPACE_OBSERVABLE_OPERATOR_MODE",
    "matter_space_observable_contract",
    "normalized_matter_space_observable",
]
from .photon_observer_baseline import (
    PHOTON_OBSERVER_BASELINE_MODE,
    PhotonBaselineConfig,
    PhotonEmissionEvent,
    PhotonPropagationResult,
    PhotonDetectorRecord,
    photon_energy_momentum,
    propagate_photon,
    detect_photon,
    photon_observer_contract,
)

__all__ += [
    "PHOTON_OBSERVER_BASELINE_MODE",
    "PhotonBaselineConfig",
    "PhotonEmissionEvent",
    "PhotonPropagationResult",
    "PhotonDetectorRecord",
    "photon_energy_momentum",
    "propagate_photon",
    "detect_photon",
    "photon_observer_contract",
]
from .resource_selection_physical_cost_map import (
    PHYSICAL_COST_MAP_OPERATOR_MODE,
    PHYSICAL_COST_MAP_STATUS,
    PhysicalCostMapValidationError,
    PhysicalCostMapRecord,
    PhysicalCostMapResult,
    map_normalized_work_to_si,
)

__all__ += [
    "PHYSICAL_COST_MAP_OPERATOR_MODE",
    "PHYSICAL_COST_MAP_STATUS",
    "PhysicalCostMapValidationError",
    "PhysicalCostMapRecord",
    "PhysicalCostMapResult",
    "map_normalized_work_to_si",
]

from .uet_covariant_parent import (
    COVARIANT_PARENT_STATUS,
    CovariantParentConfig,
    CovariantParentState,
    CovariantParentResult,
    evaluate_conservative_parent,
    covariant_parent_contract,
)

__all__ += [
    "COVARIANT_PARENT_STATUS",
    "CovariantParentConfig",
    "CovariantParentState",
    "CovariantParentResult",
    "evaluate_conservative_parent",
    "covariant_parent_contract",
]

from .uet_coarse_graining import (
    COARSE_GRAINING_STATUS,
    SUPPORTED_C_LANES,
    CoarseGrainingRecord,
    CollectiveCoordinateState,
    CoarseGrainingConsistency,
    ScaleDependenceResult,
    CoarseGrainingOperator,
    coarse_grain,
    refine_coarse_graining,
    coarse_graining_consistency,
    scale_dependence_audit,
    coarse_graining_contract,
)

__all__ += [
    "COARSE_GRAINING_STATUS",
    "SUPPORTED_C_LANES",
    "CoarseGrainingRecord",
    "CollectiveCoordinateState",
    "CoarseGrainingConsistency",
    "ScaleDependenceResult",
    "CoarseGrainingOperator",
    "coarse_grain",
    "refine_coarse_graining",
    "coarse_graining_consistency",
    "scale_dependence_audit",
    "coarse_graining_contract",
]

from .uet_covariant_open_system import (
    OPEN_SYSTEM_STATUS,
    KMSCoefficientRecord,
    MemoryKernelRecord,
    NoiseKernelRecord,
    EntropyCurrentLedger,
    OpenSystemConfig,
    OpenSystemEvolutionResult,
    derive_retarded_kernel,
    derive_noise_kernel,
    entropy_current_divergence,
    open_system_evolution,
    open_system_contract,
)

__all__ += [
    "OPEN_SYSTEM_STATUS",
    "KMSCoefficientRecord",
    "MemoryKernelRecord",
    "NoiseKernelRecord",
    "EntropyCurrentLedger",
    "OpenSystemConfig",
    "OpenSystemEvolutionResult",
    "derive_retarded_kernel",
    "derive_noise_kernel",
    "entropy_current_divergence",
    "open_system_evolution",
    "open_system_contract",
]

from .uet_covariant_theory_spine import (
    THEORY_SPINE_OPERATOR_MODE,
    THEORY_SPINE_STATUS,
    TheorySpineConfig,
    Covariant3p1State,
    CovariantConstraintState,
    TheoryStepResult,
    characteristic_analysis,
    recommended_max_dt,
    theory_spine_step,
    theory_spine_contract,
)

__all__ += [
    "THEORY_SPINE_OPERATOR_MODE",
    "THEORY_SPINE_STATUS",
    "TheorySpineConfig",
    "Covariant3p1State",
    "CovariantConstraintState",
    "TheoryStepResult",
    "characteristic_analysis",
    "recommended_max_dt",
    "theory_spine_step",
    "theory_spine_contract",
]

from .uet_quantum_measurement import (
    QUANTUM_MEASUREMENT_STATUS,
    DensityOperator,
    QuantumChannel,
    QuantumInstrument,
    POVMRecord,
    MeasurementContext,
    QuantumOutcome,
    ObserverQuantumRecord,
    born_probabilities,
    apply_quantum_channel,
    conditional_state_update,
    sample_or_record_outcome,
    partial_trace_bipartite,
    expectation,
    quantum_measurement_contract,
)

__all__ += [
    "QUANTUM_MEASUREMENT_STATUS",
    "DensityOperator",
    "QuantumChannel",
    "QuantumInstrument",
    "POVMRecord",
    "MeasurementContext",
    "QuantumOutcome",
    "ObserverQuantumRecord",
    "born_probabilities",
    "apply_quantum_channel",
    "conditional_state_update",
    "sample_or_record_outcome",
    "partial_trace_bipartite",
    "expectation",
    "quantum_measurement_contract",
]

from .uet_quantum_interpretations import (
    INTERPRETATION_STATUS,
    AgentBeliefRecord,
    RelationalStateRecord,
    OperationalViewRecord,
    InterpretationComparison,
    operational_view,
    qbist_view,
    relational_view,
    compare_empirical_predictions,
    interpretation_contract,
)

__all__ += [
    "INTERPRETATION_STATUS",
    "AgentBeliefRecord",
    "RelationalStateRecord",
    "OperationalViewRecord",
    "InterpretationComparison",
    "operational_view",
    "qbist_view",
    "relational_view",
    "compare_empirical_predictions",
    "interpretation_contract",
]

from .uet_gr_correspondence import (
    GR_CORRESPONDENCE_STATUS,
    GRBenchmarkRecord,
    minkowski_null_control,
    flat_flrw_control,
    schwarzschild_exterior_null_control,
    newtonian_poisson_residual,
    gr_correspondence_contract,
)

__all__ += [
    "GR_CORRESPONDENCE_STATUS",
    "GRBenchmarkRecord",
    "minkowski_null_control",
    "flat_flrw_control",
    "schwarzschild_exterior_null_control",
    "newtonian_poisson_residual",
    "gr_correspondence_contract",
]

from .uet_curved_3p1_constraints import (
    ADM_CONSTRAINT_INTERFACE_STATUS,
    ADMGeometryState,
    ADMMatterProjection,
    ADMConstraintResult,
    evaluate_adm_constraints,
    minkowski_adm_control,
    flat_flrw_adm_control,
    adm_constraint_contract,
)

__all__ += [
    "ADM_CONSTRAINT_INTERFACE_STATUS",
    "ADMGeometryState",
    "ADMMatterProjection",
    "ADMConstraintResult",
    "evaluate_adm_constraints",
    "minkowski_adm_control",
    "flat_flrw_adm_control",
    "adm_constraint_contract",
]

from .uet_curved_3p1_geometry import (
    CURVED_3P1_GEOMETRY_OPERATOR_STATUS,
    SpatialGeometryResult,
    periodic_central_derivative,
    compute_periodic_spatial_geometry,
    compute_periodic_momentum_tensor_divergence,
    adm_geometry_from_periodic_grid,
    curved_3p1_geometry_operator_contract,
)

__all__ += [
    "CURVED_3P1_GEOMETRY_OPERATOR_STATUS",
    "SpatialGeometryResult",
    "periodic_central_derivative",
    "compute_periodic_spatial_geometry",
    "compute_periodic_momentum_tensor_divergence",
    "adm_geometry_from_periodic_grid",
    "curved_3p1_geometry_operator_contract",
]

from .uet_curved_3p1_adm_evolution import (
    ADM_EVOLUTION_OPERATOR_STATUS,
    ADMStressProjection,
    ADMEvolutionRHS,
    ADMPrincipalSymbolResult,
    compute_adm_evolution_rhs,
    fixed_gauge_adm_principal_symbol,
    adm_evolution_contract,
)

__all__ += [
    "ADM_EVOLUTION_OPERATOR_STATUS",
    "ADMStressProjection",
    "ADMEvolutionRHS",
    "ADMPrincipalSymbolResult",
    "compute_adm_evolution_rhs",
    "fixed_gauge_adm_principal_symbol",
    "adm_evolution_contract",
]

from .uet_curved_3p1_generalized_harmonic import (
    GH_PRINCIPAL_SYSTEM_STATUS,
    GHParameters,
    GHNonlinearParameters,
    GHPrincipalSymbolResult,
    GHLinearRHS,
    GHKinematics,
    GHNonlinearVacuumRHS,
    gh_principal_symbol,
    gh_characteristic_fields,
    reconstruct_gh_state,
    gh_reduction_constraint,
    gh_curl_constraint,
    gh_gauge_constraint,
    derive_gh_kinematics,
    reconstruct_metric_derivatives,
    lowered_christoffel_from_gh_state,
    gh_gauge_constraint_grid,
    gh_gamma0_damping_term,
    compute_linear_gh_reduction_damped_rhs,
    compute_nonlinear_vacuum_gh_rhs,
    generalized_harmonic_contract,
)

__all__ += [
    "GH_PRINCIPAL_SYSTEM_STATUS",
    "GHParameters",
    "GHNonlinearParameters",
    "GHPrincipalSymbolResult",
    "GHLinearRHS",
    "GHKinematics",
    "GHNonlinearVacuumRHS",
    "gh_principal_symbol",
    "gh_characteristic_fields",
    "reconstruct_gh_state",
    "gh_reduction_constraint",
    "gh_curl_constraint",
    "gh_gauge_constraint",
    "derive_gh_kinematics",
    "reconstruct_metric_derivatives",
    "lowered_christoffel_from_gh_state",
    "gh_gauge_constraint_grid",
    "gh_gamma0_damping_term",
    "compute_linear_gh_reduction_damped_rhs",
    "compute_nonlinear_vacuum_gh_rhs",
    "generalized_harmonic_contract",
]

from .uet_curved_3p1_gh_evolution import (
    GH_TIME_EVOLUTION_STATUS,
    GHEvolutionState,
    GHTimeIntegrationParameters,
    GHConstraintNorms,
    GHTimeEvolutionResult,
    gh_constraint_norms,
    gh_cfl_timestep,
    rk4_periodic_vacuum_gh_step,
    evolve_periodic_vacuum_gh,
    harmonic_gauge_wave_state,
    generalized_harmonic_time_evolution_contract,
)

__all__ += [
    "GH_TIME_EVOLUTION_STATUS",
    "GHEvolutionState",
    "GHTimeIntegrationParameters",
    "GHConstraintNorms",
    "GHTimeEvolutionResult",
    "gh_constraint_norms",
    "gh_cfl_timestep",
    "rk4_periodic_vacuum_gh_step",
    "evolve_periodic_vacuum_gh",
    "harmonic_gauge_wave_state",
    "generalized_harmonic_time_evolution_contract",
]
