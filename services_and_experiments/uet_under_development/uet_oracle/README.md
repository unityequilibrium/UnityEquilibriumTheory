# UET Oracle

Oracle infrastructure for verifying energy consumption, land registry, and asset holdings for the UET economic system.

## Overview

`uet_oracle` provides a decentralized oracle system for verifying real-world data required for UET's asset-backed economic model. It supports multiple oracle types with reputation tracking and automatic failover.

## Features

- **Multi-Type Oracles**: Energy, Land, and Asset verification
- **Reputation System**: Track oracle accuracy and reliability
- **Automatic Failover**: Try multiple oracles until one succeeds
- **Signature Verification**: Cryptographic verification of oracle responses
- **Status Management**: Track oracle status (Active, Inactive, Maintenance, Compromised)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Oracle System                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Energy       │  │ Land         │  │ Asset        │     │
│  │ Verifier     │  │ Verifier     │  │ Verifier     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Oracle       │  │ Reputation   │  │ Status       │     │
│  │ Registry     │  │ System       │  │ Management   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Setup Oracle Registry

```rust
use uet_oracle::*;

let mut registry = OracleRegistry::new();

let oracle_id = Uuid::new_v4();
let oracle = OracleInfo {
    id: oracle_id,
    name: "Energy Oracle 1".to_string(),
    oracle_type: OracleType::Energy,
    config: OracleConfig {
        oracle_type: OracleType::Energy,
        endpoint: "https://energy-oracle.example.com".to_string(),
        api_key: Some("api-key-123".to_string()),
        timeout_seconds: 30,
        min_reputation_threshold: 0.8,
    },
    status: OracleStatus::Active,
    reputation: ReputationScore {
        oracle_id,
        score: 1.0,
        total_reports: 0,
        correct_reports: 0,
        last_updated: Utc::now(),
    },
    created_at: Utc::now(),
};

registry.register_oracle(oracle);
```

### Verify Energy Consumption

```rust
let energy_verifier = EnergyVerifier::new(registry);

let request = EnergyVerificationRequest {
    node_id: Uuid::new_v4(),
    period_start: Utc::now() - chrono::Duration::hours(24),
    period_end: Utc::now(),
    expected_kwh: 1000.0,
};

let response = energy_verifier.verify_energy(request).await?;

println!("Energy verified: {} kWh", response.actual_kwh);
```

### Verify Land Registry

```rust
let land_verifier = LandVerifier::new(registry);

let request = LandVerificationRequest {
    land_id: "LAND-001".to_string(),
    jurisdiction: "US-CA".to_string(),
    owner_id: "OWNER-001".to_string(),
};

let response = land_verifier.verify_land(request).await?;

println!("Land verified: {} sqm", response.land_area_sqm);
```

### Verify Asset Holdings

```rust
let asset_verifier = AssetVerifier::new(registry);

let request = AssetVerificationRequest {
    asset_type: "bitcoin".to_string(),
    asset_id: "btc-address".to_string(),
    expected_amount: 10.0,
};

let response = asset_verifier.verify_asset(request).await?;

println!("Asset verified: {} BTC", response.actual_amount);
```

## Reputation System

Oracles are tracked based on their accuracy:

- **Score**: 0.0 to 1.0 (percentage of correct reports)
- **Total Reports**: Number of verification attempts
- **Correct Reports**: Number of successful verifications
- **Threshold**: Minimum score required to be considered reputable

Oracles with scores below the threshold are automatically marked as inactive.

## Oracle Types

| Type | Purpose | Data Verified |
|------|---------|---------------|
| Energy | Electricity consumption | kWh consumed by nodes |
| Land | Land registry | Land area, ownership |
| Asset | Asset holdings | Bitcoin, Gold, Patents |

## Security

- **Signature Verification**: All oracle responses are cryptographically signed
- **Reputation Tracking**: Unreliable oracles are automatically disabled
- **Multi-Oracle Consensus**: Try multiple oracles for verification
- **Status Management**: Oracles can be marked as compromised

## Integration

Oracle integrates with:
- `uet_governance`: For oracle configuration updates via governance
- `uet_security`: For signature verification
- `uet_chain`: For recording verification results on ledger

## Testing

```bash
cargo test --package uet_oracle
```

## License

MIT
