use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SignatureAlgorithm {
    Dilithium3,
    SphincsSha2128f,
    Ed25519,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HashAlgorithm {
    Sha3256,
    Sha3512,
    Blake3,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CryptoSuite {
    pub schema_version: u16,
    pub sig_alg: SignatureAlgorithm,
    pub hash_alg: HashAlgorithm,
    pub key_id: String,
}

impl Default for CryptoSuite {
    fn default() -> Self {
        Self {
            schema_version: 1,
            sig_alg: SignatureAlgorithm::Dilithium3,
            hash_alg: HashAlgorithm::Sha3256,
            key_id: "unset".to_string(),
        }
    }
}
