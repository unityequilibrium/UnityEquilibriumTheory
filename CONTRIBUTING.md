# 🤝 Contributing to UET Harness

Thank you for your interest in contributing! 🎉

---

## 📋 Ways to Contribute

### 🐛 Report Bugs

Open an issue with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

### 📖 Documentation

- Improve README, docstrings, or tutorials
- Add examples for new use cases
- Fix typos or clarify explanations

### 🔬 Add Physics Tests

- Propose new validation tests
- Add real data comparisons
- Extend to new physics domains

### 🚀 Code Improvements

- Performance optimizations
- Bug fixes
- New features (discuss first in an issue)

---

## 🧪 Current Test Status (2026-01-01)

| Domain | Tests | Pass Rate |
|:---|:---:|:---:|
| **Galaxies (SPARC)** | 154 | 73% |
| **Dwarfs (LITTLE THINGS)** | 26 | 69% |
| **EM (Casimir)** | 12 | 92% |
| **Total** | 180+ | ✅ |

### 🎯 Areas Needing Work:

1. **Compact galaxies** - 40% pass rate (needs improvement)
2. **Cosmology** - Not tested against CMB/LSS
3. **Mathematical rigor** - Parameter derivation needed
4. **Peer review** - Academic validation pending

---

## 🔧 Development Setup

```bash
git clone https://github.com/unityequilibrium/Equation-UET-v0.8.7.git
cd Equation-UET-v0.8.7

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install numpy scipy matplotlib

# Run tests
cd research_uet
python lab/galaxies/test_175_galaxies.py
```

---

## 📝 Pull Request Guidelines

1. **Fork** the repository
2. **Create a branch** for your feature
3. **Write tests** if applicable
4. **Update docs** if needed
5. **Submit PR** with clear description

---

## 💡 Feature Requests

Before proposing a new feature:

1. Check existing issues
2. Open a discussion issue first
3. Explain the use case
4. Be patient for feedback

---

## 🔬 Physics Contributions

If you're adding new physics tests:

1. **Use UET equations** - Must use the core `Ω[C, I]` framework
2. **Real data required** - Include citations to data sources
3. **Document limitations** - Be honest about what doesn't work

---

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Accept that UET has limitations (it's a simulation framework, not a universal law)

---

## 📬 Contact

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

*Thank you for helping improve UET!* 🙏
