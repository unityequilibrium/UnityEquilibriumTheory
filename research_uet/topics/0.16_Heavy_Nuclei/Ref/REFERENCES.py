"""
References: Heavy Nuclei
========================

DOIs for all data sources used in this topic.
"""

REFERENCES = {
    "nuclear_mass": [
        {
            "title": "AME2020 atomic mass evaluation (II)",
            "authors": "Wang, M., Huang, W.J., Kondev, F.G. et al.",
            "journal": "Chinese Physics C 45, 030003",
            "year": 2021,
            "doi": "10.1088/1674-1137/abddaf",
            "data": "Nuclear binding energies for all isotopes",
            "source": "AME2020",
        },
        {
            "title": "Nuclear ground-state masses and deformations",
            "authors": "Möller, P., Sierk, A.J., Ichikawa, T., Sagawa, H.",
            "journal": "Atomic Data and Nuclear Data Tables 109-110, 1",
            "year": 2016,
            "doi": "10.1016/j.adt.2015.10.002",
            "data": "FRDM mass model",
        },
    ],
}

DATA_FILES = {
    "Code/heavy_binding/test_heavy_binding.py": {
        "source": "AME2020",
        "doi": "10.1088/1674-1137/abddaf",
        "verified": True,
    },
}


def list_references():
    """List all references."""
    print("=" * 60)
    print("0.16 HEAVY NUCLEI REFERENCES")
    print("=" * 60)
    for category, refs in REFERENCES.items():
        print(f"\n{category.upper()}:")
        for ref in refs:
            print(f"  [{ref['year']}] {ref['title']}")
            print(f"         DOI: {ref['doi']}")


if __name__ == "__main__":
    list_references()
