from pathlib import Path
import csv,json,math
ROOT=Path(__file__).resolve().parents[2]
META=Path("docs/data/external/economics/global/wdi/2026-07-16/country_metadata.json")
PANEL=ROOT/"Data/03_Research/uet_global_wdi_panel.csv"
ART=ROOT/"Result/artifacts/0_25_global_wdi_leave_one_region_out.json"
def corr(x,y):
 if len(x)<3:return None
 mx=sum(x)/len(x);my=sum(y)/len(y);den=math.sqrt(sum((z-mx)**2 for z in x)*sum((z-my)**2 for z in y));return None if den==0 else sum((a-mx)*(b-my) for a,b in zip(x,y))/den
def main():
 meta=json.loads(META.read_text())[1];reg={r.get("iso2Code"):r.get("region",{}).get("value") for r in meta if r.get("region",{}).get("id")!="NA" and r.get("iso2Code")};rows=[r for r in csv.DictReader(PANEL.open(encoding="utf-8")) if r["country_code"] in reg];out={}
 for ex in sorted(set(reg.values())):
  d={};x=[];y=[]
  for r in rows:
   if reg[r["country_code"]]!=ex:d.setdefault(r["country_code"],[]).append(r)
  for rs in d.values():
   rs.sort(key=lambda z:int(z["year"]))
   for a,b in zip(rs,rs[1:]):
    try:x.append(math.log(float(b["NY.GDP.PCAP.KD"])/float(a["NY.GDP.PCAP.KD"])));y.append(math.log(float(b["EG.USE.PCAP.KG.OE"])/float(a["EG.USE.PCAP.KG.OE"])))
    except:pass
  out[ex]={"correlation":corr(x,y),"pairs":len(x)}
 ART.write_text(json.dumps({"schema_version":"1.0","status":"PASS" if len({r["country_code"] for r in rows})>=30 else "WARN","countries_joined":len({r["country_code"] for r in rows}),"regions":out,"join_policy":"ISO2 panel id to metadata iso2Code; aggregates excluded by region id NA","claim_boundary":"Descriptive regional robustness only; no causal claim."},indent=2)+"\n");print("regional WDI audit complete",len(rows))
if __name__=="__main__":main()
