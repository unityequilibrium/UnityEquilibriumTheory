import os

base = r"C:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics\0.20_Atomic_Physics"

print(f"Scanning {base}...")
found = False
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith(".py"):
            print(f"FOUND: {os.path.join(root, f)}")
            found = True

if not found:
    print("CRITICAL: No python files found in Topic 0.20!")
