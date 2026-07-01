use ed25519_dalek::{SigningKey, VerifyingKey, Signer as DalekSigner, Verifier as DalekVerifier, Signature};
use pqcrypto_dilithium::dilithium3;
use pqcrypto_traits::sign::{PublicKey as PqPublicKey, SecretKey as PqSecretKey, DetachedSignature};
use rand::rngs::OsRng;

use crate::algorithms::SignatureAlgorithm;
use crate::signing::{SecurityError, Signer, Verifier};

/// Real Ed25519 keypair signer
pub struct Ed25519Signer {
    key_id: String,
    signing_key: SigningKey,
}

impl Ed25519Signer {
    pub fn generate(key_id: impl Into<String>) -> Self {
        let mut csprng = OsRng;
        let signing_key = SigningKey::generate(&mut csprng);
        Self {
            key_id: key_id.into(),
            signing_key,
        }
    }

    pub fn from_bytes(key_id: impl Into<String>, secret: &[u8; 32]) -> Self {
        let signing_key = SigningKey::from_bytes(secret);
        Self {
            key_id: key_id.into(),
            signing_key,
        }
    }

    pub fn public_key_bytes(&self) -> [u8; 32] {
        self.signing_key.verifying_key().to_bytes()
    }

    pub fn secret_key_bytes(&self) -> [u8; 32] {
        self.signing_key.to_bytes()
    }
}

impl Signer for Ed25519Signer {
    fn algorithm(&self) -> SignatureAlgorithm {
        SignatureAlgorithm::Ed25519
    }

    fn key_id(&self) -> &str {
        &self.key_id
    }

    fn sign(&self, message: &[u8]) -> Result<Vec<u8>, SecurityError> {
        let sig = self.signing_key.sign(message);
        Ok(sig.to_bytes().to_vec())
    }
}

/// Ed25519 public key verifier
pub struct Ed25519Verifier {
    key_id: String,
    verifying_key: VerifyingKey,
}

impl Ed25519Verifier {
    pub fn new(key_id: impl Into<String>, public_key_bytes: &[u8; 32]) -> Result<Self, SecurityError> {
        let verifying_key = VerifyingKey::from_bytes(public_key_bytes)
            .map_err(|_| SecurityError::InvalidSignature)?;
        Ok(Self {
            key_id: key_id.into(),
            verifying_key,
        })
    }

    pub fn from_signer(signer: &Ed25519Signer) -> Self {
        Self {
            key_id: signer.key_id.clone(),
            verifying_key: signer.signing_key.verifying_key(),
        }
    }
}

impl Verifier for Ed25519Verifier {
    fn algorithm(&self) -> SignatureAlgorithm {
        SignatureAlgorithm::Ed25519
    }

    fn key_id(&self) -> &str {
        &self.key_id
    }

    fn verify(&self, message: &[u8], signature: &[u8]) -> Result<(), SecurityError> {
        if signature.len() != 64 {
            return Err(SecurityError::InvalidSignature);
        }
        let sig_bytes: [u8; 64] = signature.try_into().unwrap();
        let sig = Signature::from_bytes(&sig_bytes);
        self.verifying_key
            .verify(message, &sig)
            .map_err(|_| SecurityError::InvalidSignature)
    }
}

/// Real Dilithium3 (ML-DSA-65) post-quantum signer
pub struct Dilithium3Signer {
    key_id: String,
    public_key: dilithium3::PublicKey,
    secret_key: dilithium3::SecretKey,
}

impl Dilithium3Signer {
    pub fn generate(key_id: impl Into<String>) -> Self {
        let (pk, sk) = dilithium3::keypair();
        Self {
            key_id: key_id.into(),
            public_key: pk,
            secret_key: sk,
        }
    }

    pub fn from_bytes(key_id: impl Into<String>, secret_bytes: &[u8], public_bytes: &[u8]) -> Result<Self, SecurityError> {
        let secret_key = dilithium3::SecretKey::from_bytes(secret_bytes)
            .map_err(|_| SecurityError::InvalidSignature)?;
        let public_key = dilithium3::PublicKey::from_bytes(public_bytes)
            .map_err(|_| SecurityError::InvalidSignature)?;
        Ok(Self {
            key_id: key_id.into(),
            public_key,
            secret_key,
        })
    }

    pub fn public_key_bytes(&self) -> Vec<u8> {
        pqcrypto_traits::sign::PublicKey::as_bytes(&self.public_key).to_vec()
    }

    pub fn secret_key_bytes(&self) -> Vec<u8> {
        pqcrypto_traits::sign::SecretKey::as_bytes(&self.secret_key).to_vec()
    }
}

impl Signer for Dilithium3Signer {
    fn algorithm(&self) -> SignatureAlgorithm {
        SignatureAlgorithm::Dilithium3
    }

    fn key_id(&self) -> &str {
        &self.key_id
    }

    fn sign(&self, message: &[u8]) -> Result<Vec<u8>, SecurityError> {
        let sig = dilithium3::detached_sign(message, &self.secret_key);
        Ok(pqcrypto_traits::sign::DetachedSignature::as_bytes(&sig).to_vec())
    }
}

/// Dilithium3 public key verifier
pub struct Dilithium3Verifier {
    key_id: String,
    public_key: dilithium3::PublicKey,
}

impl Dilithium3Verifier {
    pub fn new(key_id: impl Into<String>, pk_bytes: &[u8]) -> Result<Self, SecurityError> {
        let public_key = dilithium3::PublicKey::from_bytes(pk_bytes)
            .map_err(|_| SecurityError::InvalidSignature)?;
        Ok(Self {
            key_id: key_id.into(),
            public_key,
        })
    }

    pub fn from_signer(signer: &Dilithium3Signer) -> Self {
        Self {
            key_id: signer.key_id.clone(),
            public_key: signer.public_key.clone(),
        }
    }
}

impl Verifier for Dilithium3Verifier {
    fn algorithm(&self) -> SignatureAlgorithm {
        SignatureAlgorithm::Dilithium3
    }

    fn key_id(&self) -> &str {
        &self.key_id
    }

    fn verify(&self, message: &[u8], signature: &[u8]) -> Result<(), SecurityError> {
        let sig = dilithium3::DetachedSignature::from_bytes(signature)
            .map_err(|_| SecurityError::InvalidSignature)?;
        dilithium3::verify_detached_signature(&sig, message, &self.public_key)
            .map_err(|_| SecurityError::InvalidSignature)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ed25519_sign_verify() {
        let signer = Ed25519Signer::generate("test-ed25519");
        let verifier = Ed25519Verifier::from_signer(&signer);

        let message = b"hello UET blockchain";
        let sig = signer.sign(message).unwrap();

        assert!(verifier.verify(message, &sig).is_ok());
        assert!(verifier.verify(b"tampered", &sig).is_err());
    }

    #[test]
    fn ed25519_roundtrip_from_bytes() {
        let signer1 = Ed25519Signer::generate("key-1");
        let secret = signer1.secret_key_bytes();
        let public = signer1.public_key_bytes();

        let signer2 = Ed25519Signer::from_bytes("key-1", &secret);
        let verifier = Ed25519Verifier::new("key-1", &public).unwrap();

        let msg = b"restore from bytes";
        let sig = signer2.sign(msg).unwrap();
        assert!(verifier.verify(msg, &sig).is_ok());
    }

    #[test]
    fn dilithium3_sign_verify() {
        let signer = Dilithium3Signer::generate("test-dilithium");
        let verifier = Dilithium3Verifier::from_signer(&signer);

        let message = b"quantum resistant UET proof";
        let sig = signer.sign(message).unwrap();

        assert!(verifier.verify(message, &sig).is_ok());
        assert!(verifier.verify(b"tampered", &sig).is_err());
    }

    #[test]
    fn dilithium3_roundtrip_from_bytes() {
        let signer = Dilithium3Signer::generate("pq-key-1");
        let pk_bytes = signer.public_key_bytes();

        let verifier = Dilithium3Verifier::new("pq-key-1", &pk_bytes).unwrap();

        let msg = b"roundtrip dilithium";
        let sig = signer.sign(msg).unwrap();
        assert!(verifier.verify(msg, &sig).is_ok());
    }
}
