use crate::types::*;
use crate::registry::OracleRegistry;
use reqwest::Client;
use std::time::Duration;

/// Energy verifier
pub struct EnergyVerifier {
    client: Client,
    registry: OracleRegistry,
}

impl EnergyVerifier {
    /// Create a new energy verifier
    pub fn new(registry: OracleRegistry) -> Self {
        Self {
            client: Client::new(),
            registry,
        }
    }

    /// Verify energy consumption
    pub async fn verify_energy(
        &mut self,
        request: EnergyVerificationRequest,
    ) -> Result<EnergyVerificationResponse, OracleError> {
        // Get active and reputable energy oracles
        let oracle_ids: Vec<_> = self.registry
            .get_active_reputable_oracles(OracleType::Energy)
            .iter()
            .map(|o| o.id)
            .collect();

        if oracle_ids.is_empty() {
            return Err(OracleError::VerificationFailed(
                "No active reputable energy oracles available".to_string(),
            ));
        }

        // Get oracles again for verification
        let oracles = self.registry.get_active_reputable_oracles(OracleType::Energy);

        // Try each oracle until one succeeds
        for oracle_id in oracle_ids {
            // Get oracle for verification
            let oracles_for_verify = self.registry.get_active_reputable_oracles(OracleType::Energy);
            let oracle = oracles_for_verify.iter().find(|o| o.id == oracle_id);

            if let Some(oracle) = oracle {
                match self.verify_with_oracle(&request, oracle).await {
                    Ok(response) => {
                        // Update reputation
                        let _ = self.registry.update_reputation(oracle_id, true);
                        return Ok(response);
                    }
                    Err(e) => {
                        // Update reputation (incorrect)
                        let _ = self.registry.update_reputation(oracle_id, false);
                        continue;
                    }
                }
            }
        }

        Err(OracleError::VerificationFailed(
            "All energy oracles failed".to_string(),
        ))
    }

    /// Verify with a specific oracle
    async fn verify_with_oracle(
        &self,
        request: &EnergyVerificationRequest,
        oracle: &OracleInfo,
    ) -> Result<EnergyVerificationResponse, OracleError> {
        let url = format!("{}/verify", oracle.config.endpoint);

        let response = self
            .client
            .post(&url)
            .timeout(Duration::from_secs(oracle.config.timeout_seconds))
            .header("Authorization", format!("Bearer {}", oracle.config.api_key.as_ref().unwrap_or(&String::new())))
            .json(request)
            .send()
            .await
            .map_err(|e| OracleError::NetworkError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(OracleError::VerificationFailed(format!(
                "Oracle returned status: {}",
                response.status()
            )));
        }

        let verification_response: EnergyVerificationResponse = response
            .json()
            .await
            .map_err(|_| OracleError::InvalidResponseFormat)?;

        // Verify signature
        // TODO: Implement signature verification using uet_security

        Ok(verification_response)
    }
}

/// Land verifier
pub struct LandVerifier {
    client: Client,
    registry: OracleRegistry,
}

impl LandVerifier {
    /// Create a new land verifier
    pub fn new(registry: OracleRegistry) -> Self {
        Self {
            client: Client::new(),
            registry,
        }
    }

    /// Verify land registry
    pub async fn verify_land(
        &mut self,
        request: LandVerificationRequest,
    ) -> Result<LandVerificationResponse, OracleError> {
        // Get active and reputable land oracles
        let oracle_ids: Vec<_> = self.registry
            .get_active_reputable_oracles(OracleType::Land)
            .iter()
            .map(|o| o.id)
            .collect();

        if oracle_ids.is_empty() {
            return Err(OracleError::VerificationFailed(
                "No active reputable land oracles available".to_string(),
            ));
        }

        // Try each oracle until one succeeds
        for oracle_id in oracle_ids {
            // Get oracle for this iteration
            let oracles = self.registry.get_active_reputable_oracles(OracleType::Land);
            if let Some(oracle) = oracles.iter().find(|o| o.id == oracle_id) {
                let endpoint = oracle.config.endpoint.clone();
                let timeout_seconds = oracle.config.timeout_seconds;
                let api_key = oracle.config.api_key.clone();

                match self.verify_with_oracle(&request, &endpoint, timeout_seconds, api_key).await {
                    Ok(response) => {
                        let _ = self.registry.update_reputation(oracle_id, true);
                        return Ok(response);
                    }
                    Err(e) => {
                        let _ = self.registry.update_reputation(oracle_id, false);
                        continue;
                    }
                }
            }
        }

        Err(OracleError::VerificationFailed(
            "All land oracles failed".to_string(),
        ))
    }

    /// Verify with a specific oracle
    async fn verify_with_oracle(
        &mut self,
        request: &LandVerificationRequest,
        endpoint: &str,
        timeout_seconds: u64,
        api_key: Option<String>,
    ) -> Result<LandVerificationResponse, OracleError> {
        let url = format!("{}/verify", endpoint);

        let response = self
            .client
            .post(&url)
            .timeout(Duration::from_secs(timeout_seconds))
            .header("Authorization", format!("Bearer {}", api_key.as_ref().unwrap_or(&String::new())))
            .json(request)
            .send()
            .await
            .map_err(|e| OracleError::NetworkError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(OracleError::VerificationFailed(format!(
                "Oracle returned status: {}",
                response.status()
            )));
        }

        let verification_response: LandVerificationResponse = response
            .json()
            .await
            .map_err(|_| OracleError::InvalidResponseFormat)?;

        Ok(verification_response)
    }
}

/// Asset verifier
pub struct AssetVerifier {
    client: Client,
    registry: OracleRegistry,
}

impl AssetVerifier {
    /// Create a new asset verifier
    pub fn new(registry: OracleRegistry) -> Self {
        Self {
            client: Client::new(),
            registry,
        }
    }

    /// Verify asset holdings
    pub async fn verify_asset(
        &mut self,
        request: AssetVerificationRequest,
    ) -> Result<AssetVerificationResponse, OracleError> {
        // Get active and reputable asset oracles
        let oracle_ids: Vec<_> = self.registry
            .get_active_reputable_oracles(OracleType::Asset)
            .iter()
            .map(|o| o.id)
            .collect();

        if oracle_ids.is_empty() {
            return Err(OracleError::VerificationFailed(
                "No active reputable asset oracles available".to_string(),
            ));
        }

        // Try each oracle until one succeeds
        for oracle_id in oracle_ids {
            // Get oracle for this iteration
            let oracles = self.registry.get_active_reputable_oracles(OracleType::Asset);
            if let Some(oracle) = oracles.iter().find(|o| o.id == oracle_id) {
                match self.verify_with_oracle(&request, oracle).await {
                    Ok(response) => {
                        let _ = self.registry.update_reputation(oracle_id, true);
                        return Ok(response);
                    }
                    Err(e) => {
                        let _ = self.registry.update_reputation(oracle_id, false);
                        continue;
                    }
                }
            }
        }

        Err(OracleError::VerificationFailed(
            "All asset oracles failed".to_string(),
        ))
    }

    /// Verify with a specific oracle
    async fn verify_with_oracle(
        &self,
        request: &AssetVerificationRequest,
        oracle: &OracleInfo,
    ) -> Result<AssetVerificationResponse, OracleError> {
        let url = format!("{}/verify", oracle.config.endpoint);

        let response = self
            .client
            .post(&url)
            .timeout(Duration::from_secs(oracle.config.timeout_seconds))
            .header("Authorization", format!("Bearer {}", oracle.config.api_key.as_ref().unwrap_or(&String::new())))
            .json(request)
            .send()
            .await
            .map_err(|e| OracleError::NetworkError(e.to_string()))?;

        if !response.status().is_success() {
            return Err(OracleError::VerificationFailed(format!(
                "Oracle returned status: {}",
                response.status()
            )));
        }

        let verification_response: AssetVerificationResponse = response
            .json()
            .await
            .map_err(|_| OracleError::InvalidResponseFormat)?;

        Ok(verification_response)
    }
}
