use crate::parameters::{UETParameters, K_B, ParameterDeriver};
use serde::{Deserialize, Serialize};

/// Core engine for the Unity Equilibrium Theory.
/// Derives physical parameters (Kappa, Beta) from first principles:
/// 1. Beta = k_B * T * ln(2) (Landauer Principle)
/// 2. Kappa = Beta / InfoDensity
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnityCalculator {
    pub scale: f64,             // Characteristic length scale (m)
    pub temperature: f64,       // System temperature (K)
    pub info_density: f64,      // Information density (bits/m^3)
}

impl ParameterDeriver for UnityCalculator {
    fn derive(&self) -> UETParameters {
        self.derive_parameters()
    }
}

impl UnityCalculator {
    pub fn new(scale: f64, temperature: f64, info_density: f64) -> Self {
        Self {
            scale,
            temperature,
            info_density,
        }
    }

    /// Derives UETParameters from the current state.
    /// Implements the universal scaling laws and Landauer coupling.
    pub fn derive_parameters(&self) -> UETParameters {
        let ln2 = 2.0f64.ln();

        // 1. Beta derivation (Energy per bit)
        let beta = K_B * self.temperature * ln2;

        // 2. Kappa derivation (Information Inertia)
        // If info_density is 0, we fallback to a safe small value to avoid NaN
        let safe_density = if self.info_density > 0.0 { self.info_density } else { 1e-10 };
        let mut kappa = beta / safe_density;

        // Apply Planck Boundary (The Universe's Floor)
        // From 0.23_Unity_Scale_Link: The minimum valid information tension in the universe is 0.5
        if kappa < 0.5 {
            kappa = 0.5;
        }

        // 3. Construct Parameters with Context
        let mut params = UETParameters::default();
        params.kappa = kappa;
        params.beta = beta;
        params.temperature = self.temperature;
        params.scale = format!("{:.2e}m", self.scale);
        params.origin = "Unity First-Principles (Landauer)".to_string();

        params
    }

    /// Calculate the Unity-Scaling factor for a transition between two scales.
    pub fn get_scaling_ratio(scale_from: f64, scale_to: f64) -> f64 {
        // Based on T ∝ scale^(-2/3) and Rho ∝ scale^(-3)
        let temp_ratio = (scale_to / scale_from).powf(-2.0 / 3.0);
        let density_ratio = (scale_from / scale_to).powf(3.0);
        temp_ratio * density_ratio
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_landauer_at_room_temp() {
        // At 300K, Beta should be ~0.0179 eV
        let calc = UnityCalculator::new(0.001, 300.0, 1e18);
        let params = calc.derive_parameters();

        let beta_ev = params.beta / 1.602176634e-19;
        assert!((beta_ev - 0.0179).abs() < 0.001);
    }

    #[test]
    fn test_planck_boundary() {
        // Scenario with extreme information density near a black hole singularity
        // Density is massive, which would naturally drive kappa towards 0.
        let extrem_density = 1e40;
        let calc = UnityCalculator::new(1e-35, 300.0, extrem_density);
        let params = calc.derive_parameters();

        // The Planck boundary safety must arrest the fall precisely at 0.5
        assert_eq!(params.kappa, 0.5, "Planck boundary minimum of 0.5 not enforced!");
    }
}
