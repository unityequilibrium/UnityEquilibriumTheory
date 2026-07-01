//! Stratum V1 protocol client for pool mining.

mod protocol;
mod client;

pub use client::StratumClient;
pub use protocol::*;
