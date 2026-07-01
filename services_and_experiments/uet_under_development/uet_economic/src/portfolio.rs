use crate::types::*;
use std::collections::HashMap;
use chrono::Utc;

/// Portfolio rotation engine
pub struct PortfolioRotationEngine {
    config: EconomicConfig,
}

impl PortfolioRotationEngine {
    /// Create a new portfolio rotation engine
    pub fn new(config: EconomicConfig) -> Self {
        Self { config }
    }

    /// Check if a task family should be added to the portfolio
    pub fn should_add_family(
        &self,
        family_name: &str,
        current_portfolio: &HashMap<String, TaskFamilyInfo>,
    ) -> bool {
        // Check if already exists
        if current_portfolio.contains_key(family_name) {
            return false;
        }

        // Check concentration limit
        let total_weight: f64 = current_portfolio.values().map(|f| f.weight).sum();
        if total_weight >= 0.95 {
            return false; // Portfolio nearly full
        }

        true
    }

    /// Check if a task family should be removed from the portfolio
    pub fn should_remove_family(
        &self,
        family_name: &str,
        task_family: &TaskFamilyInfo,
    ) -> bool {
        // Remove if completion rate is too low (too hard)
        if task_family.completion_rate < 0.1 {
            return true;
        }

        // Remove if concentration is too high
        if task_family.weight > self.config.max_task_family_weight {
            return true;
        }

        false
    }

    /// Calculate weight adjustments for task families
    pub fn calculate_weight_adjustments(
        &self,
        task_families: &HashMap<String, TaskFamilyInfo>,
    ) -> Vec<(String, f64)> {
        let mut adjustments = Vec::new();

        for (name, info) in task_families {
            let new_weight = if info.completion_rate > 0.9 {
                // Too easy: decrease weight
                (info.weight * 0.9).max(self.config.min_task_family_weight)
            } else if info.completion_rate < 0.5 {
                // Too hard: decrease weight
                (info.weight * 0.8).max(self.config.min_task_family_weight)
            } else {
                // Optimal: maintain weight
                info.weight
            };

            if (new_weight - info.weight).abs() > 0.01 {
                adjustments.push((name.clone(), new_weight));
            }
        }

        adjustments
    }

    /// Execute portfolio rotation
    pub fn rotate_portfolio(
        &self,
        current_portfolio: &HashMap<String, TaskFamilyInfo>,
        new_families: Vec<String>,
    ) -> PortfolioRotationResult {
        let mut added_families = Vec::new();
        let mut removed_families = Vec::new();
        let mut adjusted_weights = Vec::new();

        // Check for families to add
        for family_name in new_families {
            if self.should_add_family(&family_name, current_portfolio) {
                added_families.push(family_name);
            }
        }

        // Check for families to remove
        for (name, info) in current_portfolio {
            if self.should_remove_family(name, info) {
                removed_families.push(name.clone());
            }
        }

        // Calculate weight adjustments
        let adjustments = self.calculate_weight_adjustments(current_portfolio);
        adjusted_weights = adjustments;

        PortfolioRotationResult {
            added_families,
            removed_families,
            adjusted_weights,
            timestamp: Utc::now(),
        }
    }

    /// Check concentration limits
    pub fn check_concentration(
        &self,
        task_families: &HashMap<String, TaskFamilyInfo>,
    ) -> Result<(), EconomicError> {
        for (name, info) in task_families {
            if info.weight > self.config.max_task_family_weight {
                return Err(EconomicError::ConcentrationLimitExceeded(
                    info.weight * 100.0,
                    self.config.max_task_family_weight * 100.0,
                ));
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_portfolio_rotation() {
        let config = EconomicConfig::default();
        let engine = PortfolioRotationEngine::new(config);

        let mut portfolio = HashMap::new();
        portfolio.insert(
            "cosmology".to_string(),
            TaskFamilyInfo {
                name: "cosmology".to_string(),
                weight: 0.3,
                difficulty: 1.0,
                completion_rate: 0.9,
                work_units_completed: 1000,
                work_units_assigned: 1111,
            },
        );

        let result = engine.rotate_portfolio(&portfolio, vec!["neutrino".to_string()]);

        assert!(result.added_families.contains(&"neutrino".to_string()));
        println!("✅ Portfolio rotation test passed: added {:?}", result.added_families);
    }

    #[test]
    fn test_concentration_check() {
        let config = EconomicConfig::default();
        let engine = PortfolioRotationEngine::new(config);

        let mut portfolio = HashMap::new();
        portfolio.insert(
            "test".to_string(),
            TaskFamilyInfo {
                name: "test".to_string(),
                weight: 0.6, // Above max 0.5
                difficulty: 1.0,
                completion_rate: 0.8,
                work_units_completed: 1000,
                work_units_assigned: 1250,
            },
        );

        let result = engine.check_concentration(&portfolio);
        assert!(result.is_err());

        println!("✅ Concentration check test passed");
    }

    #[test]
    fn test_weight_adjustments() {
        let config = EconomicConfig::default();
        let engine = PortfolioRotationEngine::new(config);

        let mut portfolio = HashMap::new();
        portfolio.insert(
            "easy_task".to_string(),
            TaskFamilyInfo {
                name: "easy_task".to_string(),
                weight: 0.4,
                difficulty: 1.0,
                completion_rate: 0.95, // Too easy
                work_units_completed: 950,
                work_units_assigned: 1000,
            },
        );

        let adjustments = engine.calculate_weight_adjustments(&portfolio);
        assert!(!adjustments.is_empty());

        println!("✅ Weight adjustments test passed: {:?}", adjustments);
    }
}
