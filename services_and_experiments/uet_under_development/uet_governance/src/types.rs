use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;
use chrono::{DateTime, Utc};

/// Unique identifier for a proposal
pub type ProposalId = Uuid;

/// Unique identifier for a voter (node or token holder)
pub type VoterId = Uuid;

/// Proposal types that can be submitted to governance
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ProposalType {
    /// Adjust difficulty parameters for a task family
    DifficultyAdjustment {
        task_family: String,
        new_difficulty: f64,
    },
    /// Adjust issuance budget for an epoch
    IssuanceBudgetAdjustment {
        epoch: u64,
        new_budget: u64,
    },
    /// Add a new task family to the portfolio
    TaskFamilyAddition {
        family_name: String,
        weight: f64,
    },
    /// Remove a task family from the portfolio
    TaskFamilyRemoval {
        family_name: String,
    },
    /// Adjust task family weights
    TaskFamilyWeightAdjustment {
        family_name: String,
        new_weight: f64,
    },
    /// Emergency disable of a compromised task family
    EmergencyDisable {
        family_name: String,
        reason: String,
    },
    /// Update oracle configuration
    OracleConfigUpdate {
        oracle_type: String,
        config_update: serde_json::Value,
    },
    /// Update governance parameters (voting period, quorum, etc.)
    GovernanceParameterUpdate {
        parameter_name: String,
        new_value: serde_json::Value,
    },
    /// Minting policy changes
    MintingPolicyUpdate {
        policy_name: String,
        policy_config: serde_json::Value,
    },
}

/// Proposal status throughout its lifecycle
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ProposalStatus {
    /// Proposal created, not yet submitted for voting
    Draft,
    /// Proposal submitted, voting in progress
    Voting,
    /// Voting completed, proposal passed
    Passed,
    /// Voting completed, proposal failed
    Failed,
    /// Proposal executed successfully
    Executed,
    /// Proposal execution failed
    ExecutionFailed,
    /// Proposal cancelled by proposer
    Cancelled,
    /// Proposal vetoed by emergency authority
    Vetoed,
}

/// Vote cast by a voter
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum Vote {
    Approve,
    Reject,
    Abstain,
}

/// A governance proposal
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Proposal {
    pub id: ProposalId,
    pub proposal_type: ProposalType,
    pub proposer_id: VoterId,
    pub title: String,
    pub description: String,
    pub created_at: DateTime<Utc>,
    pub voting_start: Option<DateTime<Utc>>,
    pub voting_end: Option<DateTime<Utc>>,
    pub status: ProposalStatus,
    pub votes: HashMap<VoterId, Vote>,
    pub execution_result: Option<ExecutionResult>,
}

impl Proposal {
    /// Calculate total votes for each option
    pub fn vote_counts(&self) -> (u64, u64, u64) {
        let mut approve = 0u64;
        let mut reject = 0u64;
        let mut abstain = 0u64;

        for vote in self.votes.values() {
            match vote {
                Vote::Approve => approve += 1,
                Vote::Reject => reject += 1,
                Vote::Abstain => abstain += 1,
            }
        }

        (approve, reject, abstain)
    }

    /// Calculate approval percentage (excluding abstentions)
    pub fn approval_percentage(&self) -> Option<f64> {
        let (approve, reject, abstain) = self.vote_counts();
        let total = approve + reject;

        if total == 0 {
            None
        } else {
            Some((approve as f64 / total as f64) * 100.0)
        }
    }
}

/// Result of proposal execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionResult {
    pub success: bool,
    pub message: String,
    pub executed_at: DateTime<Utc>,
}

/// Governance configuration parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GovernanceConfig {
    /// Minimum voting period in hours
    pub min_voting_period_hours: u64,
    /// Maximum voting period in hours
    pub max_voting_period_hours: u64,
    /// Minimum quorum percentage required for proposal to be valid
    pub min_quorum_percentage: f64,
    /// Minimum approval percentage required for proposal to pass
    pub min_approval_percentage: f64,
    /// Time lock period in hours before proposal execution
    pub time_lock_hours: u64,
    /// Emergency authority voter ID
    pub emergency_authority_id: Option<VoterId>,
}

impl Default for GovernanceConfig {
    fn default() -> Self {
        Self {
            min_voting_period_hours: 24,
            max_voting_period_hours: 168, // 7 days
            min_quorum_percentage: 30.0,
            min_approval_percentage: 60.0,
            time_lock_hours: 24,
            emergency_authority_id: None,
        }
    }
}

/// Governance state
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GovernanceState {
    pub proposals: HashMap<ProposalId, Proposal>,
    pub config: GovernanceConfig,
    pub voters: HashMap<VoterId, VoterInfo>,
}

/// Information about a voter
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VoterInfo {
    pub id: VoterId,
    pub name: String,
    pub voting_weight: u64,
    pub is_active: bool,
}

/// Voting power calculation strategy
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VotingPowerStrategy {
    /// One vote per voter (1 person = 1 vote)
    OnePersonOneVote,
    /// Proportional to token holdings
    TokenWeighted,
    /// Proportional to node contribution (work units completed)
    NodeWeighted,
    /// Quadratic voting (sqrt of weight)
    Quadratic,
    /// Hybrid strategy
    Hybrid {
        token_weight: f64,
        node_weight: f64,
    },
}

/// Governance error types
#[derive(Debug, thiserror::Error)]
pub enum GovernanceError {
    #[error("Proposal not found: {0}")]
    ProposalNotFound(ProposalId),

    #[error("Voter not found: {0}")]
    VoterNotFound(VoterId),

    #[error("Proposal is not in voting status")]
    ProposalNotInVotingStatus,

    #[error("Voting period has ended")]
    VotingPeriodEnded,

    #[error("Voting has not started")]
    VotingNotStarted,

    #[error("Quorum not met: {0}% required, {1}% achieved")]
    QuorumNotMet(f64, f64),

    #[error("Approval threshold not met: {0}% required, {1}% achieved")]
    ApprovalThresholdNotMet(f64, f64),

    #[error("Proposal execution failed: {0}")]
    ExecutionFailed(String),

    #[error("Unauthorized action")]
    Unauthorized,

    #[error("Invalid proposal type for current state")]
    InvalidProposalType,
}
