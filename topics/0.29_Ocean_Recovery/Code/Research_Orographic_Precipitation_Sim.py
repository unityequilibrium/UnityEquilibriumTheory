"""
🚀 UET-ENVIRONMENTAL: ARTIFICIAL OROGRAPHIC PRECIPITATION SIMULATOR (A-Mountain)
Topic: 0.29 Ocean Recovery / 0.30 Mega Flora / 0.31 Infrastructure
Goal: Transform Arid Zones (Australia) via virtual topographical lift.
"""

import numpy as np
import time

def simulate_a_mountain(virtual_height_m, wind_speed_kmh, humidity_percent):
    """
    Simulates the moisture condensation via forced orographic lift.
    
    virtual_height_m: Height of the acoustic pressure wall (m).
    wind_speed_kmh: Incoming ocean wind speed (km/h).
    humidity_percent: Relative humidity of incoming air (%).
    """
    
    # Constants
    lapse_rate = 0.0065  # 6.5C decrease per 1000m
    g = 9.81             # Gravity (m/s^2)
    R_air = 287.05       # Individual gas constant for dry air
    temp_at_sea_level = 30.0 # Standard desert-coast temp (Celsius)
    
    # 1. Adiabatic Cooling Calculation
    target_temp = temp_at_sea_level - (lapse_rate * virtual_height_m)
    delta_t = temp_at_sea_level - target_temp
    
    # 2. Moisture Condensation Logic (Simplified UET-Atmosphere)
    # Using Clausius-Clapeyron approximation (simplified for UET Grid)
    saturation_vapor_pressure_sea = 6.11 * 10**((7.5 * temp_at_sea_level) / (237.3 + temp_at_sea_level))
    actual_vapor_pressure = saturation_vapor_pressure_sea * (humidity_percent / 100.0)
    
    saturation_vapor_pressure_summit = 6.11 * 10**((7.5 * target_temp) / (237.3 + target_temp))
    
    # 3. Precipitation Potential (g of water per kg of air)
    # delta_w is the amount of water air can no longer hold when cooled.
    if actual_vapor_pressure > saturation_vapor_pressure_summit:
        precip_efficiency = 0.42 # UET-Grid dynamic efficiency
        delta_w = (actual_vapor_pressure - saturation_vapor_pressure_summit) * precip_efficiency
    else:
        delta_w = 0.0 # Air did not reach dew point
        
    # 4. Energy Requirement for Acoustic Barrier (Topic 0.31)
    # Force required to move mass of air: F = m * v^2 / h (simplified)
    # A-Mountain is a 1km wide slice for simulation.
    air_density = 1.225 # kg/m^3
    wind_speed_ms = wind_speed_kmh / 3.6
    air_mass_per_sec = air_density * wind_speed_ms * 1000 * virtual_height_m # m=rho*V
    
    # Energy to lift air: P = m*g*h / efficiency
    uet_acoustic_efficiency = 0.88 # Axiom 5 Phase Locking
    power_required_mw = (air_mass_per_sec * g * virtual_height_m) / (uet_acoustic_efficiency * 1e6)
    
    return {
        "Delta T (°C)": -delta_t,
        "Summit Temp (°C)": target_temp,
        "Precipitation (g/m3)": delta_w,
        "Acoustic Power Req (MW)": power_required_mw,
        "Rain Gain Label": "🟢 HIGH" if delta_w > 1.0 else "🟡 MARGINAL" if delta_w > 0.1 else "🔴 DRY"
    }

# --- RUNNING SHOWCASE ---
print("🔊 UET A-MOUNTAIN SIMULATOR (Acoustic Orographic Lift)")
print("Target: Arid Zone Re-greening (Australia Case Study)")
print("-" * 50)

# Scenario: Incoming Ocean wind from the Great Australian Bight
H = 2000.0   # 2km Virtual Height (Topic 0.31 Lattice Anchor)
V = 35.0     # 35 km/h Wind
RH = 75.0    # 75% Coastal Humidity

results = simulate_a_mountain(H, V, RH)

for key, val in results.items():
    if isinstance(val, float):
        print(f"{key:<25}: {val:>10.2f}")
    else:
        print(f"{key:<25}: {val:>10}")

print("-" * 50)
print(f"🚀 STATS: A 2000m barrier converts {results['Precipitation (g/m3)']*1000:.1f} mL of water per m³ of air.")
print(f"☀️ SUSTAINABILITY: Requires {results['Acoustic Power Req (MW)']/25:.1f} Topic 0.37 Solar Paint Hubs.")
print("-" * 50)
