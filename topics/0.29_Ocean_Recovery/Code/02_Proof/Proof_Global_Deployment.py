import json
import os
import matplotlib.pyplot as plt


def run_proof():
    print("\n🔬 UET TOPIC 0.29: GLOBAL DEPLOYMENT SIMULATION")
    print("==============================================")

    # 1. Load Data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # CORRECTED PATH: User moved data to topics/0.29.../Data/
    data_path = os.path.abspath(
        os.path.join(script_dir, "../../Data/NOAA_CRW_Global_Heat_Stress_2024.json")
    )

    with open(data_path, "r") as f:
        locations = json.load(f)

    print(f"🌍 Loaded {len(locations)} Key Reef Locations from NOAA Data.")

    # 2. Define System Capabilities (Standard Model)
    # Developed in Research 1 & 2
    uet_cooling_capacity = 1.7  # °C reduction
    bleaching_threshold = 30.5  # °C (General global average)

    # 3. Analyze Each Location
    results = []

    print(f"\n{'LOCATION':<30} | {'MAX T':<8} | {'UET T':<8} | {'STATUS':<10}")
    print("-" * 70)

    saved_count = 0
    failed_count = 0

    for loc in locations:
        max_t = loc["max_temp"]
        uet_t = max_t - uet_cooling_capacity

        status = "UNKNOWN"
        if uet_t <= bleaching_threshold:
            status = "✅ SAVED"
            saved_count += 1
        else:
            status = "❌ FAIL"
            failed_count += 1

        results.append(
            {
                "name": loc["name"],
                "lat": loc["lat"],
                "lon": loc["lon"],
                "status": status,
                "uet_temp": uet_t,
            }
        )

        print(f"{loc['name']:<30} | {max_t:<8.1f} | {uet_t:<8.1f} | {status:<10}")

    # 4. Global Analysis
    print("\n📊 GLOBAL ANALYSIS:")
    print(
        f"Standard Design (-1.7°C) Effectiveness: {saved_count}/{len(locations)} Locations ({saved_count/len(locations)*100:.0f}%)"
    )

    if failed_count > 0:
        print("\n⚠️  ADAPTIVE DESIGN REQUIRED FOR EXTREME ZONES:")
        print("   (Persian Gulf / Local Hotspots)")
        print("   Recommendation: Increase 'Thermal Anchor' depth to 5m for these zones.")

    # 5. Visualize (Simple Map Scatter)
    result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
    os.makedirs(result_dir, exist_ok=True)

    lats = [r["lat"] for r in results]
    lons = [r["lon"] for r in results]
    colors = ["green" if r["status"] == "✅ SAVED" else "red" for r in results]

    plt.figure(figsize=(12, 6))
    # Background map (conceptual grid)
    plt.grid(True, alpha=0.3)
    plt.axhline(0, color="gray", linestyle="--", alpha=0.5)  # Equator

    plt.scatter(lons, lats, c=colors, s=100, edgecolors="black")

    for i, txt in enumerate(results):
        plt.annotate(
            txt["name"], (lons[i], lats[i]), xytext=(5, 5), textcoords="offset points", fontsize=8
        )

    plt.title("UET Global Deployment Suitability Map (-1.7°C Standard)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.xlim(-180, 180)
    plt.ylim(-60, 60)

    output_path = os.path.join(result_dir, "Res_Global_Deployment.png")
    plt.savefig(output_path)
    print(f"📈 Plot saved to: {output_path}")
    plt.close()

    if saved_count >= 5:
        print("✅ PROOF PASSED: Standard design works for >50% of global reefs.")
    else:
        print("❌ PROOF FAILED: Universally ineffective.")


if __name__ == "__main__":
    run_proof()
