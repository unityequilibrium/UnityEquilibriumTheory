pub mod algorithms;
pub mod envelope;
pub mod hashing;
pub mod signing;
pub mod keys;
pub mod keymanager;

pub use algorithms::{CryptoSuite, HashAlgorithm, SignatureAlgorithm};
pub use envelope::SignedEnvelope;
pub use signing::{MockSigner, SecurityError, Signer, Verifier};
pub use keys::{Ed25519Signer, Ed25519Verifier, Dilithium3Signer, Dilithium3Verifier};
pub use keymanager::{KeyManager, KeyManagerError, KeyMetadata};

#[cfg(test)]
mod tests {
    use super::*;
    use serde::{Deserialize, Serialize};

    #[derive(Debug, Serialize, Deserialize, PartialEq)]
    struct Payload {
        value: u64,
    }

    #[test]
    fn roundtrip_signed_envelope() {
        let payload = Payload { value: 42 };
        let signer = MockSigner::new("node-a", SignatureAlgorithm::Dilithium3);
        let suite = CryptoSuite::default();

        let envelope = SignedEnvelope::sign("payload.test", &payload, suite, &signer)
            .expect("sign should succeed");
        envelope.verify(&signer).expect("verify should succeed");

        let decoded: Payload = envelope.decode_payload().expect("decode payload");
        assert_eq!(decoded, payload);
    }
}
