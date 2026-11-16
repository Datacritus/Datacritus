"""Homepage comparison catalogue generated from the verified snapshot."""
from datetime import date
import math
import json

def render(snapshot, history):
    # Public-facing measures selected for relevance and understandable units.
    # Curated from Greek/English search-result themes: pay, prices, housing,
    # employment and household finances. This is not a search-volume ranking.
    codes = set('''
ESTAT.SALARY.FTE AMECO.RWCDC FP.CPI.TOTL.ZG ESTAT.INFLATION.FOOD
ESTAT.HOUSING.OVERBURDEN ESTAT.HOUSING.COST.MEDIAN
SL.UEM.TOTL.ZS SL.UEM.1524.ZS ESTAT.UNEMPLOYMENT.LONGTERM
NY.GDP.MKTP.KD.ZG NY.GDP.PCAP.KD
ESTAT.POVERTY.AROPE ESTAT.INCOME.MEDIAN
ESTAT.ENDS.MEET.GREATDIFFICULTY ESTAT.EXPENSES.UNEXPECTED
'''.split())
    groups = {}
    for metric in snapshot['metrics']:
        if metric['code'] not in codes:
            continue
        rows = dict(metric['series']['GRC'])
        periods = []
        for term in history['governments']:
            start = date.fromisoformat(term['start'])
            end = date.fromisoformat(term['end'] or history['verifiedAt'])
            years = [y for y in range(start.year, end.year) if start <= date(y,1,1) and end >= date(y+1,1,1)]
            if len(years) < 3 or any(not isinstance(rows.get(y),(int,float)) or not math.isfinite(rows[y]) for y in years):
                continue
            points = [rows[y] for y in years]
            party = history.get('parties', {}).get(term.get('party'), {})
            periods.append(dict(id=term['id'],name=term['name'],party=party,government=term['coalition'],termYears=[start.year,end.year],ongoing=not bool(term['end']),years=years,mean=sum(points)/len(points),first=points[0],last=points[-1]))
        pairs = [[i,j] for i,a in enumerate(periods) for j,b in enumerate(periods) if i < j and len(a['years'])==len(b['years'])]
        if pairs:
            groups.setdefault(metric['categories'][0],[]).append(dict(code=metric['code'],title=metric['title'],unit=metric['unit'],source=metric['sourceName'],latest=max(([y,v] for y,v in rows.items() if isinstance(v,(int,float)) and math.isfinite(v)),key=lambda p:p[0]),periods=periods,pairs=pairs))
    return json.dumps(list(groups.values()),ensure_ascii=False).replace('<','\\u003c')
