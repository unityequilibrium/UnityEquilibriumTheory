# UET Governance

Decentralized governance system for managing UET's economic policy, including difficulty adjustment, issuance budget, task portfolio rotation, and other economic parameters.

## Overview

`uet_governance` provides a complete governance framework for the UET ecosystem, enabling decentralized decision-making for economic policy changes. It supports multiple voting strategies (1-person-1-vote, token-weighted, node-weighted, quadratic voting) and includes a proposal lifecycle management system with policy execution.

## Features

- **Voting Protocol**: Flexible voting power calculation strategies
- **Proposal Lifecycle**: Draft → Voting → Passed/Failed → Executed
- **Policy Execution**: Extensible handler system for policy changes
- **Emergency Veto**: Emergency authority can veto proposals
- **Quorum & Approval Thresholds**: Configurable governance parameters
- **Time Lock**: Delayed execution to prevent rushed changes

## Usage

```rust
use uet_governance::*;
use uet_governance::policy::{DifficultyAdjustmentHandler, TaskFamilyAdditionHandler};

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
engine.manager().add_voter(VoterInfo {
    id: voter_id,
    name: "University Node".to_string(),
    voting_weight: 1000,
    is_active: true,
});

// Create a proposal
let proposal_id = engine.manager().create_proposal(
    voter_id,
    ProposalType::DifficultyAdjustment {
        task_family: "cosmology".to_string(),
        new_difficulty: 1.5,
    },
    "Increase Cosmology Difficulty".to_string(),
    "Adjust difficulty to maintain optimal work unit completion rate".to_string(),
)?;

// Submit for voting
engine.manager().submit_proposal(proposal_id)?;

// Cast votes
engine.manager().cast_vote(proposal_id, voter_id, Vote::Approve)?;

// Finalize voting
engine.manager().finalize_voting(proposal_id)?;

// Execute the proposal
engine.execute_proposal(proposal_id)?;
```

## Voting Strategies

### One Person One Vote
Each voter gets exactly 1 vote, regardless of their weight.

### Token Weighted
Voting power is proportional to token holdings.

### Node Weighted
Voting power is proportional to node contribution (work units completed).

### Quadratic
Voting power = sqrt(weight), reducing whale influence.

### Hybrid
Combines token and node weights with configurable ratios.

## Proposal Types

- `DifficultyAdjustment`: Adjust difficulty parameters for a task family
- `IssuanceBudgetAdjustment`: Adjust issuance budget for an epoch
- `TaskFamilyAddition`: Add a new task family to the portfolio
- `TaskFamilyRemoval`: Remove a task family from the portfolio
- `TaskFamilyWeightAdjustment`: Adjust task family weights
- `EmergencyDisable`: Emergency disable of a compromised task family
- `OracleConfigUpdate`: Update oracle configuration
- `GovernanceParameterUpdate`: Update governance parameters
- `MintingPolicyUpdate`: Minting policy changes

## Governance Configuration

```rust
GovernanceConfig {
    min_voting_period_hours: 24,
    max_voting_period_hours: 168, // 7 days
    min_quorum_percentage: 30.0,
    min_approval_percentage: 60.0,
    time_lock_hours: 24,
    emergency_authority_id: Some(authority_id),
}
```

## Integration

Governance integrates with:
- `uet_chain`: For ledger-based proposal recording
- `uet_security`: For signing proposals and votes
- `uet_oracle` (planned): For oracle verification in policy execution

## Testing

Run tests:
```bash
cargo test --package uet_governance
```

## License

MIT
