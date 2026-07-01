use crate::types::*;
use crate::amm::AMM;
use std::collections::HashMap;
use uuid::Uuid;
use chrono::Utc;
use rust_decimal::prelude::*;

/// Market engine
pub struct MarketEngine {
    pools: HashMap<PoolId, LiquidityPool>,
    pairs: HashMap<PairId, TradingPair>,
    amm: AMM,
}

impl MarketEngine {
    /// Create a new market engine
    pub fn new(fee_rate: Decimal) -> Self {
        Self {
            pools: HashMap::new(),
            pairs: HashMap::new(),
            amm: AMM::new(fee_rate),
        }
    }

    /// Create a trading pair
    pub fn create_pair(&mut self, base_asset: String, quote_asset: String) -> PairId {
        let pair_id = Uuid::new_v4();
        let pair = TradingPair {
            id: pair_id,
            base_asset,
            quote_asset,
            created_at: Utc::now(),
        };

        self.pairs.insert(pair_id, pair);
        pair_id
    }

    /// Create a liquidity pool
    pub fn create_pool(
        &mut self,
        pair_id: PairId,
        base_reserve: Decimal,
        quote_reserve: Decimal,
    ) -> Result<PoolId, MarketError> {
        if !self.pairs.contains_key(&pair_id) {
            return Err(MarketError::PairNotFound(pair_id));
        }

        let pool_id = Uuid::new_v4();
        let lp_token_supply = base_reserve; // Simplified LP token calculation

        let pool = LiquidityPool {
            id: pool_id,
            pair_id,
            base_reserve,
            quote_reserve,
            lp_token_supply,
            fee_rate: self.amm.fee_rate,
            created_at: Utc::now(),
        };

        self.pools.insert(pool_id, pool);
        Ok(pool_id)
    }

    /// Execute a swap
    pub fn execute_swap(
        &self,
        pool_id: PoolId,
        input_amount: Decimal,
        slippage_tolerance: Decimal,
    ) -> Result<TradeResult, MarketError> {
        let pool = self
            .pools
            .get(&pool_id)
            .ok_or(MarketError::PoolNotFound(pool_id))?;

        // Calculate output
        let output_amount = self.amm.calculate_output(
            input_amount,
            pool.base_reserve,
            pool.quote_reserve,
        )?;

        // Calculate minimum output with slippage
        let min_output = self
            .amm
            .calculate_min_output(output_amount, slippage_tolerance)?;

        // Check if output meets minimum
        if output_amount < min_output {
            let actual_slippage = (Decimal::ONE - (output_amount / output_amount)) * Decimal::from_str("100").unwrap();
            return Err(MarketError::SlippageTooHigh(actual_slippage, slippage_tolerance * Decimal::from_str("100").unwrap()));
        }

        // Calculate fee
        let fee = input_amount * self.amm.fee_rate;

        Ok(TradeResult {
            order_id: Uuid::new_v4(),
            executed_amount: output_amount,
            executed_price: pool.spot_price(),
            fee,
            timestamp: Utc::now(),
        })
    }

    /// Get a pool by ID
    pub fn get_pool(&self, pool_id: PoolId) -> Option<&LiquidityPool> {
        self.pools.get(&pool_id)
    }

    /// Get a pair by ID
    pub fn get_pair(&self, pair_id: PairId) -> Option<&TradingPair> {
        self.pairs.get(&pair_id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rust_decimal::prelude::*;

    #[test]
    fn test_market_roundtrip() {
        let mut engine = MarketEngine::new(Decimal::from_str("0.003").unwrap());

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
                Decimal::from_str("0.01").unwrap(), // 1% slippage tolerance
            )
            .unwrap();

        assert!(result.executed_amount > Decimal::ZERO);
        assert!(result.executed_price > Decimal::ZERO);

        println!("✅ Market roundtrip test passed");
        println!("   Executed: {} UET -> {} USD", result.executed_amount, result.executed_price);
    }
}
