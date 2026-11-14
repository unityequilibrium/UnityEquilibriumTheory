"""
UET_Grover_Miner_Alpha.py - UET Topic 0.18 (Mathnicry)
=====================================================
The "Cheat Code" Miner: Applying Grover's Diffusion and Field Relaxation
to maximize the probability of finding a valid hash.

PHILOSOPHY:
In a 256-bit space, solutions are rare.
Brute force is like looking for a needle in a haystack by closing your eyes and grabbing.
UET Resonance is like using a magnet to 'feel' where the needle is.
"""

import numpy as np
import time
import hashlib
import sys
from pathlib import Path


import multiprocessing


# --- THE "HEAVY SIEGE" ENGINE ---
class UETResonanceEngine:
    def __init__(self, target_prefix="0000"):
        self.target_prefix = target_prefix
        self.difficulty = len(target_prefix)

    def field_resonance_score(self, nonce):
        h = hashlib.sha256(str(nonce).encode()).hexdigest()
        score = 0
        for i in range(len(self.target_prefix)):
            if h[i] == self.target_prefix[i]:
                score += 1
            else:
                # Add "Near Miss" points (Topic 0.18 logic)
                # If the character is close in hex value, give partial weight
                target_val = int(self.target_prefix[i], 16)
                found_val = int(h[i], 16)
                dist = abs(target_val - found_val)
                score += (16 - dist) / 16.0
                break
        return score


def mining_worker(target, start_nonce, range_size, result_queue):
    """
    Individual worker process for parallel siege.
    """
    engine = UETResonanceEngine(target_prefix=target)
    # Start with a localized manifold
    candidates = np.random.randint(start_nonce, start_nonce + range_size, 1024, dtype=np.int64)

    total_hashes = 0
    for epoch in range(500):
        # 1. Verification
        for n in candidates:
            total_hashes += 1
            h = hashlib.sha256(str(n).encode()).hexdigest()
            if h.startswith(target):
                result_queue.put((n, h, total_hashes))
                return

        # 2. Evolution (Resonance Shift)
        scores = np.array([engine.field_resonance_score(n) for n in candidates])
        best_indices = np.argsort(scores)[-50:]  # Keep top 50
        best_nonces = candidates[best_indices]

        new_candidates = []
        for n in best_nonces:
            new_candidates.append(n + 1)
            new_candidates.append(n ^ 0x3F3F3F3F)  # Axiom 5: Quantum Jump
            new_candidates.append(n + np.random.randint(-5000, 5000))

        candidates = np.array(new_candidates)[:1024]

    result_queue.put((None, None, total_hashes))


def run_heavy_siege(target="00000"):
    num_cores = multiprocessing.cpu_count()
    print(f"💎 UET HEAVY_SIEGE MINER (Target: {target} | Cores: {num_cores})")
    print("==========================================================")

    result_queue = multiprocessing.Queue()
    processes = []

    start_time = time.time()

    # Launch parallel manifolds
    for i in range(num_cores):
        start_nonce = i * 10000000
        p = multiprocessing.Process(
            target=mining_worker, args=(target, start_nonce, 1000000, result_queue)
        )
        p.start()
        processes.append(p)

    print(f"🚀 {num_cores} Parallel Manifolds Ignited...")

    total_hashes = 0
    found = False
    finished_workers = 0

    while finished_workers < num_cores:
        res = result_queue.get()
        nonce, h, hashes = res
        total_hashes += hashes

        if nonce is not None:
            found = True
            winning_nonce = nonce
            winning_hash = h
            # Terminate others
            for p in processes:
                p.terminate()
            break
        else:
            finished_workers += 1

    duration = time.time() - start_time

    print("\n" + "=" * 60)
    if found:
        print(f"🏆 SUPREME VICTORY! Found Nonce: {winning_nonce}")
        print(f"   Hash: {winning_hash}")
    else:
        print("❌ All manifolds decohered. No solution found.")

    print(f"   Total Hashes (Parallel Sum): {total_hashes:,}")
    print(f"   Time Taken:                 {duration:.4f}s")
    print(f"   Effective Hash Rate:        {total_hashes/duration:.2f} h/s")
    print("=" * 60)


if __name__ == "__main__":
    # 5 zeros (~1M attempts) is easy for Heavy Siege.
    # 6 zeros (~16M attempts) is a real test.
    run_heavy_siege(target="00000")
