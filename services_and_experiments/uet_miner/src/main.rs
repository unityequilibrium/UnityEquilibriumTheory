//! # UET GPU Bitcoin Miner
//!
//! A Rust implementation of a Bitcoin miner with Stratum V1 protocol support.
//! Designed for educational purposes and UET research.
//!
//! ## Architecture
//! - `stratum/` - Stratum protocol client (TCP + JSON-RPC)
//! - `mining/` - Block header construction
//! - `hash/` - SHA256 double-hash implementation (CPU baseline)
//! - `gpu/` - GPU compute module (wgpu/Vulkan for AMD RX 6600 XT)

mod stratum;
mod mining;
mod hash;
mod gpu;
mod benchmark;

use anyhow::Result;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

use crate::stratum::StratumClient;

/// Configuration for the miner
#[derive(Debug, Clone)]
pub struct MinerConfig {
    pub pool_url: String,
    pub pool_port: u16,
    pub wallet: String,
    pub worker: String,
}

impl Default for MinerConfig {
    fn default() -> Self {
        Self {
            // ViaBTC BCH Pool
            pool_url: "bch.viabtc.io".to_string(),
            pool_port: 3333,
            wallet: "Santa001".to_string(),  // ViaBTC account name
            worker: "001".to_string(),       // Worker ID
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .with_target(false)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    // Parse CLI arguments
    let args: Vec<String> = std::env::args().collect();

    // Check for benchmark mode
    if args.len() > 1 && args[1] == "benchmark" {
        benchmark::run_cpu_benchmark();
        return Ok(());
    }

    info!("========================================");
    info!("  🦀 UET RUST BITCOIN MINER v0.2.0");
    info!("  Research Project - Topic 0.18");
    info!("  GPU Accelerated (AMD RX 6600 XT)");
    info!("========================================");
    let config = if args.len() >= 4 {
        MinerConfig {
            pool_url: args[1].clone(),
            pool_port: args[2].parse().unwrap_or(3333),
            wallet: args[3].clone(),
            worker: if args.len() > 4 { args[4].clone() } else { "x".to_string() },
        }
    } else {
        info!("Usage: uet_miner <url> <port> <user> [pass/worker]");
        info!("No args provided, using default (ViaBTC BCH)...");
        MinerConfig::default()
    };

    info!("Pool:   {}:{}", config.pool_url, config.pool_port);
    info!("Wallet: {}.{}", config.wallet, config.worker);
    info!("");

    // Initialize GPU
    info!("[GPU] Initializing...");
    let gpu_miner = match gpu::compute::GpuMiner::new().await {
        Ok(miner) => {
            info!("[GPU] ✅ Initialized: {}", miner.device_name());
            Some(std::sync::Arc::new(miner))
        }
        Err(e) => {
            info!("[GPU] ⚠️ GPU not available, using CPU only: {}", e);
            None
        }
    };
    info!("");

    // Create and run the stratum client
    let mut client = StratumClient::new(config, gpu_miner);
    client.run().await?;

    Ok(())
}
