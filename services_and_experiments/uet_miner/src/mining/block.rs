//! Bitcoin block header construction for mining.
//!
//! Block Header Structure (80 bytes):
//! - Version: 4 bytes (little-endian)
//! - Previous Hash: 32 bytes (byte-swapped)
//! - Merkle Root: 32 bytes (byte-swapped)
//! - Timestamp: 4 bytes (little-endian)
//! - Bits (difficulty): 4 bytes (little-endian)
//! - Nonce: 4 bytes (little-endian)

use crate::hash::sha256::{sha256d, hex_to_bytes, reverse_hex};

/// Represents a mining job from the pool.
#[derive(Debug, Clone)]
pub struct MiningJob {
    pub job_id: String,
    pub prev_hash: String,
    pub coinbase1: String,
    pub coinbase2: String,
    pub merkle_branches: Vec<String>,
    pub version: String,
    pub nbits: String,
    pub ntime: String,
    pub clean_jobs: bool,
}

/// Build coinbase transaction from parts.
///
/// Coinbase = coinbase1 + extranonce1 + extranonce2 + coinbase2
pub fn build_coinbase(
    coinbase1: &str,
    coinbase2: &str,
    extranonce1: &str,
    extranonce2: &str,
) -> Vec<u8> {
    let coinbase_hex = format!("{}{}{}{}", coinbase1, extranonce1, extranonce2, coinbase2);
    hex_to_bytes(&coinbase_hex)
}

/// Calculate merkle root from coinbase hash and merkle branches.
pub fn calculate_merkle_root(coinbase: &[u8], merkle_branches: &[String]) -> [u8; 32] {
    let mut merkle = sha256d(coinbase);

    for branch in merkle_branches {
        let branch_bytes = hex_to_bytes(branch);

        // Concatenate merkle + branch and hash
        let mut combined = Vec::with_capacity(64);
        combined.extend_from_slice(&merkle);
        combined.extend_from_slice(&branch_bytes);

        merkle = sha256d(&combined);
    }

    merkle
}

/// Build 80-byte block header.
///
/// # Arguments
/// * `version` - Block version (hex, 8 chars)
/// * `prev_hash` - Previous block hash (hex, 64 chars)
/// * `merkle_root` - Merkle root (32 bytes)
/// * `ntime` - Timestamp (hex, 8 chars)
/// * `nbits` - Difficulty bits (hex, 8 chars)
/// * `nonce` - Nonce value
///
/// # Returns
/// 80-byte block header
pub fn build_block_header(
    version: &str,
    prev_hash: &str,
    merkle_root: &[u8; 32],
    ntime: &str,
    nbits: &str,
    nonce: u32,
) -> [u8; 80] {
    let mut header = [0u8; 80];

    // Version: little-endian
    let version_bytes = hex_to_bytes(&reverse_hex(version));
    header[0..4].copy_from_slice(&version_bytes[0..4]);

    // Previous hash: byte-swapped
    let prev_hash_bytes = hex_to_bytes(&reverse_hex(prev_hash));
    header[4..36].copy_from_slice(&prev_hash_bytes);

    // Merkle root: byte-swapped
    let reversed_merkle: Vec<u8> = merkle_root.iter().rev().copied().collect();
    header[36..68].copy_from_slice(&reversed_merkle);

    // nTime: little-endian
    let ntime_bytes = hex_to_bytes(&reverse_hex(ntime));
    header[68..72].copy_from_slice(&ntime_bytes[0..4]);

    // nBits: little-endian
    let nbits_bytes = hex_to_bytes(&reverse_hex(nbits));
    header[72..76].copy_from_slice(&nbits_bytes[0..4]);

    // Nonce: little-endian
    header[76..80].copy_from_slice(&nonce.to_le_bytes());

    header
}

/// Hash block header and check if it meets target.
pub fn mine_single_nonce(header_base: &[u8; 76], nonce: u32, target: u128) -> Option<[u8; 32]> {
    let mut header = [0u8; 80];
    header[0..76].copy_from_slice(header_base);
    header[76..80].copy_from_slice(&nonce.to_le_bytes());

    let hash = sha256d(&header);

    // Check if hash meets target (simplified)
    let hash_val = u128::from_le_bytes(hash[0..16].try_into().unwrap());
    if hash_val <= target {
        Some(hash)
    } else {
        None
    }
}

/// Format nonce for Stratum submission.
///
/// Returns 8-character hex string (big-endian format).
pub fn format_nonce_for_submit(nonce: u32) -> String {
    format!("{:08x}", nonce.swap_bytes())
}

/// Format extranonce2 for submission.
pub fn format_extranonce2(value: u32, size: usize) -> String {
    format!("{:0width$x}", value, width = size * 2)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_build_coinbase() {
        let cb = build_coinbase("01000000", "ffffffff", "08000001", "00000000");
        assert!(!cb.is_empty());
    }

    #[test]
    fn test_format_nonce() {
        let nonce = 0x12345678u32;
        let formatted = format_nonce_for_submit(nonce);
        assert_eq!(formatted.len(), 8);
    }

    #[test]
    fn test_format_extranonce2() {
        let en2 = format_extranonce2(0, 4);
        assert_eq!(en2, "00000000");

        let en2 = format_extranonce2(255, 4);
        assert_eq!(en2, "000000ff");
    }
}
