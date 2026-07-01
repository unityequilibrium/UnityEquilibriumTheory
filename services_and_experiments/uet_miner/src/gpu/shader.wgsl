// SHA256 Double Hash - WGSL Compute Shader
// Optimized for GPU parallel mining
// Works with AMD RX 6600 XT via Vulkan backend

// Round constants for SHA256
var<private> K: array<u32, 64> = array<u32, 64>(
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u,
    0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
    0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
    0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
    0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
    0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
    0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u,
    0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
    0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
    0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
    0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u,
    0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
    0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u,
    0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
    0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
    0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u
);

// Initial hash values
const H0: u32 = 0x6a09e667u;
const H1: u32 = 0xbb67ae85u;
const H2: u32 = 0x3c6ef372u;
const H3: u32 = 0xa54ff53au;
const H4: u32 = 0x510e527fu;
const H5: u32 = 0x9b05688cu;
const H6: u32 = 0x1f83d9abu;
const H7: u32 = 0x5be0cd19u;

// Input block header (80 bytes = 20 u32s)
struct BlockHeader {
    data: array<u32, 20>,
}

// Mining job input
struct MiningJob {
    header_base: array<u32, 19>,  // 76 bytes without nonce
    start_nonce: u32,
    target_hi: u32,               // Upper 32 bits of target for quick check
    target_lo: u32,               // Lower 32 bits
}

// Mining result output
struct MiningResult {
    found: u32,
    nonce: u32,
    hash: array<u32, 8>,
}

@group(0) @binding(0) var<storage, read> job: MiningJob;
@group(0) @binding(1) var<storage, read_write> result: MiningResult;

// Bitwise rotation right
fn rotr(x: u32, n: u32) -> u32 {
    return (x >> n) | (x << (32u - n));
}

// SHA256 compression functions
fn ch(x: u32, y: u32, z: u32) -> u32 {
    return (x & y) ^ (~x & z);
}

fn maj(x: u32, y: u32, z: u32) -> u32 {
    return (x & y) ^ (x & z) ^ (y & z);
}

fn sigma0(x: u32) -> u32 {
    return rotr(x, 2u) ^ rotr(x, 13u) ^ rotr(x, 22u);
}

fn sigma1(x: u32) -> u32 {
    return rotr(x, 6u) ^ rotr(x, 11u) ^ rotr(x, 25u);
}

fn gamma0(x: u32) -> u32 {
    return rotr(x, 7u) ^ rotr(x, 18u) ^ (x >> 3u);
}

fn gamma1(x: u32) -> u32 {
    return rotr(x, 17u) ^ rotr(x, 19u) ^ (x >> 10u);
}

// SHA256 hash of 80-byte block (block header)
fn sha256_80(header: array<u32, 20>) -> array<u32, 8> {
    var h = array<u32, 8>(H0, H1, H2, H3, H4, H5, H6, H7);
    var w: array<u32, 64>;

    // First block (64 bytes)
    for (var i = 0u; i < 16u; i++) {
        w[i] = header[i];
    }

    // Message schedule
    for (var i = 16u; i < 64u; i++) {
        w[i] = gamma1(w[i-2u]) + w[i-7u] + gamma0(w[i-15u]) + w[i-16u];
    }

    // Compression
    var a = h[0]; var b = h[1]; var c = h[2]; var d = h[3];
    var e = h[4]; var f = h[5]; var g = h[6]; var hh = h[7];

    for (var i = 0u; i < 64u; i++) {
        let t1 = hh + sigma1(e) + ch(e, f, g) + K[i] + w[i];
        let t2 = sigma0(a) + maj(a, b, c);
        hh = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    h[0] += a; h[1] += b; h[2] += c; h[3] += d;
    h[4] += e; h[5] += f; h[6] += g; h[7] += hh;

    // Second block (16 bytes of header + padding)
    // header[16..19] + 0x80 padding + length
    var block2: array<u32, 16>;
    block2[0] = header[16];
    block2[1] = header[17];
    block2[2] = header[18];
    block2[3] = header[19];
    block2[4] = 0x80000000u;  // Padding bit
    for (var i = 5u; i < 15u; i++) {
        block2[i] = 0u;
    }
    block2[15] = 640u;  // 80 bytes * 8 bits = 640 bits

    // Message schedule for block 2
    for (var i = 0u; i < 16u; i++) {
        w[i] = block2[i];
    }
    for (var i = 16u; i < 64u; i++) {
        w[i] = gamma1(w[i-2u]) + w[i-7u] + gamma0(w[i-15u]) + w[i-16u];
    }

    // Compression for block 2
    a = h[0]; b = h[1]; c = h[2]; d = h[3];
    e = h[4]; f = h[5]; g = h[6]; hh = h[7];

    for (var i = 0u; i < 64u; i++) {
        let t1 = hh + sigma1(e) + ch(e, f, g) + K[i] + w[i];
        let t2 = sigma0(a) + maj(a, b, c);
        hh = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    h[0] += a; h[1] += b; h[2] += c; h[3] += d;
    h[4] += e; h[5] += f; h[6] += g; h[7] += hh;

    return h;
}

// SHA256 hash of 32-byte input (the first hash result)
fn sha256_32(input: array<u32, 8>) -> array<u32, 8> {
    var h = array<u32, 8>(H0, H1, H2, H3, H4, H5, H6, H7);
    var w: array<u32, 64>;

    // Single block: 32 bytes of input + padding
    for (var i = 0u; i < 8u; i++) {
        w[i] = input[i];
    }
    w[8] = 0x80000000u;  // Padding
    for (var i = 9u; i < 15u; i++) {
        w[i] = 0u;
    }
    w[15] = 256u;  // 32 bytes * 8 bits = 256 bits

    // Message schedule
    for (var i = 16u; i < 64u; i++) {
        w[i] = gamma1(w[i-2u]) + w[i-7u] + gamma0(w[i-15u]) + w[i-16u];
    }

    // Compression
    var a = h[0]; var b = h[1]; var c = h[2]; var d = h[3];
    var e = h[4]; var f = h[5]; var g = h[6]; var hh = h[7];

    for (var i = 0u; i < 64u; i++) {
        let t1 = hh + sigma1(e) + ch(e, f, g) + K[i] + w[i];
        let t2 = sigma0(a) + maj(a, b, c);
        hh = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    h[0] += a; h[1] += b; h[2] += c; h[3] += d;
    h[4] += e; h[5] += f; h[6] += g; h[7] += hh;

    return h;
}

@compute @workgroup_size(128)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let nonce = job.start_nonce + global_id.x;

    // Build full 80-byte header with this nonce
    var header: array<u32, 20>;
    for (var i = 0u; i < 19u; i++) {
        header[i] = job.header_base[i];
    }
    header[19] = nonce;  // Nonce at end (little-endian)

    // Double SHA256
    let hash1 = sha256_80(header);
    let hash2 = sha256_32(hash1);

    // Check if hash meets target (quick check on first word - big endian)
    // Bitcoin hash comparison: hash must be <= target
    // Hash is in big-endian, so we compare from hash[0] (most significant)
    if (hash2[0] < job.target_hi ||
        (hash2[0] == job.target_hi && hash2[1] <= job.target_lo)) {
        // Found a valid nonce!
        // Simple assignment - race condition acceptable for mining
        // (any valid nonce works, doesn't matter which thread wins)
        result.found = 1u;
        result.nonce = nonce;
        for (var i = 0u; i < 8u; i++) {
            result.hash[i] = hash2[i];
        }
    }
}
