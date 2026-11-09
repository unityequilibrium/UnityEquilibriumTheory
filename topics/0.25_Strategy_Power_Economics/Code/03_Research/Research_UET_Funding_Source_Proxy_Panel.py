from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[2]
RAW=Path("docs/data/external/economics/us_historical/fred/2026-07-16")
ART=ROOT/"Result/artifacts/0_25_funding_source_proxy_panel.json"
CODES=["CPATAX","GPDI","BUSLOANS","W790RC1Q027SBEA","PCTR"]
def main():
 data={}
 for code in CODES:
  annual={}
  for r in csv.DictReader((RAW/f"{code}.csv").open(encoding="utf-8")):
   try:annual.setdefault(int(r["observation_date"][:4]),[]).append(float(r[code]))
   except:pass
  data[code]={y:sum(v)/len(v) for y,v in annual.items()}
 years=sorted(y for y in set.intersection(*(set(v) for v in data.values())) if 1959 <= y <= 2024);obs=[]
 for y in years:
  r={"year":y,**{c:data[c][y] for c in CODES}};r["profit_to_investment_ratio"]=r["CPATAX"]/r["GPDI"] if r["GPDI"] else None;r["credit_to_profit_ratio"]=r["BUSLOANS"]/r["CPATAX"] if r["CPATAX"] else None;obs.append(r)
 out={"schema_version":"1.0","status":"PASS" if len(obs)>=50 else "WARN","coverage":[years[0],years[-1]],"rows":len(obs),"series":CODES,"observations":obs,"construction":"quarterly FRED observations annualized by arithmetic mean; no imputation","interpretation":"Aggregate sectoral funding proxies only; not transaction provenance or causality.","blockers":["Transfers and equity issuance are not represented; transaction-level payer/source linkage remains blocked."]};ART.write_text(json.dumps(out,indent=2)+"\n");print("Funding proxy panel:",out["status"],len(obs))
if __name__=="__main__":main()
