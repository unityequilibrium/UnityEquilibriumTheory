use std::collections::HashMap;
use sled::Db;
use thiserror::Error;

use crate::types::{Block, Transaction, TransactionType};

#[derive(Error, Debug)]
pub enum StateError {
    #[error("Database error: {0}")]
    DbError(#[from] sled::Error),
    #[error("Serialization error: {0}")]
    SerializationError(#[from] bincode::Error),
    #[error("Insufficient funds for account {0}")]
    InsufficientFunds(String),
    #[error("Invalid transaction signature")]
    InvalidSignature,
}

pub type Result<T> = std::result::Result<T, StateError>;

/// Represents the global state of user balances
#[derive(Clone)]
pub struct StateMachine {
    db: Db,
}

impl StateMachine {
    pub fn new(db: Db) -> Self {
        Self { db }
    }

    /// Retrieve the balance for a specific address
    pub fn get_balance(&self, address: &str) -> Result<u64> {
        let key = format!("balance:{}", address);
        match self.db.get(key.as_bytes())? {
            Some(bytes) => {
                let mut amount_bytes = [0u8; 8];
                amount_bytes.copy_from_slice(&bytes);
                Ok(u64::from_be_bytes(amount_bytes))
            }
            None => Ok(0), // Default balance is 0
        }
    }

    /// Set the balance for a specific address
    fn set_balance(&self, address: &str, amount: u64) -> Result<()> {
        let key = format!("balance:{}", address);
        self.db.insert(key.as_bytes(), amount.to_be_bytes().to_vec())?;
        Ok(())
    }

    /// Apply a single transaction to the state
    pub fn apply_transaction(&self, tx: &Transaction) -> Result<()> {
        // Parse the payload (assuming a simple format for now)
        // In reality, this would use a proper serialization format like JSON/bincode
        let parsed_payload: HashMap<String, String> = serde_json::from_str(&tx.payload_json)
            .unwrap_or_default();

        match tx.tx_type {
            TransactionType::ComputeReward => {
                // Miner earns reward
                if let Some(to_address) = parsed_payload.get("miner_address") {
                    let reward: u64 = parsed_payload.get("reward").and_then(|v| v.parse().ok()).unwrap_or(0);
                    let current = self.get_balance(to_address)?;
                    self.set_balance(to_address, current + reward)?;
                }
            }
            TransactionType::Transfer => {
                if let (Some(from_address), Some(to_address), Some(amount_str)) = (
                    parsed_payload.get("from"),
                    parsed_payload.get("to"),
                    parsed_payload.get("amount"),
                ) {
                    let amount: u64 = amount_str.parse().unwrap_or(0);
                    let from_balance = self.get_balance(from_address)?;

                    if from_balance < amount {
                        return Err(StateError::InsufficientFunds(from_address.clone()));
                    }

                    // Deduct from sender
                    self.set_balance(from_address, from_balance - amount)?;

                    // Add to receiver
                    let to_balance = self.get_balance(to_address)?;
                    self.set_balance(to_address, to_balance + amount)?;
                }
            }
            TransactionType::Governance => {
                // Not implemented yet
            }
        }

        Ok(())
    }

    /// Apply an entire block to the state
    pub fn apply_block(&self, block: &Block) -> Result<()> {
        // In a real system, you would create an atomic batch here
        for tx in &block.transactions {
            self.apply_transaction(tx)?;
        }

        self.db.flush()?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::Utc;
    use uet_security::{CryptoSuite, HashAlgorithm, SignatureAlgorithm};

    #[test]
    fn test_state_machine_transfer() {
        let db = sled::Config::new().temporary(true).open().unwrap();
        let state = StateMachine::new(db);

        // Give initial reward to Alice
        let reward_tx = Transaction {
            tx_id: "tx1".to_string(),
            tx_type: TransactionType::ComputeReward,
            payload_json: r#"{"miner_address":"alice","reward":"100"}"#.to_string(),
            suite: CryptoSuite {
                schema_version: 1,
                sig_alg: SignatureAlgorithm::Dilithium3,
                hash_alg: HashAlgorithm::Sha3256,
                key_id: "sys".to_string(),
            },
            signature_hex: "sig".to_string(),
            created_at: Utc::now(),
        };

        state.apply_transaction(&reward_tx).unwrap();
        assert_eq!(state.get_balance("alice").unwrap(), 100);
        assert_eq!(state.get_balance("bob").unwrap(), 0);

        // Transfer from Alice to Bob
        let transfer_tx = Transaction {
            tx_id: "tx2".to_string(),
            tx_type: TransactionType::Transfer,
            payload_json: r#"{"from":"alice","to":"bob","amount":"30"}"#.to_string(),
            suite: CryptoSuite {
                schema_version: 1,
                sig_alg: SignatureAlgorithm::Dilithium3,
                hash_alg: HashAlgorithm::Sha3256,
                key_id: "alice#k1".to_string(),
            },
            signature_hex: "sig".to_string(),
            created_at: Utc::now(),
        };

        state.apply_transaction(&transfer_tx).unwrap();
        assert_eq!(state.get_balance("alice").unwrap(), 70);
        assert_eq!(state.get_balance("bob").unwrap(), 30);

        // Insufficient funds test
        let fail_tx = Transaction {
            tx_id: "tx3".to_string(),
            tx_type: TransactionType::Transfer,
            payload_json: r#"{"from":"bob","to":"alice","amount":"50"}"#.to_string(),
            suite: CryptoSuite::default(),
            signature_hex: "sig".to_string(),
            created_at: Utc::now(),
        };

        let res = state.apply_transaction(&fail_tx);
        assert!(matches!(res, Err(StateError::InsufficientFunds(_))));
    }
}