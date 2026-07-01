use crate::types::*;
use chrono::Utc;
use std::collections::HashMap;

/// Difficulty adjustment engine
pub struct DifficultyAdjustmentEngine {
    config: EconomicConfig,
}

impl DifficultyAdjustmentEngine {
    /// Create a new difficulty adjustment engine
    pub fn new(config: EconomicConfig) -> Self {
        Self { config }
    }

    /// Calculate difficulty adjustment for a task family
    pub fn calculate_adjustment(
        &self,
        task_family: &str,
        current_difficulty: f64,
        completion_rate: f64,
    ) -> Result<DifficultyAdjustmentResult, EconomicError> {
        if current_difficulty <= 0.0 {
            return Err(EconomicError::InvalidDifficulty(current_difficulty));
        }

        if completion_rate < 0.0 || completion_rate > 1.0 {
            return Err(EconomicError::CalculationFailed(
                "Invalid completion rate".to_string(),
            ));
        }

        let target_rate = self.config.target_completion_rate;
        let sensitivity = self.config.difficulty_sensitivity;

        // Calculate adjustment factor
        let adjustment_factor = if completion_rate > target_rate {
            // Too easy: increase difficulty
            1.0 + sensitivity * (completion_rate - target_rate)
        } else if completion_rate < target_rate {
            // Too hard: decrease difficulty
            1.0 - sensitivity * (target_rate - completion_rate)
        } else {
            1.0 // No adjustment needed
        };

        // Apply adjustment
        let new_difficulty = current_difficulty * adjustment_factor;

        // Clamp to limits
        let clamped_difficulty = new_difficulty
            .max(self.config.min_difficulty_multiplier)
            .min(self.config.max_difficulty_multiplier);

        let reason = format!(
            "Completion rate {:.1}% vs target {:.1}%",
            completion_rate * 100.0,
            target_rate * 100.0
        );

        Ok(DifficultyAdjustmentResult {
            task_family: task_family.to_string(),
            old_difficulty: current_difficulty,
            new_difficulty: clamped_difficulty,
            adjustment_factor,
            reason,
            timestamp: Utc::now(),
        })
    }

    /// Batch calculate difficulty adjustments for multiple task families
    pub fn calculate_batch_adjustments(
        &self,
        task_families: &HashMap<String, TaskFamilyInfo>,
    ) -> Vec<DifficultyAdjustmentResult> {
        task_families
            .iter()
            .filter_map(|(name, info)| {
                self.calculate_adjustment(name, info.difficulty, info.completion_rate)
                    .ok()
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_difficulty_adjustment_increase() {
        let config = EconomicConfig::default();
        let engine = DifficultyAdjustmentEngine::new(config);

        let result = engine
            .calculate_adjustment("test", 1.0, 0.9) // 90% completion, target 80%
            .unwrap();

        assert!(result.new_difficulty > result.old_difficulty);
        println!("✅ Difficulty increase test passed: {} -> {}", result.old_difficulty, result.new_difficulty);
    }

    #[test]
    fn test_difficulty_adjustment_decrease() {
        let config = EconomicConfig::default();
        let engine = DifficultyAdjustmentEngine::new(config);

        let result = engine
            .calculate_adjustment("test", 1.0, 0.6) // 60% completion, target 80%
            .unwrap();

        assert!(result.new_difficulty < result.old_difficulty);
        println!("✅ Difficulty decrease test passed: {} -> {}", result.old_difficulty, result.new_difficulty);
    }

    #[test]
    fn test_difficulty_clamping() {
        let config = EconomicConfig::default();
        let engine = DifficultyAdjustmentEngine::new(config);

        // Test max clamp
        let result = engine
            .calculate_adjustment("test", 100.0, 1.0) // 100% completion
            .unwrap();
        assert!(result.new_difficulty <= config.max_difficulty_multiplier);

        // Test min clamp
        let result = engine
            .calculate_adjustment("test", 0.01, 0.0) // 0% completion
            .unwrap();
        assert!(result.new_difficulty >= config.min_difficulty_multiplier);

        println!("✅ Difficulty clamping test passed");
    }
}
