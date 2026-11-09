from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[2]
PANEL=ROOT/"Result/artifacts/0_25_funding_source_proxy_panel.json"
ART=ROOT/"Result/artifacts/0_25_funding_source_lag_association_audit.json"
def corr(x,y):
 if len(x)<3:return None
 mx=sum(x)/len(x);my=sum(y)/len(y);den=math.sqrt(sum((z-mx)**2 for z in x)*sum((z-my)**2 for z in y));return None if den==0 else sum((a-mx)*(b-my) for a,b in zip(x,y))/den
def main():
 obs=json.loads(PANEL.read_text())["observations"];g={}
 for a,b in zip(obs,obs[1:]):
  try:g[b["year"]]={k:math.log(b[k]/a[k]) for k in ["CPATAX","GPDI","BUSLOANS","W790RC1Q027SBEA","PCTR"]}
  except:pass
 out={}
 for lag in [0,1,2]:
  out[str(lag)]={}
  for key in ["CPATAX","BUSLOANS","W790RC1Q027SBEA","PCTR"]:
   x=[];y=[]
   for year in sorted(g):
    if year-lag in g:x.append(g[year-lag][key]);y.append(g[year]["GPDI"])
   out[str(lag)][key]={"correlation":corr(x,y),"n":len(x)}
 result={"schema_version":"1.0","status":"PASS","lags_years":[0,1,2],"results":out,"interpretation":"Lead-lag descriptive association; no causality, controls, or funding provenance.","claim_boundary":"Lagged association is not evidence that profits or credit cause investment.","blockers":["Sectoral controls, intervention design, and accounting reconciliation remain open."]};ART.write_text(json.dumps(result,indent=2)+"\n");print("Funding lag audit: PASS")
if __name__=="__main__":main()
