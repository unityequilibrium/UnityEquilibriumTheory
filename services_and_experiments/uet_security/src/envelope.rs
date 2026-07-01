use serde::{de::DeserializeOwned, Deserialize, Serialize};

use crate::{
    algorithms::{CryptoSuite, SignatureAlgorithm},
    hashing::digest_hex,
    signing::{SecurityError, Signer, Verifier},
};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SignedEnvelope {
    pub suite: CryptoSuite,
    pub payload_type: String,
    pub payload_json: String,
    pub payload_hash_hex: String,
    pub signature_hex: String,
}

impl SignedEnvelope {
    pub fn sign<T: Serialize>(
        payload_type: impl Into<String>,
        payload: &T,
        mut suite: CryptoSuite,
        signer: &dyn Signer,
    ) -> Result<Self, SecurityError> {
        suite.key_id = signer.key_id().to_string();
        suite.sig_alg = signer.algorithm();

        let payload_json = serde_json::to_string(payload)
            .map_err(|_| SecurityError::UnsupportedAlgorithm(SignatureAlgorithm::Ed25519))?;
        let payload_hash_hex = digest_hex(suite.hash_alg, payload_json.as_bytes());

        let signature = signer.sign(payload_hash_hex.as_bytes())?;
        let signature_hex = signature
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect::<String>();

        Ok(Self {
            suite,
            payload_type: payload_type.into(),
            payload_json,
            payload_hash_hex,
            signature_hex,
        })
    }

    pub fn verify(&self, verifier: &dyn Verifier) -> Result<(), SecurityError> {
        let recomputed = digest_hex(self.suite.hash_alg, self.payload_json.as_bytes());
        if recomputed != self.payload_hash_hex {
            return Err(SecurityError::InvalidSignature);
        }

        let sig_bytes = hex_decode(&self.signature_hex)?;
        verifier.verify(self.payload_hash_hex.as_bytes(), &sig_bytes)
    }

    pub fn decode_payload<T: DeserializeOwned>(&self) -> Result<T, serde_json::Error> {
        serde_json::from_str(&self.payload_json)
    }
}

fn hex_decode(s: &str) -> Result<Vec<u8>, SecurityError> {
    if s.len() % 2 != 0 {
        return Err(SecurityError::InvalidSignature);
    }

    let mut out = Vec::with_capacity(s.len() / 2);
    for i in (0..s.len()).step_by(2) {
        let byte = u8::from_str_radix(&s[i..i + 2], 16).map_err(|_| SecurityError::InvalidSignature)?;
        out.push(byte);
    }
    Ok(out)
}
