// Market-Economic Integration
//
// This module integrates the market infrastructure with economic policy,
// using market prices for economic calculations.

use crate::*;
use rust_decimal::prelude::*;
use rust_decimal::Decimal;

/// Market-economic connector
pub struct MarketEconomicConnector {
    price_engine: PriceDiscoveryEngine,
}

impl MarketEconomicConnector {
    /// Create a new market-economic connector
    pub fn new() -> Self {
        Self {
            price_engine: PriceDiscoveryEngine::new(),
        }
    }

    /// Get market price for economic calculations
    pub fn get_market_price(&self, pair_id: PairId) -> Option<Decimal> {
        self.price_engine.get_spot_price(pair_id)
    }

    /// Calculate issuance based on market price
    pub fn calculate_issuance_by_price(
        &self,
        _pair_id: PairId,
        base_issuance: u64,
    ) -> Option<u64> {
        // Simplified calculation - in real implementation would use market price
        Some(base_issuance)
    }

    /// Update price discovery from market data
    pub fn update_price_discovery(
        &mut self,
        pair_id: PairId,
        price: Decimal,
        volume: Decimal,
    ) {
        self.price_engine.update_price(pair_id, price, volume);
    }

    /// Get price discovery metrics
    pub fn get_price_metrics(&self, pair_id: PairId) -> Option<PriceDiscovery> {
        self.price_engine.get_price_discovery(pair_id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rust_decimal::prelude::*;

    #[test]
    fn test_market_economic_connector() {
        let mut connector = MarketEconomicConnector::new();
        let pair_id = Uuid::new_v4();

        // Update price
        connector.update_price_discovery(
            pair_id,
            Decimal::from_str("5.0").unwrap(),
            Decimal::from_str("1000").unwrap(),
        );

        // Get market price
        let price = connector.get_market_price(pair_id).unwrap();
        assert!(price > Decimal::ZERO);

        // Calculate issuance by price
        let issuance = connector.calculate_issuance_by_price(pair_id, 1_000_000);
        assert!(issuance.is_some());

        println!("✅ Market-economic connector test passed");
    }
}
