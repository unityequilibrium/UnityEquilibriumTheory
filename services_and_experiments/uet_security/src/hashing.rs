use crate::algorithms::HashAlgorithm;
use sha3::{Digest, Sha3_256, Sha3_512};

pub fn digest_bytes(alg: HashAlgorithm, data: &[u8]) -> Vec<u8> {
    match alg {
        HashAlgorithm::Sha3256 => Sha3_256::digest(data).to_vec(),
        HashAlgorithm::Sha3512 => Sha3_512::digest(data).to_vec(),
        HashAlgorithm::Blake3 => blake3::hash(data).as_bytes().to_vec(),
    }
}

pub fn digest_hex(alg: HashAlgorithm, data: &[u8]) -> String {
    digest_bytes(alg, data)
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect::<String>()
}
