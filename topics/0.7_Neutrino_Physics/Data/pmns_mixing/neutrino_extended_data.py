"""
Neutrino Extended Data
======================
Data for KATRIN 2025 and Borexino solar neutrino experiments.
DOI: 10.1126/science.aql2691 (Nature 2025 - KATRIN)
DOI: 10.1038/s41586-020-2934-0 (Nature 2020 - Borexino CNO)
"""

# KATRIN 2025 Results (Direct neutrino mass measurement)
# Reference: KATRIN Collaboration, Science (2025)
KATRIN_RESULTS = {
    "mass_limit_eV": 0.45,  # 90% CL upper limit on m(nu_e)
    "best_fit_eV": 0.26,  # Best fit value
    "uncertainty_eV": 0.12,
    "experiment": "KATRIN",
    "year": 2025,
    "DOI": "10.1126/science.aql2691",
}

# Borexino Solar Neutrino Results (2020)
# Reference: Borexino Collaboration, Nature 587 (2020) 577-582
SOLAR_NEUTRINOS_BOREXINO = {
    "CNO_cycle": {
        "flux_cm2_s": 6.6e8,  # CNO neutrino flux
        "uncertainty_percent": 18,
        "significance_sigma": 5.0,
    },
    "pp_chain": {
        "pp_flux": 6.1e10,  # pp chain flux
        "Be7_flux": 4.99e9,  # Be-7 flux
        "pep_flux": 1.44e8,  # pep flux
    },
    "experiment": "Borexino",
    "location": "Gran Sasso, Italy",
    "DOI": "10.1038/s41586-020-2934-0",
}

# Cosmic Neutrino Background (CNB) theoretical predictions
CNB_DATA = {
    "temperature_K": 1.95,  # T_nu = (4/11)^(1/3) * T_cmb
    "density_per_cm3": 56,  # per flavor, ~336 total
    "decoupling_MeV": 2.3,  # Neutrino decoupling temperature
    "N_eff": 3.045,  # Effective number of species (SM)
    "DOI": "10.1016/j.physrep.2021.01.001",
}
