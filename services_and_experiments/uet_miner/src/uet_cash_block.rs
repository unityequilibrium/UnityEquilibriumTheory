use serde::{Deserialize, Serialize};
use sha3::{Digest, Sha3_256};
use crate::mining::uet_cash::{ProofOfWork};
use uet_security::{CryptoSuite, Signer, Verifier};

/// Uet-Cash Block Structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UetCashBlock {
    pub header: BlockHeader,
    pub body: BlockBody,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BlockHeader {
    pub prev_hash: String,
    pub proof_root: String,
    pub state_root: String,
    pub timestamp: u64,
    pub difficulty: u64,
    pub height: u64,
    pub proposer_signature_hex: String,
    pub suite: CryptoSuite,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BlockBody {
    pub transactions: Vec<Transaction>,
    pub proofs: Vec<ProofOfWork>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub tx_id: String,
    pub inputs: Vec<TxInput>,
    pub outputs: Vec<TxOutput>,
    pub timestamp: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxInput {
    pub prev_tx_id: String,
    pub output_index: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxOutput {
    pub address: String,
    pub amount: u64,
}

impl UetCashBlock {
    pub fn new(prev_hash: String, difficulty: u64, height: u64, suite: CryptoSuite) -> Self {
        Self {
            header: BlockHeader {
                prev_hash,
                proof_root: String::new(),
                state_root: String::new(),
                timestamp: 0,
                difficulty,
                height,
                proposer_signature_hex: String::new(),
                suite,
            },
            body: BlockBody {
                transactions: Vec::new(),
                proofs: Vec::new(),
            },
        }
    }

    /// Add proof to block
    pub fn add_proof(&mut self, proof: ProofOfWork) {
        self.body.proofs.push(proof);
    }

    /// Add transaction to block
    pub fn add_transaction(&mut self, tx: Transaction) {
        self.body.transactions.push(tx);
    }

    /// Calculate Merkle root of proofs
    pub fn calculate_proof_root(&self) -> String {
        if self.body.proofs.is_empty() {
            return String::new();
        }

        let mut hashes: Vec<String> = self.body.proofs
            .iter()
            .map(|p| p.result_hash_hex.clone())
            .collect();

        while hashes.len() > 1 {
            let mut new_hashes = Vec::new();
            for i in (0..hashes.len()).step_by(2) {
                let left = &hashes[i];
                let right = if i + 1 < hashes.len() {
                    &hashes[i + 1]
                } else {
                    left
                };

                let combined = format!("{}{}", left, right);
                let mut hasher = Sha3_256::new();
                hasher.update(combined.as_bytes());
                new_hashes.push(hex::encode(hasher.finalize()));
            }
            hashes = new_hashes;
        }

        hashes[0].clone()
    }

    /// Calculate Merkle root of transactions
    pub fn calculate_tx_root(&self) -> String {
        if self.body.transactions.is_empty() {
            return String::new();
        }

        let mut hashes: Vec<String> = self.body.transactions
            .iter()
            .map(|t| t.tx_id.clone())
            .collect();

        while hashes.len() > 1 {
            let mut new_hashes = Vec::new();
            for i in (0..hashes.len()).step_by(2) {
                let left = &hashes[i];
                let right = if i + 1 < hashes.len() {
                    &hashes[i + 1]
                } else {
                    left
                };

                let combined = format!("{}{}", left, right);
                let mut hasher = Sha3_256::new();
                hasher.update(combined.as_bytes());
                new_hashes.push(hex::encode(hasher.finalize()));
            }
            hashes = new_hashes;
        }

        hashes[0].clone()
    }

    /// Calculate block hash
    pub fn calculate_hash(&self) -> String {
        let header_str = serde_json::to_string(&self.header).unwrap();
        let mut hasher = Sha3_256::new();
        hasher.update(header_str.as_bytes());
        hex::encode(hasher.finalize())
    }

    /// Finalize block (calculate roots, timestamp, and signature)
    pub fn finalize<S: Signer>(&mut self, signer: &S) {
        self.header.proof_root = self.calculate_proof_root();
        self.header.state_root = self.calculate_tx_root();
        self.header.timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        // Calculate header hash before adding signature
        let header_hash = self.calculate_hash_without_signature();

        // Sign the header hash
        let sig = signer.sign(header_hash.as_bytes()).unwrap();
        self.header.proposer_signature_hex = hex::encode(sig);
    }

    /// Calculate block hash without signature (for signing)
    fn calculate_hash_without_signature(&self) -> String {
        let mut header_without_sig = self.header.clone();
        header_without_sig.proposer_signature_hex = String::new();
        let header_str = serde_json::to_string(&header_without_sig).unwrap();
        let mut hasher = Sha3_256::new();
        hasher.update(header_str.as_bytes());
        hex::encode(hasher.finalize())
    }

    /// Validate block
    pub fn validate<V: Verifier>(&self, verifier: &V) -> bool {
        // Verify proof root matches
        if self.header.proof_root != self.calculate_proof_root() {
            println!("Proof root mismatch: {} != {}", self.header.proof_root, self.calculate_proof_root());
            return false;
        }

        // Verify state root matches
        if self.header.state_root != self.calculate_tx_root() {
            println!("State root mismatch: {} != {}", self.header.state_root, self.calculate_tx_root());
            return false;
        }

        // Verify header signature
        let header_hash = self.calculate_hash_without_signature();
        let sig_bytes = hex::decode(&self.header.proposer_signature_hex).unwrap();
        println!("Header hash: {}", header_hash);
        println!("Signature hex: {}", self.header.proposer_signature_hex);
        println!("Signature bytes: {:?}", sig_bytes);
        if verifier.verify(header_hash.as_bytes(), &sig_bytes).is_err() {
            println!("Signature verification failed");
            return false;
        }

        // Verify all proofs meet difficulty
        for proof in &self.body.proofs {
            let leading_zeros = proof.result_hash_hex
                .chars()
                .take_while(|c| *c == '0')
                .count();

            if leading_zeros < (self.header.difficulty as usize).min(16) {
                println!("Proof difficulty check failed: {} < {}", leading_zeros, self.header.difficulty);
                return false;
            }
        }

        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use uet_security::{MockSigner, SignatureAlgorithm, CryptoSuite};

    #[test]
    fn test_block_creation() {
        let suite = CryptoSuite::default();
        let block = UetCashBlock::new(
            "prev_hash".to_string(),
            1000000,
            1,
            suite,
        );

        assert_eq!(block.header.height, 1);
        assert_eq!(block.header.difficulty, 1000000);
    }

    #[test]
    fn test_block_validation() {
        let suite = CryptoSuite::default();
        let signer = MockSigner::new("node-a", SignatureAlgorithm::Dilithium3);

        let mut block = UetCashBlock::new(
            "prev_hash".to_string(),
            2,
            1,
            suite.clone(),
        );

        let task = crate::mining::uet_cash::MiningTask {
            task_id: "test".to_string(),
            family: crate::mining::uet_cash::TaskFamily::EquilibriumCertificate,
            input_seed: vec![1.0, 2.0],
            difficulty: 2,
            created_at: 0,
        };

        let miner = crate::mining::uet_cash::UetCashMiner::new(task, "node-a".to_string(), suite);
        if let Some(proof) = miner.mine(10000, &signer) {
            block.add_proof(proof);
        }

        block.finalize(&signer);
        assert!(block.validate(&signer));
    }
}
