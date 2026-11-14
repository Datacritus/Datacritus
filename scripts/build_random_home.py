"""Small homepage comparison catalogue generated from the verified snapshot."""
from datetime import date
import json

def render(snapshot, history):
    codes = {'SL.UEM.TOTL.ZS','FP.CPI.TOTL.ZG','NY.GDP.MKTP.KD.ZG','SP.DYN.LE00.IN','ESTAT.INTERNET.HOUSEHOLDS','ESTAT.HOUSING.OVERBURDEN','SL.UEM.1524.ZS','SE.XPD.TOTL.GD.ZS','SH.XPD.CHEX.GD.ZS'}
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
            if len(years) < 3 or any(not isinstance(rows.get(y),(int,float)) for y in years):
                continue
            points = [rows[y] for y in years]
            periods.append(dict(id=term['id'],name=term['name'],years=years,mean=sum(points)/len(points),first=points[0],last=points[-1]))
        pairs = [[a,b] for i,a in enumerate(periods) for b in periods[i+1:] if len(a['years'])==len(b['years'])]
        if pairs:
            groups.setdefault(metric['categories'][0],[]).append(dict(code=metric['code'],title=metric['title'],unit=metric['unit'],source=metric['sourceName'],pairs=pairs))
    return json.dumps(list(groups.values()),ensure_ascii=False).replace('<','\\u003c')
