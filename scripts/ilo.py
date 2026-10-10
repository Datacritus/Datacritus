"""Reviewed ILOSTAT annual aggregate slices, with pinned national sources."""
import csv
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import time
import urllib.request
import urllib.error
from catalog import COUNTRIES

MANIFEST=json.loads(Path(__file__).with_name('ilo_selection.json').read_text())
STATUS={'':'','A':'Adjusted','B':'Break in series','M':'Model-based extrapolation','U':'Unreliable','R':'Real value','I':'Imputation'}
TOC_URL='https://rplumber.ilo.org/metadata/toc/indicator?format=.csv'
WARNING={
'en':'Labour-force survey aggregates using ILO harmonised definitions (13th ICLS series). Actual hours, temporary contracts and part-time employment describe different conditions, not a government score. Definitions and survey methods can change; source notes and breaks are retained. National source IDs are pinned: newer Spanish/Portuguese source IDs need review before extension. No model extrapolation, unreliable values, imputation, interpolation or synthetic EU total. Changes during a term do not establish causation.',
'el':'Συγκεντρωτικά στοιχεία Έρευνας Εργατικού Δυναμικού με εναρμονισμένους ορισμούς του ILO (σειρές 13ου ICLS). Ώρες, προσωρινές συμβάσεις και μερική απασχόληση περιγράφουν διαφορετικές συνθήκες, όχι βαθμολογία κυβέρνησης. Ορισμοί και μέθοδοι μεταβάλλονται· διατηρούνται σημειώσεις και ασυνέχειες. Οι εθνικές πηγές είναι συγκεκριμένες: νέοι κωδικοί Ισπανίας/Πορτογαλίας απαιτούν έλεγχο. Χωρίς προέκταση μοντέλου, αναξιόπιστες τιμές, συμπλήρωση, παρεμβολή ή τεχνητό σύνολο ΕΕ. Οι μεταβολές στη θητεία δεν αποδεικνύουν αιτιότητα.'}

def api_url(config):
    return 'https://rplumber.ilo.org/data/indicator?id='+config['indicator']+'_A&ref_area=GRC%2BDEU%2BFRA%2BESP%2BPRT'+('&sex='+config['dimensions']['sex'] if config['dimensions']['sex'] else '')+'&timefrom=1974&timeto='+str(dt.date.today().year)+'&type=both&format=.csv'

def parse_csv(raw, config):
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    required={'ref_area','source','indicator','time','obs_value','obs_status','note_indicator.label','note_source.label'}
    if not rows or not required.issubset(rows[0]):raise ValueError('Empty or invalid ILO response')
    out={c:{} for c in COUNTRIES}
    for row in rows:
        country=row['ref_area']
        if country not in config['sources'] or row['source']!=config['sources'][country] or row['indicator']!=config['indicator']:continue
        if any(row.get(k,'')!=v for k,v in config['dimensions'].items()):continue
        if not row['time'].isdigit():raise ValueError('Nonannual ILO observation')
        year=int(row['time'])
        if not 1974<=year<=dt.date.today().year:continue
        status=row['obs_status']
        if status not in STATUS:raise ValueError('Unreviewed ILO status '+status)
        value=float(row['obs_value']) if row['obs_value'].strip() else None
        if value is not None and (not math.isfinite(value) or value<0 or value>(168 if config['unit']=='hours per week' else 100)):raise ValueError('Invalid ILO rate/hours value')
        if status in ('M','U','I'):value=None
        if str(year) in out[country]:raise ValueError('Duplicate ILO year')
        notes=[row.get(k,'') for k in ('note_indicator.label','note_source.label') if row.get(k,'')]
        flag='; '.join(([status+': '+STATUS[status]] if status else [])+notes)
        out[country][str(year)]={'value':value,'flags':flag,'source':row['source'],'sourceLabel':row.get('source.label',''),'noteIndicator':row.get('note_indicator',''),'noteSource':row.get('note_source','')}
    return out

def metrics_from_receipt(receipt):
    metrics=[]
    for config in MANIFEST:
        points=receipt['observations'][config['code']]
        series={c:[[int(y),p['value']] for y,p in sorted(points[c].items(),key=lambda x:int(x[0]))] for c in COUNTRIES}
        for c in config['sources']:
            valid=[p for p in series[c] if p[1] is not None]
            if len(valid)<10 or valid[-1][0]<2020 or len({p[1] for p in valid})<2 or len(valid)/(valid[-1][0]-valid[0][0]+1)<.7:raise ValueError('Insufficient ILO coverage '+config['code']+'/'+c)
        greek=[p for p in series['GRC'] if p[1] is not None]
        upstream=receipt['files'][config['indicator']]
        meta=receipt['metadata'][config['indicator']]
        credit='ILO, ILOSTAT; '+meta['indicator.label']+'; '+config['indicator']+'; https://ilostat.ilo.org/data/ (accessed '+receipt['retrievedAt'][:10]+'). CC BY 4.0. English/Greek labels adapted by DATACRITUS; not reviewed or endorsed by the ILO.'
        metrics.append({**config,'iloSelectionId':config['indicator'],'source':'ILO','sourceName':'ILOSTAT — '+meta['database.label'],'provider':config.get('provider','ILO; national Labour Force Surveys'),'providerTitle':meta['indicator.label'],
          'sourceUrl':'https://ilostat.ilo.org/data/','apiUrl':upstream['url'],'metadataUrl':config['methodologyUrl'],'accessMethod':'api','sourceVersion':'ILOSTAT annual best-source aggregates; reviewed national source IDs; 13th ICLS','sourceUpdatedAt':dt.datetime.strptime(meta['last.update'],'%d/%m/%Y %H:%M:%S').isoformat(),
          'retrievedAt':receipt['retrievedAt'],'sha256':upstream['sha256'],'rawReceiptSha256':receipt.get('receiptSha256'),'upstreamHashes':{config['indicator']:upstream['sha256'],'metadata':receipt['metadataSha256']},'attribution':credit,'measurementType':config.get('measurementType','harmonised labour-force survey aggregate'),'interpretation':config.get('interpretation',WARNING),
          'transformation':'Exact annual indicator, reviewed sex/classification dimensions and pinned country/source IDs. Original units. M/U/I values suppressed, flags and source notes retained. No interpolation or EU aggregate.',
          'series':series,'flags':{c:{y:p['flags'] for y,p in points[c].items() if p['flags']} for c in COUNTRIES},'uncertainty':{c:{} for c in COUNTRIES},'uncertaintyLevel':None,
          'coverage':{'start':greek[0][0],'end':greek[-1][0],'observations':len(greek)},'subtopic':config.get('subtopic',{'id':'working-conditions','title':{'en':'Working conditions','el':'Συνθήκες εργασίας'}})})
    return metrics

def fetch(url):
    delays=(5,15,30)
    for attempt in range(len(delays)+1):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Datacritus/1.0 (https://www.datacritus.gr)'})
            with urllib.request.urlopen(req,timeout=55) as r:return r.read()
        except (urllib.error.URLError,TimeoutError,OSError) as exc:
            if isinstance(exc,urllib.error.HTTPError) and exc.code not in (408,429,500,502,503,504):raise
            if attempt==len(delays):raise
            print('ILO transient transport failure; retrying in',delays[attempt],'seconds:',str(exc),flush=True)
            time.sleep(delays[attempt])

def collect_all(raw_dir,cached=False):
    path=raw_dir/'ilo-receipt.json'
    if cached:receipt=json.loads(path.read_text())
    else:
        raw=fetch(TOC_URL);(raw_dir/'ilo-metadata-toc.csv').write_bytes(raw)
        toc={r['indicator']:r for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))) if r['freq']=='A'}
        receipt={'retrievedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'metadataSha256':hashlib.sha256(raw).hexdigest(),'metadata':{},'files':{},'observations':{}}
        for config in MANIFEST:
            code=config['indicator'];meta=toc[code]
            if dt.datetime.strptime(meta['last.update'],'%d/%m/%Y %H:%M:%S').date()<dt.date(2023,5,3):raise ValueError('ILO data rights need review')
            url=api_url(config);raw=fetch(url);(raw_dir/('ilo-source-'+code+'.csv')).write_bytes(raw)
            receipt['metadata'][code]=meta;receipt['files'][code]={'url':url,'sha256':hashlib.sha256(raw).hexdigest()};receipt['observations'][config['code']]=parse_csv(raw,config)
            print('ILO fetched',code,flush=True)
        metrics_from_receipt(receipt)
        temp=path.with_suffix('.tmp');temp.write_text(json.dumps(receipt,ensure_ascii=False,separators=(',',':')));temp.replace(path)
    receipt['receiptSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    return metrics_from_receipt(receipt)
