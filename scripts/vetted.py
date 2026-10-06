"""Reviewed expansion only: 263 distinct definitions, four reproducible sources.

No keys, interpolation, invented EU aggregates, rankings, or mixed vintages.
Pinned research releases require an explicit review before changing versions.
"""
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import time
import urllib.parse
import urllib.request
from catalog import COUNTRIES
from vetted_labels import GREEK

MANIFEST = json.loads(Path(__file__).with_name('vetted_manifest.json').read_text())
VDEM_COMMIT = 'f4dd26922e658442524dfd954bf14f7ebe622d5d'
VDEM_BASE = f'https://raw.githubusercontent.com/vdeminstitute/vdemdata/{VDEM_COMMIT}/data/'
SOURCES = {
 'vdem': {'name':'V-Dem v16', 'url':'https://www.v-dem.net/data/the-v-dem-dataset/', 'data':VDEM_BASE+'vdem.RData', 'metadata':VDEM_BASE+'codebook.RData', 'version':'16 (2026)', 'citation':'V-Dem Project (2026), Country-Year Dataset v16, doi:10.23696/vdemds26', 'updated':None},
 'pwt': {'name':'Penn World Table 11.0', 'url':'https://www.rug.nl/ggdc/productivity/pwt/', 'data':'https://dataverse.nl/api/access/datafile/554105?format=original', 'metadata':'https://doi.org/10.34894/FABVLR', 'version':'11.0', 'citation':'Feenstra, Inklaar and Timmer (2015), The Next Generation of the Penn World Table; PWT 11.0, doi:10.34894/FABVLR', 'updated':'2025-10-07'},
 'undp': {'name':'UNDP Human Development Report 2025', 'url':'https://hdr.undp.org/data-center/documentation-and-downloads', 'data':'https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv', 'metadata':'https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_metadata.xlsx', 'version':'HDR 2025', 'citation':'UNDP (2025), Human Development Report 2025: A matter of choice—People and possibilities in the age of AI. New York', 'updated':None},
 'uis': {'name':'UNESCO Institute for Statistics', 'url':'https://databrowser.uis.unesco.org/', 'metadata':'https://api.uis.unesco.org/api/public/openapi/schema.json', 'version':'API release recorded per indicator', 'citation':'UNESCO Institute for Statistics, UIS Data Browser', 'updated':None},
}
WARNINGS = {
 'vdem': {'en':'Research estimates, not administrative counts. Bounds, where supplied, cover 68% of model probability for each annual estimate; they are not confidence intervals for term averages. Small differences may be uncertain. Scales and directions differ across indicators. Related components and composites are not independent evidence.', 'el':'Ερευνητικές εκτιμήσεις, όχι διοικητικές καταμετρήσεις. Τα διαθέσιμα όρια καλύπτουν το 68% της πιθανότητας του μοντέλου ανά έτος, όχι τον μέσο όρο θητείας. Μικρές διαφορές μπορεί να είναι αβέβαιες. Οι κλίμακες και η κατεύθυνση διαφέρουν ανά δείκτη. Σύνθετοι δείκτες και συνιστώσες δεν είναι ανεξάρτητες αποδείξεις.'},
 'pwt': {'en':'Research estimates from one PWT release. Price levels are relative ratios, not inflation rates; capital and productivity indices are not percentages. Historical estimates may be revised. Original quality flags are retained.', 'el':'Ερευνητικές εκτιμήσεις από μία έκδοση PWT. Τα επίπεδα τιμών είναι σχετικοί λόγοι, όχι πληθωρισμός· οι δείκτες κεφαλαίου και παραγωγικότητας δεν είναι ποσοστά. Διατηρούνται οι σημάνσεις ποιότητας της πηγής.'},
 'undp': {'en':'One internally consistent HDR 2025 release. Composite indices and their components are related measures, not independent evidence. Income inequality for 2023 reuses the source’s 2022 estimate; the original reference period is flagged.', 'el':'Ενιαία ιστορική έκδοση HDR 2025. Οι σύνθετοι δείκτες και οι συνιστώσες τους είναι συναφή μέτρα, όχι ανεξάρτητες αποδείξεις. Η εισοδηματική ανισότητα του 2023 χρησιμοποιεί την εκτίμηση του 2022, όπως ορίζει η πηγή.'},
 'uis': {'en':'Both sexes, national series, exact education level in the definition. Gross ratios may exceed 100%. National and UIS estimates and source footnotes are retained; not-applicable and suppressed observations remain missing.', 'el':'Εθνικές σειρές και για τα δύο φύλα, με τη βαθμίδα εκπαίδευσης στον ορισμό. Τα ακαθάριστα ποσοστά μπορεί να ξεπερνούν το 100%. Διατηρούνται οι σημάνσεις εκτιμήσεων και οι υποσημειώσεις· μη εφαρμόσιμα και απόρρητα στοιχεία παραμένουν κενά.'},
}

def numeric(value):
    if value is None or value == '': return None
    try: n = float(value)
    except (TypeError, ValueError): raise ValueError(f'Non-numeric source value: {value!r}')
    return n if math.isfinite(n) else None

def put(rows, code, country, year, value, flags='', bounds=None):
    if country not in COUNTRIES or not 1974 <= int(year) <= dt.datetime.now(dt.timezone.utc).year: return
    year = int(year)
    if year in rows[code][country]: raise ValueError(f'Duplicate observation: {code}/{country}/{year}')
    rows[code][country][year] = {'value':numeric(value), 'flags':flags, 'bounds':bounds}

def empty(configs):
    return {m['sourceCode']:{c:{} for c in COUNTRIES} for m in configs}

def download(url, path):
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0' if 'hdr.undp.org' in url else 'Datacritus source-validation/1.0', 'Referer':'https://hdr.undp.org/data-center/documentation-and-downloads'})
            with urllib.request.urlopen(req, timeout=100) as response: raw=response.read()
            if not raw: raise ValueError('Empty source response')
            if raw.lstrip().lower().startswith((b'<!doctype html', b'<html')): raise ValueError('Provider returned HTML instead of data')
            temp=path.with_suffix(path.suffix+'.tmp'); temp.write_bytes(raw); temp.replace(path)
            return hashlib.sha256(raw).hexdigest()
        except Exception as exc:
            error=exc
            if attempt<2: time.sleep(1+attempt)
    raise RuntimeError(f'{url}: {error}')

def parse_uis(payload, configs):
    if payload.get('hints'): raise ValueError(f'UIS returned query warnings: {payload["hints"]}')
    rows=empty(configs); metadata={x['indicatorCode']:x for x in payload['indicatorMetadata']}
    for p in payload['records']:
        code=p['indicatorId']
        if code not in rows: continue
        magnitude=p.get('magnitude'); qualifier=p.get('qualifier')
        if magnitude not in (None,'NIL','NA','SUPP','LOWREL','INCLUDED','INCLUDES'): raise ValueError('Unknown UIS magnitude')
        if qualifier not in (None,'NAT_EST','UIS_EST'): raise ValueError('Unknown UIS qualifier')
        notes=p.get('footnotes',[])
        unavailable=magnitude in ('NA','SUPP','INCLUDED') or any(n.get('type')=='Data Status' and n.get('value')=='NA' for n in notes)
        flags='; '.join(x for x in [magnitude,qualifier]+[f"{n['type']}: {n['value']}" for n in notes if n.get('type')!='Source'] if x)
        put(rows,code,p['geoUnit'],p['year'],None if unavailable else p['value'],flags)
    defs={}
    for m in configs:
        p=metadata[m['sourceCode']]
        definitions=[g.get('definition','') for g in p.get('glossaryTerms',[])]
        defs[m['sourceCode']]={'title':p['name'],'definition':p['name']+'. '+ ' '.join(definitions), 'release':p.get('lastDataUpdateDescription'), 'updated':None, 'sourceDateLabel':p.get('lastDataUpdate'), 'disaggregations':p.get('disaggregations',[])}
    return rows,defs

def parse_undp(raw, workbook, configs):
    import openpyxl
    rows=empty(configs)
    source=list(csv.DictReader(io.StringIO(raw.decode('latin-1'))))
    seen=set()
    for p in source:
        country=p['iso3']
        if country not in COUNTRIES: continue
        if country in seen: raise ValueError('Duplicate UNDP country')
        seen.add(country)
        for m in configs:
            code=m['sourceCode']
            for col,value in p.items():
                if col.startswith(code+'_') and col[len(code)+1:].isdigit():
                    year=int(col[len(code)+1:]); flag='SOURCE_REFERENCE_2022' if code=='ineq_inc' and year==2023 else ''
                    put(rows,code,country,year,value,flag)
    w=openpyxl.load_workbook(workbook,read_only=True,data_only=True)
    defs={}
    for sheet in w:
        for p in sheet.values:
            if p and len(p)>2 and p[1] in rows:
                defs[p[1]]={'title':str(p[0]),'definition':str(p[0])+'. Source-documented history: '+str(p[2]),'history':str(p[2])}
    w.close()
    if set(defs)!=set(rows): raise ValueError('UNDP metadata does not match selected identifiers')
    return rows,defs

def parse_pwt(path, configs):
    import openpyxl
    rows=empty(configs); w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    legend={p[0]:p[1] for p in w['Legend'].values if p and p[0] and len(p)>1 and p[1]}
    sheet=w['Data']; sheet.reset_dimensions(); it=iter(sheet.values); header=next(it)
    for values in it:
        p=dict(zip(header,values)); country=p.get('countrycode')
        if country not in COUNTRIES or not p.get('year'): continue
        flags='; '.join(f'{k}: {p[k]}' for k in ('i_irr','i_outlier','i_xr') if p.get(k) is not None)
        for m in configs: put(rows,m['sourceCode'],country,p['year'],p.get(m['sourceCode']),flags)
    w.close()
    return rows,{m['sourceCode']:{'title':legend[m['sourceCode']],'definition':legend[m['sourceCode']]} for m in configs}

def parse_vdem(path, codebook, configs):
    import pyreadr
    frame=next(iter(pyreadr.read_r(str(path)).values()))
    book=next(iter(pyreadr.read_r(str(codebook)).values()))
    rows=empty(configs); names={'Greece':'GRC','Germany':'DEU','France':'FRA','Spain':'ESP','Portugal':'PRT'}
    subset=frame[frame.country_name.isin(names)&(frame.year>=1974)]
    for m in configs:
        code=m['sourceCode']
        if code not in frame: raise ValueError('V-Dem indicator missing: '+code)
        for _,p in subset.iterrows():
            bounds=None
            if code+'_codelow' in frame and code+'_codehigh' in frame:
                low=numeric(p[code+'_codelow']); high=numeric(p[code+'_codehigh'])
                if low is not None and high is not None:
                    if low>high: raise ValueError('Reversed V-Dem bounds')
                    bounds=[low,high]
            put(rows,code,names[p.country_name],p.year,p[code],'MODEL_ESTIMATE',bounds)
    defs={}
    for m in configs:
        matches=book[book.tag==m['sourceCode']]
        if len(matches)!=1: raise ValueError('Ambiguous V-Dem codebook match')
        p=matches.iloc[0]
        def text(k): return str(p[k]) if p[k] is not None and str(p[k])!='nan' else ''
        defs[m['sourceCode']]={'title':text('name').strip(),'definition':' '.join(text(k) for k in ('question','clarification','responses','scale','notes','crosscoder_aggregation','cy_aggregation','convergence') if text(k)), 'scale':text('scale'),'responses':text('responses'),'measurementType':text('vartype'),'aggregation':text('cy_aggregation')}
        if text('vartype')!=m['measurementType'] or text('scale')!=m['unit']: raise ValueError('Unreviewed V-Dem scale/type change')
    return rows,defs

def metrics_from_receipt(receipt):
    provider=receipt['provider']; source=SOURCES[provider]; metrics=[]
    for m in (x for x in MANIFEST if x['provider']==provider):
        code=m['sourceCode']; meta=receipt['definitions'][code]; scale=100 if provider=='pwt' and code in ('labsh','irr','delta') else 1
        unit=('% of GDP' if code=='labsh' else '%') if scale==100 else ('%' if m['unit']=='percent' else m['unit'])
        if provider=='vdem': unit='model interval estimate' if m['measurementType']=='C' else ('index (0–1)' if '0-1' in m['unit'].replace(' ','') or '0–1' in m['unit'].replace(' ','') else 'model index')
        series={c:[] for c in COUNTRIES}; flags={c:{} for c in COUNTRIES}; bounds={c:{} for c in COUNTRIES}
        for c,years in receipt['observations'][code].items():
            for year,p in sorted(years.items(),key=lambda p:int(p[0])):
                value=p['value']; series[c].append([int(year),None if value is None else value*scale])
                if p['flags']: flags[c][str(year)]=p['flags']
                if p['bounds'] is not None: bounds[c][str(year)]=p['bounds']
        greek=[p for p in series['GRC'] if p[1] is not None]
        if (len(greek)<m['minimumGreekObservations']*.8 or len(greek)<10
                or greek[-1][0]<2020 or len({p[1] for p in greek})<2
                or len(greek)/(greek[-1][0]-greek[0][0]+1)<.7):
            raise ValueError('Vetted coverage lost: '+m['code'])
        title=m['title']
        metrics.append({**m,'title':{'en':title,'el':GREEK.get(m['code'],title)},'categories':[m['category']], 'unit':unit,'change':'pp' if unit.startswith('%') else 'absolute', 'source':source['name'],'sourceName':source['name'],'provider':source['name'], 'providerTitle':meta['title'],'definition':meta['definition'],'definitionEl':None,'sourceUrl':source['url'],'metadataUrl':source['metadata'],'apiUrl':receipt['dataUrl'],'accessMethod':'api' if provider=='uis' else 'download','sourceUpdatedAt':meta.get('updated',source['updated']),'sourceDateLabel':meta.get('sourceDateLabel'),'retrievedAt':receipt['retrievedAt'],'sha256':receipt['sha256'],'rawReceiptSha256':receipt['receiptSha256'],'upstreamHashes':receipt['upstreamHashes'],'sourceVersion':meta.get('release') or source['version'],'attribution':source['citation'],'measurementType':'expert/composite estimate' if provider=='vdem' else 'research estimate' if provider=='pwt' else 'statistical/composite series','interpretation':WARNINGS[provider],'scaleDefinition':meta.get('scale',unit),'responseAnchors':meta.get('responses'),'series':series,'flags':flags,'uncertainty':bounds,'uncertaintyLevel':.68 if provider=='vdem' and any(bounds.values()) else None,'coverage':{'start':greek[0][0],'end':greek[-1][0],'observations':len(greek)},'transformation':{'multiplier':scale,'originalUnit':m['unit']},'titleLanguage':'en' if m['code'] not in GREEK else 'en/el'})
    return metrics

def collect_provider(provider, raw, cached=False):
    source=SOURCES[provider]; configs=[m for m in MANIFEST if m['provider']==provider]; receipt_path=raw/f'vetted-{provider}.json'
    if cached and receipt_path.exists():
        receipt=json.loads(receipt_path.read_text()); receipt['receiptSha256']=hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        return metrics_from_receipt(receipt)
    if provider=='uis':
        query=[('indicator',m['sourceCode']) for m in configs]+[('geoUnit',c) for c in COUNTRIES if c!='EUU']+[('start','1974'),('end',str(dt.datetime.now(dt.timezone.utc).year)),('indicatorMetadata','true'),('footnotes','true')]
        url='https://api.uis.unesco.org/api/public/data/indicators?'+urllib.parse.urlencode(query)
        path=raw/'vetted-uis-source.json'; digest=download(url,path); observations,definitions=parse_uis(json.loads(path.read_bytes()),configs); hashes={url:digest}
    else:
        url=source['data']; path=raw/f'vetted-{provider}-source'
        path=path.with_suffix('.xlsx' if provider=='pwt' else '.RData' if provider=='vdem' else '.csv')
        digest=download(url,path); hashes={url:digest}
        if provider=='pwt': observations,definitions=parse_pwt(path,configs)
        else:
            meta=raw/f'vetted-{provider}-metadata'
            meta=meta.with_suffix('.RData' if provider=='vdem' else '.xlsx'); hashes[source['metadata']]=download(source['metadata'],meta)
            if provider=='vdem': observations,definitions=parse_vdem(path,meta,configs)
            else: observations,definitions=parse_undp(path.read_bytes(),meta,configs)
    receipt={'provider':provider,'dataUrl':url,'retrievedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'sha256':digest,'upstreamHashes':hashes,'observations':observations,'definitions':definitions}
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,separators=(',',':')))
    receipt['receiptSha256']=hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    metrics=metrics_from_receipt(receipt); print(f'Verified {provider}: {len(metrics)} indicators',flush=True); return metrics

def collect_all(raw, cached=False):
    # Sequential parsing keeps peak memory bounded for the full V-Dem R dataset.
    return [metric for provider in SOURCES for metric in collect_provider(provider,raw,cached)]
