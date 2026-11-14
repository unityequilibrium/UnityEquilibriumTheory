"""
REFERENCES.py - 0.20 Atomic Physics
====================================
"""

REFERENCES = {
    "primary": {
        "Atomic_Evidence": {
            "title": "NIST ASD Research Evidence",
            "local_file": "RESEARCH_EVIDENCE.md",
        }
    }
}


def list_references():
    print("0.20 Atomic Physics References")
    for name, ref in REFERENCES["primary"].items():
        print(f"📚 {name}: File {ref['local_file']}")


if __name__ == "__main__":
    list_references()
