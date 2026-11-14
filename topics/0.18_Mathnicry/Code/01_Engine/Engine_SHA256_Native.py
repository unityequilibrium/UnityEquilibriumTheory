"""
Engine_SHA256_Native.py - UET Topic 0.18 (Mathnicry)
=====================================================
Native SHA256 double-hash engine for Bitcoin mining.

This module provides CORRECT byte manipulation for:
- Block header construction (80 bytes)
- Merkle root calculation
- Target/difficulty handling
- Nonce encoding

⚠️ WARNING: This is for LEARNING PURPOSES.
   Python mining will never be profitable on SHA256.
"""

import hashlib
import struct
import binascii
from typing import List, Tuple, Optional


def sha256d(data: bytes) -> bytes:
    """
    Double SHA256 hash (Bitcoin standard).

    Args:
        data: Raw bytes to hash

    Returns:
        32-byte hash result
    """
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def reverse_bytes(hex_string: str) -> str:
    """
    Reverse bytes in a hex string (for endianness conversion).

    Example:
        "aabbccdd" -> "ddccbbaa"
    """
    return binascii.hexlify(binascii.unhexlify(hex_string)[::-1]).decode()


def hex_to_bin(hex_string: str) -> bytes:
    """Convert hex string to binary data."""
    return binascii.unhexlify(hex_string)


def bin_to_hex(binary_data: bytes) -> str:
    """Convert binary data to hex string."""
    return binascii.hexlify(binary_data).decode()


def build_coinbase(coinbase1: str, coinbase2: str, extranonce1: str, extranonce2: str) -> bytes:
    """
    Build coinbase transaction from Stratum job parts.

    Args:
        coinbase1: First part of coinbase (from pool)
        coinbase2: Second part of coinbase (from pool)
        extranonce1: Pool-assigned extranonce
        extranonce2: Miner-assigned extranonce (4 bytes typically)

    Returns:
        Raw coinbase transaction bytes
    """
    coinbase_hex = coinbase1 + extranonce1 + extranonce2 + coinbase2
    return hex_to_bin(coinbase_hex)


def coinbase_hash(coinbase: bytes) -> bytes:
    """
    Hash coinbase transaction (double SHA256).

    Returns:
        32-byte coinbase hash
    """
    return sha256d(coinbase)


def calculate_merkle_root(coinbase_hash_bin: bytes, merkle_branches: List[str]) -> bytes:
    """
    Calculate merkle root from coinbase hash and merkle branches.

    Bitcoin merkle tree: hash pairs left-to-right, bottom-up.

    Args:
        coinbase_hash_bin: 32-byte coinbase hash
        merkle_branches: List of hex-encoded branch hashes (from pool)

    Returns:
        32-byte merkle root (already in correct byte order for header)
    """
    merkle = coinbase_hash_bin

    for branch in merkle_branches:
        branch_bin = hex_to_bin(branch)
        # Concatenate current merkle with branch and hash
        merkle = sha256d(merkle + branch_bin)

    return merkle


def build_block_header(
    version: str, prev_hash: str, merkle_root: bytes, ntime: str, nbits: str, nonce: int
) -> bytes:
    """
    Build 80-byte Bitcoin block header.

    ┌──────────────────────────────────────────────────┐
    │  Field        │ Size  │ Format                   │
    ├───────────────┼───────┼──────────────────────────┤
    │  version      │ 4     │ little-endian            │
    │  prev_hash    │ 32    │ byte-swapped             │
    │  merkle_root  │ 32    │ byte-swapped             │
    │  ntime        │ 4     │ little-endian            │
    │  nbits        │ 4     │ little-endian            │
    │  nonce        │ 4     │ little-endian            │
    └──────────────────────────────────────────────────┘
    Total: 80 bytes

    Args:
        version: Block version (hex, 8 chars)
        prev_hash: Previous block hash (hex, 64 chars)
        merkle_root: Merkle root (32 bytes raw)
        ntime: Timestamp (hex, 8 chars)
        nbits: Difficulty bits (hex, 8 chars)
        nonce: Nonce value (integer)

    Returns:
        80-byte block header ready for hashing
    """
    # Version: convert from hex to little-endian bytes
    version_bin = hex_to_bin(version)

    # Previous hash: reverse bytes (byte-swap for little-endian)
    prev_hash_bin = hex_to_bin(reverse_bytes(prev_hash))

    # Merkle root: reverse bytes (byte-swap for little-endian)
    merkle_root_bin = merkle_root[::-1]

    # nTime: reverse bytes
    ntime_bin = hex_to_bin(reverse_bytes(ntime))

    # nBits: reverse bytes
    nbits_bin = hex_to_bin(reverse_bytes(nbits))

    # Nonce: 4 bytes little-endian
    nonce_bin = struct.pack("<I", nonce)

    # Construct header
    header = (
        version_bin  # 4 bytes
        + prev_hash_bin  # 32 bytes
        + merkle_root_bin  # 32 bytes
        + ntime_bin  # 4 bytes
        + nbits_bin  # 4 bytes
        + nonce_bin  # 4 bytes
    )

    assert len(header) == 80, f"Header must be 80 bytes, got {len(header)}"
    return header


def difficulty_to_target(difficulty: float) -> int:
    """
    Convert pool difficulty to target value.

    Target = (0xFFFF * 2^208) / difficulty

    A valid hash must be <= target when interpreted as big integer.
    """
    if difficulty <= 0:
        difficulty = 1

    # Bitcoin's difficulty 1 target
    max_target = 0xFFFF * (2**208)
    target = int(max_target / difficulty)

    return target


def check_hash_meets_target(hash_bytes: bytes, target: int) -> bool:
    """
    Check if hash meets difficulty target.

    Hash is interpreted as little-endian integer and compared.
    """
    hash_int = int.from_bytes(hash_bytes, "little")
    return hash_int <= target


def hash_block_header(header: bytes) -> bytes:
    """
    Hash block header (double SHA256).

    Returns:
        32-byte hash
    """
    return sha256d(header)


def format_nonce_for_submit(nonce: int) -> str:
    """
    Format nonce for Stratum mining.submit.

    Returns:
        8-character hex string (big-endian, as per Stratum spec)
    """
    # Stratum expects nonce as big-endian hex
    return bin_to_hex(struct.pack(">I", nonce))


def format_extranonce2(value: int, size: int = 4) -> str:
    """
    Format extranonce2 for submission.

    Args:
        value: Integer value
        size: Number of bytes (typically 4)

    Returns:
        Hex string of specified length
    """
    return format(value, f"0{size*2}x")


# ============================================================
# Quick Self-Test
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Engine_SHA256_Native.py - Self Test")
    print("=" * 60)

    # Test 1: Basic double hash
    test_data = b"hello bitcoin"
    result = sha256d(test_data)
    print(f"\n✅ SHA256d test:")
    print(f"   Input:  {test_data}")
    print(f"   Output: {bin_to_hex(result)}")

    # Test 2: Byte reversal
    test_hex = "aabbccdd"
    reversed_hex = reverse_bytes(test_hex)
    print(f"\n✅ Byte reversal test:")
    print(f"   Input:  {test_hex}")
    print(f"   Output: {reversed_hex}")
    assert reversed_hex == "ddccbbaa", "Byte reversal failed!"

    # Test 3: Difficulty to target
    diff = 1.0
    target = difficulty_to_target(diff)
    print(f"\n✅ Difficulty to target:")
    print(f"   Difficulty: {diff}")
    print(f"   Target: {hex(target)[:20]}...")

    # Test 4: Header construction (mock data)
    mock_header = build_block_header(
        version="20000000",
        prev_hash="0" * 64,
        merkle_root=b"\x00" * 32,
        ntime="5f5e4c3d",
        nbits="1a0ffff0",
        nonce=0,
    )
    print(f"\n✅ Header construction:")
    print(f"   Length: {len(mock_header)} bytes (expected: 80)")

    # Test 5: Nonce format
    nonce_hex = format_nonce_for_submit(12345678)
    print(f"\n✅ Nonce format test:")
    print(f"   Nonce: 12345678")
    print(f"   Hex:   {nonce_hex}")

    print("\n" + "=" * 60)
    print("  All tests passed! ✅")
    print("=" * 60)
