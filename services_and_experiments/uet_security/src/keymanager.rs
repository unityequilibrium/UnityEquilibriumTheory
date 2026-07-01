use std::path::{Path, PathBuf};
use std::fs;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use chrono::{DateTime, Utc};

use crate::algorithms::SignatureAlgorithm;
use crate::keys::{Ed25519Signer, Ed25519Verifier, Dilithium3Signer, Dilithium3Verifier};
use crate::signing::SecurityError;

#[derive(Error, Debug)]
pub enum KeyManagerError {
    #[error("Key not found: {0}")]
    KeyNotFound(String),
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),
    #[error("Security error: {0}")]
    SecurityError(#[from] SecurityError),
    #[error("Key already exists: {0}")]
    KeyAlreadyExists(String),
    #[error("Unsupported algorithm for key management: {0:?}")]
    UnsupportedAlgorithm(SignatureAlgorithm),
}

pub type Result<T> = std::result::Result<T, KeyManagerError>;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KeyMetadata {
    pub key_id: String,
    pub algorithm: SignatureAlgorithm,
    pub created_at: DateTime<Utc>,
    pub rotated_from: Option<String>,
    pub is_active: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct StoredKey {
    pub metadata: KeyMetadata,
    pub secret_key_hex: String,
    pub public_key_hex: String,
}

/// Manages cryptographic keys: generation, storage, loading, and rotation.
pub struct KeyManager {
    storage_dir: PathBuf,
}

impl KeyManager {
    /// Create a new KeyManager backed by a directory on disk.
    pub fn new<P: AsRef<Path>>(storage_dir: P) -> Result<Self> {
        let dir = storage_dir.as_ref().to_path_buf();
        fs::create_dir_all(&dir)?;
        Ok(Self { storage_dir: dir })
    }

    /// Generate a new keypair and store it.
    pub fn generate_key(&self, key_id: &str, algorithm: SignatureAlgorithm) -> Result<KeyMetadata> {
        let path = self.key_path(key_id);
        if path.exists() {
            return Err(KeyManagerError::KeyAlreadyExists(key_id.to_string()));
        }

        let (secret_hex, public_hex) = match algorithm {
            SignatureAlgorithm::Ed25519 => {
                let signer = Ed25519Signer::generate(key_id);
                (
                    hex::encode(signer.secret_key_bytes()),
                    hex::encode(signer.public_key_bytes()),
                )
            }
            SignatureAlgorithm::Dilithium3 => {
                let signer = Dilithium3Signer::generate(key_id);
                (
                    hex::encode(signer.secret_key_bytes()),
                    hex::encode(signer.public_key_bytes()),
                )
            }
            other => return Err(KeyManagerError::UnsupportedAlgorithm(other)),
        };

        let metadata = KeyMetadata {
            key_id: key_id.to_string(),
            algorithm,
            created_at: Utc::now(),
            rotated_from: None,
            is_active: true,
        };

        let stored = StoredKey {
            metadata: metadata.clone(),
            secret_key_hex: secret_hex,
            public_key_hex: public_hex,
        };

        let json = serde_json::to_string_pretty(&stored)?;
        fs::write(&path, json)?;

        Ok(metadata)
    }

    /// Load an Ed25519 signer from stored key.
    pub fn load_ed25519_signer(&self, key_id: &str) -> Result<Ed25519Signer> {
        let stored = self.load_stored_key(key_id)?;
        if stored.metadata.algorithm != SignatureAlgorithm::Ed25519 {
            return Err(KeyManagerError::UnsupportedAlgorithm(stored.metadata.algorithm));
        }

        let secret_bytes = hex_to_32_bytes(&stored.secret_key_hex)?;
        Ok(Ed25519Signer::from_bytes(key_id, &secret_bytes))
    }

    /// Load an Ed25519 verifier from stored key.
    pub fn load_ed25519_verifier(&self, key_id: &str) -> Result<Ed25519Verifier> {
        let stored = self.load_stored_key(key_id)?;
        if stored.metadata.algorithm != SignatureAlgorithm::Ed25519 {
            return Err(KeyManagerError::UnsupportedAlgorithm(stored.metadata.algorithm));
        }

        let public_bytes = hex_to_32_bytes(&stored.public_key_hex)?;
        Ed25519Verifier::new(key_id, &public_bytes).map_err(KeyManagerError::SecurityError)
    }

    /// Load a Dilithium3 signer from stored key.
    pub fn load_dilithium3_signer(&self, key_id: &str) -> Result<Dilithium3Signer> {
        let stored = self.load_stored_key(key_id)?;
        if stored.metadata.algorithm != SignatureAlgorithm::Dilithium3 {
            return Err(KeyManagerError::UnsupportedAlgorithm(stored.metadata.algorithm));
        }

        let secret_bytes = hex_to_vec(&stored.secret_key_hex)?;
        let public_bytes = hex_to_vec(&stored.public_key_hex)?;
        Dilithium3Signer::from_bytes(key_id, &secret_bytes, &public_bytes)
            .map_err(KeyManagerError::SecurityError)
    }

    /// Load a Dilithium3 verifier from stored key.
    pub fn load_dilithium3_verifier(&self, key_id: &str) -> Result<Dilithium3Verifier> {
        let stored = self.load_stored_key(key_id)?;
        if stored.metadata.algorithm != SignatureAlgorithm::Dilithium3 {
            return Err(KeyManagerError::UnsupportedAlgorithm(stored.metadata.algorithm));
        }

        let public_bytes = hex_to_vec(&stored.public_key_hex)?;
        Dilithium3Verifier::new(key_id, &public_bytes).map_err(KeyManagerError::SecurityError)
    }

    /// Rotate a key: generate a new key and mark the old one as inactive.
    pub fn rotate_key(&self, old_key_id: &str, new_key_id: &str) -> Result<KeyMetadata> {
        let old_stored = self.load_stored_key(old_key_id)?;
        let algorithm = old_stored.metadata.algorithm;

        // Mark old key as inactive
        let mut updated_old = old_stored;
        updated_old.metadata.is_active = false;
        let old_json = serde_json::to_string_pretty(&updated_old)?;
        fs::write(self.key_path(old_key_id), old_json)?;

        // Generate new key
        let mut new_meta = self.generate_key(new_key_id, algorithm)?;

        // Update new key metadata to reference the old key
        let new_stored = self.load_stored_key(new_key_id)?;
        let mut updated_new = new_stored;
        updated_new.metadata.rotated_from = Some(old_key_id.to_string());
        let new_json = serde_json::to_string_pretty(&updated_new)?;
        fs::write(self.key_path(new_key_id), new_json)?;

        new_meta.rotated_from = Some(old_key_id.to_string());
        Ok(new_meta)
    }

    /// List all stored key metadata.
    pub fn list_keys(&self) -> Result<Vec<KeyMetadata>> {
        let mut keys = Vec::new();
        for entry in fs::read_dir(&self.storage_dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("json") {
                let content = fs::read_to_string(&path)?;
                let stored: StoredKey = serde_json::from_str(&content)?;
                keys.push(stored.metadata);
            }
        }
        keys.sort_by(|a, b| b.created_at.cmp(&a.created_at));
        Ok(keys)
    }

    /// Delete a key from storage.
    pub fn delete_key(&self, key_id: &str) -> Result<()> {
        let path = self.key_path(key_id);
        if !path.exists() {
            return Err(KeyManagerError::KeyNotFound(key_id.to_string()));
        }
        fs::remove_file(path)?;
        Ok(())
    }

    /// Get the public key hex for a key.
    pub fn get_public_key_hex(&self, key_id: &str) -> Result<String> {
        let stored = self.load_stored_key(key_id)?;
        Ok(stored.public_key_hex)
    }

    fn key_path(&self, key_id: &str) -> PathBuf {
        self.storage_dir.join(format!("{}.json", key_id))
    }

    fn load_stored_key(&self, key_id: &str) -> Result<StoredKey> {
        let path = self.key_path(key_id);
        if !path.exists() {
            return Err(KeyManagerError::KeyNotFound(key_id.to_string()));
        }
        let content = fs::read_to_string(path)?;
        let stored: StoredKey = serde_json::from_str(&content)?;
        Ok(stored)
    }
}

fn hex_to_32_bytes(hex_str: &str) -> Result<[u8; 32]> {
    let bytes = hex_to_vec(hex_str)?;
    if bytes.len() != 32 {
        return Err(KeyManagerError::SecurityError(SecurityError::InvalidSignature));
    }
    let mut out = [0u8; 32];
    out.copy_from_slice(&bytes);
    Ok(out)
}

fn hex_to_vec(hex_str: &str) -> Result<Vec<u8>> {
    hex::decode(hex_str).map_err(|_| KeyManagerError::SecurityError(SecurityError::InvalidSignature))
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_generate_and_load_ed25519() {
        let dir = tempdir().unwrap();
        let km = KeyManager::new(dir.path()).unwrap();

        let meta = km.generate_key("node-1", SignatureAlgorithm::Ed25519).unwrap();
        assert_eq!(meta.key_id, "node-1");
        assert!(meta.is_active);

        let signer = km.load_ed25519_signer("node-1").unwrap();
        let verifier = km.load_ed25519_verifier("node-1").unwrap();

        let msg = b"test message";
        let sig = signer.sign(msg).unwrap();
        assert!(verifier.verify(msg, &sig).is_ok());
    }

    #[test]
    fn test_generate_and_load_dilithium3() {
        let dir = tempdir().unwrap();
        let km = KeyManager::new(dir.path()).unwrap();

        let meta = km.generate_key("pq-node-1", SignatureAlgorithm::Dilithium3).unwrap();
        assert_eq!(meta.key_id, "pq-node-1");

        let signer = km.load_dilithium3_signer("pq-node-1").unwrap();
        let verifier = km.load_dilithium3_verifier("pq-node-1").unwrap();

        let msg = b"quantum safe message";
        let sig = signer.sign(msg).unwrap();
        assert!(verifier.verify(msg, &sig).is_ok());
    }

    #[test]
    fn test_key_rotation() {
        let dir = tempdir().unwrap();
        let km = KeyManager::new(dir.path()).unwrap();

        km.generate_key("key-v1", SignatureAlgorithm::Ed25519).unwrap();
        let rotated = km.rotate_key("key-v1", "key-v2").unwrap();

        assert_eq!(rotated.rotated_from, Some("key-v1".to_string()));
        assert!(rotated.is_active);

        // Old key should be inactive
        let keys = km.list_keys().unwrap();
        let old = keys.iter().find(|k| k.key_id == "key-v1").unwrap();
        assert!(!old.is_active);
    }

    #[test]
    fn test_list_and_delete_keys() {
        let dir = tempdir().unwrap();
        let km = KeyManager::new(dir.path()).unwrap();

        km.generate_key("a", SignatureAlgorithm::Ed25519).unwrap();
        km.generate_key("b", SignatureAlgorithm::Dilithium3).unwrap();

        let keys = km.list_keys().unwrap();
        assert_eq!(keys.len(), 2);

        km.delete_key("a").unwrap();
        let keys = km.list_keys().unwrap();
        assert_eq!(keys.len(), 1);
        assert_eq!(keys[0].key_id, "b");
    }

    #[test]
    fn test_duplicate_key_error() {
        let dir = tempdir().unwrap();
        let km = KeyManager::new(dir.path()).unwrap();

        km.generate_key("dup", SignatureAlgorithm::Ed25519).unwrap();
        let result = km.generate_key("dup", SignatureAlgorithm::Ed25519);
        assert!(matches!(result, Err(KeyManagerError::KeyAlreadyExists(_))));
    }
}
