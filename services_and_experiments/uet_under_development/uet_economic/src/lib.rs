// UET Economic - Economic Policy Engine
//
// This crate provides economic policy engines for difficulty adjustment,
// issuance budget calculation, and portfolio rotation.

pub mod types;
pub mod difficulty;
pub mod issuance;
pub mod portfolio;
pub mod governance_integration;

pub use types::*;
pub use difficulty::DifficultyAdjustmentEngine;
pub use issuance::IssuanceBudgetEngine;
pub use portfolio::PortfolioRotationEngine;
pub use governance_integration::{EconomicPolicyHandler, EconomicPolicyAction};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_economic_roundtrip() {
        let config = EconomicConfig::default();

        // Difficulty adjustment
        let diff_engine = DifficultyAdjustmentEngine::new(config.clone());
        let diff_result = diff_engine
            .calculate_adjustment("cosmology", 1.0, 0.9)
            .unwrap();
        assert!(diff_result.new_difficulty > diff_result.old_difficulty);

        // Issuance budget
        let issuance_engine = IssuanceBudgetEngine::new(config.clone());
        let issuance_result = issuance_engine
            .calculate_budget(1, 500_000.0, 100_000)
            .unwrap();
        assert!(issuance_result.total_issuance > 0);

        // Portfolio rotation
        let portfolio_engine = PortfolioRotationEngine::new(config);
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
        let rotation_result = portfolio_engine.rotate_portfolio(&portfolio, vec!["neutrino".to_string()]);
        assert!(rotation_result.added_families.contains(&"neutrino".to_string()));

        println!("✅ Economic roundtrip test passed");
    }
}
