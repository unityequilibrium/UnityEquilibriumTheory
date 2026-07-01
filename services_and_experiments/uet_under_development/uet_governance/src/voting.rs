use crate::types::*;
use std::collections::HashMap;

/// Voting protocol for governance
pub struct VotingProtocol {
    config: GovernanceConfig,
    power_strategy: VotingPowerStrategy,
}

impl VotingProtocol {
    /// Create a new voting protocol with the given configuration
    pub fn new(config: GovernanceConfig, power_strategy: VotingPowerStrategy) -> Self {
        Self {
            config,
            power_strategy,
        }
    }

    /// Get the configuration
    pub fn config(&self) -> &GovernanceConfig {
        &self.config
    }

    /// Calculate voting power for a voter
    pub fn calculate_voting_power(&self, voter_id: &VoterId, voters: &HashMap<VoterId, VoterInfo>) -> Result<u64, GovernanceError> {
        let voter = voters.get(voter_id)
            .ok_or(GovernanceError::VoterNotFound(*voter_id))?;

        if !voter.is_active {
            return Ok(0);
        }

        match &self.power_strategy {
            VotingPowerStrategy::OnePersonOneVote => Ok(1),
            VotingPowerStrategy::TokenWeighted => Ok(voter.voting_weight),
            VotingPowerStrategy::NodeWeighted => Ok(voter.voting_weight),
            VotingPowerStrategy::Quadratic => {
                // Quadratic voting: power = sqrt(weight)
                let weight = voter.voting_weight as f64;
                Ok(weight.sqrt() as u64)
            }
            VotingPowerStrategy::Hybrid { token_weight, node_weight } => {
                // Hybrid: combine token and node weights
                let token_power = (voter.voting_weight as f64) * token_weight;
                let node_power = (voter.voting_weight as f64) * node_weight;
                Ok((token_power + node_power) as u64)
            }
        }
    }

    /// Calculate total voting power for a proposal
    pub fn total_voting_power(&self, voters: &HashMap<VoterId, VoterInfo>) -> u64 {
        voters.values()
            .filter(|v| v.is_active)
            .map(|v| {
                match &self.power_strategy {
                    VotingPowerStrategy::OnePersonOneVote => 1,
                    VotingPowerStrategy::TokenWeighted => v.voting_weight,
                    VotingPowerStrategy::NodeWeighted => v.voting_weight,
                    VotingPowerStrategy::Quadratic => {
                        (v.voting_weight as f64).sqrt() as u64
                    }
                    VotingPowerStrategy::Hybrid { token_weight, node_weight } => {
                        let token_power = (v.voting_weight as f64) * token_weight;
                        let node_power = (v.voting_weight as f64) * node_weight;
                        (token_power + node_power) as u64
                    }
                }
            })
            .sum()
    }

    /// Calculate voting power for a specific vote
    pub fn vote_power(&self, voter_id: &VoterId, vote: &Vote, voters: &HashMap<VoterId, VoterInfo>) -> u64 {
        let base_power = self.calculate_voting_power(voter_id, voters).unwrap_or(0);

        // Abstentions don't count toward approval/rejection
        if *vote == Vote::Abstain {
            0
        } else {
            base_power
        }
    }

    /// Calculate quorum achieved for a proposal
    pub fn quorum_achieved(
        &self,
        proposal: &Proposal,
        voters: &HashMap<VoterId, VoterInfo>,
    ) -> Result<(f64, bool), GovernanceError> {
        let total_power = self.total_voting_power(voters);
        if total_power == 0 {
            return Ok((0.0, false));
        }

        let mut voted_power = 0u64;
        for (voter_id, vote) in &proposal.votes {
            let power = self.vote_power(voter_id, vote, voters);
            voted_power += power;
        }

        let quorum_percentage = (voted_power as f64 / total_power as f64) * 100.0;
        let quorum_met = quorum_percentage >= self.config.min_quorum_percentage;

        Ok((quorum_percentage, quorum_met))
    }

    /// Calculate approval achieved for a proposal
    pub fn approval_achieved(
        &self,
        proposal: &Proposal,
        voters: &HashMap<VoterId, VoterInfo>,
    ) -> Result<(f64, bool), GovernanceError> {
        let mut approve_power = 0u64;
        let mut reject_power = 0u64;

        for (voter_id, vote) in &proposal.votes {
            let power = self.vote_power(voter_id, vote, voters);
            match vote {
                Vote::Approve => approve_power += power,
                Vote::Reject => reject_power += power,
                Vote::Abstain => {}
            }
        }

        let total = approve_power + reject_power;
        if total == 0 {
            return Ok((0.0, false));
        }

        let approval_percentage = (approve_power as f64 / total as f64) * 100.0;
        let approval_met = approval_percentage >= self.config.min_approval_percentage;

        Ok((approval_percentage, approval_met))
    }

    /// Check if a proposal passes voting
    pub fn check_proposal_passes(
        &self,
        proposal: &Proposal,
        voters: &HashMap<VoterId, VoterInfo>,
    ) -> Result<bool, GovernanceError> {
        let (quorum_pct, quorum_met) = self.quorum_achieved(proposal, voters)?;
        let (approval_pct, approval_met) = self.approval_achieved(proposal, voters)?;

        if !quorum_met {
            return Err(GovernanceError::QuorumNotMet(
                self.config.min_quorum_percentage,
                quorum_pct,
            ));
        }

        if !approval_met {
            return Err(GovernanceError::ApprovalThresholdNotMet(
                self.config.min_approval_percentage,
                approval_pct,
            ));
        }

        Ok(true)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn test_one_person_one_vote() {
        let config = GovernanceConfig::default();
        let protocol = VotingProtocol::new(config, VotingPowerStrategy::OnePersonOneVote);

        let mut voters = HashMap::new();
        voters.insert(
            Uuid::new_v4(),
            VoterInfo {
                id: Uuid::new_v4(),
                name: "Voter1".to_string(),
                voting_weight: 1000,
                is_active: true,
            },
        );
        voters.insert(
            Uuid::new_v4(),
            VoterInfo {
                id: Uuid::new_v4(),
                name: "Voter2".to_string(),
                voting_weight: 500,
                is_active: true,
            },
        );

        let voter_id = voters.keys().next().unwrap();
        let power = protocol.calculate_voting_power(voter_id, &voters).unwrap();
        assert_eq!(power, 1);
    }

    #[test]
    fn test_quadratic_voting() {
        let config = GovernanceConfig::default();
        let protocol = VotingProtocol::new(config, VotingPowerStrategy::Quadratic);

        let mut voters = HashMap::new();
        let voter_id = Uuid::new_v4();
        voters.insert(
            voter_id,
            VoterInfo {
                id: voter_id,
                name: "Voter1".to_string(),
                voting_weight: 100,
                is_active: true,
            },
        );

        let power = protocol.calculate_voting_power(&voter_id, &voters).unwrap();
        // sqrt(100) = 10
        assert_eq!(power, 10);
    }
}
