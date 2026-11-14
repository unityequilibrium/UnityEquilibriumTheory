import numpy as np


class OceanHeatSink:
    def __init__(self, volume_m3=1.0, wall_thickness_m=0.2):
        """
        Thermodynamic Model of a "Living Heat Sink".

        Physics Principles:
        1. Ground Coupling: Conduction from deep sand bed (stable cold source).
        2. Thermal Inertia: Resistance to temperature change due to mass.
        3. Passive Flow: Chimney effect allowing slow water exchange.
        """
        # 1. Structure Properties (Geopolymer + Graphene)
        self.density_concrete = 2400.0  # kg/m3
        self.specific_heat_concrete = 1000.0  # J/kg/K (High thermal mass)
        self.conductivity_graphene_mix = 20.0  # W/mK (Optimized: High-grade Graphene)

        self.volume = volume_m3
        self.wall_thickness = wall_thickness_m

        # Calculate Thermal Mass (Capacity) -> J/K
        self.mass = self.volume * self.density_concrete
        self.heat_capacity = self.mass * self.specific_heat_concrete

        # 2. Environment Constants
        self.ground_temp = 26.0  # Deep Sand Bed (Stable)
        # Reduced exchange rate to realistic "Sanctuary" (0.02% per second turnover)
        self.water_exchange_rate = 0.0002

        # 3. State
        self.internal_temp = 26.0  # Start at equilibrium with ground

    def update(self, ambient_temp, dt_seconds=60):
        """
        Update internal temperature based on Energy Flux (Joules).
        dT = Net_Energy_In / Total_Heat_Capacity
        """
        # Physics Constants
        c_water = 4186.0  # J/kg/K
        rho_water = 1025.0  # kg/m3

        # 1. Calculate Total Heat Capacity of the System (Structure + Internal Water)
        # Assume 50% porosity (Gyroid)
        vol_concrete = self.volume * 0.5
        vol_water = self.volume * 0.5

        mass_concrete = vol_concrete * self.density_concrete
        mass_water = vol_water * rho_water

        # Total Limit to change (Thermal Mass)
        C_total = (mass_concrete * self.specific_heat_concrete) + (mass_water * c_water)

        # 2. Energy Fluxes (Watts = J/s)

        # A. Advection (Water Flow)
        # Mass flow rate = % exchange * vol_water * density
        m_dot = self.water_exchange_rate * vol_water * rho_water

        # Power In = m_dot * c_p * deltaT
        P_flow = m_dot * c_water * (ambient_temp - self.internal_temp)

        # B. Conduction (Ground Cooling)
        # Power Out = k * A * deltaT / d
        # Effective Area = Footprint (approx volume^(2/3))
        area = self.volume ** (2 / 3)
        # Enhanced conductivity from Graphene
        k_eff = self.conductivity_graphene_mix

        # Heat transfer from ground to internal (if ground < internal, P_ground is negative = cooling)
        P_ground = k_eff * area * (self.ground_temp - self.internal_temp) / self.wall_thickness

        # 3. Total Energy Change
        # Net Power = Flow (Warming) + Ground (Cooling)
        P_net = P_flow + P_ground

        # Energy gained/lost in dt
        Energy_delta = P_net * dt_seconds

        # 4. Temperature Change
        delta_T = Energy_delta / C_total

        self.internal_temp += delta_T
        return self.internal_temp

    def get_status(self):
        return {
            "Internal Temp": f"{self.internal_temp:.2f} C",
            "Thermal Mass": f"{self.heat_capacity/1e6:.2f} MJ/K",
        }
