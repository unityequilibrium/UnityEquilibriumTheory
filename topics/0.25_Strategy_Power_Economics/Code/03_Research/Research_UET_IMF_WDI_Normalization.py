from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[2]
META=Path("docs/data/external/economics/global/wdi/2026-07-16/country_metadata.json")
IMF=Path("docs/data/external/economics/global/imf/2026-07-16/PCPIPCH.json")
WDI=ROOT/"Data/03_Research/uet_global_wdi_panel.csv"
ART=ROOT/"Result/artifacts/0_25_global_imf_wdi_normalization.json"
def main():
 meta=json.loads(META.read_text())[1];iso3to2={r["id"]:r.get("iso2Code") for r in meta if r.get("iso2Code")};wdi={r["country_code"] for r in csv.DictReader(WDI.open(encoding="utf-8"))};vals=json.loads(IMF.read_text())["values"]["PCPIPCH"];matched={c for c in vals if iso3to2.get(c) in wdi};years={c:sum(2000<=int(y)<=2024 for y in v) for c,v in vals.items() if c in matched};complete={c:n for c,n in years.items() if n>=20};out={"schema_version":"1.0","status":"PASS" if len(complete)>=30 else "WARN","imf_countries":len(vals),"matched_to_wdi_panel":len(matched),"matched_20_plus_years":len(complete),"coverage_window":[2000,2024],"join_policy":"IMF ISO3 -> World Bank metadata iso2Code -> WDI panel ISO2; aggregates excluded","missingness_policy":"no imputation","claim_boundary":"Measurement comparison only; no causal inflation claim."};ART.write_text(json.dumps(out,indent=2)+"\n");print("IMF-WDI normalization:",out["status"],len(complete))
if __name__=="__main__":main()
