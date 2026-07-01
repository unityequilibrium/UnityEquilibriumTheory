use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};
use rust_decimal::Decimal;

/// Unique identifier for a trading pair
pub type PairId = Uuid;

/// Unique identifier for a liquidity pool
pub type PoolId = Uuid;

/// Trading pair
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TradingPair {
    pub id: PairId,
    pub base_asset: String, // e.g., "UET"
    pub quote_asset: String, // e.g., "USD"
    pub created_at: DateTime<Utc>,
}

/// Liquidity pool
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LiquidityPool {
    pub id: PoolId,
    pub pair_id: PairId,
    pub base_reserve: Decimal,
    pub quote_reserve: Decimal,
    pub lp_token_supply: Decimal,
    pub fee_rate: Decimal, // e.g., 0.003 for 0.3%
    pub created_at: DateTime<Utc>,
}

impl LiquidityPool {
    /// Calculate spot price (quote per base)
    pub fn spot_price(&self) -> Decimal {
        if self.base_reserve.is_zero() {
            return Decimal::ZERO;
        }
        self.quote_reserve / self.base_reserve
    }

    /// Calculate liquidity depth
    pub fn liquidity_depth(&self) -> Decimal {
        self.base_reserve * self.spot_price()
    }
}

/// Trade order
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OrderSide {
    Buy,
    Sell,
}

/// Order type
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OrderType {
    Market,
    Limit,
}

/// Trade order
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Order {
    pub id: Uuid,
    pub pair_id: PairId,
    pub side: OrderSide,
    pub order_type: OrderType,
    pub amount: Decimal,
    pub price: Option<Decimal>, // For limit orders
    pub created_at: DateTime<Utc>,
}

/// Trade result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TradeResult {
    pub order_id: Uuid,
    pub executed_amount: Decimal,
    pub executed_price: Decimal,
    pub fee: Decimal,
    pub timestamp: DateTime<Utc>,
}

/// Price discovery data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceDiscovery {
    pub pair_id: PairId,
    pub spot_price: Decimal,
    pub twap_price: Decimal, // Time-weighted average price
    pub volume_24h: Decimal,
    pub high_24h: Decimal,
    pub low_24h: Decimal,
    pub timestamp: DateTime<Utc>,
}

/// Market error types
#[derive(Debug, thiserror::Error)]
pub enum MarketError {
    #[error("Insufficient liquidity")]
    InsufficientLiquidity,

    #[error("Invalid price: {0}")]
    InvalidPrice(String),

    #[error("Invalid amount: {0}")]
    InvalidAmount(String),

    #[error("Pool not found: {0}")]
    PoolNotFound(PoolId),

    #[error("Pair not found: {0}")]
    PairNotFound(PairId),

    #[error("Slippage too high: {0}% > {1}%")]
    SlippageTooHigh(Decimal, Decimal),

    #[error("Calculation failed: {0}")]
    CalculationFailed(String),
}
