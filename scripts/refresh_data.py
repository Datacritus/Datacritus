#!/usr/bin/env python3
"""Fetch official World Bank observations atomically. No API keys or dependencies.

A failed response never replaces the published snapshot. Retain provider nulls;
do not interpolate, carry forward, generate, or splice different series.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import time
import urllib.parse
import urllib.request
from catalog import CATEGORIES, CATEGORY_NOTES, COUNTRIES, METRICS
from eurostat import collect_all

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
NOW = dt.datetime.now(dt.timezone.utc)

def fetch(url):
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Datacritus/1.0 (public statistics dashboard; https://www.datacritus.gr)'})
            with urllib.request.urlopen(req, timeout=55) as res:
                raw = res.read()
            payload = json.loads(raw)
            if not isinstance(payload,list) or len(payload)!=2 or not isinstance(payload[0],dict) or 'message' in payload[0]:
                raise ValueError('Provider returned an error or unexpected response')
            if int(payload[0].get('pages',1))>1:
                raise ValueError('Response is paginated; refusing a truncated snapshot')
            return payload, raw
        except Exception as exc:
            error=exc
            if attempt<2: time.sleep(1+attempt)
    raise RuntimeError(f'{url}: {error}')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cached-metadata',action='store_true',help='Use already fetched metadata for this build only')
    args=parser.parse_args()
    RAW.mkdir(parents=True,exist_ok=True)
    metadata={}
    for source in ('2','3'):
        path=RAW/f'metadata-{source}.json'
        if args.cached_metadata and path.exists(): payload=json.loads(path.read_text())
        else:
            payload,raw=fetch(f'https://api.worldbank.org/v2/source/{source}/indicator?format=json&per_page=20000')
            path.write_bytes(raw)
        metadata[source]={m['id']:m for m in payload[1]}
    invalid=[m['code'] for m in METRICS if m['code'] not in metadata[m['source']]]
    if invalid: raise ValueError(f'Unknown indicator identifiers: {invalid}')
    # Batches stay below the API URL and row limits.
    jobs=[]
    for source in ('2','3'):
        codes=[m['code'] for m in METRICS if m['source']==source]
        for offset in range(0,len(codes),8): jobs.append((source,codes[offset:offset+8]))
    def collect(job):
        source,codes=job
        query=urllib.parse.urlencode({'source':source,'format':'json','date':f'1974:{NOW.year}','per_page':20000})
        url=f"https://api.worldbank.org/v2/country/{';'.join(COUNTRIES)}/indicator/{';'.join(codes)}?{query}"
        payload,raw=fetch(url)
        name=f'wb-{source}-{codes[0]}.json'
        (RAW/name).write_bytes(raw)
        print(f'Fetched {len(codes)} indicators: {len(payload[1] or [])} rows',flush=True)
        return codes,payload,url,hashlib.sha256(raw).hexdigest()
    values={m['code']:{c:{} for c in COUNTRIES} for m in METRICS}
    provenance={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for codes,payload,url,digest in executor.map(collect,jobs):
            for code in codes: provenance[code]={'apiUrl':url,'retrievedAt':NOW.isoformat(),'sourceUpdatedAt':payload[0].get('lastupdated'),'sha256':digest}
            for row in payload[1] or []:
                code=row['indicator']['id'];country=row.get('countryiso3code');year=int(row['date']);value=row['value']
                if code not in values or country not in COUNTRIES: continue
                if value is not None and (not isinstance(value,(int,float)) or not math.isfinite(value)):raise ValueError('Invalid observation')
                if year in values[code][country]:raise ValueError('Duplicate observation')
                values[code][country][year]=value
    metrics=[]
    for m in METRICS:
        meta=metadata[m['source']][m['code']]
        series={c:[[year,value] for year,value in sorted(years.items())] for c,years in values[m['code']].items()}
        greek=[p for p in series['GRC'] if p[1] is not None]
        item={**m,'providerTitle':meta['name'],'definition':meta.get('sourceNote') or ('Perception-based composite governance estimate for '+meta['name'].split(' - ')[0]+'. Combines household, firm and expert assessments using the WGI aggregation model. Estimates usually lie around -2.5 to +2.5, with higher values indicating stronger governance. These are not percentages; uncertainty must be considered when comparing scores.' if m['source']=='3' else meta['name']),
              'provider':meta.get('sourceOrganization','World Bank'),'sourceName':meta.get('source',{}).get('value','World Bank'),
              'sourceUrl':('https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation' if m['source']=='3' else f"https://data.worldbank.org/indicator/{m['code']}?locations=GR"),
              'metadataUrl':f"https://api.worldbank.org/v2/indicator/{m['code']}?format=json",
              **provenance[m['code']],'series':series,'coverage':{'start':greek[0][0] if greek else None,'end':greek[-1][0] if greek else None,'observations':len(greek)}}
        metrics.append(item)
        print(m['code'],len(greek),greek[-1] if greek else 'No Greece observations',flush=True)
    metrics.extend(collect_all(RAW))
    if sum(bool(m['coverage']['observations']) for m in metrics)<40:raise ValueError('Insufficient real data; refusing to replace snapshot')
    previous_path=ROOT/'data'/'indicators.json'
    if previous_path.exists():
        previous=json.loads(previous_path.read_text())
        old={m['code']:m for m in previous['metrics']}
        for m in metrics:
            old_count=old.get(m['code'],{}).get('coverage',{}).get('observations',0)
            if old_count and m['coverage']['observations']<old_count*0.8:
                raise ValueError(f"Unexpected coverage loss for {m['code']}; review upstream change")
    dataset={'schemaVersion':1,'retrievedAt':NOW.isoformat(),'countries':COUNTRIES,
             'categories':[{'id':i,'title':{'en':en,'el':el},'note':CATEGORY_NOTES.get(i)} for i,en,el in CATEGORIES],
             'metrics':metrics,'licenceUrl':'https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets',
             'licenceNote':'World Bank dataset terms and Eurostat reuse policy apply to their respective series; individual third-party sources may have additional terms. See source attribution for every series.'}
    temp=previous_path.with_suffix('.tmp')
    temp.write_text(json.dumps(dataset,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    temp.replace(previous_path)
    print(f'Saved {len(metrics)} verified indicator series to {previous_path}',flush=True)

if __name__=='__main__':main()
