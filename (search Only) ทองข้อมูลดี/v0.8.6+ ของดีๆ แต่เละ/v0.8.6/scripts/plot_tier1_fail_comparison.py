#!/usr/bin/env python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the ledger
df = pd.read_csv('runs_tier1_fail/ledger.csv')

# Extract case names and relevant columns
cases = [cid.split('_', 2)[-1] for cid in df['case_id']]  # Extract the failure type
omega0 = df['Omega0']
omegat = df['OmegaT']
status = df['status']

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Colors based on status
colors = ['red' if s == 'FAIL' else 'green' for s in status]

# Plot Omega0
bars1 = ax1.bar(cases, omega0, color=colors, alpha=0.7)
ax1.set_ylabel('Omega0')
ax1.set_title('Omega0 Comparison (Tier1 Fail Cases)')
ax1.grid(True, alpha=0.3)
ax1.set_yscale('symlog')  # Use symlog for large range

# Add status labels
for bar, stat in zip(bars1, status):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + (height*0.1 if height > 0 else height*0.9),
             f'{stat}', ha='center', va='bottom' if height > 0 else 'top', fontweight='bold')

# Plot OmegaT
bars2 = ax2.bar(cases, omegat, color=colors, alpha=0.7)
ax2.set_ylabel('OmegaT')
ax2.set_title('OmegaT Comparison (Tier1 Fail Cases)')
ax2.grid(True, alpha=0.3)
ax2.set_yscale('symlog')  # Use symlog for extreme values

# Add status labels
for bar, stat in zip(bars2, status):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + (height*0.1 if height > 0 else height*0.9),
             f'{stat}', ha='center', va='bottom' if height > 0 else 'top', fontweight='bold')

plt.tight_layout()
plt.savefig('runs_tier1_fail/tier1_fail_comparison.png', dpi=160, bbox_inches='tight')
plt.show()