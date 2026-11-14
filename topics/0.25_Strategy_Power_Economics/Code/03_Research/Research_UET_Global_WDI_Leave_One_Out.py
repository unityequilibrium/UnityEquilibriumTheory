from pathlib import Path
import csv,json,math
ROOT=Path(__file__).resolve().parents[2]
PANEL=ROOT/"Data/03_Research/uet_global_wdi_panel.csv"
ART=ROOT/"Result/artifacts/0_25_global_wdi_leave_one_out.json"
def corr(a,b):
 if len(a)<3:return None
 ma=sum(a)/len(a);mb=sum(b)/len(b);den=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b));return None if den==0 else sum((x-ma)*(y-mb) for x,y in zip(a,b))/den
def run(exclude=None):
 d={}
 for r in csv.DictReader(PANEL.open(encoding="utf-8")):
  if r["country_code"]!=exclude:d.setdefault(r["country_code"],[]).append(r)
 x=[];y=[]
 for rs in d.values():
  rs.sort(key=lambda z:int(z["year"]))
  for a,b in zip(rs,rs[1:]):
   try:x.append(math.log(float(b["NY.GDP.PCAP.KD"])/float(a["NY.GDP.PCAP.KD"])));y.append(math.log(float(b["EG.USE.PCAP.KG.OE"])/float(a["EG.USE.PCAP.KG.OE"])))
   except (ValueError,ZeroDivisionError):pass
 return corr(x,y),len(x)
def main():
 rows=list(csv.DictReader(PANEL.open(encoding="utf-8")));full,n=run();vals=[]
 for c in sorted({r["country_code"] for r in rows}):
  v,_=run(c)
  if v is not None:vals.append(v)
 out={"schema_version":"1.0","status":"PASS" if len(vals)>=30 else "WARN","rows":len(rows),"countries_evaluated":len(vals),"full_panel_change_correlation":full,"full_panel_change_pairs":n,"leave_one_country_out":{"positive":sum(v>0 for v in vals),"negative":sum(v<0 for v in vals),"min":min(vals) if vals else None,"median":sorted(vals)[len(vals)//2] if vals else None,"max":max(vals) if vals else None},"interpretation":"Descriptive robustness only; not causal and not measurement invariance.","blockers":["PPP/exchange-rate split and formal measurement-invariance tests remain open."]};ART.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8");print("Global WDI leave-one-out:",out["status"],len(vals))
if __name__=="__main__":main()
