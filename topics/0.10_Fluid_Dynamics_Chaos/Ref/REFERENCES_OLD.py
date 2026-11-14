"""
REFERENCES.py - 0.10 Fluid Dynamics & Chaos
============================================
DOIs for all data sources used in this topic.
"""

REFERENCES = {
    "primary": {
        "Reynolds_Original": {
            "title": "An Experimental Investigation of the Circumstances Which Determine Transition",
            "authors": ["Reynolds, O."],
            "journal": "Phil. Trans. R. Soc.",
            "volume": 174,
            "pages": "935-982",
            "year": 1883,
            "doi": "10.1098/rstl.1883.0029",
        },
        "Kolmogorov": {
            "title": "The local structure of turbulence in incompressible viscous fluid",
            "authors": ["Kolmogorov, A.N."],
            "journal": "Proceedings of the USSR Academy of Sciences",
            "volume": 30,
            "pages": "299-303",
            "year": 1941,
            "doi": "10.1098/rspa.1991.0075",
        },
    },
    "supplementary": [
        {
            "name": "General Physics Reference",
            "local_files": ["gr-qc_9504004.pdf", "1606.09251.pdf", "1609.05917.pdf"],
        }
    ],
}


def print_references():
    print("0.10 Fluid Dynamics & Chaos - References")
    for name, ref in REFERENCES["primary"].items():
        print(f"📚 {name}: DOI {ref['doi']}")


if __name__ == "__main__":
    print_references()
