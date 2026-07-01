# Under Development Components

## Overview

This folder contains components that are currently under development or not yet started.

## Components Status

### ⏸️ In Progress (Started but incomplete)

#### uet_chain - Blockchain Core
**Status:** Started (minimal structure)
**Priority:** HIGH (Phase 1)
**Dependencies:** uet_security

**Missing Features:**
- Consensus engine (Tendermint/PBFT)
  - Block proposal
  - Voting mechanism
  - Finality
  - Fork resolution
- State machine
  - UTXO model or account model
  - State transitions
  - Transaction validation
- Storage layer
  - RocksDB/LMDB integration
  - Block storage
  - State DB
  - Indexing
- P2P networking
  - libp2p integration
  - Node discovery
  - Gossip protocol
  - Message routing

**Next Steps:**
1. Research libp2p integration
2. Implement consensus engine
3. Implement state machine
4. Implement storage layer

---

#### uet_kb - Knowledge Base
**Status:** Started (basic structure)
**Priority:** MEDIUM (Phase 2)
**Dependencies:** uet_core

**Missing Features:**
- Vector database integration (LanceDB)
- MCP server implementation
- JSON-RPC interface
- Knowledge base queries
- Database queries (PostgreSQL)

**Next Steps:**
1. Implement MCP server
2. Integrate LanceDB
3. Add query interface

---

### ⏸️ Not Started (Empty/WIP)

#### uet_governance - Governance System
**Status:** Empty/WIP
**Priority:** LOW (Phase 5)
**Dependencies:** None

**Missing Features:**
- Voting mechanism
- Proposal system
- Execution logic
- Governance parameters

**Notes:** Deferred until core blockchain is complete

---

#### uet_oracle - Oracle Infrastructure
**Status:** Empty/WIP
**Priority:** LOW (Phase 5)
**Dependencies:** None

**Missing Features:**
- Verification logic
- Data feeds
- Bridge to external data

**Notes:** Deferred until core blockchain is complete

---

#### uet_economic - Economic Policies
**Status:** Empty/WIP
**Priority:** LOW (Phase 5)
**Dependencies:** None

**Missing Features:**
- Token issuance
- Difficulty adjustment
- Reward distribution
- Economic parameters

**Notes:** Deferred until core blockchain is complete

---

#### uet_market - Market Infrastructure
**Status:** Empty/WIP
**Priority:** LOW (Phase 6)
**Dependencies:** None

**Missing Features:**
- AMM (Automated Market Maker)
- Price discovery
- Trading interface
- Liquidity pools

**Notes:** Deferred until core blockchain is complete

---

## Development Priority

### Phase 1 (Months 1-3) - Blockchain Core
1. **uet_chain** - Consensus engine
2. **uet_chain** - State machine
3. **uet_chain** - Storage layer
4. **uet_chain** - P2P networking

### Phase 2 (Months 3-4) - Security & Key Management
1. **Real Dilithium signatures** (replace MockSigner)
2. **Key management** (rotation, revocation)
3. **Transport security** (mTLS, hybrid KEX)
4. **Security monitoring**

### Phase 3 (Months 4-5) - API & Wallet
1. **JSON-RPC API**
2. **Wallet implementation**

### Phase 4 (Months 5-6) - Testing & Optimization
1. Comprehensive testing
2. Performance optimization
3. Documentation

### Phase 5 (Months 6-9) - Governance & Economics
1. **uet_governance**
2. **uet_economic**
3. **uet_oracle**

### Phase 6 (Months 9-12) - Market & Advanced Features
1. **uet_market**
2. Smart contracts
3. Cross-chain bridges

---

## Required Libraries

### For uet_chain
```toml
libp2p = "0.53"           # P2P networking
tokio = "1.0"             # Async runtime
rocksdb = "0.22"          # Embedded database
lmdb = "0.9"              # Alternative storage
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

### For uet_kb
```toml
lancedb = "0.4"           # Vector database
arrow-array = "50"
sqlx = { version = "0.7", features = ["postgres"] }
crossbeam-channel = "0.5"
```

---

## Reference Projects

| Project | Purpose | Key Learnings |
|---------|---------|---------------|
| Solana | High-performance blockchain | Parallel processing, account model |
| Polkadot | Multi-chain architecture | Substrate framework, XCMP |
| Cosmos SDK | Tendermint-based chains | ABCI, IBC, governance |
| Ethereum | Smart contract platform | EVM, state management |
| Tendermint | BFT consensus | Consensus engine |

---

## Notes

- All components in this folder are work-in-progress
- Focus on uet_chain first (Phase 1)
- Governance/Oracle/Economic/Market are deferred
- See `../STATUS_REPORT.md` for detailed status
- See `../PRODUCTION_ROADMAP.md` for full roadmap
