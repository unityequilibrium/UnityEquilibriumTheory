import random
import math


class StandardCVDCompetitor:
    def simulate_random_nucleation(self, area_nm2):
        """
        Simulates standard CVD graphene growth (Random Thermal).
        Result: Polycrystalline structure with grain boundaries.
        """
        nucleation_sites = int(area_nm2 * 0.1)
        grains = []
        for _ in range(nucleation_sites):
            # Random orientation (0-60 degrees)
            angle = random.uniform(0, 60.0)
            grains.append(angle)

        # Defect Calculation (Mismatch at boundaries)
        defects = 0
        for i in range(len(grains) - 1):
            mismatch = abs(grains[i] - grains[i + 1])
            if mismatch > 5.0:  # If misaligned by > 5 deg
                defects += 1

        defect_density = (defects / area_nm2) * 100
        return defect_density, "POLYCRYSTALLINE"


def run_competitor():
    print("🥊 COMPETITOR ANALYSIS: STANDARD CVD")
    print("====================================")

    comp = StandardCVDCompetitor()
    density, structure = comp.simulate_random_nucleation(1000)

    print(f"Structure Type: {structure}")
    print(f"Grain Boundary Defects: {density:.2f} per nm^2")
    print("Conclusion: High entropy process results in resistive boundaries.")

    # SAVE RESULT
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    topic_root = os.path.dirname(os.path.dirname(script_dir))
    result_dir = os.path.join(topic_root, "Result", "04_Competitor")
    os.makedirs(result_dir, exist_ok=True)

    with open(os.path.join(result_dir, "Res_Defect_Analysis.txt"), "w", encoding="utf-8") as f:
        f.write("Standard CVD Defect Simulation\n")
        f.write("==============================\n")
        f.write(f"Structure Type: {structure}\n")
        f.write(f"Defect Density: {density:.2f} defects/nm^2\n")
        f.write(
            "Observation: Random thermal nucleation creates high-resistance grain boundaries.\n"
        )

    print(f"📝 Result saved to Result/04_Competitor/Res_Defect_Analysis.txt")


if __name__ == "__main__":
    run_competitor()
