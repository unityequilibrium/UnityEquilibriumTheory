use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, Duration};
use uuid::Uuid;

/// Economic policy parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EconomicConfig {
    /// Target work unit completion rate (percentage)
    pub target_completion_rate: f64,
    /// Difficulty adjustment sensitivity (0.0 to 1.0)
    pub difficulty_sensitivity: f64,
    /// Maximum difficulty multiplier
    pub max_difficulty_multiplier: f64,
    /// Minimum difficulty multiplier
    pub min_difficulty_multiplier: f64,
    /// Epoch duration in hours
    pub epoch_duration_hours: u64,
    /// Maximum issuance per epoch
    pub max_issuance_per_epoch: u64,
    /// Minimum issuance per epoch
    pub min_issuance_per_epoch: u64,
    /// Maximum task family concentration (percentage)
    pub max_task_family_concentration: f64,
    /// Minimum task family weight
    pub min_task_family_weight: f64,
    /// Maximum task family weight
    pub max_task_family_weight: f64,
}

impl Default for EconomicConfig {
    fn default() -> Self {
        Self {
            target_completion_rate: 0.8, // 80% target completion
            difficulty_sensitivity: 0.1,
            max_difficulty_multiplier: 10.0,
            min_difficulty_multiplier: 0.1,
            epoch_duration_hours: 24, // 24 hours per epoch
            max_issuance_per_epoch: 1_000_000,
            min_issuance_per_epoch: 100_000,
            max_task_family_concentration: 0.5, // Max 50% concentration
            min_task_family_weight: 0.05,
            max_task_family_weight: 0.5,
        }
    }
}

/// Task family information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskFamilyInfo {
    pub name: String,
    pub weight: f64,
    pub difficulty: f64,
    pub completion_rate: f64,
    pub work_units_completed: u64,
    pub work_units_assigned: u64,
}

/// Difficulty adjustment result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DifficultyAdjustmentResult {
    pub task_family: String,
    pub old_difficulty: f64,
    pub new_difficulty: f64,
    pub adjustment_factor: f64,
    pub reason: String,
    pub timestamp: DateTime<Utc>,
}

/// Issuance budget calculation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IssuanceBudgetResult {
    pub epoch: u64,
    pub total_issuance: u64,
    pub energy_input_kwh: f64,
    pub issuance_per_kwh: f64,
    pub timestamp: DateTime<Utc>,
}

/// Portfolio rotation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PortfolioRotationResult {
    pub added_families: Vec<String>,
    pub removed_families: Vec<String>,
    pub adjusted_weights: Vec<(String, f64)>,
    pub timestamp: DateTime<Utc>,
}

/// Economic error types
#[derive(Debug, thiserror::Error)]
pub enum EconomicError {
    #[error("Task family not found: {0}")]
    TaskFamilyNotFound(String),

    #[error("Invalid difficulty value: {0}")]
    InvalidDifficulty(f64),

    #[error("Invalid weight value: {0}")]
    InvalidWeight(f64),

    #[error("Concentration limit exceeded: {0}% > {1}%")]
    ConcentrationLimitExceeded(f64, f64),

    #[error("Insufficient data for calculation")]
    InsufficientData,

    #[error("Calculation failed: {0}")]
    CalculationFailed(String),
}
