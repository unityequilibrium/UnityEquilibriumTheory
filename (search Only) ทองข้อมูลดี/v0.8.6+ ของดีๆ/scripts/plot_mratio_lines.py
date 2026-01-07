# scripts/plot_mratio_lines.py
import re, argparse
import pandas as pd
import matplotlib.pyplot as plt

rx = re.compile(r"toy_cm_Mr(?P<Mr>[-\d\.]+)_s(?P<s>[-\+\d\.]+)_seed(?P<seed>\d+)")
def parse(row):
    m = rx.search(str(row))
    if not m: return None
    return float(m["Mr"]), float(m["s"]), int(m["seed"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="runs_toy_coffee_milk/ledger.csv")
    args = ap.parse_args()

    df = pd.read_csv(args.ledger)
    parsed = df["case_id"].apply(parse)
    df = df[parsed.notna()].copy()
    df[["Mr","s","seed"]] = pd.DataFrame(parsed.dropna().tolist(), index=df.index)
    df["abs_s"] = df["s"].abs()

    plt.figure()
    for Mr, sub in df.groupby("Mr"):
        g = sub.groupby("abs_s")["OmegaT"].mean().reset_index().sort_values("abs_s")
        plt.plot(g["abs_s"], g["OmegaT"], marker="o", label=f"Mr={Mr:g}")
    plt.title("Toy: OmegaT vs |s| (separate lines by M_ratio)")
    plt.xlabel("|s|")
    plt.ylabel("OmegaT (mean)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
