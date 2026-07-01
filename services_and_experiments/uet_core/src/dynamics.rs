use crate::fields::Field;
use crate::parameters::{UETParameters, ParameterDeriver};
use crate::calculator::UnityCalculator;
use ndarray::ArrayD;

// =============================================================================
// AXIOM 1: ENERGY CONSERVATION - POTENTIAL V(C)
// =============================================================================

pub fn potential_v(c: &Field, params: &UETParameters) -> Field {
    // V(C) = (α/2)(C-C0)² + (γ/4)(C-C0)⁴
    let diff = c.clone() - Field::new(ArrayD::from_elem(c.0.raw_dim(), params.c0));

    // (α/2) * diff^2
    let term1 = diff.0.mapv(|x| params.alpha / 2.0 * x.powi(2));
    // (γ/4) * diff^4
    let term2 = diff.0.mapv(|x| params.gamma / 4.0 * x.powi(4));

    Field::new(term1 + term2)
}

// =============================================================================
// AXIOM 3: GRADIENT TERM
// =============================================================================

pub fn gradient_term(c: &Field, dx: f64, params: &UETParameters) -> f64 {
    // (κ/2)|∇C|²
    let grad_sq = c.gradient_magnitude_squared(dx);
    let integral = grad_sq.integral(dx); // ∫ |∇C|² dx

    (params.kappa / 2.0) * integral
}

// =============================================================================
// MASTER EQUATION: OMEGA FUNCTIONAL
// =============================================================================

pub fn compute_omega(
    c: &Field,
    i: Option<&Field>,
    dx: f64,
    params: &UETParameters,
) -> f64 {
    // 1. Potential Energy V(C)
    let v_field = potential_v(c, params);
    let potential_integral = v_field.integral(dx);

    // 2. Gradient Term (A3)
    let grad_integral = gradient_term(c, dx, params);

    // 3. Information Coupling (A2)
    let info_integral = if let Some(info_field) = i {
        // β ∫ C·I dx
        // Element-wise product
        let product = c.0.clone() * info_field.0.clone(); // Array * Array
        let integral = Field::new(product).integral(dx);
        params.beta * integral
    } else {
        0.0
    };

    // Sum them up (Basic version with A1, A2, A3)
    // Add more axioms as needed (A4, A5, etc.)
    potential_integral + grad_integral + info_integral
}

/// Dynamic Master Equation calculation using Unity Scaling.
pub fn compute_omega_unity(
    c: &Field,
    i: Option<&Field>,
    dx: f64,
    calculator: &UnityCalculator,
) -> f64 {
    let params = calculator.derive();
    compute_omega(c, i, dx, &params)
}
