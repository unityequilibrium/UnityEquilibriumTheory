use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::algorithms::SignatureAlgorithm;

#[derive(Debug, Error)]
pub enum SecurityError {
    #[error("unsupported signature algorithm: {0:?}")]
    UnsupportedAlgorithm(SignatureAlgorithm),
    #[error("invalid signature")]
    InvalidSignature,
}

pub trait Signer {
    fn algorithm(&self) -> SignatureAlgorithm;
    fn key_id(&self) -> &str;
    fn sign(&self, message: &[u8]) -> Result<Vec<u8>, SecurityError>;
}

pub trait Verifier {
    fn algorithm(&self) -> SignatureAlgorithm;
    fn key_id(&self) -> &str;
    fn verify(&self, message: &[u8], signature: &[u8]) -> Result<(), SecurityError>;
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MockSigner {
    pub key_id: String,
    pub algorithm: SignatureAlgorithm,
}

impl MockSigner {
    pub fn new(key_id: impl Into<String>, algorithm: SignatureAlgorithm) -> Self {
        Self {
            key_id: key_id.into(),
            algorithm,
        }
    }
}

impl Signer for MockSigner {
    fn algorithm(&self) -> SignatureAlgorithm {
        self.algorithm
    }

    fn key_id(&self) -> &str {
        &self.key_id
    }

    fn sign(&self, message: &[u8]) -> Result<Vec<u8>, SecurityError> {
        let mut sig = self.key_id.as_bytes().to_vec();
        sig.extend_from_slice(message);
        Ok(sig)
    }
}

impl Verifier for MockSigner {
    fn algorithm(&self) -> SignatureAlgorithm {
        self.algorithm
    }

    fn key_id(&self) -> &str {
        &self.key_id
    }

    fn verify(&self, message: &[u8], signature: &[u8]) -> Result<(), SecurityError> {
        let expected = self.sign(message)?;
        if expected == signature {
            Ok(())
        } else {
            Err(SecurityError::InvalidSignature)
        }
    }
}
