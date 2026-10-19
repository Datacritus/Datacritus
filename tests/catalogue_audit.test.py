"""Coverage and duplicate-screen regression fixtures; no network calls."""
import copy,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('catalogue_audit',ROOT/'tools/audit_catalogue.py');A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
d=json.loads((ROOT/'data/indicators.json').read_text());h=json.loads((ROOT/'data/history.json').read_text())
before=json.dumps(d,sort_keys=True);r=A.audit(d,h,'2026-10-19')
assert len(r['metrics'])==len(d['metrics'])==sum(c['count'] for c in r['categories'])
assert r['summary']['defaultPairScreenPass']<=r['summary']['defaultPairTwoEach']<=r['summary']['defaultPairHasBoth']
assert before==json.dumps(d,sort_keys=True),'Audit must not change published data'
a=copy.deepcopy(d['metrics'][0]);a['series']={'GRC':[[2016,0],[2017,None],[2018,2],[2020,4],[2021,6],[2022,8]]};a['flags']={'GRC':{'2016':'e'}}
b=copy.deepcopy(a);b['code']='TEST.DUPLICATE'
fixture={**d,'metrics':[a,b]};f=A.audit(fixture,h,'2026-10-19');row=f['metrics'][0]
assert row['greekObservations']==5 and row['internalMissingYears']==[2017,2019]
assert row['periods']['2015-09-21']['observedYears']==[2016,2018]
assert row['periods']['2015-09-21']['coverage']==.6667
assert row['defaultPairTwoEach'] and not row['defaultPairScreenPass']
assert row['flags']==[{'year':2016,'flag':'e'}]
assert row['currentTermScreenPass'] is False
assert f['duplicateReview']['identicalGreekSeriesGroups']==[[a['code'],b['code']]]
assert A.full_years({'start':'2020-01-01','end':'2022-01-01'},'2026-10-19')==[2020,2021]
assert A.full_years({'start':'2020-03-01','end':'2020-05-01'},'2026-10-19')==[]
print('Catalogue audit: full years, null/zero, gaps, coverage screens, flags, duplicates and immutable snapshot passed')
