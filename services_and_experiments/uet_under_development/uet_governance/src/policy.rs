use crate::types::*;
use crate::proposal::ProposalManager;
use std::collections::HashMap;

/// Policy execution engine
pub struct PolicyEngine {
    manager: ProposalManager,
    policy_handlers: HashMap<String, Box<dyn PolicyHandler>>,
}

/// Trait for handling policy execution
pub trait PolicyHandler: Send + Sync {
    fn execute(&self, proposal: &Proposal) -> Result<ExecutionResult, GovernanceError>;
}

impl PolicyEngine {
    /// Create a new policy engine
    pub fn new(manager: ProposalManager) -> Self {
        Self {
            manager,
            policy_handlers: HashMap::new(),
        }
    }

    /// Register a policy handler
    pub fn register_handler(&mut self, policy_name: String, handler: Box<dyn PolicyHandler>) {
        self.policy_handlers.insert(policy_name, handler);
    }

    /// Execute a passed proposal
    pub fn execute_proposal(&mut self, proposal_id: ProposalId) -> Result<(), GovernanceError> {
        let proposal = self.manager.get_proposal(proposal_id)
            .ok_or(GovernanceError::ProposalNotFound(proposal_id))?;

        if proposal.status != ProposalStatus::Passed {
            return Err(GovernanceError::InvalidProposalType);
        }

        // Get the appropriate handler based on proposal type
        let handler_key = match &proposal.proposal_type {
            ProposalType::DifficultyAdjustment { .. } => "difficulty_adjustment",
            ProposalType::IssuanceBudgetAdjustment { .. } => "issuance_budget",
            ProposalType::TaskFamilyAddition { .. } => "task_family_addition",
            ProposalType::TaskFamilyRemoval { .. } => "task_family_removal",
            ProposalType::TaskFamilyWeightAdjustment { .. } => "task_family_weight",
            ProposalType::EmergencyDisable { .. } => "emergency_disable",
            ProposalType::OracleConfigUpdate { .. } => "oracle_config",
            ProposalType::GovernanceParameterUpdate { .. } => "governance_param",
            ProposalType::MintingPolicyUpdate { .. } => "minting_policy",
        };

        let handler = self.policy_handlers.get(handler_key)
            .ok_or(GovernanceError::ExecutionFailed(
                "No handler registered for this proposal type".to_string()
            ))?;

        // Execute the policy
        let result = handler.execute(proposal)?;

        // Update proposal status
        if let Some(p) = self.manager.get_proposal_mut(proposal_id) {
            p.execution_result = Some(result.clone());
            p.status = if result.success {
                ProposalStatus::Executed
            } else {
                ProposalStatus::ExecutionFailed
            };
        }

        Ok(())
    }

    /// Get the proposal manager
    pub fn manager(&mut self) -> &mut ProposalManager {
        &mut self.manager
    }
}

/// Example handler for difficulty adjustment
pub struct DifficultyAdjustmentHandler;

impl PolicyHandler for DifficultyAdjustmentHandler {
    fn execute(&self, proposal: &Proposal) -> Result<ExecutionResult, GovernanceError> {
        if let ProposalType::DifficultyAdjustment { task_family, new_difficulty } = &proposal.proposal_type {
            // In a real implementation, this would update the difficulty in the chain
            println!(
                "Adjusting difficulty for task family '{}' to {}",
                task_family, new_difficulty
            );

            Ok(ExecutionResult {
                success: true,
                message: format!(
                    "Difficulty adjusted for {} to {}",
                    task_family, new_difficulty
                ),
                executed_at: chrono::Utc::now(),
            })
        } else {
            Err(GovernanceError::InvalidProposalType)
        }
    }
}

/// Example handler for task family addition
pub struct TaskFamilyAdditionHandler;

impl PolicyHandler for TaskFamilyAdditionHandler {
    fn execute(&self, proposal: &Proposal) -> Result<ExecutionResult, GovernanceError> {
        if let ProposalType::TaskFamilyAddition { family_name, weight } = &proposal.proposal_type {
            // In a real implementation, this would add the task family to the portfolio
            println!(
                "Adding task family '{}' with weight {}",
                family_name, weight
            );

            Ok(ExecutionResult {
                success: true,
                message: format!(
                    "Task family {} added with weight {}",
                    family_name, weight
                ),
                executed_at: chrono::Utc::now(),
            })
        } else {
            Err(GovernanceError::InvalidProposalType)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::voting::VotingProtocol;

    #[test]
    fn test_policy_execution() {
        let config = GovernanceConfig::default();
        let protocol = VotingProtocol::new(config, VotingPowerStrategy::OnePersonOneVote);
        let manager = ProposalManager::new(protocol);
        let mut engine = PolicyEngine::new(manager);

        // Register handlers
        engine.register_handler(
            "difficulty_adjustment".to_string(),
            Box::new(DifficultyAdjustmentHandler),
        );
        engine.register_handler(
            "task_family_addition".to_string(),
            Box::new(TaskFamilyAdditionHandler),
        );

        // Add a voter
        let voter_id = Uuid::new_v4();
        engine.manager().add_voter(VoterInfo {
            id: voter_id,
            name: "Test Voter".to_string(),
            voting_weight: 100,
            is_active: true,
        });

        // Create and submit a proposal
        let proposal_id = engine
            .manager()
            .create_proposal(
                voter_id,
                ProposalType::DifficultyAdjustment {
                    task_family: "test".to_string(),
                    new_difficulty: 1.5,
                },
                "Test Proposal".to_string(),
                "Test Description".to_string(),
            )
            .unwrap();

        engine.manager().submit_proposal(proposal_id).unwrap();
        engine.manager().cast_vote(proposal_id, voter_id, Vote::Approve).unwrap();

        // Finalize voting (manually set status for testing)
        if let Some(p) = engine.manager().get_proposal_mut(proposal_id) {
            p.status = ProposalStatus::Passed;
        }

        // Execute the proposal
        engine.execute_proposal(proposal_id).unwrap();

        let proposal = engine.manager().get_proposal(proposal_id).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Executed);
    }
}
