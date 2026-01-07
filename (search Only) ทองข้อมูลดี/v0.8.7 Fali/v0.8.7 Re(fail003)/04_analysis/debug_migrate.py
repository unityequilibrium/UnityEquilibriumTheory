import os
import shutil
import glob

# BRUTE FORCE SEARCH & MIGRATE
base = os.getcwd()  # c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7
print(f"Base: {base}")

# Target V3
target_dir = os.path.join(base, "research_v3", "01_data", "real_legacy", "markets")
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# Walk EVERYTHING in 'research' to find CSVs
search_root = os.path.join(base, "research")
print(f"Walking: {search_root}")

found = 0
for root, dirs, files in os.walk(search_root):
    for file in files:
        if file.lower().endswith(".csv"):
            full_path = os.path.join(root, file)
            # Filter for market data only
            if "market_data" in full_path or "AAPL" in file or "SP500" in file:
                print(f"Found: {file}")
                try:
                    shutil.copy(full_path, target_dir)
                    found += 1
                except Exception as e:
                    print(f"Error copying {file}: {e}")

print(f"✅ Migrated {found} market files to V3.")
