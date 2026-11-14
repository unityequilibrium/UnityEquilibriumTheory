"""
REFERENCES.py
=============
Registry of Scientific Sources for Topic 0.26 (Dynamic Universe).
Standard: UET-Ref-v1.0
"""

SOURCES = {
    "PIONEER_1998": {
        "title": "Indication, from Pioneer 10/11, Galileo, and Ulysses Data, of an Apparent Anomalous, Weak, Long-Range Acceleration",
        "authors": [
            "Anderson, J. D.",
            "Laing, P. A.",
            "Lau, E. L.",
            "Liu, A. S.",
            "Nieto, M. M.",
            "Turyshev, S. G.",
        ],
        "year": 1998,
        "journal": "Physical Review Letters",
        "volume": 81,
        "pages": "2858-2861",
        "doi": "10.1103/PhysRevLett.81.2858",
        "key_finding": "Anomalous acceleration a_P = (8.74 +/- 1.33) x 10^-8 cm/s^2 directed towards the Sun.",
    },
    "SPARC_2016": {
        "title": "SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and H-alpha Rotation Curves",
        "authors": ["Lelli, F.", "McGaugh, S. S.", "Schombert, J. M."],
        "year": 2016,
        "journal": "The Astronomical Journal",
        "volume": 152,
        "issue": 6,
        "key_finding": "High-quality rotation curves for benchmarking dark matter models.",
    },
    "RELATIVITY_STANDARD": {
        "title": "Special Relativity",
        "context": "Lorentz Transformation required for high-velocity particle/fluid analysis per User Request.",
        "formula": "gamma = 1 / sqrt(1 - v^2/c^2)",
    },
}


def get_citation(key):
    if key in SOURCES:
        s = SOURCES[key]
        return f"{s['authors'][0]} et al. ({s['year']}). {s['title']}."
    return "Unknown Source"
