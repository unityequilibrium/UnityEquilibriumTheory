// UET Oracle - Oracle Infrastructure for Energy, Land, and Asset Verification
//
// This crate provides oracle infrastructure for verifying energy consumption,
// land registry, and asset holdings for the UET economic system.

pub mod types;
pub mod registry;
pub mod verifier;
pub mod ledger_integration;

pub use types::*;
pub use registry::OracleRegistry;
pub use verifier::{EnergyVerifier, LandVerifier, AssetVerifier};
pub use ledger_integration::{OracleEvent, OracleLedgerRecorder};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_oracle_registry() {
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

        println!("✅ Oracle registry test passed");
    }

    #[test]
    fn test_reputation_system() {
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

        println!("✅ Reputation system test passed");
    }

    #[test]
    fn test_oracle_filtering() {
        let mut registry = OracleRegistry::new();

        // Add multiple oracles
        for i in 0..3 {
            let oracle_id = Uuid::new_v4();
            let oracle = OracleInfo {
                id: oracle_id,
                name: format!("Energy Oracle {}", i),
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
                    total_reports: 10,
                    correct_reports: 10,
                    last_updated: Utc::now(),
                },
                created_at: Utc::now(),
            };
            registry.register_oracle(oracle);
        }

        let energy_oracles = registry.get_oracles_by_type(OracleType::Energy);
        assert_eq!(energy_oracles.len(), 3);

        let active_reputable = registry.get_active_reputable_oracles(OracleType::Energy);
        assert_eq!(active_reputable.len(), 3);

        println!("✅ Oracle filtering test passed");
    }
}
