"""
REFERENCES.py - 0.15 Cluster Dynamics
=====================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "Zwicky_1933": "Fritz Zwicky - Die Rotverschiebung (Discovery of Dark Matter)",
        "BulletCluster_2006": "Clowe et al. - Direct Empirical Proof of Dark Matter",
        "Bahcall_1988": "Neta Bahcall - Large-Scale Structure Review",
        "JWST_CEERS_2023": "Finkelstein et al. - CEERS Program (z > 10 Galaxies) DOI: 10.17909/z7p0-8481",
        "JWST_GLASS_2022": "Treu et al. - GLASS-JWST ERS (z > 10 Galaxies) DOI: 10.17909/kw3c-n857",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Common mappings
    mapping = {
        "Zwicky_1933": "Zwicky Die Rotverschiebung",
        "BulletCluster_2006": "Direct Empirical Proof Existence Dark Matter",
        "Bahcall_1988": "Large-Scale Structure Universe Galaxy Clusters",
    }

    search_name = mapping.get(name, name)

    # Try generic search in PDF folder
    for pdf in REFERENCES["PDF_DIR"].glob("*.pdf"):
        if search_name.lower() in pdf.name.lower():
            return pdf

    return None


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.15 Cluster Dynamics - References")
    print("=" * 60)
    print(f"Analysis: {REFERENCES['ANALYSIS']}")
    print(f"Pdf Dir: {REFERENCES['PDF_DIR']}\n")

    print("Key Papers:")
    for key, desc in REFERENCES["KEY_PAPERS"].items():
        ref_path = get_ref_path(key)
        status = "✅ FOUND" if ref_path else "❌ MISSING (Run Downloader)"
        print(f"  * {key}: {desc} [{status}]")


if __name__ == "__main__":
    list_references()
