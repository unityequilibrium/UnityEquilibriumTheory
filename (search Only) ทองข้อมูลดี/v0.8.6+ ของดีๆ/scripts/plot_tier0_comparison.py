#!/usr/bin/env python
import pandas as pd
import matplotlib.pyplot as plt

# Read the ledger
df = pd.read_csv('runs_tier0/ledger.csv')

# Extract model and relevant columns
models = df['model']
omega0 = df['Omega0']
omegat = df['OmegaT']

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot Omega0
ax1.bar(models, omega0, color=['skyblue', 'lightcoral'])
ax1.set_ylabel('Omega0')
ax1.set_title('Omega0 Comparison')
ax1.grid(True, alpha=0.3)

# Plot OmegaT
ax2.bar(models, omegat, color=['skyblue', 'lightcoral'])
ax2.set_ylabel('OmegaT')
ax2.set_title('OmegaT Comparison')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('runs_tier0/tier0_comparison.png', dpi=160, bbox_inches='tight')
plt.show()