use crate::types::*;
use crate::voting::VotingProtocol;
use chrono::{Duration, Utc};
use std::collections::HashMap;
use uuid::Uuid;

/// Proposal lifecycle manager
pub struct ProposalManager {
    protocol: VotingProtocol,
    state: GovernanceState,
}

impl ProposalManager {
    /// Create a new proposal manager
    pub fn new(protocol: VotingProtocol) -> Self {
        Self {
            protocol,
            state: GovernanceState {
                proposals: HashMap::new(),
                config: GovernanceConfig::default(),
                voters: HashMap::new(),
            },
        }
    }

    /// Add a voter to the governance system
    pub fn add_voter(&mut self, voter: VoterInfo) {
        self.state.voters.insert(voter.id, voter);
    }

    /// Create a new proposal
    pub fn create_proposal(
        &mut self,
        proposer_id: VoterId,
        proposal_type: ProposalType,
        title: String,
        description: String,
    ) -> Result<ProposalId, GovernanceError> {
        // Verify proposer exists and is active
        let proposer = self.state.voters.get(&proposer_id)
            .ok_or(GovernanceError::VoterNotFound(proposer_id))?;

        if !proposer.is_active {
            return Err(GovernanceError::Unauthorized);
        }

        let proposal = Proposal {
            id: Uuid::new_v4(),
            proposal_type,
            proposer_id,
            title,
            description,
            created_at: Utc::now(),
            voting_start: None,
            voting_end: None,
            status: ProposalStatus::Draft,
            votes: HashMap::new(),
            execution_result: None,
        };

        let proposal_id = proposal.id;
        self.state.proposals.insert(proposal_id, proposal);

        Ok(proposal_id)
    }

    /// Submit a proposal for voting
    pub fn submit_proposal(&mut self, proposal_id: ProposalId) -> Result<(), GovernanceError> {
        let proposal = self.state.proposals.get_mut(&proposal_id)
            .ok_or(GovernanceError::ProposalNotFound(proposal_id))?;

        if proposal.status != ProposalStatus::Draft {
            return Err(GovernanceError::InvalidProposalType);
        }

        let now = Utc::now();
        let voting_start = now;
        let voting_end = now + Duration::hours(self.protocol.config().max_voting_period_hours as i64);

        proposal.voting_start = Some(voting_start);
        proposal.voting_end = Some(voting_end);
        proposal.status = ProposalStatus::Voting;

        Ok(())
    }

    /// Cast a vote on a proposal
    pub fn cast_vote(
        &mut self,
        proposal_id: ProposalId,
        voter_id: VoterId,
        vote: Vote,
    ) -> Result<(), GovernanceError> {
        let proposal = self.state.proposals.get_mut(&proposal_id)
            .ok_or(GovernanceError::ProposalNotFound(proposal_id))?;

        if proposal.status != ProposalStatus::Voting {
            return Err(GovernanceError::ProposalNotInVotingStatus);
        }

        // Verify voter exists and is active
        let voter = self.state.voters.get(&voter_id)
            .ok_or(GovernanceError::VoterNotFound(voter_id))?;

        if !voter.is_active {
            return Err(GovernanceError::Unauthorized);
        }

        // Check if voting period has ended
        if let Some(voting_end) = proposal.voting_end {
            if Utc::now() > voting_end {
                return Err(GovernanceError::VotingPeriodEnded);
            }
        }

        // Record the vote
        proposal.votes.insert(voter_id, vote);

        Ok(())
    }

    /// Finalize voting for a proposal
    pub fn finalize_voting(&mut self, proposal_id: ProposalId) -> Result<ProposalStatus, GovernanceError> {
        let proposal = self.state.proposals.get_mut(&proposal_id)
            .ok_or(GovernanceError::ProposalNotFound(proposal_id))?;

        if proposal.status != ProposalStatus::Voting {
            return Err(GovernanceError::ProposalNotInVotingStatus);
        }

        // Check if voting period has ended
        if let Some(voting_end) = proposal.voting_end {
            if Utc::now() < voting_end {
                return Err(GovernanceError::VotingNotStarted);
            }
        }

        // Check if proposal passes
        match self.protocol.check_proposal_passes(proposal, &self.state.voters) {
            Ok(true) => {
                proposal.status = ProposalStatus::Passed;
            }
            Ok(false) => {
                proposal.status = ProposalStatus::Failed;
            }
            Err(_) => {
                proposal.status = ProposalStatus::Failed;
            }
        }

        Ok(proposal.status.clone())
    }

    /// Get mutable reference to proposal (internal use)
    pub fn get_proposal_mut(&mut self, proposal_id: ProposalId) -> Option<&mut Proposal> {
        self.state.proposals.get_mut(&proposal_id)
    }

    /// Cancel a proposal (only by proposer)
    pub fn cancel_proposal(&mut self, proposal_id: ProposalId, proposer_id: VoterId) -> Result<(), GovernanceError> {
        let proposal = self.state.proposals.get_mut(&proposal_id)
            .ok_or(GovernanceError::ProposalNotFound(proposal_id))?;

        if proposal.proposer_id != proposer_id {
            return Err(GovernanceError::Unauthorized);
        }

        if proposal.status != ProposalStatus::Draft {
            return Err(GovernanceError::InvalidProposalType);
        }

        proposal.status = ProposalStatus::Cancelled;

        Ok(())
    }

    /// Veto a proposal (only by emergency authority)
    pub fn veto_proposal(&mut self, proposal_id: ProposalId, authority_id: VoterId) -> Result<(), GovernanceError> {
        let proposal = self.state.proposals.get_mut(&proposal_id)
            .ok_or(GovernanceError::ProposalNotFound(proposal_id))?;

        // Verify emergency authority
        if let Some(emergency_id) = self.protocol.config().emergency_authority_id {
            if authority_id != emergency_id {
                return Err(GovernanceError::Unauthorized);
            }
        } else {
            return Err(GovernanceError::Unauthorized);
        }

        proposal.status = ProposalStatus::Vetoed;

        Ok(())
    }

    /// Get a proposal by ID
    pub fn get_proposal(&self, proposal_id: ProposalId) -> Option<&Proposal> {
        self.state.proposals.get(&proposal_id)
    }

    /// Get all proposals
    pub fn get_all_proposals(&self) -> &HashMap<ProposalId, Proposal> {
        &self.state.proposals
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_proposal() {
        let config = GovernanceConfig::default();
        let protocol = VotingProtocol::new(config, VotingPowerStrategy::OnePersonOneVote);
        let mut manager = ProposalManager::new(protocol);

        let voter_id = Uuid::new_v4();
        manager.add_voter(VoterInfo {
            id: voter_id,
            name: "Test Voter".to_string(),
            voting_weight: 100,
            is_active: true,
        });

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

        let proposal = manager.get_proposal(proposal_id).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Draft);
    }

    #[test]
    fn test_submit_and_vote() {
        let config = GovernanceConfig::default();
        let protocol = VotingProtocol::new(config, VotingPowerStrategy::OnePersonOneVote);
        let mut manager = ProposalManager::new(protocol);

        let voter_id = Uuid::new_v4();
        manager.add_voter(VoterInfo {
            id: voter_id,
            name: "Test Voter".to_string(),
            voting_weight: 100,
            is_active: true,
        });

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

        manager.submit_proposal(proposal_id).unwrap();
        manager.cast_vote(proposal_id, voter_id, Vote::Approve).unwrap();

        let proposal = manager.get_proposal(proposal_id).unwrap();
        assert_eq!(proposal.votes.len(), 1);
    }
}
