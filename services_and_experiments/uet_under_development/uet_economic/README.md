# UET Economic

Economic policy engine for difficulty adjustment, issuance budget calculation, and portfolio rotation.

## Overview

`uet_economic` provides the core economic policy logic for UET, including:
- Difficulty adjustment based on work unit completion rates
- Issuance budget calculation based on energy input
- Portfolio rotation to maintain task family diversity

## Features

- **Difficulty Adjustment**: Adaptive difficulty based on completion rates
- **Issuance Budget**: Energy-based minting with clamping
- **Portfolio Rotation**: Automatic task family weight adjustment
- **Concentration Limits**: Prevent dominance of single task families

## Usage

### Difficulty Adjustment

```rust
use uet_economic::*;

let config = EconomicConfig::default();
let engine = DifficultyAdjustmentEngine::new(config);

// Calculate difficulty adjustment
let result = engine.calculate_adjustment(
    "cosmology",  // task family
    1.0,           // current difficulty
    0.9,           // completion rate (90%)
)?;

println!("Difficulty: {} -> {}", result.old_difficulty, result.new_difficulty);
```

### Issuance Budget

```rust
let engine = IssuanceBudgetEngine::new(config);

// Calculate issuance budget for epoch
let result = engine.calculate_budget(
    1,              // epoch number
    500_000.0,      // energy input (kWh)
    100_000,        // work units completed
)?;

println!("Issuance: {} UET Coin", result.total_issuance);
```

### Portfolio Rotation

```rust
let engine = PortfolioRotationEngine::new(config);

// Rotate portfolio based on performance
let result = engine.rotate_portfolio(
    &current_portfolio,
    vec!["neutrino".to_string()], // new families to add
);

println!("Added: {:?}", result.added_families);
println!("Removed: {:?}", result.removed_families);
```

## Economic Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_completion_rate` | 0.8 | Target work unit completion rate (80%) |
| `difficulty_sensitivity` | 0.1 | Difficulty adjustment sensitivity |
| `max_difficulty_multiplier` | 10.0 | Maximum difficulty multiplier |
| `min_difficulty_multiplier` | 0.1 | Minimum difficulty multiplier |
| `epoch_duration_hours` | 24 | Epoch duration in hours |
| `max_issuance_per_epoch` | 1,000,000 | Maximum issuance per epoch |
| `min_issuance_per_epoch` | 100,000 | Minimum issuance per epoch |
| `max_task_family_concentration` | 0.5 | Maximum task family concentration (50%) |
| `min_task_family_weight` | 0.05 | Minimum task family weight |
| `max_task_family_weight` | 0.5 | Maximum task family weight |

## Difficulty Adjustment Logic

```
if completion_rate > target:
    new_difficulty = current * (1 + sensitivity * (completion_rate - target))
elif completion_rate < target:
    new_difficulty = current * (1 - sensitivity * (target - completion_rate))
else:
    new_difficulty = current
```

## Issuance Budget Logic

```
issuance_per_kwh = max_issuance / 1,000,000
calculated_issuance = energy_input_kwh * issuance_per_kwh
clamped_issuance = clamp(calculated, min_issuance, max_issuance)
```

## Portfolio Rotation Logic

- **Add**: New families if portfolio not full
- **Remove**: Families with <10% completion rate or >max weight
- **Adjust**: Decrease weight if completion rate >90% (too easy) or <50% (too hard)

## Integration

Economic engine integrates with:
- `uet_governance`: For policy execution when proposals pass
- `uet_oracle`: For energy input verification
- `uet_chain`: For recording economic policy changes

## Testing

```bash
cargo test --package uet_economic
```

## License

MIT
