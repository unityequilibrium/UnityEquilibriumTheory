# REFERENCES.py - Topic 0.31: Space-Time Propulsion

REFERENCES = {
    "KUGELBLITZ_MOTHER": {
        "title": "Geons",
        "author": "John Archibald Wheeler",
        "year": 1955,
        "journal": "Physical Review",
        "summary": "Coined the term Kugelblitz—a black hole created from pure radiation (light/gamma rays). Foundation for energy-to-mass collapse.",
    },
    "SINGULARITY_VANGUARD": {
        "title": "The Schwarzschild Kugelblitz: A Starship Engine for the Next Millennium",
        "author": "Jeffrey S. Lee",
        "year": 2013,
        "source": "arXiv:1301.1648",
        "summary": "Explores the use of Hawking radiation from a micro-singularity to accelerate a spacecraft to relativistic speeds (0.1c - 0.7c).",
    },
    "HAWKING_RADIATION": {
        "title": "Black hole explosions?",
        "author": "Stephen Hawking",
        "year": 1974,
        "journal": "Nature",
        "summary": "Proved that black holes emit thermal radiation and evaporate. Essential for the 'Disposable Anchor' logic in UET SGS.",
    },
    "OBERTH_EFFECT": {
        "title": "Ways to Spaceflight (Wege zur Raumschiffahrt)",
        "author": "Hermann Oberth",
        "year": 1929,
        "summary": "The principle that a rocket engine's effectiveness increases with high velocity—justifying the 'Perisling' acceleration in UET SGS.",
    },
}


def get_ref(key):
    return REFERENCES.get(key, "Reference not found.")
