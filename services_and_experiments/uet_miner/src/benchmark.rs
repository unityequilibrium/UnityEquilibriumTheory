use crate::hash::sha256::sha256d;
use rayon::prelude::*;
use std::time::Instant;
use tracing::info;

pub fn run_cpu_benchmark() {
    info!("========================================");
    info!("🧪 CPU BENCHMARK MODE");
    info!("========================================");

    // 1. Single Threaded
    info!("Running Single-Threaded Benchmark (5s)...");
    let start = Instant::now();
    let mut hashes_single = 0u64;
    let duration = 5.0; // seconds
    let mut data = [0u8; 80]; // Mock block header

    while start.elapsed().as_secs_f64() < duration {
        // Simple mutation to prevent optimization
        data[0] = data[0].wrapping_add(1);
        let _ = sha256d(&data);
        hashes_single += 1;
    }

    let elapsed_single = start.elapsed().as_secs_f64();
    let mh_single = (hashes_single as f64 / elapsed_single) / 1_000_000.0;
    info!("Single-Threaded Speed: {:.2} MH/s", mh_single);

    // 2. Multi-Threaded
    info!("Running Multi-Threaded Benchmark (Rayon)...");

    // Estimate count for decent duration (aim for ~100M hashes to stress test)
    // If single thread is ~2MH/s, multi on 8 core might be ~16MH/s.
    // Let's try to run for a fixed huge amount.
    let batch_size = 10_000_000;

    let start_multi = Instant::now();
    (0..batch_size).into_par_iter().for_each(|i| {
         let mut d = [0u8; 80];
         d[0] = (i % 255) as u8;
         let _ = sha256d(&d);
    });
    let elapsed_multi = start_multi.elapsed().as_secs_f64();

    let mh_multi = (batch_size as f64 / elapsed_multi) / 1_000_000.0;
    info!("Multi-Threaded Speed:  {:.2} MH/s (Sample: 10M hashes)", mh_multi);

    info!("========================================");
    info!("RESULTS:");
    info!("Single-Core: {:.2} MH/s", mh_single);
    info!("Multi-Core:  {:.2} MH/s", mh_multi);
    info!("Speedup:     {:.2}x", mh_multi / mh_single);
    info!("========================================");
}
