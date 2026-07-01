use crate::types::*;
use std::collections::HashMap;
use chrono::{Utc, Duration, DateTime};
use rust_decimal::prelude::*;

/// Price discovery engine
pub struct PriceDiscoveryEngine {
    prices: HashMap<PairId, PriceData>,
}

#[derive(Debug, Clone)]
struct PriceData {
    spot_price: Decimal,
    twap_numerator: Decimal,
    twap_denominator: Decimal,
    volume_24h: Decimal,
    high_24h: Decimal,
    low_24h: Decimal,
    last_update: DateTime<Utc>,
}

impl PriceDiscoveryEngine {
    /// Create a new price discovery engine
    pub fn new() -> Self {
        Self {
            prices: HashMap::new(),
        }
    }

    /// Update price for a trading pair
    pub fn update_price(
        &mut self,
        pair_id: PairId,
        price: Decimal,
        volume: Decimal,
    ) {
        let now = Utc::now();
        let entry = self.prices.entry(pair_id).or_insert_with(|| PriceData {
            spot_price: price,
            twap_numerator: Decimal::ZERO,
            twap_denominator: Decimal::ZERO,
            volume_24h: Decimal::ZERO,
            high_24h: price,
            low_24h: price,
            last_update: now,
        });

        // Update spot price
        entry.spot_price = price;

        // Update TWAP
        let time_weight = Decimal::from_str("1").unwrap(); // Simplified
        entry.twap_numerator += price * time_weight;
        entry.twap_denominator += time_weight;

        // Update 24h volume
        entry.volume_24h += volume;

        // Update high/low
        if price > entry.high_24h {
            entry.high_24h = price;
        }
        if price < entry.low_24h {
            entry.low_24h = price;
        }

        entry.last_update = now;

        // Reset 24h data if older than 24 hours
        if now.signed_duration_since(entry.last_update).num_hours() >= 24 {
            entry.volume_24h = Decimal::ZERO;
            entry.high_24h = price;
            entry.low_24h = price;
        }
    }

    /// Get price discovery data for a pair
    pub fn get_price_discovery(&self, pair_id: PairId) -> Option<PriceDiscovery> {
        let entry = self.prices.get(&pair_id)?;

        let twap_price = if entry.twap_denominator.is_zero() {
            entry.spot_price
        } else {
            entry.twap_numerator / entry.twap_denominator
        };

        Some(PriceDiscovery {
            pair_id,
            spot_price: entry.spot_price,
            twap_price,
            volume_24h: entry.volume_24h,
            high_24h: entry.high_24h,
            low_24h: entry.low_24h,
            timestamp: entry.last_update,
        })
    }

    /// Get spot price for a pair
    pub fn get_spot_price(&self, pair_id: PairId) -> Option<Decimal> {
        self.prices.get(&pair_id).map(|d| d.spot_price)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_price_discovery() {
        let mut engine = PriceDiscoveryEngine::new();
        let pair_id = Uuid::new_v4();

        // Update prices
        engine.update_price(pair_id, Decimal::from_str("1.0").unwrap(), Decimal::from_str("100").unwrap());
        engine.update_price(pair_id, Decimal::from_str("1.1").unwrap(), Decimal::from_str("200").unwrap());
        engine.update_price(pair_id, Decimal::from_str("1.05").unwrap(), Decimal::from_str("150").unwrap());

        let discovery = engine.get_price_discovery(pair_id).unwrap();

        assert!(discovery.spot_price > Decimal::from_str("1.0").unwrap());
        assert!(discovery.volume_24h > Decimal::from_str("400").unwrap());
        assert!(discovery.high_24h >= discovery.spot_price);
        assert!(discovery.low_24h <= discovery.spot_price);

        println!("✅ Price discovery test passed");
        println!("   Spot price: {}", discovery.spot_price);
        println!("   TWAP price: {}", discovery.twap_price);
        println!("   Volume 24h: {}", discovery.volume_24h);
    }
}
