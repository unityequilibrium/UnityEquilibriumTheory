use std::path::Path;
use sled::Db;
use thiserror::Error;

use crate::types::Block;

#[derive(Error, Debug)]
pub enum StorageError {
    #[error("Database error: {0}")]
    DbError(#[from] sled::Error),
    #[error("Serialization error: {0}")]
    SerializationError(#[from] bincode::Error),
    #[error("Block not found at height {0}")]
    BlockNotFound(u64),
    #[error("Invalid data format")]
    InvalidData,
}

pub type Result<T> = std::result::Result<T, StorageError>;

/// Handles persistent storage of blocks and chain metadata
#[derive(Clone)]
pub struct ChainStorage {
    db: Db,
}

impl ChainStorage {
    /// Open or create the database at the given path
    pub fn open<P: AsRef<Path>>(path: P) -> Result<Self> {
        let db = sled::open(path)?;
        Ok(Self { db })
    }

    /// Save a block to storage
    pub fn save_block(&self, block: &Block) -> Result<()> {
        let height_bytes = block.header.height.to_be_bytes();
        let block_bytes = bincode::serialize(block)?;

        // Key is prefix "b:" + height
        let mut key = b"b:".to_vec();
        key.extend_from_slice(&height_bytes);

        self.db.insert(key, block_bytes)?;

        // Also update the latest height
        self.save_latest_height(block.header.height)?;

        // Ensure written to disk
        self.db.flush()?;

        Ok(())
    }

    /// Retrieve a block by its height
    pub fn get_block(&self, height: u64) -> Result<Option<Block>> {
        let height_bytes = height.to_be_bytes();
        let mut key = b"b:".to_vec();
        key.extend_from_slice(&height_bytes);

        match self.db.get(&key)? {
            Some(bytes) => {
                let block: Block = bincode::deserialize(&bytes)?;
                Ok(Some(block))
            }
            None => Ok(None),
        }
    }

    /// Save the latest block height
    fn save_latest_height(&self, height: u64) -> Result<()> {
        let height_bytes = height.to_be_bytes();
        self.db.insert(b"meta:latest_height", height_bytes.to_vec())?;
        Ok(())
    }

    /// Get the latest block height
    pub fn get_latest_height(&self) -> Result<Option<u64>> {
        match self.db.get(b"meta:latest_height")? {
            Some(bytes) => {
                if bytes.len() != 8 {
                    return Err(StorageError::InvalidData);
                }
                let mut height_bytes = [0u8; 8];
                height_bytes.copy_from_slice(&bytes);
                Ok(Some(u64::from_be_bytes(height_bytes)))
            }
            None => Ok(None),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{BlockHeader, TaskFamily};
    use chrono::Utc;
    use tempfile::tempdir;
    use uet_security::{CryptoSuite, HashAlgorithm, SignatureAlgorithm};

    #[test]
    fn test_save_and_get_block() {
        let dir = tempdir().unwrap();
        let storage = ChainStorage::open(dir.path()).unwrap();

        let header = BlockHeader {
            height: 42,
            previous_block_hash_hex: "0000000".to_string(),
            proposer_node_id: "node-1".to_string(),
            tx_merkle_root_hex: "tx-root".to_string(),
            proof_root_hex: "proof-root".to_string(),
            state_root_hex: "state-root".to_string(),
            timestamp: Utc::now(),
            suite: CryptoSuite {
                schema_version: 1,
                sig_alg: SignatureAlgorithm::Dilithium3,
                hash_alg: HashAlgorithm::Sha3256,
                key_id: "node-1#k1".to_string(),
            },
            signature_hex: "signature".to_string(),
        };

        let block = Block {
            header,
            transactions: vec![],
            work_proofs: vec![],
        };

        // Save block
        storage.save_block(&block).unwrap();

        // Get block back
        let retrieved = storage.get_block(42).unwrap().unwrap();
        assert_eq!(retrieved.header.height, 42);
        assert_eq!(retrieved.header.proposer_node_id, "node-1");

        // Check latest height
        let latest = storage.get_latest_height().unwrap().unwrap();
        assert_eq!(latest, 42);
    }
}
