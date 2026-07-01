use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::time::{SystemTime, UNIX_EPOCH};

/// Anti-cheat controls for Uet-Cash mining
pub struct AntiCheatController {
    used_nonces: HashSet<UsedNonce>,
    epoch_start: u64,
    epoch_duration: u64,
}

#[derive(Debug, Clone, Hash, Eq, PartialEq, Serialize, Deserialize)]
pub struct UsedNonce {
    pub task_id: String,
    pub node_id: String,
    pub nonce: u64,
}

impl AntiCheatController {
    pub fn new(epoch_duration_seconds: u64) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        Self {
            used_nonces: HashSet::new(),
            epoch_start: now / epoch_duration_seconds * epoch_duration_seconds,
            epoch_duration: epoch_duration_seconds,
        }
    }

    /// Check if nonce has been used (replay protection)
    pub fn is_nonce_used(&self, task_id: &str, node_id: &str, nonce: u64) -> bool {
        let used_nonce = UsedNonce {
            task_id: task_id.to_string(),
            node_id: node_id.to_string(),
            nonce,
        };

        self.used_nonces.contains(&used_nonce)
    }

    /// Mark nonce as used
    pub fn mark_nonce_used(&mut self, task_id: &str, node_id: &str, nonce: u64) {
        let used_nonce = UsedNonce {
            task_id: task_id.to_string(),
            node_id: node_id.to_string(),
            nonce,
        };

        self.used_nonces.insert(used_nonce);
    }

    /// Check if we're in a new epoch and reset if needed
    pub fn check_epoch(&mut self) {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let current_epoch_start = now / self.epoch_duration * self.epoch_duration;

        if current_epoch_start != self.epoch_start {
            self.epoch_start = current_epoch_start;
            self.used_nonces.clear();
        }
    }

    /// Get current epoch start time
    pub fn epoch_start(&self) -> u64 {
        self.epoch_start
    }

    /// Get epoch duration
    pub fn epoch_duration(&self) -> u64 {
        self.epoch_duration
    }
}

/// Fraud proof for challenging invalid proofs
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FraudProof {
    pub block_hash: String,
    pub proof_index: usize,
    pub reason: FraudReason,
    pub challenger_id: String,
    pub timestamp: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FraudReason {
    InvalidDifficulty,
    InvalidSignature,
    ReplayAttack,
    StolenProof,
}

impl FraudProof {
    pub fn new(
        block_hash: String,
        proof_index: usize,
        reason: FraudReason,
        challenger_id: String,
    ) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        Self {
            block_hash,
            proof_index,
            reason,
            challenger_id,
            timestamp,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_replay_protection() {
        let mut controller = AntiCheatController::new(3600); // 1 hour epoch

        // First use should be allowed
        assert!(!controller.is_nonce_used("task1", "node1", 100));
        controller.mark_nonce_used("task1", "node1", 100);

        // Second use should be blocked
        assert!(controller.is_nonce_used("task1", "node1", 100));

        // Different nonce should be allowed
        assert!(!controller.is_nonce_used("task1", "node1", 101));

        // Different node should be allowed
        assert!(!controller.is_nonce_used("task1", "node2", 100));
    }

    #[test]
    fn test_epoch_reset() {
        let mut controller = AntiCheatController::new(1); // 1 second epoch for testing

        controller.mark_nonce_used("task1", "node1", 100);
        assert!(controller.is_nonce_used("task1", "node1", 100));

        // Wait for epoch to pass
        std::thread::sleep(std::time::Duration::from_millis(1100));
        controller.check_epoch();

        // After epoch reset, nonce should be available again
        assert!(!controller.is_nonce_used("task1", "node1", 100));
    }

    #[test]
    fn test_fraud_proof() {
        let fraud_proof = FraudProof::new(
            "block_hash".to_string(),
            0,
            FraudReason::InvalidDifficulty,
            "challenger".to_string(),
        );

        assert_eq!(fraud_proof.block_hash, "block_hash");
        assert_eq!(fraud_proof.proof_index, 0);
        assert!(matches!(fraud_proof.reason, FraudReason::InvalidDifficulty));
        assert_eq!(fraud_proof.challenger_id, "challenger");
    }
}
