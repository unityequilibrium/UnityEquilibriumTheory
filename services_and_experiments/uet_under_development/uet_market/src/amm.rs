use crate::types::*;
use rust_decimal::Decimal;
use rust_decimal::prelude::*;

/// Automated Market Maker (AMM)
pub struct AMM {
    pub fee_rate: Decimal,
}

impl AMM {
    /// Create a new AMM with the given fee rate
    pub fn new(fee_rate: Decimal) -> Self {
        Self { fee_rate }
    }

    /// Calculate output amount for a swap (constant product formula)
    ///
    /// Formula: output = (input * reserve_out) / (reserve_in + input)
    pub fn calculate_output(
        &self,
        input_amount: Decimal,
        reserve_in: Decimal,
        reserve_out: Decimal,
    ) -> Result<Decimal, MarketError> {
        if input_amount.is_zero() {
            return Ok(Decimal::ZERO);
        }

        if reserve_in.is_zero() || reserve_out.is_zero() {
            return Err(MarketError::InsufficientLiquidity);
        }

        let input_with_fee = input_amount * (Decimal::ONE - self.fee_rate);
        let numerator = input_with_fee * reserve_out;
        let denominator = reserve_in + input_with_fee;

        Ok(numerator / denominator)
    }

    /// Calculate price impact
    pub fn calculate_price_impact(
        &self,
        input_amount: Decimal,
        reserve_in: Decimal,
    ) -> Result<Decimal, MarketError> {
        if reserve_in.is_zero() {
            return Err(MarketError::InsufficientLiquidity);
        }

        let price_impact = input_amount / (reserve_in + input_amount);
        Ok(price_impact)
    }

    /// Calculate minimum output with slippage tolerance
    pub fn calculate_min_output(
        &self,
        output_amount: Decimal,
        slippage_tolerance: Decimal,
    ) -> Result<Decimal, MarketError> {
        if slippage_tolerance < Decimal::ZERO || slippage_tolerance > Decimal::ONE {
            return Err(MarketError::InvalidPrice(
                "Slippage tolerance must be between 0 and 1".to_string(),
            ));
        }

        let min_output = output_amount * (Decimal::ONE - slippage_tolerance);
        Ok(min_output)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_output() {
        let amm = AMM::new(Decimal::from_str("0.003").unwrap()); // 0.3% fee

        // Example: 100 UET -> USD
        // Reserve: 10,000 UET, 50,000 USD
        let input = Decimal::from_str("100").unwrap();
        let reserve_in = Decimal::from_str("10000").unwrap();
        let reserve_out = Decimal::from_str("50000").unwrap();

        let output = amm
            .calculate_output(input, reserve_in, reserve_out)
            .unwrap();

        // Expected: ~494 USD (with 0.3% fee)
        assert!(output > Decimal::from_str("490").unwrap());
        assert!(output < Decimal::from_str("500").unwrap());

        println!("✅ Calculate output test passed: {} USD", output);
    }

    #[test]
    fn test_price_impact() {
        let amm = AMM::new(Decimal::from_str("0.003").unwrap());

        let input = Decimal::from_str("100").unwrap();
        let reserve_in = Decimal::from_str("10000").unwrap();

        let impact = amm.calculate_price_impact(input, reserve_in).unwrap();

        // 100 / (10000 + 100) = 0.0099 (~1%)
        assert!(impact > Decimal::from_str("0.009").unwrap());
        assert!(impact < Decimal::from_str("0.011").unwrap());

        println!("✅ Price impact test passed: {:.2}%", impact * Decimal::from_str("100").unwrap());
    }
}
