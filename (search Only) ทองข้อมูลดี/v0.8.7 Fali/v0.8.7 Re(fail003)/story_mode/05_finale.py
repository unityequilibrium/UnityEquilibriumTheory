import subprocess
import os
import sys
import time

# --- CONFIG ---
STORY_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\story_mode"
SCRIPTS = ["01_the_origin.py", "02_the_realization.py", "03_the_expansion.py", "04_the_bridge.py"]


def run_script(script_name):
    script_path = os.path.join(STORY_DIR, script_name)
    print(f"\n🚀 Launching {script_name}...\n")
    time.sleep(1)  # Dramatic pause
    subprocess.run([sys.executable, script_path], check=False)
    time.sleep(1)


def main():
    print(
        r"""
    #######################################################
             UNITY EQUILIBRIUM THEORY (UET)
                 STORY MODE: THE FINALE 🎼
    #######################################################
    
    "A journey from the edge of the universe to the
     depths of the human mind."
     
    Initiating Sequence...
    """
    )

    for script in SCRIPTS:
        run_script(script)

    print(
        r"""
    #######################################################
                 🎬 THE END (OR BEGINNING?)
    #######################################################
     
     The evidence is conclusive.
     Gravity (k=1)
     Money (k=1)
     Society (k~1.7)
     Quantum (k=2)
     Mind (beta~2)
     
     Everything flows. Everything scales.
     Unity Equilibrium is the map of that flow.
     
     CONGRATULATIONS.
    #######################################################
    """
    )


if __name__ == "__main__":
    main()
