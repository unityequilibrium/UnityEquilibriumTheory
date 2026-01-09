"""
References: Atomic Physics
==========================

DOIs for all data sources used in this topic.
"""

REFERENCES = {
    "hydrogen_spectrum": [
        {
            "title": "NIST Atomic Spectra Database (version 5.11)",
            "authors": "Kramida, A., Ralchenko, Yu., Reader, J. and NIST ASD Team",
            "year": 2023,
            "doi": "10.18434/T4W30F",
            "url": "https://physics.nist.gov/asd",
            "data": "Hydrogen Balmer series wavelengths",
            "source": "NIST",
        },
    ],
    "rydberg_constant": [
        {
            "title": "CODATA recommended values of the fundamental physical constants: 2018",
            "authors": "Tiesinga, E., Mohr, P.J., Newell, D.B. & Taylor, B.N.",
            "journal": "J. Phys. Chem. Ref. Data 50, 033105",
            "year": 2021,
            "doi": "10.1063/5.0064853",
            "data": "R∞ = 10973731.568160(21) m⁻¹",
            "source": "NIST/CODATA",
        },
    ],
}

DATA_FILES = {
    "Code/hydrogen_spectrum/test_hydrogen_spectrum.py": {
        "source": "NIST ASD, CODATA 2018",
        "doi": "10.18434/T4W30F",
        "verified": True,
    },
}


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.20 ATOMIC PHYSICS REFERENCES")
    print("=" * 60)
    for category, refs in REFERENCES.items():
        print(f"\n{category.upper()}:")
        for ref in refs:
            print(f"  [{ref['year']}] {ref['title']}")
            print(f"         DOI: {ref['doi']}")


if __name__ == "__main__":
    list_references()
