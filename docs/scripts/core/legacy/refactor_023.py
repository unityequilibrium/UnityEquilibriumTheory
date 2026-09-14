import shutil
import os

BASE = r"C:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics\0.23_Condensed_Matter"

# Move Code
src_solver = os.path.join(BASE, "Code", "baseline", "superfluid_solver.py")
src_run = os.path.join(BASE, "Code", "baseline", "run_superfluid_experiment.py")

dst_dir = os.path.join(BASE, "Code", "section 1", "code")

if os.path.exists(src_solver):
    shutil.move(src_solver, os.path.join(dst_dir, "superfluid_solver.py"))
    print("Moved solver.")

if os.path.exists(src_run):
    shutil.move(src_run, os.path.join(dst_dir, "run_superfluid_experiment.py"))
    print("Moved runner.")

# Remove legacy/baseline folders if empty
try:
    shutil.rmtree(os.path.join(BASE, "Code", "baseline"))
    shutil.rmtree(os.path.join(BASE, "Code", "legacy"))
    print("Cleaned up old folders.")
except:
    pass
