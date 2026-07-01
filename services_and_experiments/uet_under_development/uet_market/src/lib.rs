// UET Market - AMM, Liquidity Pools, and Price Discovery
//
// This crate provides market infrastructure for UET Coin trading,
// including automated market making, liquidity pools, and price discovery.

pub mod types;
pub mod amm;
pub mod price;
pub mod market;
pub mod economic_integration;
pub mod governance_integration;

pub use types::*;
pub use amm::AMM;
pub use price::PriceDiscoveryEngine;
pub use market::MarketEngine;
pub use economic_integration::MarketEconomicConnector;
pub use governance_integration::MarketGovernanceHandler;

#[cfg(test)]
mod tests {
    use super::*;
    use rust_decimal::prelude::*;

    #[test]
    fn test_market_integration() {
        let mut engine = MarketEngine::new(Decimal::from_str("0.003").unwrap());
        let mut price_engine = PriceDiscoveryEngine::new();

        // Create pair
        let pair_id = engine.create_pair("UET".to_string(), "USD".to_string());

        // Create pool
        let pool_id = engine
            .create_pool(pair_id, Decimal::from_str("10000").unwrap(), Decimal::from_str("50000").unwrap())
            .unwrap();

        // Execute swap
        let result = engine
            .execute_swap(
                pool_id,
                Decimal::from_str("100").unwrap(),
                Decimal::from_str("0.01").unwrap(),
            )
            .unwrap();

        // Update price discovery
        price_engine.update_price(pair_id, result.executed_price, result.executed_amount);

        let discovery = price_engine.get_price_discovery(pair_id).unwrap();

        assert!(discovery.spot_price > Decimal::ZERO);
        assert!(discovery.volume_24h > Decimal::ZERO);

        println!("✅ Market integration test passed");
    }
}
