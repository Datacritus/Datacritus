"""Validate published data, cabinet continuity and (when present) raw provenance."""
import datetime as dt, hashlib, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from eurostat import parse_payload, transform_series
from catalog import METRICS
from eurostat import CATALOG
from vetted import MANIFEST, metrics_from_receipt
from oecd import MANIFEST as OECD_MANIFEST, metrics_from_receipt as replay_oecd
D=json.loads((ROOT/'data/indicators.json').read_text());H=json.loads((ROOT/'data/history.json').read_text())
expected={m['code'] for m in METRICS+CATALOG+MANIFEST+OECD_MANIFEST}
assert {m['code'] for m in D['metrics']}==expected
assert len(D['metrics'])==len(expected)
assert len(D['categories'])==12
from taxonomy import PRIMARY, classify
assert set(PRIMARY)==expected
assert all(m['categories']==[m['primaryCategory']] and classify(m)==m for m in D['metrics'])
countries=set(D['countries']);cats={c['id'] for c in D['categories']}
# Unit conversions must preserve missing observations and real zero values.
assert transform_series({'GRC':[[2020,500],[2021,None],[2022,0]]},{'scale':0.01})=={'GRC':[[2020,5],[2021,None],[2022,0]]}
by_code={m['code']:m for m in D['metrics']}
assert by_code['ESTAT.POLICE.DENSITY']['unit']=='officers per 1,000 people'
assert by_code['ESTAT.POLICE.DENSITY']['change']=='absolute'
assert by_code['ESTAT.MOTHERS.AGE']['change']=='absolute'
assert by_code['ESTAT.GOV.EXPENDITURE']['change']=='pp'
assert countries=={'GRC','EUU','DEU','FRA','ESP','PRT'}
assert {c for m in D['metrics'] for c in m['categories']}==cats
count=0
for m in D['metrics']:
 assert m['definition'] and m['sourceUrl'].startswith('https://') and m['apiUrl'].startswith('https://')
 assert set(m['series'])==countries
 assert len(m['sha256'])==64
 assert m['change'] in ('pp','absolute')
 for rows in m['series'].values():
  years=[p[0] for p in rows];assert years==sorted(set(years)),m['code']
  for year,value in rows:
   assert 1974<=year<=dt.datetime.now(dt.timezone.utc).year
   assert value is None or isinstance(value,(int,float)) and math.isfinite(value)
   count+=value is not None
 greek=[p for p in m['series']['GRC'] if p[1] is not None]
 assert greek,m['code']
 assert m['coverage']=={'start':greek[0][0],'end':greek[-1][0],'observations':len(greek)}
for i,g in enumerate(H['governments']):
 dt.date.fromisoformat(g['start']);assert g['party'] in H['parties']
 if i+1<len(H['governments']):assert g['end']==H['governments'][i+1]['start']
assert H['governments'][-1]['end'] is None
assert len(H['elections'])==20
assert len({e['date'] for e in H['elections']})==20
raw={hashlib.sha256(p.read_bytes()).hexdigest():p for p in (ROOT/'data/raw').glob('*.json')}
checked=0
receipts={}
upstream_hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data/raw').glob('vetted-*-source.*')}
upstream_hashes.update(hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data/raw').glob('vetted-*-metadata.*'))
for m in D['metrics']:
 if m.get('oecdAuditId'):
  path=raw.get(m['rawReceiptSha256'])
  if path:
   if 'oecd' not in receipts:
    payload=json.loads(path.read_text());payload['receiptSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    receipts['oecd']={x['code']:x for x in replay_oecd(payload)}
   replay=receipts['oecd'][m['code']]
   for key in ('series','flags','unit','change','definition','coverage','upstreamHashes','transformation'):
    assert replay[key]==m[key],(m['code'],key)
   for flow,digest in m['upstreamHashes'].items():
    original=ROOT/'data/raw'/('oecd-source-'+flow.replace('@','-')+'.csv')
    assert original.exists() and hashlib.sha256(original.read_bytes()).hexdigest()==digest
   checked+=1
  continue
 if m.get('auditId'):
  path=raw.get(m['rawReceiptSha256'])
  if path:
   assert set(m['upstreamHashes'].values())<=upstream_hashes, 'Missing original source bytes'
   provider=m['code'].split('.')[0].lower()
   if provider not in receipts:
    payload=json.loads(path.read_text());payload['receiptSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    receipts[provider]={x['code']:x for x in metrics_from_receipt(payload)}
   replay=receipts[provider][m['code']]
   for key in ('series','flags','uncertainty','unit','change','definition','coverage','upstreamHashes','transformation'):
    assert replay[key]==m[key],(m['code'],key)
   checked+=1
  continue
 if m['sha256'] not in raw:continue
 payload=json.loads(raw[m['sha256']].read_text())
 if m['source']=='Eurostat':
  series,flags=parse_payload(payload);assert transform_series(series,m)==m['series'];assert flags==m['flags']
 else:
  upstream={c:{} for c in countries}
  for p in payload[1]:
   if p['indicator']['id']==m['code'] and p['countryiso3code'] in countries:upstream[p['countryiso3code']][int(p['date'])]=p['value']
  assert {c:[[y,v] for y,v in sorted(rows.items())] for c,rows in upstream.items()}==m['series']
 checked+=1
if raw:assert checked==len(D['metrics'])
print(f'Validated {len(D["metrics"])} indicators, {count} observations, 26 cabinet periods; {checked} raw source matches')

# Expansion gate: publication keeps the audited coverage, interpretation and unique slices.
from expansion import WORLD_BANK, EUROSTAT
from urllib.parse import urlparse, parse_qs
slices=set()
for metric in D['metrics']:
 if metric['source']=='Eurostat':
  url=urlparse(metric['apiUrl']);params=parse_qs(url.query)
  signature=(url.path,tuple(sorted((k,tuple(v)) for k,v in params.items() if k not in ('geo','lang'))))
  assert signature not in slices, f'Duplicate Eurostat slice: {metric["code"]}'
  slices.add(signature)
for config in WORLD_BANK+EUROSTAT:
 m=by_code[config['code']]
 assert m['title']['en'] and m['title']['el'] and m['definitionEl']
 assert m['auditCode']==config['auditCode']
 assert m['change']==('pp' if m['unit'].startswith('%') else 'absolute')
 years={c:{y for y,v in m['series'][c] if v is not None and y<=2024} for c in ('GRC','ESP','PRT')}
 assert len(set.intersection(*years.values()))>=5,m['code']
 g=[(y,v) for y,v in m['series']['GRC'] if v is not None]
 assert len(g)>=10 and g[-1][0]>=2020 and len({v for y,v in g})>1,m['code']
 assert len(g)/(g[-1][0]-g[0][0]+1)>=0.7,m['code']
assert by_code['ESTAT.SALARY.FTE']['change']=='absolute'
assert by_code['ESTAT.INCOME.MEDIAN']['change']=='absolute'
assert by_code['ESTAT.UNEMPLOYMENT.LONGTERM']['unit']=='% of labour force ages 15–74'
assert by_code['ESTAT.JUSTICE.PRISON.RATE']['change']=='absolute'
print(f'Validated {len(WORLD_BANK)+len(EUROSTAT)} additions: coverage, bilingual definitions and unique source slices')

for config in MANIFEST:
 m=by_code[config['code']]
 assert m['auditId']==config['auditId'] and m['license']==config['license']
 assert m['termsUrl'].startswith('https://') and m['attribution'] and m['sourceVersion']
 assert m['interpretation']['en'] and m['interpretation']['el']
 assert m['series']['EUU']==[], 'Never invent an EU aggregate'
 if config['provider']=='vdem':
  assert m['uncertaintyLevel']==(.68 if any(m['uncertainty'].values()) else None) and m['change']=='absolute'
  for c,years in m['uncertainty'].items():
   values=dict(m['series'][c])
   for year,(low,high) in years.items():
    assert math.isfinite(low) and math.isfinite(high) and low<=high and int(year) in values
 assert m['coverage']['observations']>=10 and m['coverage']['end']>=2020
assert len(MANIFEST)==263
print('Validated all 263 reviewed additions, source versions, licences, units and uncertainty')

assert len(OECD_MANIFEST)==20
for config in OECD_MANIFEST:
 m=by_code[config['code']]
 assert m['publicationReady'] and m['unit']=='% of GDP' and m['change']=='pp'
 assert m['title']['el'] and m['definitionEl'] and m['interpretation']['el']
 assert m['series']['EUU']==[] and m['coverage']['observations']>=10
 assert m['license']=='OECD data terms (attribution required)' and m['sourceRightsBasis']
 for c in ('GRC','DEU','FRA','ESP','PRT'):
  assert len([p for p in m['series'][c] if p[1] is not None])>=5,(m['code'],c)
print('Validated 20 selected OECD indicators: exact slices, bilingual context, source terms and comparison coverage')
