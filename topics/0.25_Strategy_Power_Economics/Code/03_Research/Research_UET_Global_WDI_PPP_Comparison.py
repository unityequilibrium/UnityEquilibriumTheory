from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
RAW=Path("docs/data/external/economics/global/wdi/2026-07-16")
ART=ROOT/"Result/artifacts/0_25_global_wdi_ppp_comparison.json"
def main():
 a=json.loads((RAW/"NY.GDP.PCAP.KD.json").read_text())[1];b=json.loads((RAW/"NY.GDP.PCAP.PP.KD.json").read_text())[1]
 x={(r.get("country",{}).get("id"),int(r["date"])):r["value"] for r in a if r.get("value") is not None};y={(r.get("country",{}).get("id"),int(r["date"])):r["value"] for r in b if r.get("value") is not None};v=[y[k]/x[k] for k in set(x)&set(y) if x[k]]
 out={"schema_version":"1.0","status":"PASS" if len(v)>1000 else "WARN","rows":len(v),"countries":len({k[0] for k in set(x)&set(y)}),"ratio_median":sorted(v)[len(v)//2],"ratio_min":min(v),"ratio_max":max(v),"unit_policy":"PPP and constant-USD measures remain separate; no pooling in primary diagnostic","claim_boundary":"PPP comparison is a measurement robustness lane, not a causal or welfare conclusion."};ART.write_text(json.dumps(out,indent=2)+"\n");print("WDI PPP comparison:",out["status"],len(v))
if __name__=="__main__":main()
