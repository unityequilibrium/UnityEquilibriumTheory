pub mod canonical;
pub mod ledger;
pub mod types;
pub mod storage;
pub mod state;
pub mod p2p;
pub mod consensus;

pub use canonical::{canonical_hash_hex, canonical_json, merkle_root_hex, CanonicalError};
pub use ledger::{assemble_block, build_unsigned_header, proof_hashes_hex, sign_header, tx_hashes_hex};
pub use types::{
    Block, BlockHeader, TaskFamily, Transaction, TransactionType, VerificationArtifact, WorkProof,
    WorkTask,
};

#[cfg(test)]
mod tests {
    use chrono::Utc;
    use uet_security::{CryptoSuite, HashAlgorithm, MockSigner, SignatureAlgorithm};

    use crate::{
        assemble_block, build_unsigned_header,
        types::{TaskFamily, Transaction, TransactionType, VerificationArtifact, WorkProof},
    };

    #[test]
    fn build_block_with_pouw_proof() {
        let tx = Transaction {
            tx_id: "tx-1".to_string(),
            tx_type: TransactionType::ComputeReward,
            payload_json: "{\"reward\":1}".to_string(),
            suite: CryptoSuite::default(),
            signature_hex: "aa".to_string(),
            created_at: Utc::now(),
        };

        let proof = WorkProof {
            task_id: "task-1".to_string(),
            node_id: "node-a".to_string(),
            result_hash_hex: "deadbeef".to_string(),
            verification_artifact: VerificationArtifact {
                artifact_kind: "equilibrium_certificate".to_string(),
                artifact_hash_hex: "cafe".to_string(),
                verifier_hint: "deterministic-check-v1".to_string(),
            },
            runtime_ms: 120,
            nonce: 7,
            suite: CryptoSuite {
                schema_version: 1,
                sig_alg: SignatureAlgorithm::Dilithium3,
                hash_alg: HashAlgorithm::Sha3256,
                key_id: "node-a#k1".to_string(),
            },
            signature_hex: "bb".to_string(),
        };

        let mut header = build_unsigned_header(
            1,
            "genesis",
            "node-a",
            &[tx.clone()],
            &[proof.clone()],
            HashAlgorithm::Sha3256,
        )
        .expect("header build");

        let signer = MockSigner::new("node-a#k1", SignatureAlgorithm::Dilithium3);
        crate::sign_header(&mut header, &signer, HashAlgorithm::Sha3256, &TaskFamily::EquilibriumCertificate)
            .expect("sign header");

        let block = assemble_block(header, vec![tx], vec![proof]);
        assert_eq!(block.header.height, 1);
        assert!(!block.header.tx_merkle_root_hex.is_empty());
        assert!(!block.header.proof_root_hex.is_empty());
        assert!(!block.header.signature_hex.is_empty());
    }
}
