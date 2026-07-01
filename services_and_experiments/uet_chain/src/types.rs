use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uet_security::CryptoSuite;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum TaskFamily {
    DeterministicSimulation,
    OptimizationBounded,
    EquilibriumCertificate,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkTask {
    pub task_id: String,
    pub family: TaskFamily,
    pub input_seed: String,
    pub difficulty: u32,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationArtifact {
    pub artifact_kind: String,
    pub artifact_hash_hex: String,
    pub verifier_hint: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkProof {
    pub task_id: String,
    pub node_id: String,
    pub result_hash_hex: String,
    pub verification_artifact: VerificationArtifact,
    pub runtime_ms: u64,
    pub nonce: u64,
    pub suite: CryptoSuite,
    pub signature_hex: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TransactionType {
    ComputeReward,
    Transfer,
    Governance,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub tx_id: String,
    pub tx_type: TransactionType,
    pub payload_json: String,
    pub suite: CryptoSuite,
    pub signature_hex: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BlockHeader {
    pub height: u64,
    pub previous_block_hash_hex: String,
    pub tx_merkle_root_hex: String,
    pub proof_root_hex: String,
    pub state_root_hex: String,
    pub proposer_node_id: String,
    pub timestamp: DateTime<Utc>,
    pub suite: CryptoSuite,
    pub signature_hex: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Block {
    pub header: BlockHeader,
    pub transactions: Vec<Transaction>,
    pub work_proofs: Vec<WorkProof>,
}
