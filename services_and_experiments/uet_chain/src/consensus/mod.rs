use std::sync::Arc;
use tokio::sync::RwLock;
use thiserror::Error;

use crate::types::Block;
use crate::state::{StateMachine, StateError};
use crate::storage::{ChainStorage, StorageError};

#[derive(Error, Debug)]
pub enum ConsensusError {
    #[error("State error: {0}")]
    StateError(#[from] StateError),
    #[error("Storage error: {0}")]
    StorageError(#[from] StorageError),
    #[error("Invalid block: {0}")]
    InvalidBlock(String),
}

pub type Result<T> = std::result::Result<T, ConsensusError>;

/// Handles rules for accepting blocks and processing transactions
pub struct ConsensusEngine {
    storage: Arc<ChainStorage>,
    state: Arc<RwLock<StateMachine>>,
}

impl ConsensusEngine {
    pub fn new(storage: Arc<ChainStorage>, state: Arc<RwLock<StateMachine>>) -> Self {
        Self { storage, state }
    }

    /// Validates a new block before accepting it
    pub async fn validate_block(&self, block: &Block) -> Result<()> {
        let latest_height = self.storage.get_latest_height()?.unwrap_or(0);

        // 1. Check height sequence
        if block.header.height != latest_height + 1 && latest_height != 0 {
            return Err(ConsensusError::InvalidBlock(format!(
                "Expected height {}, got {}",
                latest_height + 1,
                block.header.height
            )));
        }

        // 2. Check previous hash
        if latest_height > 0 {
            if let Some(prev_block) = self.storage.get_block(latest_height)? {
                let hash_alg = prev_block.header.suite.hash_alg.clone();
                let expected_prev_hash = crate::canonical_hash_hex(hash_alg, &prev_block.header)
                    .unwrap_or_default();

                if block.header.previous_block_hash_hex != expected_prev_hash {
                    return Err(ConsensusError::InvalidBlock("Previous block hash mismatch".to_string()));
                }
            }
        }

        // 3. Verify Merkle Roots
        let hash_alg = block.header.suite.hash_alg.clone();

        let computed_tx_root = crate::tx_hashes_hex(&block.transactions, hash_alg.clone())
            .map(|hashes| crate::merkle_root_hex(&hashes, hash_alg.clone()))
            .unwrap_or_default();

        if computed_tx_root != block.header.tx_merkle_root_hex {
            return Err(ConsensusError::InvalidBlock("Transaction Merkle root mismatch".to_string()));
        }

        let computed_proof_root = crate::proof_hashes_hex(&block.work_proofs, hash_alg.clone())
            .map(|hashes| crate::merkle_root_hex(&hashes, hash_alg.clone()))
            .unwrap_or_default();

        if computed_proof_root != block.header.proof_root_hex {
            return Err(ConsensusError::InvalidBlock("Proof Merkle root mismatch".to_string()));
        }

        // 4. Verify Signatures (In a real system, verify the proposer's Dilithium signature here)
        // This relies on uet_security verification logic

        Ok(())
    }

    /// Accepts a valid block, applying it to state and saving it to storage
    pub async fn process_block(&self, block: Block) -> Result<()> {
        self.validate_block(&block).await?;

        // Lock state for writing
        let state = self.state.write().await;

        // Apply to state machine (this will revert if invalid transaction is found)
        state.apply_block(&block)?;

        // Save to persistent storage
        self.storage.save_block(&block)?;

        Ok(())
    }
}