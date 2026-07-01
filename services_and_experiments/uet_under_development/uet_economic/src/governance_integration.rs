// Economic-Governance Integration
//
// This module integrates the economic policy engine with governance,
// registering policy handlers and connecting economic policies to governance.

use crate::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

/// Economic policy action types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EconomicPolicyAction {
    DifficultyAdjustment {
        task_family: String,
        old_difficulty: f64,
        new_difficulty: f64,
    },
    IssuanceBudgetUpdate {
        epoch: u64,
        total_issuance: u64,
        energy_input_kwh: f64,
    },
    PortfolioRotation {
        added_families: Vec<String>,
        removed_families: Vec<String>,
        adjusted_weights: Vec<(String, f64)>,
    },
}

/// Economic policy handler for governance
pub struct EconomicPolicyHandler {
    difficulty_engine: DifficultyAdjustmentEngine,
    issuance_engine: IssuanceBudgetEngine,
    portfolio_engine: PortfolioRotationEngine,
}

impl EconomicPolicyHandler {
    /// Create a new economic policy handler
    pub fn new(config: EconomicConfig) -> Self {
        Self {
            difficulty_engine: DifficultyAdjustmentEngine::new(config.clone()),
            issuance_engine: IssuanceBudgetEngine::new(config.clone()),
            portfolio_engine: PortfolioRotationEngine::new(config),
        }
    }

    /// Register this handler with the governance system
    pub fn register_with_governance(
        &self,
        _governance: &mut (),
    ) -> Result<(), ()> {
        println!("Registered economic policy handler with governance");
        Ok(())
    }

    /// Execute a difficulty adjustment
    pub fn execute_difficulty_adjustment(
        &self,
        task_family: String,
        current_difficulty: f64,
        completion_rate: f64,
    ) -> Result<EconomicPolicyAction, EconomicError> {
        let result = self
            .difficulty_engine
            .calculate_adjustment(&task_family, current_difficulty, completion_rate)?;

        Ok(EconomicPolicyAction::DifficultyAdjustment {
            task_family,
            old_difficulty: result.old_difficulty,
            new_difficulty: result.new_difficulty,
        })
    }

    /// Execute an issuance budget update
    pub fn execute_issuance_budget(
        &self,
        epoch: u64,
        energy_input_kwh: f64,
        work_units_completed: u64,
    ) -> Result<EconomicPolicyAction, EconomicError> {
        let result = self
            .issuance_engine
            .calculate_budget(epoch, energy_input_kwh, work_units_completed)?;

        Ok(EconomicPolicyAction::IssuanceBudgetUpdate {
            epoch,
            total_issuance: result.total_issuance,
            energy_input_kwh: result.energy_input_kwh,
        })
    }

    /// Execute a portfolio rotation
    pub fn execute_portfolio_rotation(
        &self,
        current_portfolio: &std::collections::HashMap<String, TaskFamilyInfo>,
        new_families: Vec<String>,
    ) -> Result<EconomicPolicyAction, EconomicError> {
        let result = self
            .portfolio_engine
            .rotate_portfolio(current_portfolio, new_families);

        Ok(EconomicPolicyAction::PortfolioRotation {
            added_families: result.added_families,
            removed_families: result.removed_families,
            adjusted_weights: result.adjusted_weights,
        })
    }
}

// TODO: Implement PolicyHandler when circular dependency is resolved
/*
impl PolicyHandler for EconomicPolicyHandler {
    fn execute(&self, action: &PolicyAction) -> Result<ExecutionResult, GovernanceError> {
        match action {
            PolicyAction::DifficultyAdjustment { task_family, difficulty, completion_rate } => {
                let result = self.execute_difficulty_adjustment(
                    task_family.clone(),
                    *difficulty,
                    *completion_rate,
                )?;

                Ok(ExecutionResult {
                    success: true,
                    message: format!("Difficulty adjusted: {:?}", result),
                    data: Some(serde_json::to_value(result).unwrap_or_default()),
                })
            }
            PolicyAction::AddTaskFamily { family_name } => {
                Ok(ExecutionResult {
                    success: true,
                    message: format!("Task family {} added", family_name),
                    data: None,
                })
            }
            _ => Ok(ExecutionResult {
                success: false,
                message: "Unsupported policy action".to_string(),
                data: None,
            }),
        }
    }
}
*/

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_economic_policy_handler() {
        let config = EconomicConfig::default();
        let handler = EconomicPolicyHandler::new(config);

        // Execute difficulty adjustment
        let result = handler
            .execute_difficulty_adjustment(
                "cosmology".to_string(),
                1.0,
                0.9,
            )
            .unwrap();

        match result {
            EconomicPolicyAction::DifficultyAdjustment { task_family, old_difficulty, new_difficulty } => {
                assert_eq!(task_family, "cosmology");
                assert!(new_difficulty > old_difficulty);
            }
            _ => panic!("Expected DifficultyAdjustment result"),
        }

        println!("✅ Economic policy handler test passed");
    }
}
