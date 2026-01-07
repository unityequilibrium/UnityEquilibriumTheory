# scripts/ue_loglines.py
from __future__ import annotations
import argparse, csv, math, re
from pathlib import Path
import numpy as np
import pandas as pd

# ---------- utils ----------
def split_top_level(s: str, sep: str = ",") -> list[str]:
    out, buf, depth = [], [], 0
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            tok = "".join(buf).strip()
            if tok:
                out.append(tok)
            buf = []
        else:
            buf.append(ch)
    tok = "".join(buf).strip()
    if tok:
        out.append(tok)
    return out

def try_float(x: str):
    try:
        return float(x)
    except Exception:
        return None

_quartic_re = re.compile(r"^quartic\((.*)\)$", re.IGNORECASE)

def parse_quartic(v: str) -> dict[str, float]:
    m = _quartic_re.match(v.strip())
    if not m:
        return {}
    inner = m.group(1)
    parts = split_top_level(inner, ",")
    d = {}
    for p in parts:
        if "=" not in p:
            continue
        k, val = p.split("=", 1)
        fv = try_float(val.strip())
        if fv is not None:
            d[k.strip()] = fv
    return d

def parse_params(params_str: str) -> dict[str, float]:
    feats = {}
    if not isinstance(params_str, str) or not params_str.strip():
        return feats
    tokens = split_top_level(params_str.strip(), ",")
    for t in tokens:
        if "=" not in t:
            continue
        k, v = t.split("=", 1)
        k, v = k.strip(), v.strip()
        fv = try_float(v)
        if fv is not None:
            feats[k] = fv
            continue
        if k in ("V","VC","VI"):
            q = parse_quartic(v)
            for qk, qv in q.items():
                feats[f"{k}_{qk}"] = qv

    # unify single-field to VC/VI
    if "V_a" in feats and "VC_a" not in feats:
        feats["VC_a"] = feats["V_a"]; feats["VC_delta"] = feats.get("V_delta", np.nan); feats["VC_s"] = feats.get("V_s", 0.0)
        feats["VI_a"] = feats["V_a"]; feats["VI_delta"] = feats.get("V_delta", np.nan); feats["VI_s"] = feats.get("V_s", 0.0)

    # derived
    if "kC" in feats and "kI" in feats and feats["kI"] != 0:
        feats["k_ratio"] = feats["kC"]/feats["kI"]
    if "MC" in feats and "MI" in feats and feats["MI"] != 0:
        feats["M_ratio"] = feats["MC"]/feats["MI"]
    if "VC_delta" in feats and "VI_delta" in feats:
        feats["delta_asym"] = feats["VC_delta"] - feats["VI_delta"]
        feats["delta_sum"]  = feats["VC_delta"] + feats["VI_delta"]
    if "VC_s" in feats and "VI_s" in feats:
        feats["s_asym"] = feats["VC_s"] - feats["VI_s"]
        feats["s_sum"]  = feats["VC_s"] + feats["VI_s"]
        feats["s_abs_max"] = max(abs(feats["VC_s"]), abs(feats["VI_s"]))
    return feats

def load_matrix_features(paths: list[Path]) -> pd.DataFrame:
    rows = []
    for mp in paths:
        with mp.open("r", encoding="utf-8", newline="") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                case_id = (r.get("case_id") or "").strip()
                if not case_id:
                    continue
                base = {
                    "case_id": case_id,
                    "integrator": (r.get("integrator") or "").strip(),
                    "grid_cfg": try_float((r.get("grid") or "").strip()) or np.nan,
                    "dt_cfg":   try_float((r.get("dt") or "").strip()) or np.nan,
                    "T_cfg":    try_float((r.get("T") or "").strip()) or np.nan,
                }
                base.update(parse_params(r.get("params") or ""))
                rows.append(base)
    df = pd.DataFrame(rows).drop_duplicates("case_id", keep="first")
    return df

def load_validation(runs_dir: Path) -> pd.DataFrame:
    # pick the best available validation file
    for name in ["validation_stress.csv","validation_tilt_ledger.csv","validation_tilt.csv","validation.csv"]:
        p = runs_dir/name
        if p.exists():
            return pd.read_csv(p)
    # fallback: ledger only
    led = pd.read_csv(runs_dir/"ledger.csv")
    out = led[["run_id","case_id","status"]].copy()
    out["grade"] = np.where(out["status"]=="PASS","PASS","FAIL")
    out["reasons"] = ""
    return out

def train_test_split_idx(n, test_size, seed):
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    n_test = int(round(n*test_size))
    test = idx[:n_test]
    train = idx[n_test:]
    return train, test

# ----- minimal ML (no sklearn) -----
def standardize(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    return (X-mu)/sd, mu, sd

def sigmoid(z): return 1/(1+np.exp(-z))

def fit_logreg(X, y, steps=5000, lr=0.05, l2=1e-2):
    # simple GD logistic regression
    w = np.zeros(X.shape[1])
    b = 0.0
    for _ in range(steps):
        p = sigmoid(X@w + b)
        grad_w = (X.T@(p-y))/len(y) + l2*w
        grad_b = float((p-y).mean())
        w -= lr*grad_w
        b -= lr*grad_b
    return w, b

def fit_ridge(X, y, l2=1e-2):
    # closed-form ridge
    XtX = X.T@X
    A = XtX + l2*np.eye(X.shape[1])
    w = np.linalg.solve(A, X.T@y)
    b = float(y.mean() - X.mean(axis=0)@w)
    return w, b

def auc_score(y, p):
    # AUC without sklearn (rank-based)
    y = y.astype(int)
    if len(np.unique(y)) < 2: return float("nan")
    order = np.argsort(p)
    y_sorted = y[order]
    n1 = y_sorted.sum()
    n0 = len(y_sorted) - n1
    ranks = np.arange(1, len(y_sorted)+1)
    s1 = ranks[y_sorted==1].sum()
    return float((s1 - n1*(n1+1)/2) / (n0*n1))

def f1_score(y, yhat):
    y = y.astype(int); yhat = yhat.astype(int)
    tp = ((y==1)&(yhat==1)).sum()
    fp = ((y==0)&(yhat==1)).sum()
    fn = ((y==1)&(yhat==0)).sum()
    if tp==0: return 0.0
    prec = tp/(tp+fp) if (tp+fp)>0 else 0.0
    rec  = tp/(tp+fn) if (tp+fn)>0 else 0.0
    return 2*prec*rec/(prec+rec) if (prec+rec)>0 else 0.0

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--matrices", nargs="+", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--out_csv", default="runs_ml/ue_dataset.csv")
    args = ap.parse_args()

    runs = [Path(r) for r in args.runs]
    mats = [Path(m) for m in args.matrices]

    feat = load_matrix_features(mats)
    val = pd.concat([load_validation(r) for r in runs], ignore_index=True)

    df = val.merge(feat, on="case_id", how="left")
    df["y_pass"] = (df["grade"]=="PASS").astype(int)

    # choose numeric features
    drop = {"run_id","case_id","model","status","grade","reasons"}
    num_cols = [c for c in df.columns if c not in drop and pd.api.types.is_numeric_dtype(df[c])]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        med = float(np.nanmedian(df[c].to_numpy())) if np.isfinite(np.nanmedian(df[c].to_numpy())) else 0.0
        df[c] = df[c].fillna(med)

    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_csv, index=False)

    X = df[num_cols].to_numpy(dtype=float)
    y = df["y_pass"].to_numpy(dtype=int)
    yreg = pd.to_numeric(df["OmegaT"], errors="coerce").fillna(0.0).to_numpy(dtype=float)

    tr, te = train_test_split_idx(len(df), args.test_size, args.seed)
    Xtr, Xte = X[tr], X[te]
    ytr, yte = y[tr], y[te]
    rtr, rte = yreg[tr], yreg[te]

    Xtr_s, mu, sd = standardize(Xtr)
    Xte_s = (Xte - mu)/sd

    # ----- classifier logline -----
    if len(np.unique(y)) < 2:
        print(f"[UET-ML][clf] single-class label (all grade=PASS). skip classifier. rows={len(df)}")
    else:
        w,b = fit_logreg(Xtr_s, ytr, steps=6000, lr=0.05, l2=1e-2)
        p = sigmoid(Xte_s@w + b)
        yhat = (p>=0.5).astype(int)
        acc = float((yhat==yte).mean())
        f1 = float(f1_score(yte, yhat))
        auc = float(auc_score(yte, p))
        print(f"[UET-ML][clf] split seed={args.seed} train={len(tr)} test={len(te)} | acc={acc:.4f} f1={f1:.4f} auc={auc:.4f}")
        top = np.argsort(np.abs(w))[::-1][:10]
        print("[UET-ML][clf] top_features:", ", ".join([f"{num_cols[i]}={w[i]:+.3f}" for i in top]))

    # ----- regression logline -----
    w,b = fit_ridge(Xtr_s, rtr, l2=1e-2)
    pred = Xte_s@w + b
    rmse = float(math.sqrt(((pred-rte)**2).mean()))
    # R2
    denom = float(((rte-rte.mean())**2).sum())
    r2 = 1.0 - float(((pred-rte)**2).sum())/denom if denom>0 else float("nan")
    print(f"[UET-ML][reg] split seed={args.seed} train={len(tr)} test={len(te)} | RMSE(OmegaT)={rmse:.6g} R2={r2:.4f}")
    top = np.argsort(np.abs(w))[::-1][:10]
    print("[UET-ML][reg] top_features:", ", ".join([f"{num_cols[i]}={w[i]:+.3f}" for i in top]))

    print(f"[UET-ML] wrote dataset: {args.out_csv} rows={len(df)} features={len(num_cols)}")

if __name__ == "__main__":
    main()
