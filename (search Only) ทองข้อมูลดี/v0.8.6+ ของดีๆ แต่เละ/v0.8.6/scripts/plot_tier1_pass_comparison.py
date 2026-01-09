#!/usr/bin/env python
import pandas as pd
import matplotlib.pyplot as plt


def main():
    df = pd.read_csv('runs_tier1_pass/ledger_tier1.csv')

    # Short labels: model + seed
    df['label'] = df['case_id'] + '\n' + df['variant']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    colors = df['model'].map({'C_only': 'tab:blue', 'C_I': 'tab:orange'})

    # Omega0
    ax1.bar(df['label'], df['Omega0'], color=colors)
    ax1.set_title('Omega0 (tier1_pass)')
    ax1.set_ylabel('Omega0')
    ax1.set_xticklabels(df['label'], rotation=45, ha='right')
    ax1.grid(alpha=0.3)

    # OmegaT (use symlog to handle small values)
    ax2.bar(df['label'], df['OmegaT'], color=colors)
    ax2.set_title('OmegaT (tier1_pass)')
    ax2.set_ylabel('OmegaT')
    ax2.set_yscale('symlog')
    ax2.set_xticklabels(df['label'], rotation=45, ha='right')
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    out = 'runs_tier1_pass/tier1_pass_comparison.png'
    fig.savefig(out, dpi=160, bbox_inches='tight')
    print('Wrote', out)


if __name__ == '__main__':
    main()
