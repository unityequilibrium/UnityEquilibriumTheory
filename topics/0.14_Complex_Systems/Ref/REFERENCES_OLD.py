"""
REFERENCES.py - 0.14 Complex Systems
======================================
DOIs for all data sources used in this topic.
"""

REFERENCES = {
    "primary": {
        "HRV_Biology": {
            "title": "Heart rate variability: Standards of measurement, physiological interpretation, and clinical use",
            "authors": ["Task Force of ESC and NASPE"],
            "journal": "Circulation",
            "volume": 93,
            "pages": "1043-1065",
            "year": 1996,
            "doi": "10.1161/01.CIR.93.5.1043",
        },
        "Stock_Market": {
            "title": "Quantifying Stock-Price Response to Demand Fluctuations",
            "authors": [
                "Gabaix, X.",
                "Gopikrishnan, P.",
                "Plerou, V.",
                "Stanley, H.E.",
            ],
            "journal": "Nature",
            "volume": 423,
            "pages": "267",
            "year": 2003,
            "doi": "10.1038/nature01624",
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
    print("0.14 Complex Systems - References")
    for name, ref in REFERENCES["primary"].items():
        print(f"📚 {name}: DOI {ref['doi']}")


if __name__ == "__main__":
    print_references()
