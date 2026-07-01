// Governance-Chain Integration
//
// This module integrates the governance system with the ledger,
// recording proposals, votes, and execution results on-chain.

use crate::*;
use uet_chain::*;
use uet_security::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

/// Governance event types for ledger recording
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum GovernanceEvent {
    ProposalCreated {
        proposal_id: Uuid,
        proposer_id: Uuid,
        proposal_type: ProposalType,
        title: String,
        description: String,
        timestamp: DateTime<Utc>,
    },
    VoteCast {
        proposal_id: Uuid,
        voter_id: Uuid,
        vote: Vote,
        voting_power: u64,
        timestamp: DateTime<Utc>,
    },
    ProposalFinalized {
        proposal_id: Uuid,
        status: ProposalStatus,
        approval_votes: u64,
        total_votes: u64,
        timestamp: DateTime<Utc>,
    },
    PolicyExecuted {
        proposal_id: Uuid,
        policy_type: String,
        result: ExecutionResult,
        timestamp: DateTime<Utc>,
    },
}

/// Governance ledger recorder
pub struct GovernanceLedgerRecorder {
    // In a real implementation, this would hold a reference to the chain
}

impl GovernanceLedgerRecorder {
    /// Create a new governance ledger recorder
    pub fn new() -> Self {
        Self {}
    }

    /// Record a governance event to the ledger
    pub fn record_event(&self, event: GovernanceEvent) -> Result<(), GovernanceError> {
        // In a real implementation, this would:
        // 1. Serialize the event
        // 2. Create a transaction
        // 3. Submit to the chain
        // 4. Wait for confirmation

        println!("Recording governance event: {:?}", event);
        Ok(())
    }

    /// Create a proposal and record it
    pub fn create_and_record_proposal(
        &self,
        proposer_id: Uuid,
        proposal_type: ProposalType,
        title: String,
        description: String,
    ) -> Result<Uuid, GovernanceError> {
        let proposal_id = Uuid::new_v4();

        let event = GovernanceEvent::ProposalCreated {
            proposal_id,
            proposer_id,
            proposal_type,
            title,
            description,
            timestamp: Utc::now(),
        };

        self.record_event(event)?;
        Ok(proposal_id)
    }

    /// Record a vote
    pub fn record_vote(
        &self,
        proposal_id: Uuid,
        voter_id: Uuid,
        vote: Vote,
        voting_power: u64,
    ) -> Result<(), GovernanceError> {
        let event = GovernanceEvent::VoteCast {
            proposal_id,
            voter_id,
            vote,
            voting_power,
            timestamp: Utc::now(),
        };

        self.record_event(event)
    }

    /// Record proposal finalization
    pub fn record_finalization(
        &self,
        proposal_id: Uuid,
        status: ProposalStatus,
        approval_votes: u64,
        total_votes: u64,
    ) -> Result<(), GovernanceError> {
        let event = GovernanceEvent::ProposalFinalized {
            proposal_id,
            status,
            approval_votes,
            total_votes,
            timestamp: Utc::now(),
        };

        self.record_event(event)
    }

    /// Record policy execution
    pub fn record_execution(
        &self,
        proposal_id: Uuid,
        policy_type: String,
        result: ExecutionResult,
    ) -> Result<(), GovernanceError> {
        let event = GovernanceEvent::PolicyExecuted {
            proposal_id,
            policy_type,
            result,
            timestamp: Utc::now(),
        };

        self.record_event(event)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_governance_ledger_recorder() {
        let recorder = GovernanceLedgerRecorder::new();

        // Create proposal
        let proposal_id = recorder
            .create_and_record_proposal(
                Uuid::new_v4(),
                ProposalType::DifficultyAdjustment,
                "Adjust Cosmology Difficulty".to_string(),
                "Increase difficulty to 1.1".to_string(),
            )
            .unwrap();

        // Record vote
        recorder
            .record_vote(
                proposal_id,
                Uuid::new_v4(),
                Vote::Approve,
                1000,
            )
            .unwrap();

        // Record finalization
        recorder
            .record_finalization(
                proposal_id,
                ProposalStatus::Passed,
                800,
                1000,
            )
            .unwrap();

        println!("✅ Governance ledger recorder test passed");
    }
}
