"""Replay the new series against provider payloads and validate their meaning."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from eurostat import EXPANSION,parse_payload,validate_selection
D={m['code']:m for m in json.loads((ROOT/'data/indicators.json').read_text())['metrics']}
assert len(EXPANSION)==37
assert len({(m['dataset'],tuple(sorted(m['params'].items()))) for m in EXPANSION})==37
for config in EXPANSION:
 m=D[config['code']];path=ROOT/'data/raw'/('eurostat-'+m['code']+'.json')
 if path.exists():
  raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==m['sha256']
  payload=json.loads(raw);validate_selection(payload,config['params']);series,flags=parse_payload(payload);assert series==m['series'] and flags==m['flags']
 greek=[(y,v) for y,v in m['series']['GRC'] if v is not None]
 assert len(greek)>=10 and greek[-1][0]>=2020
 lower,upper=config.get('valueRange',[0,100 if m['change']=='pp' else float('inf')])
 assert all(lower<=v<=upper for y,v in greek)
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
print('Eurostat expansion: 37 series, raw replay, categories, bounds, definitions and related components passed')

# Everyday-life additions use exact population denominators and explicit severe response.
selected={m['code']:m for m in EXPANSION}
assert selected['ESTAT.ENDS.MEET.GREATDIFFICULTY']['params']['lev_diff']=='GRT'
assert selected['ESTAT.DENTAL.UNMET.ACCESS']['dataset']=='hlth_silc_09'
for code in ['ESTAT.EXPENSES.UNEXPECTED','ESTAT.FOOD.AFFORDABILITY','ESTAT.ENDS.MEET.GREATDIFFICULTY']:
 assert selected[code]['params']['hhcomp']=='TOTAL' and selected[code]['params']['rskpovth']=='TOTAL'
 assert selected[code]['definitionEl']

# Ignored or changed provider filters must fail even when the returned axis is singleton.
for wrong in ({'freq':{'category':{'index':{'A':0}}},'unit':{'category':{'index':{'THS':0}}}},
              {'freq':{'category':{'index':{'A':0}}},'unit':{'category':{'index':{'PC':0,'THS':1}}}}):
 try:validate_selection({'dimension':wrong},{'unit':'PC'})
 except ValueError:pass
 else:raise AssertionError('Provider filter mismatch accepted')
for code in ['FOOD','RENT','ELECTRICITY','TRANSPORT']:
 config=selected['ESTAT.INFLATION.'+code]
 assert config['dataset']=='prc_hicp_ainr' and config['params']['unit']=='RCH_A_AVG'
 assert 'coicop18' in config['params'] and config['valueRange'][0]<0
 # Deflation is valid data, not missing or zero.
 assert any(v is not None and v<0 for y,v in D[config['code']]['series']['GRC'])
for config in EXPANSION[15:]:
 greek=dict(D[config['code']]['series']['GRC'])
 assert all(sum(greek.get(y) is not None for y in years)>=2 for years in [(2016,2017,2018),(2020,2021,2022)])
assert selected['ESTAT.CHILDCARE.UNDER3.30H']['params']['duration']=='H_GE30'
assert selected['ESTAT.WORK.CARE.INACTIVITY']['params']['unit']=='PC_POP'
assert selected['ESTAT.WORK.INTENSITY.LOW']['dataset']=='ilc_lvhl11n'
