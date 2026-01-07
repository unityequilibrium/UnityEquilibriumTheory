# scripts/plot_symmetry.py
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

    g = df.groupby(["s"])["OmegaT"].agg(["mean","std","count"]).reset_index().sort_values("s")

    plt.figure()
    plt.errorbar(g["s"], g["mean"], yerr=g["std"], fmt="o-")
    plt.title("Toy: OmegaT vs s (signed) with seed std")
    plt.xlabel("s (signed tilt)")
    plt.ylabel("OmegaT (mean)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
