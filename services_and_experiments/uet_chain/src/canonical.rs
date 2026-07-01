use serde::Serialize;
use thiserror::Error;
use uet_security::{hashing::digest_hex, HashAlgorithm};

#[derive(Debug, Error)]
pub enum CanonicalError {
    #[error("serialization error: {0}")]
    Serialization(String),
}

pub fn canonical_json<T: Serialize>(value: &T) -> Result<String, CanonicalError> {
    serde_json::to_string(value).map_err(|e| CanonicalError::Serialization(e.to_string()))
}

pub fn canonical_hash_hex<T: Serialize>(
    alg: HashAlgorithm,
    value: &T,
) -> Result<String, CanonicalError> {
    let json = canonical_json(value)?;
    Ok(digest_hex(alg, json.as_bytes()))
}

pub fn merkle_root_hex(hashes_hex: &[String], alg: HashAlgorithm) -> String {
    if hashes_hex.is_empty() {
        return digest_hex(alg, b"");
    }

    let mut layer = hashes_hex.to_vec();

    while layer.len() > 1 {
        let mut next = Vec::with_capacity((layer.len() + 1) / 2);
        for pair in layer.chunks(2) {
            let left = &pair[0];
            let right = pair.get(1).unwrap_or(left);
            let mut cat = String::with_capacity(left.len() + right.len());
            cat.push_str(left);
            cat.push_str(right);
            next.push(digest_hex(alg, cat.as_bytes()));
        }
        layer = next;
    }

    layer[0].clone()
}
