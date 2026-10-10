"""Replay the new series against provider payloads and validate their meaning."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from eurostat import EXPANSION,parse_payload
D={m['code']:m for m in json.loads((ROOT/'data/indicators.json').read_text())['metrics']}
assert len(EXPANSION)==11
assert len({(m['dataset'],tuple(sorted(m['params'].items()))) for m in EXPANSION})==11
for config in EXPANSION:
 m=D[config['code']];path=ROOT/'data/raw'/('eurostat-'+m['code']+'.json')
 if path.exists():
  raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==m['sha256']
  series,flags=parse_payload(json.loads(raw));assert series==m['series'] and flags==m['flags']
 greek=[(y,v) for y,v in m['series']['GRC'] if v is not None]
 assert len(greek)>=10 and greek[-1][0]>=2020
 assert all(v>=0 for y,v in greek)
 if m['change']=='pp':assert all(v<=100 for y,v in greek)
 assert m['termsUrl']=='https://ec.europa.eu/eurostat/help/copyright-notice'
 assert m['primaryCategory']==config['categories'][0]
 if 'HEALTH.UNMET' in m['code']:assert config['dataset']=='hlth_silc_08' and config['params']['quant_inc']=='TOTAL' and config['params']['age']=='Y_GE16'
 if 'ENERGY.' in m['code']:assert config['params']['nrg_bal'].endswith('_EED') and m['unit']=='million tonnes of oil equivalent'
 if m['code']=='ESTAT.INCOME.S80S20':assert m['change']=='absolute' and m['unit']=='ratio'
# Distinguish the same-needs denominator in hlth_silc_08b: never splice it here.
assert not any(m['dataset']=='hlth_silc_08b' for m in EXPANSION)
combined=dict(D['ESTAT.HEALTH.UNMET.ACCESS']['series']['GRC'])
components=[dict(D['ESTAT.HEALTH.UNMET.'+k]['series']['GRC']) for k in ['COST','DISTANCE','WAITING']]
for year,total in combined.items():
 if total is not None and all(c.get(year) is not None for c in components):assert abs(total-sum(c[year] for c in components))<=.21
print('Eurostat expansion: 11 series, raw replay, categories, bounds, definitions and related components passed')
