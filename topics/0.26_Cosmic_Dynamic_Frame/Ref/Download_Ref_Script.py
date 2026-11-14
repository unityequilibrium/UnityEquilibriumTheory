"""
Download_Ref_Script.py
======================
Topic: 0.26 Cosmic Dynamic Frame
Goal: Download foundational papers for the Toroidal/Cyclic Universe hypothesis.
"""

import os
import requests
import json
from pathlib import Path

# --- CONFIG ---
TOPIC_ID = "0.26_Cosmic_Dynamic_Frame"
PDF_DIR = Path(__file__).parent / "PDF_Downloads"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# Papers to Download (ArXiv IDs or Direct URLs)
PAPERS = {
    "Laniakea_Supercluster.pdf": "https://arxiv.org/pdf/1409.0880.pdf",  # Flow lines of galaxies
    "Conformal_Cyclic_Cosmology.pdf": "https://arxiv.org/pdf/1011.3706.pdf",  # Penrose's Cyclic Model
    "Toroidal_Universe_Texture.pdf": "https://arxiv.org/pdf/gr-qc/0005084.pdf",  # Topology
    "Superfluid_Vacuum_Theory.pdf": "https://arxiv.org/pdf/1508.01948.pdf",  # Vacuum as Superfluid
    "Cosmic_Topology_Status.pdf": "https://arxiv.org/pdf/1601.03350.pdf",  # Geometric constraints
}


def download_paper(name, url):
    path = PDF_DIR / name
    if path.exists():
        print(f"   [Exists] {name}")
        return

    print(f"   [Downloading] {name} from {url}...")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"   [Success] Saved to {path}")
        else:
            print(f"   [Failed] Status Code: {response.status_code}")
    except Exception as e:
        print(f"   [Error] {e}")


def run():
    print("=" * 60)
    print(f"📥 DOWNLOADING REFERENCES FOR TOPIC {TOPIC_ID}")
    print("=" * 60)

    for name, url in PAPERS.items():
        download_paper(name, url)

    # Generate Bibliography Analysis
    bib_path = Path(__file__).parent / "BIBLIOGRAPHY_ANALYSIS.md"
    with open(bib_path, "w", encoding="utf-8") as f:
        f.write("# 📚 Bibliography Analysis: Cosmic Dynamic Frame\n\n")
        f.write("## Why these papers matter to UET:\n\n")
        f.write("### 1. **Laniakea Supercluster (Tully et al.)**\n")
        f.write(
            "   - **Relevance:** Visualizes the 'Cosmic Flow' lines. Matches UET's 'River of Space' concept.\n"
        )
        f.write(
            "   - **Use Case:** Validate `Proof_Toroidal_Cycle.py` flow vectors against real Laniakea data.\n\n"
        )
        f.write("### 2. **Conformal Cyclic Cosmology (Penrose)**\n")
        f.write(
            "   - **Relevance:** Supports the 'Eternal Cycle' view (Big Bang is not the start, just a phase).\n"
        )
        f.write(
            "   - **Use Case:** Theoretical backing for UET's 'Geometric Rebirth'.\n\n"
        )
        f.write("### 3. **Superfluid Vacuum Theory (Volovik et al.)**\n")
        f.write(
            "   - **Relevance:** The core axiom of UET. Space is a fluid with zero viscosity.\n"
        )
        f.write(
            "   - **Use Case:** Justification for the 'Perpetual Engine' mechanism.\n"
        )

    print(f"\n   [Analysis] Generated {bib_path}")


if __name__ == "__main__":
    run()
