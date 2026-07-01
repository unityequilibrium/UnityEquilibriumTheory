use crate::types::*;
use std::collections::HashMap;

/// Oracle registry manages all oracles
pub struct OracleRegistry {
    oracles: HashMap<OracleId, OracleInfo>,
}

impl OracleRegistry {
    /// Create a new oracle registry
    pub fn new() -> Self {
        Self {
            oracles: HashMap::new(),
        }
    }

    /// Register an oracle
    pub fn register_oracle(&mut self, oracle: OracleInfo) {
        self.oracles.insert(oracle.id, oracle);
    }

    /// Get an oracle by ID
    pub fn get_oracle(&self, oracle_id: OracleId) -> Option<&OracleInfo> {
        self.oracles.get(&oracle_id)
    }

    /// Get all oracles
    pub fn get_all_oracles(&self) -> &HashMap<OracleId, OracleInfo> {
        &self.oracles
    }

    /// Get oracles by type
    pub fn get_oracles_by_type(&self, oracle_type: OracleType) -> Vec<&OracleInfo> {
        self.oracles
            .values()
            .filter(|o| o.oracle_type == oracle_type)
            .collect()
    }

    /// Get active and reputable oracles
    pub fn get_active_reputable_oracles(&self, oracle_type: OracleType) -> Vec<&OracleInfo> {
        self.oracles
            .values()
            .filter(|o| {
                o.oracle_type == oracle_type
                    && o.status == OracleStatus::Active
                    && o.reputation.is_reputable(o.config.min_reputation_threshold)
            })
            .collect()
    }

    /// Update oracle reputation
    pub fn update_reputation(&mut self, oracle_id: OracleId, is_correct: bool) -> Result<(), OracleError> {
        let oracle = self.oracles.get_mut(&oracle_id)
            .ok_or(OracleError::OracleNotFound(oracle_id))?;

        oracle.reputation.calculate(is_correct);

        // If reputation drops below threshold, mark as inactive
        if oracle.reputation.score < oracle.config.min_reputation_threshold {
            oracle.status = OracleStatus::Inactive;
        }

        Ok(())
    }

    /// Update oracle status
    pub fn update_status(&mut self, oracle_id: OracleId, status: OracleStatus) -> Result<(), OracleError> {
        let oracle = self.oracles.get_mut(&oracle_id)
            .ok_or(OracleError::OracleNotFound(oracle_id))?;

        oracle.status = status;

        Ok(())
    }
}

impl Default for OracleRegistry {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register_oracle() {
        let mut registry = OracleRegistry::new();

        let oracle_id = Uuid::new_v4();
        let oracle = OracleInfo {
            id: oracle_id,
            name: "Test Energy Oracle".to_string(),
            oracle_type: OracleType::Energy,
            config: OracleConfig {
                oracle_type: OracleType::Energy,
                endpoint: "https://test.com".to_string(),
                api_key: None,
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

        let retrieved = registry.get_oracle(oracle_id).unwrap();
        assert_eq!(retrieved.name, "Test Energy Oracle");
    }

    #[test]
    fn test_reputation_calculation() {
        let mut registry = OracleRegistry::new();

        let oracle_id = Uuid::new_v4();
        let oracle = OracleInfo {
            id: oracle_id,
            name: "Test Oracle".to_string(),
            oracle_type: OracleType::Energy,
            config: OracleConfig {
                oracle_type: OracleType::Energy,
                endpoint: "https://test.com".to_string(),
                api_key: None,
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

        // Simulate 10 correct reports
        for _ in 0..10 {
            registry.update_reputation(oracle_id, true).unwrap();
        }

        let retrieved = registry.get_oracle(oracle_id).unwrap();
        assert_eq!(retrieved.reputation.score, 1.0);
        assert_eq!(retrieved.reputation.total_reports, 10);
    }
}
