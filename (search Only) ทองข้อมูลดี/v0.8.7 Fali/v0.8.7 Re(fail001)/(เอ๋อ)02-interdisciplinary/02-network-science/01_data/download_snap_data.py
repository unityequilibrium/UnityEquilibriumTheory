#!/usr/bin/env python3
"""
🌐 NETWORK SCIENCE: Download Real Network Data
================================================

Downloads real-world network datasets from Stanford SNAP
for testing F = -∇Ω hypothesis on opinion/consensus dynamics.

Data Sources:
- Stanford SNAP: https://snap.stanford.edu/data/

Author: GDS Research Team
Date: 2025-12-28
"""

import urllib.request
import gzip
import os
from pathlib import Path
import shutil

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).parent
SNAP_BASE_URL = "https://snap.stanford.edu/data"

# Networks to download (small to medium size for initial testing)
NETWORKS = {
    # Social Networks
    "facebook_combined": {
        "url": f"{SNAP_BASE_URL}/facebook_combined.txt.gz",
        "description": "Facebook ego-networks (4,039 nodes, 88,234 edges)",
        "type": "undirected",
    },
    # Email Communication
    "email_enron": {
        "url": f"{SNAP_BASE_URL}/email-Enron.txt.gz",
        "description": "Enron email network (36,692 nodes, 183,831 edges)",
        "type": "undirected",
    },
    # Collaboration Networks
    "ca_grqc": {
        "url": f"{SNAP_BASE_URL}/ca-GrQc.txt.gz",
        "description": "arXiv General Relativity collaboration (5,242 nodes)",
        "type": "undirected",
    },
    "ca_hepth": {
        "url": f"{SNAP_BASE_URL}/ca-HepTh.txt.gz",
        "description": "arXiv High Energy Physics Theory (9,877 nodes)",
        "type": "undirected",
    },
}

# Classic small network (included directly - no download needed)
KARATE_CLUB = """
0 1
0 2
0 3
0 4
0 5
0 6
0 7
0 8
0 10
0 11
0 12
0 13
0 17
0 19
0 21
0 31
1 2
1 3
1 7
1 13
1 17
1 19
1 21
1 30
2 3
2 7
2 8
2 9
2 13
2 27
2 28
2 32
3 7
3 12
3 13
4 6
4 10
5 6
5 10
5 16
6 16
8 30
8 32
8 33
9 33
13 33
14 32
14 33
15 32
15 33
18 32
18 33
19 33
20 32
20 33
22 32
22 33
23 25
23 27
23 29
23 32
23 33
24 25
24 27
24 31
25 31
26 29
26 33
27 33
28 31
28 33
29 32
29 33
30 32
30 33
31 32
31 33
32 33
"""


def download_network(name: str, url: str, output_dir: Path) -> bool:
    """Download and extract a network from SNAP."""

    output_file = output_dir / f"{name}.txt"
    gz_file = output_dir / f"{name}.txt.gz"

    if output_file.exists():
        print(f"   ✅ {name} already exists")
        return True

    print(f"   📥 Downloading {name}...")

    try:
        # Download
        urllib.request.urlretrieve(url, gz_file)

        # Extract
        with gzip.open(gz_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove gz file
        gz_file.unlink()

        print(f"   ✅ Downloaded {name}")
        return True

    except Exception as e:
        print(f"   ❌ Failed to download {name}: {e}")
        if gz_file.exists():
            gz_file.unlink()
        return False


def create_karate_club(output_dir: Path):
    """Create Zachary's Karate Club network."""

    output_file = output_dir / "karate_club.txt"

    if output_file.exists():
        print("   ✅ karate_club already exists")
        return

    with open(output_file, "w") as f:
        f.write("# Zachary's Karate Club Network\n")
        f.write("# 34 nodes, 78 edges\n")
        f.write("# Classic small network for testing\n")
        f.write(KARATE_CLUB.strip())

    print("   ✅ Created karate_club.txt")


def create_readme(output_dir: Path):
    """Create README documenting data sources."""

    readme = output_dir / "README.md"

    content = """# Network Science Data

## Data Sources

All network data from [Stanford SNAP](https://snap.stanford.edu/data/).

## Networks

| File | Nodes | Edges | Type | Source |
|------|-------|-------|------|--------|
| karate_club.txt | 34 | 78 | Social | Zachary 1977 |
| facebook_combined.txt | 4,039 | 88,234 | Social | SNAP |
| email_enron.txt | 36,692 | 183,831 | Email | SNAP |
| ca_grqc.txt | 5,242 | 14,496 | Collaboration | SNAP |
| ca_hepth.txt | 9,877 | 25,998 | Collaboration | SNAP |

## File Format

Edge list format:
```
node1 node2
node1 node3
...
```

## Usage

```python
import networkx as nx

# Load network
G = nx.read_edgelist("karate_club.txt", comments='#')
print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
```

## References

1. Leskovec, J., & Krevl, A. (2014). SNAP Datasets: Stanford Large Network Dataset Collection.
2. Zachary, W. W. (1977). An information flow model for conflict and fission in small groups.

*Downloaded: 2025-12-28*
"""

    with open(readme, "w") as f:
        f.write(content)

    print("   ✅ Created README.md")


def main():
    """Download all network datasets."""

    print("\n" + "🌐" * 30)
    print("   NETWORK SCIENCE DATA DOWNLOAD")
    print("🌐" * 30)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create Karate Club (no download needed)
    print("\n📋 Creating classic networks...")
    create_karate_club(DATA_DIR)

    # Download SNAP networks
    print("\n📋 Downloading SNAP networks...")

    success = 0
    for name, info in NETWORKS.items():
        if download_network(name, info["url"], DATA_DIR):
            success += 1

    # Create README
    print("\n📋 Creating documentation...")
    create_readme(DATA_DIR)

    # Summary
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {success + 1}/{len(NETWORKS) + 1} networks ready")
    print("=" * 60)

    print(f"\n📁 Data saved to: {DATA_DIR}")
    print("\n✅ Next: Run network_analysis.py to test F = -∇Ω")


if __name__ == "__main__":
    main()
