use crate::types::*;
use chrono::Utc;

/// Issuance budget engine
pub struct IssuanceBudgetEngine {
    config: EconomicConfig,
}

impl IssuanceBudgetEngine {
    /// Create a new issuance budget engine
    pub fn new(config: EconomicConfig) -> Self {
        Self { config }
    }

    /// Calculate issuance budget for an epoch
    pub fn calculate_budget(
        &self,
        epoch: u64,
        energy_input_kwh: f64,
        work_units_completed: u64,
    ) -> Result<IssuanceBudgetResult, EconomicError> {
        if energy_input_kwh <= 0.0 {
            return Err(EconomicError::InsufficientData);
        }

        if work_units_completed == 0 {
            return Err(EconomicError::InsufficientData);
        }

        // Calculate issuance based on energy input
        // More energy = more issuance (up to max)
        let issuance_per_kwh = self.config.max_issuance_per_epoch as f64 / 1_000_000.0; // Base rate
        let calculated_issuance = (energy_input_kwh * issuance_per_kwh) as u64;

        // Clamp to limits
        let clamped_issuance = calculated_issuance
            .max(self.config.min_issuance_per_epoch)
            .min(self.config.max_issuance_per_epoch);

        Ok(IssuanceBudgetResult {
            epoch,
            total_issuance: clamped_issuance,
            energy_input_kwh,
            issuance_per_kwh,
            timestamp: Utc::now(),
        })
    }

    /// Calculate issuance based on work units
    pub fn calculate_by_work_units(
        &self,
        epoch: u64,
        work_units: u64,
        base_issuance_per_unit: f64,
    ) -> Result<IssuanceBudgetResult, EconomicError> {
        if work_units == 0 {
            return Err(EconomicError::InsufficientData);
        }

        let calculated_issuance = (work_units as f64 * base_issuance_per_unit) as u64;

        // Clamp to limits
        let clamped_issuance = calculated_issuance
            .max(self.config.min_issuance_per_epoch)
            .min(self.config.max_issuance_per_epoch);

        Ok(IssuanceBudgetResult {
            epoch,
            total_issuance: clamped_issuance,
            energy_input_kwh: 0.0,
            issuance_per_kwh: base_issuance_per_unit,
            timestamp: Utc::now(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_issuance_calculation() {
        let config = EconomicConfig::default();
        let engine = IssuanceBudgetEngine::new(config);

        let result = engine
            .calculate_budget(1, 500_000.0, 100_000) // 500k kWh, 100k work units
            .unwrap();

        assert!(result.total_issuance >= config.min_issuance_per_epoch);
        assert!(result.total_issuance <= config.max_issuance_per_epoch);

        println!("✅ Issuance calculation test passed: {} UET Coin", result.total_issuance);
    }

    #[test]
    fn test_issuance_clamping() {
        let config = EconomicConfig::default();
        let engine = IssuanceBudgetEngine::new(config);

        // Test max clamp (extreme energy input)
        let result = engine
            .calculate_budget(1, 10_000_000.0, 1_000_000)
            .unwrap();
        assert!(result.total_issuance <= config.max_issuance_per_epoch);

        // Test min clamp (minimal energy input)
        let result = engine
            .calculate_budget(1, 1.0, 1)
            .unwrap();
        assert!(result.total_issuance >= config.min_issuance_per_epoch);

        println!("✅ Issuance clamping test passed");
    }
}
