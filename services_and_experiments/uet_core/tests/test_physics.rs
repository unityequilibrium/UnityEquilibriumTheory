use uet_core::parameters::UETParameters;
use uet_core::fields::Field;
use uet_core::dynamics::compute_omega;
use ndarray::ArrayD;

#[test]
fn test_omega_vacuum_state() {
    let params = UETParameters::default();
    // C = C0 everywhere (Vacuum)
    let shape = vec![10];
    let data = ArrayD::from_elem(shape, params.c0);
    let c = Field::new(data);

    // Ω should be 0 because V(C0) = 0 and ∇C0 = 0
    let omega = compute_omega(&c, None, 0.1, &params);
    assert!(omega.abs() < 1e-9, "Vacuum energy should be zero, got {}", omega);
}

#[test]
fn test_omega_perturbed_state() {
    let params = UETParameters::default();
    // C = C0 + 1.0
    let shape = vec![10];
    let data = ArrayD::from_elem(shape, params.c0 + 1.0);
    let c = Field::new(data);

    // V(C) > 0, Gradient = 0
    let omega = compute_omega(&c, None, 0.1, &params);
    assert!(omega > 0.0, "Perturbed state should have positive energy");
}

#[test]
fn test_gradient_energy() {
    let params = UETParameters::default();
    // Linear gradient: 0, 1, 2...
    let points = 10;
    let dx = 1.0;
    let data = ArrayD::from_shape_vec(vec![points], (0..points).map(|x| x as f64).collect()).unwrap();
    let c = Field::new(data);

    // Gradient is constant = 1.0
    // (κ/2) * |1|^2 * Volume
    // But calculate it via function
    let omega = compute_omega(&c, None, dx, &params);

    // We expect some positive value from Potential + Gradient
    assert!(omega > 0.0);
}
