use crate::parameters::UETParameters;
use ndarray::{Array1, Array2, ArrayView1};
use serde::{Deserialize, Serialize};

/// UET Master Equation - Complete 7-term functional
/// Ω[C,I,J] = ∫ d³x [
///     V(C)                          # A1: Energy Conservation
///   + (κ/2)|∇C|²                    # A3: Space-Memory Gradient
///   + β C·I                         # A2: Information-Energy Coupling
///   + γ_J (J_in - J_out)·C          # A4: Semi-open Exchange (In-Ex)
///   + W_N |∇Ω_local|               # A5: Natural Will
///   + β_U(Σ,R) · V_game(C)          # A8: Dynamic Game
///   + λ Σ_layers(C_i-C_j)²          # A10: Multi-layer Coherence
/// ]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UETMasterEquation {
    pub params: UETParameters,
}

impl UETMasterEquation {
    pub fn new(params: UETParameters) -> Self {
        Self { params }
    }

    /// A1: Potential V(C) = (α/2)(C-C0)² + (γ/4)(C-C0)⁴
    pub fn potential_V(&self, C: &Array1<f64>) -> Array1<f64> {
        let diff = C - self.params.c0;
        let alpha_term = (self.params.alpha / 2.0) * diff.mapv(|x| x * x);
        let gamma_term = (self.params.gamma / 4.0) * diff.mapv(|x| x * x * x * x);
        alpha_term + gamma_term
    }

    /// A3: Gradient term (κ/2)|∇C|²
    pub fn gradient_term(&self, C: &Array1<f64>, dx: f64) -> f64 {
        if C.len() < 2 {
            return 0.0;
        }
        let grad = self.gradient(C, dx);
        (self.params.kappa / 2.0) * grad.mapv(|x| x * x).sum()
    }

    /// A2: Information coupling βCI
    pub fn information_coupling(&self, C: &Array1<f64>, I: &Array1<f64>, dx: f64) -> f64 {
        self.params.beta * (C * I).sum() * dx
    }

    /// A4: Semi-open exchange γ_J (J_in - J_out)·C
    pub fn semi_open_exchange(
        &self,
        C: &Array1<f64>,
        J_in: &Array1<f64>,
        J_out: &Array1<f64>,
        dx: f64,
    ) -> f64 {
        let net_flux = J_in - J_out;
        self.params.gamma_j * (net_flux * C).sum() * dx
    }

    /// A5: Natural Will W_N |∇Ω_local|
    pub fn natural_will(&self, C: &Array1<f64>, dx: f64) -> f64 {
        if C.len() < 2 {
            return 0.0;
        }
        let grad = self.gradient(C, dx);
        self.params.w_n * grad.mapv(|x| x.abs()).sum() * dx
    }

    /// Calculate gradient of 1D array
    fn gradient(&self, C: &Array1<f64>, dx: f64) -> Array1<f64> {
        if C.len() < 2 {
            return Array1::zeros(C.len());
        }

        let mut grad = Array1::zeros(C.len());
        for i in 1..C.len() - 1 {
            grad[i] = (C[i + 1] - C[i - 1]) / (2.0 * dx);
        }
        grad[0] = (C[1] - C[0]) / dx;
        grad[C.len() - 1] = (C[C.len() - 1] - C[C.len() - 2]) / dx;
        grad
    }

    /// A8: Dynamic Game potential V_game = β_U × C²
    pub fn game_theory_potential(&self, C: &Array1<f64>, density: f64, scale: f64) -> Array1<f64> {
        let beta_U = self.strategic_boost(density, scale);
        beta_U * C.mapv(|x| x * x)
    }

    /// Strategic boost β_U for energy-competitive systems
    pub fn strategic_boost(&self, density: f64, scale: f64) -> f64 {
        const SIGMA_CRIT: f64 = 1.37e9; // M_sun/kpc²
        let density_ratio = density / SIGMA_CRIT;

        let beta_base = 1.5 * density_ratio;

        let payoff_gradient = if density_ratio > 1.0 {
            2.0 * (1.0 + density_ratio).log10()
        } else if density_ratio < 0.1 && density_ratio > 0.0 {
            1.5 * (0.1 / (density_ratio + 1e-9)).powf(0.25)
        } else {
            0.0
        };

        let mut beta_U = beta_base + payoff_gradient;

        if scale < 2.0 && scale > 0.0 {
            beta_U *= (2.0 / scale).powf(0.3);
        }

        beta_U.clamp(1.5, 15.0)
    }

    /// A10: Multi-layer coherence λ Σ_ij (C_i - C_j)²
    pub fn layer_coherence(&self, C_layers: &[Array1<f64>], dx: f64) -> f64 {
        if C_layers.len() < 2 {
            return 0.0;
        }

        let mut coherence = 0.0;
        for i in 0..C_layers.len() {
            for j in (i + 1)..C_layers.len() {
                let diff = &C_layers[i] - &C_layers[j];
                coherence += diff.mapv(|x| x * x).sum();
            }
        }

        self.params.lambda_coherence * coherence * dx
    }

    /// Complete Omega functional Ω[C,I,J]
    pub fn omega_functional(
        &self,
        C: &Array1<f64>,
        I: Option<&Array1<f64>>,
        J_in: Option<&Array1<f64>>,
        J_out: Option<&Array1<f64>>,
        C_layers: Option<&[Array1<f64>]>,
        density: f64,
        scale: f64,
        dx: f64,
    ) -> f64 {
        // A1: Potential
        let V = self.potential_V(C);
        let potential_integral = V.sum() * dx;

        // A3: Gradient
        let gradient_integral = self.gradient_term(C, dx);

        // A2: Information coupling
        let info_integral = if let Some(I_arr) = I {
            self.information_coupling(C, I_arr, dx)
        } else {
            0.0
        };

        // A4: Semi-open exchange
        let exchange_integral = if let (Some(J_in_arr), Some(J_out_arr)) = (J_in, J_out) {
            self.semi_open_exchange(C, J_in_arr, J_out_arr, dx)
        } else {
            0.0
        };

        // A5: Natural Will
        let will_integral = self.natural_will(C, dx);

        // A8: Dynamic Game
        let game_integral = if density > 0.0 {
            let V_game = self.game_theory_potential(C, density, scale);
            V_game.sum() * dx
        } else {
            0.0
        };

        // A10: Multi-layer coherence
        let coherence_integral = if let Some(layers) = C_layers {
            self.layer_coherence(layers, dx)
        } else {
            0.0
        };

        potential_integral
            + gradient_integral
            + info_integral
            + exchange_integral
            + will_integral
            + game_integral
            + coherence_integral
    }

    /// Value equation: 𝒱 = -ΔΩ
    pub fn calculate_value(&self, omega_prev: f64, omega_curr: f64) -> f64 {
        -(omega_curr - omega_prev)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_potential_V() {
        let params = UETParameters::default();
        let eq = UETMasterEquation::new(params);
        let C = Array1::linspace(0.0, 1.0, 10);
        let V = eq.potential_V(&C);
        assert!(V.len() == 10);
    }

    #[test]
    fn test_omega_functional() {
        let params = UETParameters::default();
        let eq = UETMasterEquation::new(params);
        let C = Array1::linspace(0.0, 1.0, 10);
        let I = Array1::ones(10) * 0.1;
        let J_in = Array1::ones(10) * 0.05;
        let J_out = Array1::ones(10) * 0.03;

        let omega =
            eq.omega_functional(&C, Some(&I), Some(&J_in), Some(&J_out), None, 0.0, 1.0, 0.1);
        assert!(omega >= 0.0);
    }
}
