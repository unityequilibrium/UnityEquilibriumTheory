"""
REFERENCES.py - 0.17 Mass Generation
=====================================
"""

REFERENCES = {
    "primary": {
        "Mass_Mechanism": {
            "title": "Information-theoretic origin of mass",
            "local_files": ["1606.09251.pdf", "millennium_prize_rules_0.pdf"],
        }
    }
}


def list_references():
    print("0.17 Mass Generation References")
    for name, ref in REFERENCES["primary"].items():
        print(f"📚 {name}: Files {ref['local_files']}")


if __name__ == "__main__":
    list_references()
