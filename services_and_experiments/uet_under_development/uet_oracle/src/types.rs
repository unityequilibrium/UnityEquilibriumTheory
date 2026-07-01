use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

/// Unique identifier for an oracle
pub type OracleId = Uuid;

/// Oracle types
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum OracleType {
    /// Energy oracle: verifies electricity consumption
    Energy,
    /// Land oracle: verifies land registry
    Land,
    /// Asset oracle: verifies Bitcoin/Gold/patents
    Asset,
}

/// Oracle status
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum OracleStatus {
    /// Oracle is active and responding
    Active,
    /// Oracle is inactive
    Inactive,
    /// Oracle is under maintenance
    Maintenance,
    /// Oracle is compromised
    Compromised,
}

/// Oracle reputation score
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReputationScore {
    pub oracle_id: OracleId,
    pub score: f64, // 0.0 to 1.0
    pub total_reports: u64,
    pub correct_reports: u64,
    pub last_updated: DateTime<Utc>,
}

impl ReputationScore {
    /// Calculate reputation based on correct reports
    pub fn calculate(&mut self, is_correct: bool) {
        self.total_reports += 1;
        if is_correct {
            self.correct_reports += 1;
        }
        self.score = if self.total_reports > 0 {
            self.correct_reports as f64 / self.total_reports as f64
        } else {
            0.0
        };
        self.last_updated = Utc::now();
    }

    /// Check if oracle is reputable enough
    pub fn is_reputable(&self, threshold: f64) -> bool {
        self.score >= threshold && self.total_reports >= 10
    }
}

/// Oracle configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OracleConfig {
    pub oracle_type: OracleType,
    pub endpoint: String,
    pub api_key: Option<String>,
    pub timeout_seconds: u64,
    pub min_reputation_threshold: f64,
}

/// Oracle information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OracleInfo {
    pub id: OracleId,
    pub name: String,
    pub oracle_type: OracleType,
    pub config: OracleConfig,
    pub status: OracleStatus,
    pub reputation: ReputationScore,
    pub created_at: DateTime<Utc>,
}

/// Energy verification request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnergyVerificationRequest {
    pub node_id: Uuid,
    pub period_start: DateTime<Utc>,
    pub period_end: DateTime<Utc>,
    pub expected_kwh: f64,
}

/// Energy verification response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnergyVerificationResponse {
    pub verified: bool,
    pub actual_kwh: f64,
    pub verification_timestamp: DateTime<Utc>,
    pub oracle_id: OracleId,
    pub signature: String,
}

/// Land verification request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LandVerificationRequest {
    pub land_id: String,
    pub jurisdiction: String,
    pub owner_id: String,
}

/// Land verification response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LandVerificationResponse {
    pub verified: bool,
    pub land_area_sqm: f64,
    pub owner_verified: bool,
    pub verification_timestamp: DateTime<Utc>,
    pub oracle_id: OracleId,
    pub signature: String,
}

/// Asset verification request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AssetVerificationRequest {
    pub asset_type: String, // "bitcoin", "gold", "patent"
    pub asset_id: String,
    pub expected_amount: f64,
}

/// Asset verification response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AssetVerificationResponse {
    pub verified: bool,
    pub actual_amount: f64,
    pub verification_timestamp: DateTime<Utc>,
    pub oracle_id: OracleId,
    pub signature: String,
}

/// Oracle error types
#[derive(Debug, thiserror::Error)]
pub enum OracleError {
    #[error("Oracle not found: {0}")]
    OracleNotFound(OracleId),

    #[error("Oracle is not active: {0:?}")]
    OracleNotActive(OracleStatus),

    #[error("Oracle reputation too low: {0} < {1}")]
    ReputationTooLow(f64, f64),

    #[error("Verification failed: {0}")]
    VerificationFailed(String),

    #[error("Network error: {0}")]
    NetworkError(String),

    #[error("Timeout after {0} seconds")]
    Timeout(u64),

    #[error("Invalid response format")]
    InvalidResponseFormat,

    #[error("Signature verification failed")]
    SignatureVerificationFailed,
}
