# UET Public Repository Structure (Proposal)

## Overview
This document defines the structure for the upcoming `uet-harness-public` repository, ensuring high standards of code quality, documentation, and reproducibility.

## Directory Structure

```text
uet-harness/
├── .github/                # CI/CD workflows (GitHub Actions)
├── docs/                   # Documentation (MkDocs source)
│   ├── api/                # API reference
│   ├── theory/             # Physical derivations
│   └── tests/              # Test explanations
├── examples/               # Notebooks and tutorials
├── src/                    # Core UET source code
│   ├── uet_core/           # PDE solvers, physical kernels
│   ├── uet_analytics/      # Statistical analysis and plotting
│   └── uet_utils/          # General helpers
├── tests/                  # Automated validation suite (from v0.8.7)
│   ├── unit/               # Code unit tests
│   └── physics/            # Physical validation tests (16 topic folders)
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md         # Guidelines for collaborators
├── LICENSE                 # MIT or GPLv3
├── README.md               # Main landing page
├── requirements.txt
└── setup.py                # Package configuration
```

## Key Components

### 1. Verification Engine
The repository will include the `run_all_tests.py` script as the core verification engine. Every pull request will trigger a full 52-test validation.

### 2. Live Documentation
Hosted on GitHub Pages or Read the Docs, including interactive Plotly visualizations of the energy field.

### 3. Data Archival
Reference data (like Shen 2011 quasar catalog) will be hosted as submodules or via DVC (Data Version Control) to keep the main repo lightweight.

## Dissemination Strategy
- **Twitter/X Thread:** Announcement of open-source release.
- **Medium/Substack:** High-level walkthrough of the code and theory.
- **YouTube:** Visualizations of UET simulations.

---
*UET Public Repo Plan - 2025-12-28*
