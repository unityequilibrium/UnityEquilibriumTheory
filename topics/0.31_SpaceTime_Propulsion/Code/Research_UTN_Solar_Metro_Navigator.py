import math
import time
from datetime import datetime, timedelta

class UTNMeteorNavigator:
    """
    Universal Transit Network (UTN) Metro Navigator.
    Calculates Interplanetary 'Subway' Schedules.
    """
    def __init__(self):
        # Semi-major axes in AU (Sun is the center at 0.0)
        self.planets = {
            "Sun": 0.0,
            "Mercury": 0.39, "Venus": 0.72, "Earth": 1.0, 
            "Mars": 1.52, "Jupiter": 5.2, "Saturn": 9.54, 
            "Uranus": 19.2, "Neptune": 30.06
        }
        # Average orbital speeds (km/s)
        self.v_orbit = {
            "Earth": 29.78, "Mars": 24.07, "Jupiter": 13.07, "Neptune": 5.43
        }
        self.c_m_per_s = 299792458
        self.u_s_propulsion_kick = 5.0  # 500% Kick factor from Polar Slingshot

    def calculate_transfer_window(self, origin, destination):
        """Calculates travel time using UET Slingshot vs Traditional."""
        dist_au = abs(self.planets[destination] - self.planets[origin])
        dist_km = dist_au * 149.6e6
        dist_ly = dist_au / 63241.077 # AU to Light-Year conversion
        
        # Traditional Hohmann Transfer velocity (Rough Avg ~15 km/s)
        # v_trad in ly/day for comparison
        v_trad_km_s = 15.0 
        time_trad_days = (dist_km / (v_trad_km_s * 3600 * 24))
        
        # UET High-Vertical Slingshot (Start v_trad * kick)
        v_uet_km_s = v_trad_km_s * self.u_s_propulsion_kick
        time_uet_days = (dist_km / (v_uet_km_s * 3600 * 24))
        
        return {
            "Distance (AU)": dist_au,
            "Distance (ly)": dist_ly,
            "Traditional Transit (Days)": round(time_trad_days, 1),
            "UET High-Vertical (Days)": round(time_uet_days, 1),
            "Efficiency Gain (%)": (time_trad_days / time_uet_days) * 100
        }

    def run_live_status(self):
        print("\n🚉 UTN SOLAR METRO: DEEP SPACE NAVIGATION (ly-Scale)")
        print(f"Current System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 85)
        
        routes = [("Earth", "Mars"), ("Earth", "Jupiter"), ("Earth", "Neptune"), ("Sun", "Alpha Centauri")]
        # Add Interstellar target for scale
        self.planets["Alpha Centauri"] = 276183.0 # ~4.37 ly in AU
        
        print(f"{'Route':<20} | {'Dist (AU)':<10} | {'Dist (ly)':<15} | {'UET Travel (Days)':<15}")
        print("-" * 85)
        for origin, dest in routes:
            res = self.calculate_transfer_window(origin, dest)
            ly_str = f"{res['Distance (ly)']:,.6f}"
            print(f"{origin} -> {dest:<10} | {res['Distance (AU)']:<10} | {ly_str:<15} | {res['UET High-Vertical (Days)']:<15} 🟢")

        print("-" * 85)
        print("💡 STATUS: All High-Vertical Expressways are CLEAR.")
        print("🚦 TRAFFIC: Vertical Layers +1 (Outbound) and -1 (Inbound) sync'd.")
        print("🔋 ENERGY: Solar Paint (0.37) efficiency at 48.0%. Beam Ready.")

if __name__ == "__main__":
    nav = UTNMeteorNavigator()
    nav.run_live_status()
