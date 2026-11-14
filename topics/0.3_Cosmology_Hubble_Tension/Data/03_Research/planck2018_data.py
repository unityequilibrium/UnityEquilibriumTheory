"""
Planck 2018 Cosmological Parameters
===================================
Source: Planck Collaboration 2018, A&A 641, A6
URL: https://arxiv.org/abs/1807.06209
"""

# Hubble constant
H0 = 67.36  # ± 0.54 km/s/Mpc

# Density parameters
OMEGA_BARYON_H2 = 0.02237  # ± 0.00015
OMEGA_CDM_H2 = 0.1200      # ± 0.0012
OMEGA_LAMBDA = 0.6847      # ± 0.0073
OMEGA_MATTER = 0.3153      # = 1 - Omega_Lambda

# Other parameters
OPTICAL_DEPTH = 0.0544     # reionization optical depth
N_S = 0.9649               # scalar spectral index
SIGMA_8 = 0.8111           # amplitude of fluctuations

# Derived
AGE_UNIVERSE_GYR = 13.787  # ± 0.020 Gyr

# For UET: k_B T_CMB
T_CMB = 2.7255  # K (CMB temperature today)

if __name__ == "__main__":
    print("Planck 2018 Cosmological Parameters")
    print(f"H0 = {H0} km/s/Mpc")
    print(f"Omega_Lambda = {OMEGA_LAMBDA}")
    print(f"Age = {AGE_UNIVERSE_GYR} Gyr")
