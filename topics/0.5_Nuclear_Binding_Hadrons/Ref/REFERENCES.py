"""
REFERENCES.py - 0.5 Nuclear Binding & Hadrons
=============================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "AME2020": "Wang et al. (2021) - Atomic Mass Evaluation",
        "Yukawa_1935": "Yukawa (1935) - Meson Theory",
        "Wilson_LCD": "Wilson (1974) - Lattice QCD Confinement",
    },
    "Internal_Refs": {
        "Borexino": "Ref_Neutrino_Borexino2020_CNO.pdf",
        "KATRIN": "Ref_Neutrino_KATRIN2022_Limit.pdf",
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    # Check internal first
    if name in REFERENCES["Internal_Refs"]:
        internal = REFERENCES["PDF_DIR"] / REFERENCES["Internal_Refs"][name]
        if internal.exists():
            return internal

    # Common mappings for search
    mapping = {
        "AME2020": "Atomic Mass Evaluation",
        "Yukawa_1935": "Interaction of Elementary Particles",
        "Wilson_LCD": "Confinement of quarks",
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
    print("0.5 Nuclear Binding & Hadrons - References")
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
