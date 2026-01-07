# scripts/train_test_logline.py
import re, argparse
import numpy as np
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="runs_toy_coffee_milk/ledger.csv")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--test_size", type=float, default=0.25)
    args = ap.parse_args()

    rx = re.compile(r"toy_cm_Mr(?P<Mr>[-\d\.]+)_s(?P<s>[-\+\d\.]+)_seed(?P<seed>\d+)")
    df = pd.read_csv(args.ledger)

    rows = []
    for _, r in df.iterrows():
        m = rx.search(str(r["case_id"]))
        if not m: 
            continue
        Mr = float(m["Mr"]); s = float(m["s"])
        rows.append((Mr, s, abs(s), float(r["OmegaT"])))
    data = pd.DataFrame(rows, columns=["Mr","s","abs_s","OmegaT"]).dropna()

    # features: abs_s, Mr, interaction
    X = np.c_[data["abs_s"].values, data["Mr"].values, (data["abs_s"]*data["Mr"]).values, np.ones(len(data))]
    y = data["OmegaT"].values

    # train/test split (manual)
    rng = np.random.default_rng(args.seed)
    idx = np.arange(len(y))
    rng.shuffle(idx)
    n_test = int(len(y)*args.test_size)
    te, tr = idx[:n_test], idx[n_test:]

    Xtr, ytr = X[tr], y[tr]
    Xte, yte = X[te], y[te]

    # linear least squares
    w, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
    pred = Xte @ w

    # metrics
    mae = np.mean(np.abs(pred - yte))
    ss_res = np.sum((yte - pred)**2)
    ss_tot = np.sum((yte - np.mean(yte))**2) + 1e-12
    r2 = 1 - ss_res/ss_tot

    print("Model: OmegaT ~ a*|s| + b*Mr + c*(|s|*Mr) + d")
    print(f"Coeffs: a={w[0]:.6g}, b={w[1]:.6g}, c={w[2]:.6g}, d={w[3]:.6g}")
    print(f"Test MAE = {mae:.6g}")
    print(f"Test R^2 = {r2:.6g}")

if __name__ == "__main__":
    main()
