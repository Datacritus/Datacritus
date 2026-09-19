"""Validate published data, cabinet continuity and (when present) raw provenance."""
import datetime as dt, hashlib, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from eurostat import parse_payload
from catalog import METRICS
from eurostat import CATALOG
D=json.loads((ROOT/'data/indicators.json').read_text());H=json.loads((ROOT/'data/history.json').read_text())
expected={m['code'] for m in METRICS+CATALOG}
assert {m['code'] for m in D['metrics']}==expected
assert len(D['metrics'])==len(expected)
assert len(D['categories'])==21
countries=set(D['countries']);cats={c['id'] for c in D['categories']}
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
for m in D['metrics']:
 if m['sha256'] not in raw:continue
 payload=json.loads(raw[m['sha256']].read_text())
 if m['source']=='Eurostat':
  series,flags=parse_payload(payload);assert series==m['series'];assert flags==m['flags']
 else:
  upstream={c:{} for c in countries}
  for p in payload[1]:
   if p['indicator']['id']==m['code'] and p['countryiso3code'] in countries:upstream[p['countryiso3code']][int(p['date'])]=p['value']
  assert {c:[[y,v] for y,v in sorted(rows.items())] for c,rows in upstream.items()}==m['series']
 checked+=1
if raw:assert checked==len(D['metrics'])
print(f'Validated {len(D["metrics"])} indicators, {count} observations, 26 cabinet periods; {checked} raw source matches')
