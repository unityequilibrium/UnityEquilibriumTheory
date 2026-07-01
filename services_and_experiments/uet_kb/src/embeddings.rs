use sha3::{Digest, Sha3_256};

/// Lightweight deterministic embedding generator.
/// Uses SHA3 hashing to produce a fixed-dimension vector from text.
/// This is NOT a learned semantic embedding — it's a deterministic hash-based
/// projection suitable for exact-match retrieval and deduplication.
/// For real semantic search, integrate with an external embedding API (OpenAI, Cohere, etc.)
pub fn hash_embed(text: &str, dim: usize) -> Vec<f64> {
    let normalized = text.to_lowercase().trim().to_string();
    let mut result = Vec::with_capacity(dim);

    // Generate enough hash bytes to fill the vector
    let chunks_needed = (dim * 8 + 31) / 32; // Each SHA3-256 gives 32 bytes
    let mut all_bytes = Vec::new();

    for i in 0..chunks_needed {
        let input = format!("{}:{}", i, normalized);
        let hash = Sha3_256::digest(input.as_bytes());
        all_bytes.extend_from_slice(&hash);
    }

    // Convert bytes to f64 in [-1, 1] range
    for i in 0..dim {
        let offset = i * 8;
        if offset + 8 <= all_bytes.len() {
            let mut bytes = [0u8; 8];
            bytes.copy_from_slice(&all_bytes[offset..offset + 8]);
            let raw = u64::from_le_bytes(bytes);
            // Map to [-1, 1]
            let val = (raw as f64 / u64::MAX as f64) * 2.0 - 1.0;
            result.push(val);
        } else {
            result.push(0.0);
        }
    }

    // L2-normalize the vector
    let norm: f64 = result.iter().map(|x| x * x).sum::<f64>().sqrt();
    if norm > 0.0 {
        for v in result.iter_mut() {
            *v /= norm;
        }
    }

    result
}

/// Generate a physics-informed embedding from UET equation parameters.
/// Encodes known physical quantities into a 20-dimensional vector.
pub fn physics_embed(params: &PhysicsParams) -> Vec<f64> {
    let mut vec = vec![0.0; 20];
    vec[0] = params.energy.unwrap_or(0.0);
    vec[1] = params.information.unwrap_or(0.0);
    vec[2] = params.gamma.unwrap_or(0.0);
    vec[3] = params.temperature.unwrap_or(0.0);
    vec[4] = params.entropy.unwrap_or(0.0);
    vec[5] = params.mass.unwrap_or(0.0);
    vec[6] = params.velocity.unwrap_or(0.0);
    vec[7] = params.frequency.unwrap_or(0.0);
    vec[8] = params.wavelength.unwrap_or(0.0);
    vec[9] = params.coupling_constant.unwrap_or(0.0);
    // Slots 10-19 reserved for future UET parameters
    vec
}

#[derive(Debug, Default)]
pub struct PhysicsParams {
    pub energy: Option<f64>,
    pub information: Option<f64>,
    pub gamma: Option<f64>,
    pub temperature: Option<f64>,
    pub entropy: Option<f64>,
    pub mass: Option<f64>,
    pub velocity: Option<f64>,
    pub frequency: Option<f64>,
    pub wavelength: Option<f64>,
    pub coupling_constant: Option<f64>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hash_embed_deterministic() {
        let v1 = hash_embed("hello world", 1024);
        let v2 = hash_embed("hello world", 1024);
        assert_eq!(v1, v2);
        assert_eq!(v1.len(), 1024);
    }

    #[test]
    fn test_hash_embed_different_texts() {
        let v1 = hash_embed("UET equilibrium equation", 1024);
        let v2 = hash_embed("quantum gravity theory", 1024);
        assert_ne!(v1, v2);
    }

    #[test]
    fn test_hash_embed_normalized() {
        let v = hash_embed("test normalization", 1024);
        let norm: f64 = v.iter().map(|x| x * x).sum::<f64>().sqrt();
        assert!((norm - 1.0).abs() < 1e-10);
    }

    #[test]
    fn test_physics_embed() {
        let params = PhysicsParams {
            energy: Some(1.5),
            gamma: Some(0.8),
            ..Default::default()
        };
        let v = physics_embed(&params);
        assert_eq!(v.len(), 20);
        assert_eq!(v[0], 1.5);
        assert_eq!(v[2], 0.8);
        assert_eq!(v[3], 0.0);
    }
}
