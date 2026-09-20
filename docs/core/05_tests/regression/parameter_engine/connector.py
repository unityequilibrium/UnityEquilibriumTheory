"""
UET Data Connector Interface
============================
Standard interface for connecting the UET Parameter Engine to
external experimental databases (NASA NED, CERN Open Data, NIST).

Philosophy:
To be "Self-Driving", the engine must be able to fetch Reality
to compare against its Theory predictions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class DataConnector(ABC):
    @abstractmethod
    def fetch_constant(self, name: str) -> float:
        """Fetch a fundamental constant value (e.g. 'alpha', 'G')."""
        pass

    @abstractmethod
    def fetch_particle_mass(self, particle_name: str) -> float:
        """Fetch particle mass in GeV (e.g. 'proton', 'higgs')."""
        pass

    @abstractmethod
    def fetch_galaxy_data(self, galaxy_name: str) -> Dict[str, Any]:
        """Fetch galaxy rotation data (V_obs, R, Mass)."""
        pass


class MockDataConnector(DataConnector):
    """
    Simulates external API for testing and offline development.
    Returns standard CODATA 2024 / PDG / SPARC values.
    """

    CONSTANTS = {
        "alpha": 1 / 137.035999084,
        "G": 6.67430e-11,
        "h_bar": 1.0545718e-34,
        "sin2_theta_w": 0.23122,
    }

    PARTICLES = {
        "proton": 0.938272,
        "neutron": 0.939565,
        "electron": 0.000511,
        "muon": 0.105658,
        "tau": 1.77686,
    }

    GALAXIES = {
        "DDO154": {"V_flat": 47.0, "M_HI": 4e8, "Dist": 4.0},
        "NGC6503": {"V_flat": 116.0, "M_HI": 1e9, "Dist": 5.2},
    }

    def fetch_constant(self, name: str) -> float:
        return self.CONSTANTS.get(name, 0.0)

    def fetch_particle_mass(self, particle_name: str) -> float:
        return self.PARTICLES.get(particle_name.lower(), 0.0)

    def fetch_galaxy_data(self, galaxy_name: str) -> Dict[str, Any]:
        return self.GALAXIES.get(galaxy_name, {})
