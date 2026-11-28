"""Benchmark (sandbox, no claim): the published Chow and Hall (2008) two-compartment model on the Benedict (1915) fasts.

Model (Chow and Hall, PLoS Comput. Biol. 4, e1000045, PMC2266991), total fast I = 0, parameters as published:
    rho_F dF/dt = -(1 - p) E,   rho_L dL/dt = -p E,   p = 10.4 / (10.4 + F)   (Forbes),
    E = 0.14 L + 0.05 F + 1.55 MJ/day,   rho_F = 39.5 MJ/kg,   rho_L = 7.6 MJ/kg.
Nothing is fitted. Each fast starts at its observed day-6 weight (glycogen and water days excluded, as in T030/T036)
with an assumed fat fraction of 10, 15 or 20 percent (Benedict gives no body composition). The data were seen before;
this measures how well the mainstream reduced model describes them, it tests nothing in UET.
Result (2026-11-25): the model loses about twice the observed kg/day and its specific loss rate rises (r about 1.07)
where the data's falls (median r 0.89); see LITERATURE_MAP_FASTING.md section 5.
"""

import csv, sys, numpy as np
from collections import defaultdict
from scipy.integrate import solve_ivp
from pathlib import Path
R=str(Path(__file__).resolve().parents[3]).replace("\\","/")+"/"
RHO_F, RHO_L = 39.5, 7.6

def run(M0, f, days):
    def rhs(t, y):
        F, L = y; p = 10.4/(10.4+F); E = 0.14*L + 0.05*F + 1.55
        return [-(1-p)*E/RHO_F, -p*E/RHO_L]
    s = solve_ivp(rhs, (0, days[-1]-days[0]), [f*M0, (1-f)*M0], t_eval=np.array(days)-days[0], rtol=1e-10, atol=1e-10)
    return s.y[0]+s.y[1]

def wr(pts):
    (t0,m0),(t1,m1)=pts[0],pts[-1]; mm=np.mean([m for _,m in pts]); return (m0-m1)/((t1-t0)*mm), mm

def metrics(days, M):
    pts=list(zip(days,M)); tm=0.5*(days[0]+days[-1])
    e=[p for p in pts if p[0]<=tm]; l=[p for p in pts if p[0]>=tm]
    ke,me=wr(e); kl,ml=wr(l)
    return {"rate_kg_day": (M[0]-M[-1])/(days[-1]-days[0]), "r": kl/ke}

series=defaultdict(list)
for r in csv.DictReader(l for l in open(R+"docs/data/external/biology/fasting/benedict1915_other_fasts.csv",encoding="utf-8").read().splitlines() if l and not l.startswith("#")):
    series[r["fast"]].append((float(r["day"]),float(r["mass_kg"])))
series["L. 1912"]=[(float(r["day"]),float(r["mass_kg"])) for r in csv.DictReader(l for l in open(R+"docs/data/external/biology/fasting/benedict1915_L_body_weight.csv",encoding="utf-8").read().splitlines() if l and not l.startswith("#"))]
print(f"{'fast':22s} {'obs kg/d':>8s} " + " ".join(f"{'f='+str(f):>15s}" for f in (0.10,0.15,0.20)) + f" {'obs r':>6s} {'model r (f=.15)':>15s}")
rows=[]
for name in sorted(series):
    pts=sorted(p for p in series[name] if p[0]>=6)
    if len(pts)<9: continue
    days=[p[0] for p in pts]; M=np.array([p[1] for p in pts])
    obs=metrics(days,M)
    mods={f: metrics(days, run(M[0], f, days)) for f in (0.10,0.15,0.20)}
    rows.append((name,obs,mods))
    print(f"{name:22s} {obs['rate_kg_day']:8.3f} " + " ".join(f"{mods[f]['rate_kg_day']:15.3f}" for f in (0.10,0.15,0.20)) + f" {obs['r']:6.3f} {mods[0.15]['r']:15.3f}")
obs_rates=np.array([o['rate_kg_day'] for _,o,_ in rows]); mod_rates=np.array([m[0.15]['rate_kg_day'] for _,_,m in rows])
print("median obs/model rate (f=.15):", round(float(np.median(obs_rates/mod_rates)),3))
print("median obs r:", round(float(np.median([o['r'] for _,o,_ in rows])),3), " median model r:", round(float(np.median([m[0.15]['r'] for _,_,m in rows])),3))
