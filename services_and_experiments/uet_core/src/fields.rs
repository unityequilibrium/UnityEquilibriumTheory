use ndarray::{ArrayD, Axis, IxDyn};
use std::ops::{Add, Mul, Sub};

#[derive(Debug, Clone)]
pub struct Field(pub ArrayD<f64>);

impl Field {
    /// Create a new field from an array
    pub fn new(data: ArrayD<f64>) -> Self {
        Self(data)
    }

    /// Compute the integral of the field
    pub fn integral(&self, dx: f64) -> f64 {
        let sum: f64 = self.0.sum();
        let ndim = self.0.ndim() as i32;
        // dx^ndim
        sum * dx.powi(ndim)
    }

    /// Compute Gradient (Finite Difference)
    /// Returns vector of fields [dF/dx, dF/dy, ...]
    pub fn gradient(&self, dx: f64) -> Vec<Field> {
        let ndim = self.0.ndim();
        let mut grads = Vec::with_capacity(ndim);

        for axis in 0..ndim {
            let grad_data = compute_gradient_axis(&self.0, axis, dx);
            grads.push(Field(grad_data));
        }
        grads
    }

    /// Compute Laplacian (Finite Difference)
    /// ∇²F = d²F/dx² + d²F/dy² + ...
    pub fn laplacian(&self, dx: f64) -> Field {
        let ndim = self.0.ndim();
        let mut laplacian = ArrayD::zeros(self.0.raw_dim());

        for axis in 0..ndim {
            let d2 = compute_second_derivative(&self.0, axis, dx);
            laplacian = laplacian + d2;
        }
        Field(laplacian)
    }

    /// Compute squared magnitude of gradient |∇C|²
    pub fn gradient_magnitude_squared(&self, dx: f64) -> Field {
        let grads = self.gradient(dx);
        let mut sum_sq = ArrayD::zeros(self.0.raw_dim());

        for g in grads {
            sum_sq = sum_sq + (g.0.mapv(|x| x.powi(2)));
        }
        Field(sum_sq)
    }
}

// Helper: Finite difference gradient along axis
fn compute_gradient_axis(data: &ArrayD<f64>, axis: usize, dx: f64) -> ArrayD<f64> {
    let mut grad = ArrayD::zeros(data.raw_dim());
    let shape = data.shape();
    let axis_len = shape[axis];

    if axis_len < 2 {
        return grad;
    }

    // Interior points: (f(x+h) - f(x-h)) / 2h
    // Boundary points: Forward/Backward difference

    // Note: This is an unoptimized implementation.
    // For production, we should slice operations.
    // Given the deadline, we iterate.

    // Create Zip of indices? slice?
    // ndarray slicing is tricky for dynamic dims.
    // Simplified Loop:
    for (idx, val) in data.indexed_iter() {
        // Need to construct "prev" and "next" indices
        // ndarray::Index is usually [usize, usize...]

        // Skip for now, implement 1D/2D specific optimizations later if needed.
        // Or strictly use slicing.
    }

    // Better Approach: Use slicing with ndarray
    // grad[1..-1] = (data[2..] - data[0..-2]) / (2*dx)

    let ax = Axis(axis);
    let n = data.len_of(ax);

    if n < 2 { return grad; }

    // Central difference
    let s_next = data.slice_axis(ax, ndarray::Slice::from(2..n));
    let s_prev = data.slice_axis(ax, ndarray::Slice::from(0..n-2));
    let mut s_mid = grad.slice_axis_mut(ax, ndarray::Slice::from(1..n-1));

    // Assign: (next - prev) / 2dx
    // ndarray supports arithmetic on views
    // We need to match shapes.
    // s_next and s_prev have shape (n-2) on axis. s_mid has shape (n-2).

    // Use `azip!` or `assign`
    // s_mid.assign(&((&s_next - &s_prev) / (2.0 * dx))); -> This consumes views? No.
    let diff = &s_next - &s_prev;
    s_mid.assign(&(diff / (2.0 * dx)));

    // Boundaries
    // forward at 0: (f(1) - f(0)) / dx
    {
        let mut g0 = grad.slice_axis_mut(ax, ndarray::Slice::from(0..1));
        let d1 = data.slice_axis(ax, ndarray::Slice::from(1..2));
        let d0 = data.slice_axis(ax, ndarray::Slice::from(0..1));
        g0.assign(&((&d1 - &d0) / dx));
    }

    // backward at -1: (f(n-1) - f(n-2)) / dx
    {
        let mut g_end = grad.slice_axis_mut(ax, ndarray::Slice::from(n-1..n));
        let d_last = data.slice_axis(ax, ndarray::Slice::from(n-1..n));
        let d_prev = data.slice_axis(ax, ndarray::Slice::from(n-2..n-1));
        g_end.assign(&((&d_last - &d_prev) / dx));
    }

    grad
}

fn compute_second_derivative(data: &ArrayD<f64>, axis: usize, dx: f64) -> ArrayD<f64> {
    let mut d2 = ArrayD::zeros(data.raw_dim());
    let ax = Axis(axis);
    let n = data.len_of(ax);

    if n < 3 { return d2; }

    // Central: (f(x+h) - 2f(x) + f(x-h)) / dx^2
    let s_next = data.slice_axis(ax, ndarray::Slice::from(2..n));
    let s_curr = data.slice_axis(ax, ndarray::Slice::from(1..n-1));
    let s_prev = data.slice_axis(ax, ndarray::Slice::from(0..n-2));
    let mut s_mid = d2.slice_axis_mut(ax, ndarray::Slice::from(1..n-1));

    let term = &s_next - &(2.0 * &s_curr) + &s_prev;
    s_mid.assign(&(term / dx.powi(2)));

    // Boundaries: Copy nearest neighbor (Neumann) or zero?
    // Python code uses: laplacian[0] = laplacian[1]
    {
        let l1 = d2.slice_axis(ax, ndarray::Slice::from(1..2)).to_owned();
        let mut l0 = d2.slice_axis_mut(ax, ndarray::Slice::from(0..1));
        l0.assign(&l1);

        let l_n2 = d2.slice_axis(ax, ndarray::Slice::from(n-2..n-1)).to_owned();
        let mut l_end = d2.slice_axis_mut(ax, ndarray::Slice::from(n-1..n));
        l_end.assign(&l_n2);
    }

    d2
}

// arithmetic ops for Field
impl Add for Field {
    type Output = Self;
    fn add(self, other: Self) -> Self { Self(self.0 + other.0) }
}
impl Sub for Field {
    type Output = Self;
    fn sub(self, other: Self) -> Self { Self(self.0 - other.0) }
}
impl Mul<f64> for Field {
    type Output = Self;
    fn mul(self, scalar: f64) -> Self { Self(self.0 * scalar) }
}
