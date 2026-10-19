#!/usr/bin/env python3
"""Read-only World Bank candidate screen; never approves publication."""
import concurrent.futures,hashlib,json,urllib.request,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1];audit_date=datetime.date.today().isoformat();folder=root/'data/audits'/('catalogue-'+audit_date);out=folder/'candidate-responses';out.mkdir(parents=True,exist_ok=True)
D=json.loads((root/'data/indicators.json').read_text());existing={m['code'] for m in D['metrics']}
codes=['SH.MED.NUMW.P3','SH.STA.SUIC.P5','SH.STA.DIAB.ZS','SH.IMM.IDPT','SH.XPD.GHED.GD.ZS','SH.XPD.GHED.CH.ZS','SE.PRM.ENRL.TC.ZS','SE.SEC.ENRL.TC.ZS','IT.NET.SECR.P6','GB.XPD.RSDV.GD.ZS','IP.PAT.NRES','EG.ELC.FOSL.ZS','EN.ATM.PM25.MC.ZS','IS.VEH.NVEH.P3','IS.ROD.PAVE.ZS']
def run(code):
 r={'code':code,'alreadyPublished':code in existing,'publicationReady':False}
 if r['alreadyPublished']:return r
 for kind,url in [('metadata',f'https://api.worldbank.org/v2/indicator/{code}?source=2&format=json'),('data',f'https://api.worldbank.org/v2/country/GRC/indicator/{code}?source=2&format=json&date=1974:2026&per_page=20000')]:
  try:
   with urllib.request.urlopen(url,timeout=25) as response:raw=response.read()
   (out/f'{code}-{kind}.json').write_bytes(raw);payload=json.loads(raw)
   r[kind]={'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
   if kind=='metadata' and isinstance(payload,list) and len(payload)>1 and payload[1]:
    r['title']=payload[1][0]['name'];r['definition']=payload[1][0].get('sourceNote','')
   if kind=='data' and isinstance(payload,list) and len(payload)>1 and isinstance(payload[1],list):
    series=sorted([[int(p['date']),p['value']] for p in payload[1] if isinstance(p.get('value'),(int,float))]);r['series']=series
    years={p[0] for p in series};r['observations']=len(series);r['latestYear']=max(years) if years else None;r['earliestYear']=min(years) if years else None
    r['defaultPairCounts']=[len(years.intersection(x)) for x in [[2016,2017,2018],[2020,2021,2022]]]
    r['dataScreenPass']=len(series)>=15 and bool(years) and max(years)>=2023 and min(r['defaultPairCounts'])>=2
  except Exception as e:r[kind+'Error']=str(e)
 r['decision']='data screen passed; definition/overlap/licence review required' if r.get('dataScreenPass') else 'defer: missing, old, sparse or failed data route'
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(run,codes))
(folder/'candidate-screen.json').write_text(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'limits':'Candidate API/data checks only. Not approved for publication; no source-licence revalidation or adapter integration.','candidates':rows},ensure_ascii=False,indent=2)+'\n')
for r in rows:print(r['code'],r.get('title',''),r.get('observations'),r.get('latestYear'),r.get('dataScreenPass'),r.get('alreadyPublished'),r.get('dataError',''))
