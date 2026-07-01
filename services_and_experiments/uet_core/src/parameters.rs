use serde::{Deserialize, Serialize};

// =============================================================================
// FUNDAMENTAL CONSTANTS (CODATA 2018 / SI Exact)
// =============================================================================

pub const HBAR: f64 = 1.054571817e-34;  // Planck constant [J·s]
pub const C: f64 = 299792458.0;         // Speed of light [m/s]
pub const G: f64 = 6.67430e-11;         // Gravitational constant [m³/kg/s²]
pub const K_B: f64 = 1.380649e-23;      // Boltzmann constant [J/K]
pub const ALPHA_EM: f64 = 1.0 / 137.035999; // Fine structure constant
pub const M_SUN: f64 = 1.98847e30;      // Solar Mass (kg) [IAU 2015]

// Derived
pub const L_PLANCK: f64 = 1.616255e-35; // approx sqrt(hbar*G/c^3)

// =============================================================================
// UET PARAMETERS STRUCT
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UETParameters {
    pub kappa: f64,             // Gradient penalty (A3)
    pub beta: f64,              // Coupling constant (A2)
    pub alpha: f64,             // Equilibrium stiffness (A1)
    pub gamma: f64,             // Nonlinear stability (A1)
    pub c0: f64,                // Vacuum Expectation Value (A1)
    pub gamma_j: f64,           // Exchange rate (A4)
    pub w_n: f64,               // Natural Will (A5)
    pub lambda_coherence: f64,  // Layer coherence (A10)

    // Astrophysical (A7)
    pub rho_unity: f64,         // Pivot density
    pub ratio_0: f64,           // Halo ratio pivot
    pub gamma_uet: f64,         // Thermodynamic scaling index

    // Context
    pub temperature: f64,
    pub scale: String,          // e.g. "1e-15 m"
    pub origin: String,
}

impl Default for UETParameters {
    fn default() -> Self {
        Self {
            kappa: 0.1,
            beta: 0.1,
            alpha: 1.0,
            gamma: 0.025,
            c0: 1.0,
            gamma_j: 0.1,
            w_n: 0.05,
            lambda_coherence: 0.01,
            rho_unity: 5e7,
            ratio_0: 8.5,
            gamma_uet: 0.48,
            temperature: 293.15,
            scale: "general".to_string(),
            origin: "Fallback/Default".to_string(),
        }
    }
}

impl UETParameters {
    pub fn new(kappa: f64, beta: f64, scale: &str, origin: &str) -> Self {
        let mut p = Self::default();
        p.kappa = kappa;
        p.beta = beta;
        p.scale = scale.to_string();
        p.origin = origin.to_string();
        p
    }
}

/// Trait for entities that can derive UET parameters from their state.
pub trait ParameterDeriver {
    fn derive(&self) -> UETParameters;
}

// =============================================================================
// LEGACY PARAMETER REGISTRY (For Backward Compatibility)
// =============================================================================

pub fn get_params_legacy(scale_name: &str) -> Result<UETParameters, String> {
    let scale = match scale_name {
        "0.1" | "0.15" | "0.26" | "0.31" => "astrophysical",
        "0.2" | "0.9" | "0.12" | "0.19" => "planck",
        "0.3" | "0.4" | "0.6" | "0.7" | "0.8" | "0.11" | "0.13" | "0.14" | "0.17" | "0.18" | "0.20" => "electroweak",
        "0.5" | "0.16" => "nuclear",
        "0.10" | "0.21" | "0.22" | "0.24" | "0.25" | "0.27" | "0.28" | "0.29" | "0.30" => "macroscopic",
        s => s,
    };

    match scale {
        "planck" => Ok(UETParameters::new(0.5, 1.0, "planck", "Legacy Bekenstein Bound")),
        "electroweak" => Ok(UETParameters::new(0.5, 1.0, "electroweak", "Legacy Natural O(1)")),
        "nuclear" => Ok(UETParameters::new(0.57, 1.0, "nuclear", "Legacy QCD Calibration")),
        "astrophysical" => Ok(UETParameters::new(0.1, 0.05, "astrophysical", "Legacy SPARC Calibration")),
        "macroscopic" => Ok(UETParameters::new(0.1, 0.5, "macroscopic", "Legacy Fluid Calibration")),
        _ => Err(format!("Unknown scale: {}", scale)),
    }
}
