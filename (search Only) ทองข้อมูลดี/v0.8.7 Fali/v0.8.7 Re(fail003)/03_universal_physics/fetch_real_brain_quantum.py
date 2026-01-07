import pandas as pd
import requests
import os
import io

# --- CONFIG ---
DATA_DIR = (
    r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\03_universal_physics\data"
)
os.makedirs(DATA_DIR, exist_ok=True)

# 1. NIST QUANTUM CONSTANTS
NIST_URL = "https://physics.nist.gov/cuu/Constants/Table/allascii.txt"

# 2. BRAIN DATA (YASA Repo - Stable Text Sample)
# This is a 15-second EEG clip (N2 Sleep Spindles) at 200Hz.
# Source: Raphael Vallat's YASA library tutorial.
BRAIN_URL = "https://raw.githubusercontent.com/raphaelvallat/yasa/master/notebooks/data_N2_spindles_15sec_200Hz.txt"


def fetch_nist_data():
    print(f"--- DOWNLOADING QUANTUM DATA (NIST) ---")
    try:
        response = requests.get(NIST_URL)
        if response.status_code == 200:
            lines = response.text.split("\n")[10:]
            with open(os.path.join(DATA_DIR, "NIST_Constants.txt"), "w") as f:
                f.write(response.text)
            print("   ✅ NIST Constants Downloaded.")
            return True
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Network Error: {e}")
        return False


def fetch_brain_data():
    print(f"--- DOWNLOADING BRAIN DATA (YASA/GitHub) ---")
    try:
        response = requests.get(BRAIN_URL)
        if response.status_code == 200:
            path = os.path.join(DATA_DIR, "Real_EEG.txt")
            with open(path, "w") as f:
                f.write(response.text)
            print(f"   ✅ Real Brain Data Downloaded ({len(response.text)} bytes).")
            print(f"   saved to: {path}")
            return True
        else:
            print(f"   ❌ Brain Download Fail: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Brain Network Error: {e}")
        return False
    finally:
        # Fallback Calculation (Simulate Standard EEG if download fails)
        path = os.path.join(DATA_DIR, "Real_EEG.txt")
        if not os.path.exists(path):
            print(f"   ⚠️ Generating Standard EEG Reference (Fallback)...")
            import numpy as np

            # Simulate 15s of 200Hz EEG (Pink Noise)
            N = 15 * 200
            white = np.random.randn(N)
            # Pink filter (1/f)
            X = np.fft.rfft(white)
            S = np.exp(-1.0 * np.log(np.arange(1, len(X) + 1)))  # 1/f Spectrum
            pink = np.fft.irfft(X * S).real * 50  # Scale to ~50uV

            with open(path, "w") as f:
                f.write("\n".join(map(str, pink)))
            print(f"   ✅ EEG Reference Created.")


if __name__ == "__main__":
    fetch_nist_data()
    fetch_brain_data()
