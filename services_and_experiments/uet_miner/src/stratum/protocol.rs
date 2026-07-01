//! Stratum V1 protocol message types.
//!
//! JSON-RPC based protocol for pool mining communication.

use serde::{Deserialize, Serialize};

/// Request to subscribe to mining notifications.
#[derive(Debug, Serialize)]
pub struct SubscribeRequest {
    pub id: u64,
    pub method: &'static str,
    pub params: Vec<String>,
}

impl SubscribeRequest {
    pub fn new(id: u64, user_agent: &str) -> Self {
        Self {
            id,
            method: "mining.subscribe",
            params: vec![user_agent.to_string()],
        }
    }
}

/// Request to authorize a worker.
#[derive(Debug, Serialize)]
pub struct AuthorizeRequest {
    pub id: u64,
    pub method: &'static str,
    pub params: Vec<String>,
}

impl AuthorizeRequest {
    pub fn new(id: u64, username: &str, password: &str) -> Self {
        Self {
            id,
            method: "mining.authorize",
            params: vec![username.to_string(), password.to_string()],
        }
    }
}

/// Request to submit a share.
#[derive(Debug, Serialize)]
pub struct SubmitRequest {
    pub id: u64,
    pub method: &'static str,
    pub params: Vec<String>,
}

impl SubmitRequest {
    pub fn new(
        id: u64,
        worker_name: &str,
        job_id: &str,
        extranonce2: &str,
        ntime: &str,
        nonce: &str,
    ) -> Self {
        Self {
            id,
            method: "mining.submit",
            params: vec![
                worker_name.to_string(),
                job_id.to_string(),
                extranonce2.to_string(),
                ntime.to_string(),
                nonce.to_string(),
            ],
        }
    }
}

/// Generic JSON-RPC response.
#[derive(Debug, Deserialize)]
pub struct JsonRpcResponse {
    pub id: Option<u64>,
    pub result: Option<serde_json::Value>,
    pub error: Option<serde_json::Value>,
    pub method: Option<String>,
    pub params: Option<serde_json::Value>,
}

/// Subscription result from mining.subscribe.
#[derive(Debug, Clone)]
pub struct SubscriptionResult {
    pub subscription_id: String,
    pub extranonce1: String,
    pub extranonce2_size: usize,
}

impl SubscriptionResult {
    pub fn from_json(result: &serde_json::Value) -> Option<Self> {
        let arr = result.as_array()?;
        if arr.len() < 3 {
            return None;
        }

        // [[["mining.set_difficulty", "..."], ["mining.notify", "..."]], "extranonce1", extranonce2_size]
        let extranonce1 = arr.get(1)?.as_str()?.to_string();
        let extranonce2_size = arr.get(2)?.as_u64()? as usize;

        // Get subscription ID from first array
        let subscriptions = arr.get(0)?.as_array()?;
        let subscription_id = subscriptions
            .get(0)?
            .as_array()?
            .get(1)?
            .as_str()?
            .to_string();

        Some(Self {
            subscription_id,
            extranonce1,
            extranonce2_size,
        })
    }
}

/// Mining job notification (mining.notify).
#[derive(Debug, Clone)]
pub struct MiningNotify {
    pub job_id: String,
    pub prev_hash: String,
    pub coinbase1: String,
    pub coinbase2: String,
    pub merkle_branches: Vec<String>,
    pub version: String,
    pub nbits: String,
    pub ntime: String,
    pub clean_jobs: bool,
}

impl MiningNotify {
    pub fn from_params(params: &serde_json::Value) -> Option<Self> {
        let arr = params.as_array()?;
        if arr.len() < 9 {
            return None;
        }

        let merkle_branches: Vec<String> = arr
            .get(4)?
            .as_array()?
            .iter()
            .filter_map(|v| v.as_str().map(String::from))
            .collect();

        Some(Self {
            job_id: arr.get(0)?.as_str()?.to_string(),
            prev_hash: arr.get(1)?.as_str()?.to_string(),
            coinbase1: arr.get(2)?.as_str()?.to_string(),
            coinbase2: arr.get(3)?.as_str()?.to_string(),
            merkle_branches,
            version: arr.get(5)?.as_str()?.to_string(),
            nbits: arr.get(6)?.as_str()?.to_string(),
            ntime: arr.get(7)?.as_str()?.to_string(),
            clean_jobs: arr.get(8)?.as_bool().unwrap_or(false),
        })
    }
}

/// Difficulty setting (mining.set_difficulty).
#[derive(Debug, Clone, Copy)]
pub struct DifficultyNotify {
    pub difficulty: f64,
}

impl DifficultyNotify {
    pub fn from_params(params: &serde_json::Value) -> Option<Self> {
        let arr = params.as_array()?;
        let difficulty = arr.get(0)?.as_f64()?;
        Some(Self { difficulty })
    }
}
