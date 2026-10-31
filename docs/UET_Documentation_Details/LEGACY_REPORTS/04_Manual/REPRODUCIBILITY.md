# Reproducibility Guide

> **Goal**: Ensure every test produces identical results on any machine  
> **Last Updated**: 2026-01-11

---

## 🔒 Quick Start

Add this to the top of every test file:

```python
from docs.scripts.core.audit.reproducibility import lock_all_seeds
lock_all_seeds(42)  # UET standard seed
```

---

## 📋 Environment Requirements

### Python Version
```
Python 3.11.x (tested on 3.11.9)
```

### Dependencies
See `requirements_frozen.txt` for exact versions.

Key packages:
- numpy==1.26.4
- scipy==1.12.0
- pandas==2.2.0

### Verification Command
```bash
pip install -r requirements_frozen.txt
python -c "from docs.scripts.core.audit.reproducibility import get_environment_info; print(get_environment_info())"
```

---

## 🎲 Seed Locking

### What Gets Locked
- `random` (Python stdlib)
- `numpy.random`
- `torch` (if installed)
- `tensorflow` (if installed)

### Standard Seed
```python
UET_SEED = 42
```

### Usage in Tests
```python
from docs.scripts.core.audit.reproducibility import lock_all_seeds, hash_dataset

# Lock at start
lock_all_seeds(42)

# Your test code...
data = load_data()
data_hash = hash_dataset(data)
print(f"Dataset hash: {data_hash}")  # Should match expected
```

---

## 🔐 Dataset Hashing

Every dataset should have a verified hash:

```python
from docs.scripts.core.audit.reproducibility import hash_file

# Verify data file
expected_hash = "a1b2c3d4e5f67890..."
actual_hash = hash_file("data/sparc_175.csv")
assert actual_hash == expected_hash, "Data corruption detected!"
```

---

## 📊 Artifact Generation

Generate audit trails for test runs:

```python
from docs.scripts.core.audit.reproducibility import generate_artifact, save_artifact

results = {"rmse": 0.082, "r_squared": 0.97}
artifact = generate_artifact(
    results=results,
    dataset_hash="abc123...",
    topic="0.1_Galaxy_Rotation"
)
save_artifact(artifact, "Result/run_artifact.json")
```

### Artifact Contents
```json
{
  "timestamp": "2026-01-11T12:00:00",
  "uet_version": "0.8.7",
  "python_version": "3.11.9",
  "numpy_version": "1.26.4",
  "seed": 42,
  "topic": "0.1_Galaxy_Rotation",
  "dataset_hash": "abc123...",
  "results": {"rmse": 0.082, "r_squared": 0.97}
}
```

---

## ✅ Verification Checklist

Before submitting results:

- [ ] `lock_all_seeds(42)` at top of test file
- [ ] Dataset hash matches expected value
- [ ] Artifact JSON generated
- [ ] Results match on fresh environment

---

## 🔄 Cross-Platform Notes

| Platform | Status | Notes |
|:---------|:------:|:------|
| Windows 10/11 | ✅ | Primary development |
| Ubuntu 22.04 | ✅ | CI tested |
| macOS 14+ | ⚠️ | Minor float differences possible |

For macOS, use `tolerance=1e-9` in comparisons.

---

## 🐛 Troubleshooting

### Results differ between runs
1. Ensure `lock_all_seeds()` is called BEFORE any random operations
2. Check that all imports happen AFTER seed lock
3. Verify exact package versions

### Dataset hash mismatch
1. Re-download data using `download_data.py`
2. Check for line ending differences (CRLF vs LF)
3. Verify no preprocessing was applied

---

*Reproducibility is not optional — it's foundational.*
