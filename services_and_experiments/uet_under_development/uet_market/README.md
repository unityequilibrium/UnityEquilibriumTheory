# UET Market

Market infrastructure for UET Coin trading, including automated market making, liquidity pools, and price discovery.

## Overview

`uet_market` provides a complete market infrastructure for UET Coin, supporting:
- Automated Market Maker (AMM) with constant product formula
- Liquidity pools for trading pairs
- Price discovery with TWAP and 24h metrics
- Slippage protection and fee calculation

## Features

- **AMM**: Constant product formula with configurable fee rate
- **Liquidity Pools**: Multi-pool support with LP tokens
- **Price Discovery**: Spot price, TWAP, 24h volume, high/low
- **Slippage Protection**: Minimum output calculation

## Usage

### Create Market Engine

```rust
use uet_market::*;
use rust_decimal::prelude::*;

let engine = MarketEngine::new(Decimal::from_str("0.003").unwrap()); // 0.3% fee
```

### Create Trading Pair

```rust
let pair_id = engine.create_pair("UET".to_string(), "USD".to_string());
```

### Create Liquidity Pool

```rust
let pool_id = engine.create_pool(
    pair_id,
    Decimal::from_str("10000").unwrap(),  // 10,000 UET
    Decimal::from_str("50000").unwrap(),  // 50,000 USD
)?;
```

### Execute Swap

```rust
let result = engine.execute_swap(
    pool_id,
    Decimal::from_str("100").unwrap(),     // 100 UET input
    Decimal::from_str("0.01").unwrap(),   // 1% slippage tolerance
)?;

println!("Swapped {} UET for {} USD", result.executed_amount, result.executed_price);
```

### Price Discovery

```rust
let mut price_engine = PriceDiscoveryEngine::new();

// Update prices from trades
price_engine.update_price(pair_id, price, volume);

// Get price discovery data
let discovery = price_engine.get_price_discovery(pair_id)?;
println!("Spot price: {}", discovery.spot_price);
println!("TWAP price: {}", discovery.twap_price);
println!("Volume 24h: {}", discovery.volume_24h);
```

## AMM Formula

### Constant Product Formula

```
output = (input * reserve_out) / (reserve_in + input)
```

### Price Impact

```
price_impact = input / (reserve_in + input)
```

### Minimum Output with Slippage

```
min_output = output * (1 - slippage_tolerance)
```

## Liquidity Pools

Each pool maintains:
- **Base Reserve**: Amount of base asset (e.g., UET)
- **Quote Reserve**: Amount of quote asset (e.g., USD)
- **LP Token Supply**: Tokens representing liquidity share
- **Fee Rate**: Trading fee (default 0.3%)

### Spot Price

```
spot_price = quote_reserve / base_reserve
```

### Liquidity Depth

```
liquidity_depth = base_reserve * spot_price
```

## Price Discovery Metrics

| Metric | Description |
|--------|-------------|
| Spot Price | Current market price |
| TWAP Price | Time-weighted average price |
| Volume 24h | Trading volume in last 24 hours |
| High 24h | Highest price in last 24 hours |
| Low 24h | Lowest price in last 24 hours |

## Integration

Market integrates with:
- `uet_governance`: For fee rate adjustments via governance
- `uet_chain`: For recording trades on ledger
- `uet_economic`: For price-based economic calculations

## Testing

```bash
cargo test --package uet_market
```

## License

MIT
