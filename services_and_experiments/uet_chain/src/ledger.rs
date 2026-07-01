use chrono::Utc;
use serde::Serialize;
use uet_security::{hashing::digest_hex, HashAlgorithm, Signer};

use crate::{
    canonical::{canonical_hash_hex, merkle_root_hex, CanonicalError},
    types::{Block, BlockHeader, Transaction, WorkProof},
};

pub fn tx_hashes_hex(
    txs: &[Transaction],
    alg: HashAlgorithm,
) -> Result<Vec<String>, CanonicalError> {
    txs.iter().map(|tx| canonical_hash_hex(alg, tx)).collect()
}

pub fn proof_hashes_hex(
    proofs: &[WorkProof],
    alg: HashAlgorithm,
) -> Result<Vec<String>, CanonicalError> {
    proofs
        .iter()
        .map(|proof| canonical_hash_hex(alg, proof))
        .collect()
}

pub fn build_unsigned_header(
    height: u64,
    previous_block_hash_hex: impl Into<String>,
    proposer_node_id: impl Into<String>,
    txs: &[Transaction],
    proofs: &[WorkProof],
    alg: HashAlgorithm,
) -> Result<BlockHeader, CanonicalError> {
    let tx_hashes = tx_hashes_hex(txs, alg)?;
    let proof_hashes = proof_hashes_hex(proofs, alg)?;

    let tx_merkle_root_hex = merkle_root_hex(&tx_hashes, alg);
    let proof_root_hex = merkle_root_hex(&proof_hashes, alg);

    let state_root_hex = digest_hex(
        alg,
        format!("{}:{}", tx_merkle_root_hex, proof_root_hex).as_bytes(),
    );

    Ok(BlockHeader {
        height,
        previous_block_hash_hex: previous_block_hash_hex.into(),
        tx_merkle_root_hex,
        proof_root_hex,
        state_root_hex,
        proposer_node_id: proposer_node_id.into(),
        timestamp: Utc::now(),
        suite: uet_security::CryptoSuite::default(),
        signature_hex: String::new(),
    })
}

pub fn sign_header<T: Serialize>(
    header: &mut BlockHeader,
    signer: &dyn Signer,
    alg: HashAlgorithm,
    payload: &T,
) -> Result<(), CanonicalError> {
    header.suite.key_id = signer.key_id().to_string();
    header.suite.sig_alg = signer.algorithm();
    header.suite.hash_alg = alg;

    let payload_hash = canonical_hash_hex(alg, payload)?;
    let mut sign_bytes = payload_hash.as_bytes().to_vec();
    sign_bytes.extend_from_slice(header.state_root_hex.as_bytes());

    let sig = signer
        .sign(&sign_bytes)
        .map_err(|e| CanonicalError::Serialization(e.to_string()))?;

    header.signature_hex = sig.iter().map(|b| format!("{b:02x}")).collect();
    Ok(())
}

pub fn assemble_block(header: BlockHeader, transactions: Vec<Transaction>, work_proofs: Vec<WorkProof>) -> Block {
    Block {
        header,
        transactions,
        work_proofs,
    }
}
