// UET Governance - Decentralized Governance System
//
// This crate provides voting protocols, proposal lifecycle management,
// and policy execution for the UET economic system.

pub mod types;
pub mod voting;
pub mod proposal;
pub mod policy;
pub mod ledger_integration;

pub use types::*;
pub use voting::VotingProtocol;
pub use proposal::ProposalManager;
pub use policy::{PolicyEngine, PolicyHandler};
pub use ledger_integration::{GovernanceEvent, GovernanceLedgerRecorder};

#[cfg(test)]
mod tests {
    use super::*;
    use crate::policy::{DifficultyAdjustmentHandler, TaskFamilyAdditionHandler};

    #[test]
    fn test_governance_roundtrip() {
        // Setup governance system
        let config = GovernanceConfig::default();
        let protocol = VotingProtocol::new(config, VotingPowerStrategy::OnePersonOneVote);
        let manager = ProposalManager::new(protocol);
        let mut engine = PolicyEngine::new(manager);

        // Register policy handlers
        engine.register_handler(
            "difficulty_adjustment".to_string(),
            Box::new(DifficultyAdjustmentHandler),
        );
        engine.register_handler(
            "task_family_addition".to_string(),
            Box::new(TaskFamilyAdditionHandler),
        );

        // Add voters
        let voter1 = Uuid::new_v4();
        let voter2 = Uuid::new_v4();
        let voter3 = Uuid::new_v4();

        engine.manager().add_voter(VoterInfo {
            id: voter1,
            name: "Voter 1".to_string(),
            voting_weight: 100,
            is_active: true,
        });
        engine.manager().add_voter(VoterInfo {
            id: voter2,
            name: "Voter 2".to_string(),
            voting_weight: 100,
            is_active: true,
        });
        engine.manager().add_voter(VoterInfo {
            id: voter3,
            name: "Voter 3".to_string(),
            voting_weight: 100,
            is_active: true,
        });

        // Create a proposal
        let proposal_id = engine
            .manager()
            .create_proposal(
                voter1,
                ProposalType::DifficultyAdjustment {
                    task_family: "cosmology".to_string(),
                    new_difficulty: 1.5,
                },
                "Increase Cosmology Difficulty".to_string(),
                "Adjust difficulty to maintain optimal work unit completion rate".to_string(),
            )
            .unwrap();

        // Submit for voting
        engine.manager().submit_proposal(proposal_id).unwrap();

        // Cast votes (2 approve, 1 reject)
        engine.manager().cast_vote(proposal_id, voter1, Vote::Approve).unwrap();
        engine.manager().cast_vote(proposal_id, voter2, Vote::Approve).unwrap();
        engine.manager().cast_vote(proposal_id, voter3, Vote::Reject).unwrap();

        // Finalize voting
        let status = engine.manager().finalize_voting(proposal_id).unwrap();
        assert_eq!(status, ProposalStatus::Passed);

        // Execute the proposal
        engine.execute_proposal(proposal_id).unwrap();

        // Verify execution
        let proposal = engine.manager().get_proposal(proposal_id).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Executed);
        assert!(proposal.execution_result.is_some());
        assert!(proposal.execution_result.as_ref().unwrap().success);

        println!("✅ Governance roundtrip test passed");
        println!("   Proposal ID: {}", proposal_id);
        println!("   Votes: 2 approve, 1 reject");
        println!("   Status: Executed");
    }

    #[test]
    fn test_quadratic_voting() {
        let config = GovernanceConfig::default();
        let protocol = VotingProtocol::new(config, VotingPowerStrategy::Quadratic);
        let manager = ProposalManager::new(protocol);

        // Add voters with different weights
        let voter1 = Uuid::new_v4();
        let voter2 = Uuid::new_v4();
        let voter3 = Uuid::new_v4();

        manager.add_voter(VoterInfo {
            id: voter1,
            name: "Voter 1".to_string(),
            voting_weight: 100, // sqrt = 10
            is_active: true,
        });
        manager.add_voter(VoterInfo {
            id: voter2,
            name: "Voter 2".to_string(),
            voting_weight: 400, // sqrt = 20
            is_active: true,
        });
        manager.add_voter(VoterInfo {
            id: voter3,
            name: "Voter 3".to_string(),
            voting_weight: 900, // sqrt = 30
            is_active: true,
        });

        // Verify quadratic voting power
        let power1 = protocol.calculate_voting_power(&voter1, &manager.state.voters).unwrap();
        let power2 = protocol.calculate_voting_power(&voter2, &manager.state.voters).unwrap();
        let power3 = protocol.calculate_voting_power(&voter3, &manager.state.voters).unwrap();

        assert_eq!(power1, 10);
        assert_eq!(power2, 20);
        assert_eq!(power3, 30);

        println!("✅ Quadratic voting test passed");
        println!("   Voter 1 (weight 100): power = {}", power1);
        println!("   Voter 2 (weight 400): power = {}", power2);
        println!("   Voter 3 (weight 900): power = {}", power3);
    }

    #[test]
    fn test_emergency_veto() {
        let config = GovernanceConfig::default();
        let protocol = VotingProtocol::new(config, VotingPowerStrategy::OnePersonOneVote);
        let mut manager = ProposalManager::new(protocol);

        // Set emergency authority
        let authority_id = Uuid::new_v4();
        manager.state.config.emergency_authority_id = Some(authority_id);

        // Add voters
        let voter_id = Uuid::new_v4();
        manager.add_voter(VoterInfo {
            id: voter_id,
            name: "Test Voter".to_string(),
            voting_weight: 100,
            is_active: true,
        });

        // Create a proposal
        let proposal_id = manager
            .create_proposal(
                voter_id,
                ProposalType::DifficultyAdjustment {
                    task_family: "test".to_string(),
                    new_difficulty: 1.0,
                },
                "Test Proposal".to_string(),
                "Test Description".to_string(),
            )
            .unwrap();

        // Veto the proposal
        manager.veto_proposal(proposal_id, authority_id).unwrap();

        // Verify vetoed status
        let proposal = manager.get_proposal(proposal_id).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Vetoed);

        println!("✅ Emergency veto test passed");
    }
}
