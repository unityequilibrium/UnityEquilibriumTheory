from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[2]
PANEL=ROOT/"Result/artifacts/0_25_funding_source_proxy_panel.json"
ART=ROOT/"Result/artifacts/0_25_funding_source_association_audit.json"
def corr(x,y):
 if len(x)<3:return None
 mx=sum(x)/len(x);my=sum(y)/len(y);den=math.sqrt(sum((z-mx)**2 for z in x)*sum((z-my)**2 for z in y));return None if den==0 else sum((a-mx)*(b-my) for a,b in zip(x,y))/den
def main():
 obs=json.loads(PANEL.read_text())["observations"];rows=[]
 for a,b in zip(obs,obs[1:]):
  try:
   r={k:math.log(b[k]/a[k]) for k in ["CPATAX","GPDI","BUSLOANS","W790RC1Q027SBEA","PCTR"]};r["year"]=b["year"];rows.append(r)
  except (KeyError,ValueError,ZeroDivisionError):pass
 x=[r["GPDI"] for r in rows];ass={k:corr([r[k] for r in rows],x) for k in ["CPATAX","BUSLOANS","W790RC1Q027SBEA","PCTR"]};out={"schema_version":"1.0","status":"PASS" if len(rows)>=40 else "WARN","rows":len(rows),"target":"annual log change in GPDI","same_year_correlations_with_investment_growth":ass,"construction":"annual-average sectoral proxies; log changes; complete-case only; no imputation","interpretation":"Descriptive same-year association only; not funding causality or payment provenance.","claim_boundary":"Associations cannot be called causal without intervention design and sectoral accounting reconciliation.","blockers":["Equity, transfers, sectoral flow-of-funds reconciliation, and transaction-level payer/source remain unavailable."]};ART.write_text(json.dumps(out,indent=2)+"\n");print("Funding association audit:",out["status"],len(rows))
if __name__=="__main__":main()
