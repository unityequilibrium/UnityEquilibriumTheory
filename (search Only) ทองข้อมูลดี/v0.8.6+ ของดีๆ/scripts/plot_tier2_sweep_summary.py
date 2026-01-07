#!/usr/bin/env python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def main():
    root = Path('runs_tier2_sweep')
    ledger = root / 'ledger.csv'
    if not ledger.exists():
        raise SystemExit(f'Missing ledger: {ledger}')

    df = pd.read_csv(ledger)

    # Extract scale integer from case_id like 'tier2_sweep_s-2_seed0'
    df['scale'] = df['case_id'].str.extract(r'tier2_sweep_s(-?\d+)_seed\d+').astype(int)

    grouped = df.groupby('scale').agg({
        'Omega0': ['mean', 'std'],
        'OmegaT': ['mean', 'std']
    }).reset_index()
    # flatten columns
    grouped.columns = ['scale', 'Omega0_mean', 'Omega0_std', 'OmegaT_mean', 'OmegaT_std']

    out_csv = root / 'tier2_sweep_summary.csv'
    grouped.to_csv(out_csv, index=False)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].errorbar(grouped['scale'], grouped['Omega0_mean'], yerr=grouped['Omega0_std'],
                     fmt='o-', capsize=5)
    axes[0].set_xlabel('scale (s)')
    axes[0].set_ylabel('Omega0')
    axes[0].set_title('Omega0 mean ± std by scale')
    axes[0].grid(True, alpha=0.3)

    axes[1].errorbar(grouped['scale'], grouped['OmegaT_mean'], yerr=grouped['OmegaT_std'],
                     fmt='o-', capsize=5)
    axes[1].set_xlabel('scale (s)')
    axes[1].set_ylabel('OmegaT')
    axes[1].set_title('OmegaT mean ± std by scale')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    out_png = root / 'tier2_sweep_summary.png'
    fig.savefig(out_png, dpi=160)
    print('Wrote:', out_csv)
    print('Wrote:', out_png)


if __name__ == '__main__':
    main()
