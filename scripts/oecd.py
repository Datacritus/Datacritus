"""Twenty reviewed public-finance series; exact slices, retained source flags.

The 2025 edition is intentionally pinned. This is not a claim to cover the
latest OECD release. New editions require a metadata and comparability review.
"""
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import time
import urllib.request
from catalog import COUNTRIES

MANIFEST = json.loads(Path(__file__).with_name('oecd_selection.json').read_text())
STATUS = {'A':'Normal value','B':'Time series break','E':'Estimated value',
          'P':'Provisional value','K':'Data included in another category',
          'W':'Includes data from another category','M':'Missing value',
          'C':'Confidential','D':'Differing definition','U':'Low reliability'}
WARNING = {
 'en':'Government spending and fiscal position, not service quality or a government score. COFOG components overlap with their parent totals; do not add them together. GDP movements also affect these percentages. The reviewed 2025 edition is pinned; publication lags and source flags remain visible. Changes during a term do not establish causation.',
 'el':'Κρατικές δαπάνες και δημοσιονομική θέση, όχι ποιότητα υπηρεσιών ή βαθμολογία κυβέρνησης. Οι συνιστώσες COFOG περιλαμβάνονται στα συνολικά μεγέθη· δεν αθροίζονται με αυτά. Οι μεταβολές του ΑΕΠ επηρεάζουν επίσης τα ποσοστά. Χρησιμοποιείται η ελεγμένη έκδοση 2025, με τις αρχικές σημάνσεις και καθυστερήσεις. Οι μεταβολές στη θητεία δεν αποδεικνύουν αιτιότητα.'}

def parse_csv(raw, configs):
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    if not rows or 'OBS_VALUE' not in rows[0]:
        raise ValueError('OECD returned an empty or non-CSV response')
    output = {m['code']:{c:{} for c in COUNTRIES} for m in configs}
    for row in rows:
        country = row.get('REF_AREA')
        if country not in COUNTRIES or country == 'EUU':
            continue
        for config in configs:
            if not all(row.get(k) == v for k,v in config['dimensions'].items() if k != 'REF_AREA'):
                continue
            if not row['TIME_PERIOD'].isdigit():
                raise ValueError('Nonannual OECD observation')
            year = int(row['TIME_PERIOD'])
            if not 1974 <= year <= dt.datetime.now(dt.timezone.utc).year:
                continue
            statuses = {k:v for k,v in row.items() if k.startswith('OBS_STATUS') and v}
            if any(v not in STATUS for v in statuses.values()):
                raise ValueError(f'Unreviewed OECD status: {statuses}')
            value = float(row['OBS_VALUE']) if row['OBS_VALUE'].strip() else None
            if value is not None:
                value *= 10 ** int(row.get('UNIT_MULT') or 0)
                if not math.isfinite(value):
                    raise ValueError('Nonfinite OECD observation')
            if any(v in ('M','C','K') for v in statuses.values()):
                value = None
            years = output[config['code']][country]
            if year in years:
                raise ValueError(f'Duplicate OECD year: {config["code"]}/{country}/{year}')
            years[year] = {'value':value, 'flags':'; '.join(f'{v}: {STATUS[v]}' for v in statuses.values() if v != 'A')}
    return output

def metrics_from_receipt(receipt):
    metrics = []
    for config in MANIFEST:
        points = receipt['observations'][config['code']]
        series = {c:[[int(y),p['value']] for y,p in sorted(points[c].items(),key=lambda x:int(x[0]))] for c in COUNTRIES}
        greek = [p for p in series['GRC'] if p[1] is not None]
        if len(greek)<10 or greek[-1][0]<2020 or len({v for y,v in greek})<2:
            raise ValueError(f'Insufficient Greek OECD history: {config["code"]}')
        if len(greek)/(greek[-1][0]-greek[0][0]+1)<.7:
            raise ValueError('Sparse Greek OECD history')
        provenance = receipt['flows'][config['flow']]
        source_url = 'https://data-explorer.oecd.org/vis?df[ag]=OECD.GOV.GIP&df[id]='+config['flow']+'&df[vs]=1.0&lc=en'
        credit = f'OECD (2025), Government at a Glance 2025; OECD National Accounts / Eurostat Government Finance Statistics; {config["flow"]}; {source_url} (accessed {receipt["retrievedAt"][:10]}). Retain this acknowledgement when redistributing.'
        metrics.append({**config,'categories':[config['category']],
          'source':'OECD','sourceName':'OECD Government at a Glance 2025','provider':'OECD; OECD National Accounts / Eurostat',
          'providerTitle':config['title']['en'],'sourceUrl':source_url,'apiUrl':provenance['url'],
          'metadataUrl':config['methodologyUrl'],'accessMethod':'api', 'sourceVersion':'Government at a Glance 2025; SDMX flow 1.0',
          'sourceUpdatedAt':None,'retrievedAt':receipt['retrievedAt'],'sha256':provenance['sha256'],
          'rawReceiptSha256':receipt.get('receiptSha256'),'upstreamHashes':{config['flow']:provenance['sha256']},
          'attribution':credit,'measurementType':'official national accounts statistic','interpretation':WARNING,
          'transformation':'Exact annual general-government slice; source values multiplied by 10^UNIT_MULT; unavailable values preserved. No interpolation or EU aggregate.',
          'series':series,'flags':{c:{y:p['flags'] for y,p in points[c].items() if p['flags']} for c in COUNTRIES},
          'uncertainty':{c:{} for c in COUNTRIES},'uncertaintyLevel':None,
          'coverage':{'start':greek[0][0],'end':greek[-1][0],'observations':len(greek)},
          'subtopic':{'id':'government-spending','title':{'en':'Government spending & finances','el':'Κρατικές δαπάνες & οικονομικά'}}})
    return metrics

def collect_all(raw_dir, cached=False):
    path = raw_dir/'oecd-receipt.json'
    if cached:
        receipt = json.loads(path.read_text())
    else:
        receipt = {'retrievedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'flows':{},'observations':{}}
        for flow in dict.fromkeys(m['flow'] for m in MANIFEST):
            configs = [m for m in MANIFEST if m['flow']==flow]
            dimensions = list(configs[0]['dimensions'])
            key = []
            for dim in dimensions:
                key.append('GRC+DEU+FRA+ESP+PRT' if dim=='REF_AREA' else '+'.join(sorted({m['dimensions'][dim] for m in configs})))
            url = f'https://sdmx.oecd.org/public/rest/v1/data/OECD.GOV.GIP,{flow},1.0/'+'.'.join(key)+f'?startPeriod=1974&endPeriod={dt.date.today().year}'
            error = None
            for attempt in range(3):
                try:
                    req = urllib.request.Request(url,headers={'Accept':'application/vnd.sdmx.data+csv;version=1.0','User-Agent':'Datacritus/1.0 (public statistics dashboard; https://www.datacritus.gr)'})
                    with urllib.request.urlopen(req,timeout=55) as response:
                        raw = response.read()
                    observations = parse_csv(raw,configs)
                    break
                except Exception as exc:
                    error = exc
                    if attempt==2:
                        raise RuntimeError(f'OECD refresh failed: {url}: {error}')
                    time.sleep(2+attempt)
            (raw_dir/('oecd-source-'+flow.replace('@','-')+'.csv')).write_bytes(raw)
            receipt['flows'][flow]={'url':url,'sha256':hashlib.sha256(raw).hexdigest()}
            receipt['observations'].update(observations)
            print('OECD fetched',flow,len(configs),'selected indicators',flush=True)
        # Validate the entire selection before replacing its receipt.
        metrics_from_receipt(receipt)
        temp=path.with_suffix('.tmp');temp.write_text(json.dumps(receipt,ensure_ascii=False,separators=(',',':')));temp.replace(path)
    receipt['receiptSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    return metrics_from_receipt(receipt)
