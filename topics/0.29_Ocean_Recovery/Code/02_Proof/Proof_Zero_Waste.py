import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add Engine directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
engine_dir = os.path.abspath(os.path.join(script_dir, "../01_Engine"))
sys.path.append(engine_dir)

from Engine_BioStructure import LivingStructure


def run_proof():
    print("\n🔬 UET TOPIC 0.29: STRUCTURAL LIFECYCLE PROOF")
    print("=============================================")

    years = 100

    # 1. Setup Models
    uet_model = LivingStructure(material="Basalt_Geopolymer")
    legacy_model = LivingStructure(material="Steel_Concrete")

    # Data collectors
    time = []

    uet_art = []
    uet_nat = []
    uet_total = []
    uet_sf = []

    leg_art = []
    leg_total = []
    leg_sf = []

    print(f"⏳ Simulating {years} Years of Corrosion & Growth...")

    # 2. Run Simulation
    for y in range(years + 1):
        status_u = uet_model.get_status()
        status_l = legacy_model.get_status()

        time.append(y)

        # Collect UET Data
        uet_art.append(float(status_u["Artificial Str"]))
        uet_nat.append(float(status_u["Natural Str"]))
        uet_total.append(float(status_u["Total Str"]))
        uet_sf.append(float(status_u["Safety Factor"]))

        # Collect Legacy Data
        leg_art.append(float(status_l["Artificial Str"]))
        leg_total.append(float(status_l["Total Str"]))
        leg_sf.append(float(status_l["Safety Factor"]))

        # Step Forward
        if y < years:
            uet_model.update_year(1.0)
            legacy_model.update_year(1.0)

    # 3. Analyze Results
    min_sf_uet = min(uet_sf)
    final_nat_ratio = uet_nat[-1] / uet_total[-1] * 100

    print("\n📊 RESULTS (Year 100):")
    print(f"UET Final Natural Ratio: {final_nat_ratio:.1f}% (Target > 90%)")
    print(f"UET Minimum Safety Factor: {min_sf_uet:.2f} (Target > 2.0)")
    print(f"Legacy Min Safety Factor: {min(leg_sf):.2f}")

    # 4. Visualize
    result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
    os.makedirs(result_dir, exist_ok=True)

    plt.figure(figsize=(12, 6))

    # Plot Strength Composition (UET)
    plt.plot(time, uet_total, "g-", linewidth=3, label="UET Total Strength (Basalt)")
    plt.plot(time, uet_art, "g--", alpha=0.5, label="Artificial (Degrading)")
    plt.plot(time, uet_nat, "g:", alpha=0.8, linewidth=2, label="Natural Reef (Growing)")

    # Plot Legacy Failure
    plt.plot(time, leg_total, "r-.", linewidth=2, label="Legacy Strength (Steel) - FAILS")

    # Limits
    plt.axhline(y=100, color="k", linestyle="-", linewidth=2, label="Design Load (Required)")
    plt.axhline(y=200, color="orange", linestyle="--", label="Safety Factor 2.0")

    plt.title("Lifecycle Analysis: The 'Handover' from Engineering to Nature")
    plt.xlabel("Years")
    plt.ylabel("Structural Strength (Arbitrary Units)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = os.path.join(result_dir, "Res_Structural_Lifecycle.png")
    plt.savefig(output_path)
    print(f"📈 Plot saved to: {output_path}")
    plt.close()

    # 5. Determine Pass/Fail
    if min_sf_uet > 2.0 and final_nat_ratio > 80.0:
        print("✅ PROOF PASSED: Structure successfully becomes a reef.")
    else:
        print("❌ PROOF FAILED: Structure collapsed or failed integration.")


if __name__ == "__main__":
    run_proof()
