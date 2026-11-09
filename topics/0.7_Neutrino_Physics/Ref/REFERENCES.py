"""
REFERENCES.py - 0.7 Neutrino Physics
====================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "Davis_1968": "Davis et al. (1968) - Search for neutrinos from the Sun",
        "Pontecorvo_1967": "Pontecorvo (1967) - Neutrino Oscillation Theory",
        "SuperK_1998": "Super-Kamiokande (1998) - Evidence for Oscillation",
        "KATRIN_2022": "KATRIN Collaboration (2022) - Neutrino Mass Limit",
    },
    "Borexino_Metadata": {
        "title": "Experimental evidence of neutrinos from the CNO fusion cycle in the Sun",
        "authors": ["Borexino Collaboration"],
        "journal": "Nature",
        "year": 2020,
        "doi": "10.1038/s41586-020-2934-0",
        "local_file": "Neutrino_Borexino2020_CNO.pdf",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Check internal metadata first
    if name == "Borexino":
        path = REFERENCES["PDF_DIR"] / REFERENCES["Borexino_Metadata"]["local_file"]
        if path.exists():
            return path

    # Common mappings
    mapping = {
        "Davis_1968": "Search for neutrinos from the Sun",
        "Pontecorvo_1967": "Neutrino Experiments and the Problem",
        "SuperK_1998": "Evidence for Oscillation of Atmospheric",
        "KATRIN_2022": "KATRIN",
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
    print("0.7 Neutrino Physics - References")
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
