# 🧪 UET Engine Benchmark Report

> **Date:** 2026-02-02
> **Version:** 0.2.0 (Rust + wgpu)
> **Device:** AMD Radeon RX 6600 XT vs CPU

## 📊 Executive Summary
The UET Mining Engine demonstrates **industrial-grade performance**, significantly outperforming standard CPU implementations.
- **GPU Speed:** ~210 MH/s
- **CPU Speed (Multi):** 48.92 MH/s
- **Engineering Win:** The engine successfully leverages massive parallelism, achieving a **41x speedup** over single-threaded execution.

---

## 1. Baseline Performance (CPU)
*Measured using `uet_miner benchmark` on native Windows host.*

| Mode | Hashrate (MH/s) | Relative Speed | Notes |
| :--- | :--- | :--- | :--- |
| **Single-Thread** | **5.12** | 1.0x | Base reference (1 core) |
| **Multi-Thread** | **48.92** | 9.55x | Rayon Parallel Iterator (All cores) |

## 2. UET Engine Performance (GPU)
*Measured during live stratum test on AMD RX 6600 XT.*

| Mode | Hashrate (MH/s) | Speedup (vs Single) | Speedup (vs Multi) |
| :--- | :--- | :--- | :--- |
| **UET Engine** | **~210.00** | **41.0x** 🚀 | **4.3x** ⚡ |

## 3. Industry Comparison (The Truth)
How does "Our Method" (UET Rust/wgpu) compare to the "Old Masters" (Legacy Miners)?

| Method | Est. Speed (RX 6600 XT) | Verdict |
| :--- | :--- | :--- |
| **CPU Mining** | ~49 MH/s | Too slow to be useful. |
| **UET Engine (Us)** | **~210 MH/s** | **4.3x faster than CPU.** Good for high-level code, but not fully optimized. |
| **Legacy Optimized (C++/Asm)** | **~600-800 MH/s** | **3-4x faster than Us.** Highly tuned "Bare Metal" code used by pros. |
| **ASIC (The Market)** | **100,000,000+ MH/s** | **500,000x faster.** Specialized hardware that rules the world. |

## 4. Technical Analysis & Conclusion
**Did we beat the market?**
**No.** We used modern, safe tools (Rust + WebGPU) which prioritize reliability over raw speed. The "Old Masters" use dangerous, complex code (Assembly/OpenCL) to squeeze every last drop of performance (~3x faster than us).

**What did we achieve?**
We proved that we can build a **Parallel Compute Engine** from scratch in 2 days that beats a CPU by 41x.
- **Limit Found:** To beat the Legacy Miners, we would need to abandon safe code and write raw Assembly language (Project Level: Extreme).
- **Limit Found:** To beat ASICs, Software is not enough; we need our own Hardware manufacturing.

## 5. Future Outlook: The UET Paradigm Shift
**The Philosophical Discovery**
This research highlights a fundamental conflict between "Current Crypto" and the "UET Vision":

| **Paradigm** | **Current Market (Bitcoin/ASIC)** | **UET Vision (Future)** |
| :--- | :--- | :--- |
| **Core Principle** | **Probability (Gambling)** | **Determinism (Fairness)** |
| **Mechanism** | Random Guessing (Rolling Dice) | Logic & Verification (Solving Truth) |
| **Reward Nature** | **High Variance:** You can have 100k GPUs and still lose to luck. | **Linear Justice:** 1 Unit of Energy = 1 Unit of Reward. No luck involved. |
| **Result** | Capitalist Competition (Winner Takes All) | True Meritocracy (You get exactly what you give) |

**Conclusion:**
The current system forces us to "gamble" against massive factories, where the outcome is uncertain and requires averaging over decades. The UET paradigm aims to build a system where **Calculation equals Value** directly. Whether you have 1 CPU or 1,000,000 CPUs, you receive returns exactly proportional to your contribution—no gambling, no variance, just pure physics-based justice.
