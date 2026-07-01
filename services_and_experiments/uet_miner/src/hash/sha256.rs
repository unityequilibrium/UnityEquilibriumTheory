//! SHA256 double-hash (SHA256d) implementation for Bitcoin.
//!
//! Bitcoin uses double SHA256 (SHA256(SHA256(data))) for:
//! - Block header hashing
//! - Merkle tree computation
//! - Coinbase transaction hashing

use sha2::{Sha256, Digest};

/// Compute double SHA256 hash (Bitcoin standard).
///
/// # Arguments
/// * `data` - Raw bytes to hash
///
/// # Returns
/// 32-byte hash result
pub fn sha256d(data: &[u8]) -> [u8; 32] {
    let first_hash = Sha256::digest(data);
    let second_hash = Sha256::digest(&first_hash);

    let mut result = [0u8; 32];
    result.copy_from_slice(&second_hash);
    result
}

/// Reverse bytes in a 32-byte array (for endianness conversion).
///
/// Used for byte-swapping previous hash and merkle root in block header.
pub fn reverse_bytes_32(input: &[u8; 32]) -> [u8; 32] {
    let mut result = *input;
    result.reverse();
    result
}

/// Decode hex string to bytes.
pub fn hex_to_bytes(hex: &str) -> Vec<u8> {
    hex::decode(hex).unwrap_or_default()
}

/// Encode bytes to hex string.
pub fn bytes_to_hex(bytes: &[u8]) -> String {
    hex::encode(bytes)
}

/// Reverse bytes in a hex string.
///
/// Example: "aabbccdd" -> "ddccbbaa"
pub fn reverse_hex(hex: &str) -> String {
    let bytes = hex_to_bytes(hex);
    let reversed: Vec<u8> = bytes.into_iter().rev().collect();
    bytes_to_hex(&reversed)
}

/// Check if hash meets difficulty target.
///
/// Hash is interpreted as little-endian integer and compared.
///
/// # Arguments
/// * `hash` - 32-byte hash
/// * `target` - Target value (hash must be <= target)
pub fn hash_meets_target(hash: &[u8; 32], target: u128) -> bool {
    // Compare first 16 bytes (most significant in little-endian)
    // This is a simplified check for pool difficulty
    let hash_val = u128::from_le_bytes(hash[0..16].try_into().unwrap());
    hash_val <= target
}

/// Convert pool difficulty to target value.
///
/// Target = (0xFFFF << 208) / difficulty
/// Simplified for pool shares (not full 256-bit precision).
pub fn difficulty_to_target(difficulty: f64) -> u128 {
    if difficulty <= 0.0 {
        return u128::MAX;
    }

    // Simplified target for pool shares
    // Full precision would require 256-bit arithmetic
    let base_target: f64 = 0xFFFF as f64 * (2.0_f64.powi(48));
    (base_target / difficulty) as u128
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sha256d() {
        let data = b"hello bitcoin";
        let hash = sha256d(data);
        assert_eq!(hash.len(), 32);

        // Verify deterministic
        let hash2 = sha256d(data);
        assert_eq!(hash, hash2);
    }

    #[test]
    fn test_reverse_hex() {
        assert_eq!(reverse_hex("aabbccdd"), "ddccbbaa");
        assert_eq!(reverse_hex("0102030405060708"), "0807060504030201");
    }

    #[test]
    fn test_difficulty_to_target() {
        let target = difficulty_to_target(1.0);
        assert!(target > 0);

        // Higher difficulty = lower target
        let target_high = difficulty_to_target(10.0);
        assert!(target_high < target);
    }
}
