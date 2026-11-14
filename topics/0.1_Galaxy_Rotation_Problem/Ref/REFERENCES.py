"""
REFERENCES.py - 0.1 Galaxy Rotation Problem
============================================
Central registry for external citations and analysis.
"""

from pathlib import Path

REF_DIR = Path(__file__).parent

REFERENCES = {
    "ANALYSIS": REF_DIR / "BIBLIOGRAPHY_ANALYSIS.md",
    "PDF_DIR": REF_DIR / "PDF_Downloads",
    "DATA_DIR": REF_DIR / "Data_Source",
    "KEY_PAPERS": {
        "SPARC": "Lelli et al. (2016) - SPARC Dataset",
        "RAR": "McGaugh et al. (2016) - Radial Acceleration Relation",
        "MOND": "Milgrom (1983) - Modified Dynamics",
    },
    "SPARC_METADATA": {
        "title": "Spitzer Photometry and Accurate Rotation Curves (SPARC)",
        "authors": ["Lelli, F.", "McGaugh, S.S.", "Schombert, J.M."],
        "year": 2016,
        "doi": "10.3847/0004-6256/152/6/157",
        "local_file": "Ref_Lelli2016_SPARC.pdf",  # In PDF_Downloads
    },
}


def get_ref_path(name: str):
    """Returns path to a specific reference PDF if downloaded."""
    pdf_path = REFERENCES["PDF_DIR"] / f"{name}.pdf"
    if pdf_path.exists():
        return pdf_path

    # Check for legacy naming in moved files
    if name == "SPARC":
        legacy = REFERENCES["PDF_DIR"] / REFERENCES["SPARC_METADATA"]["local_file"]
        if legacy.exists():
            return legacy

    return None


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.1 Galaxy Rotation Problem - References")
    print("=" * 60)
    print(f"Analysis: {REFERENCES['ANALYSIS']}")
    print(f"Data Source: {REFERENCES['DATA_DIR']}\n")

    print("Key Papers:")
    for key, desc in REFERENCES["KEY_PAPERS"].items():
        print(f"  * {key}: {desc}")


if __name__ == "__main__":
    list_references()
