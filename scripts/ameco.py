"""Reusable AMECO bulk-release connector; publication requires reviewed exact slices.

Pinned release + conservative historical cutoff: forecasts are never mixed into
cabinet comparisons. Currency/base-year/unit drift fails closed. No API keys.
"""
import csv,datetime as dt,hashlib,io,json,math,time,urllib.request,zipfile
from pathlib import Path
from catalog import COUNTRIES
CONFIG=json.loads(Path(__file__).with_name('ameco_selection.json').read_text())
MANIFEST=CONFIG['selection']
SOURCE='https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database_en'
TERMS='https://commission.europa.eu/legal-notice_en'
WARNING={'en':'AMECO historical statistics and estimates, pinned to '+CONFIG['release']+'. Years from 2025 onward are excluded conservatively; the CSV has no per-observation forecast status. Historical data may be revised, linked across accounting standards or model-estimated. Components and sector breakdowns overlap; no aggregate score. Monetary conditions also reflect euro-area policy. A new release and a later historical cutoff require review.','el':'Ιστορικά στοιχεία και εκτιμήσεις AMECO, από την ελεγμένη έκδοση Ιουνίου 2026. Εξαιρούνται συντηρητικά τα έτη από το 2025· το CSV δεν δίνει σήμανση πρόβλεψης ανά παρατήρηση. Ιστορικές τιμές αναθεωρούνται και μπορεί να είναι συνδεδεμένες ή υποδειγματικές. Οι συνιστώσες και κλάδοι επικαλύπτονται· δεν προκύπτει συνολική βαθμολογία. Νεότερη έκδοση και όριο ετών απαιτούν έλεγχο.'}
def archive_rows(raw):
    if hashlib.sha256(raw).hexdigest()!=CONFIG['archiveSha256']:raise ValueError('AMECO release changed: review source version, units and forecast cutoff before updating')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        expected={f'AMECO{i}.CSV' for i in range(1,19)}
        if set(z.namelist())!=expected:raise ValueError('Unexpected AMECO archive structure')
        if sum(i.file_size for i in z.infolist())>200_000_000:raise ValueError('AMECO archive too large')
        for filename in sorted(expected):
            content=z.read(filename)
            try:text=content.decode('utf-8-sig')
            except UnicodeDecodeError:text=content.decode('cp1252')
            reader=csv.DictReader(io.StringIO(text))
            if not {'CODE','COUNTRY','TITLE','UNIT','2024','2025'}<=set(reader.fieldnames or []):raise ValueError('Missing AMECO fields')
            for row in reader:yield filename,row

def parse_archive(raw,configs=MANIFEST):
    output={m['code']:{c:{} for c in COUNTRIES} for m in configs};seen=set()
    lookup={(m['sourceFile'],m['slice'],m['variable']):m for m in configs}
    if len(lookup)!=len(configs):raise ValueError('Duplicate AMECO selection')
    for filename,row in archive_rows(raw):
        parts=row['CODE'].split('.')
        if len(parts)!=6:raise ValueError('Unexpected AMECO series key')
        country=parts[0]
        if country not in COUNTRIES or country=='EUU':continue
        config=lookup.get((filename,'.'.join(parts[1:5]),parts[5]))
        if not config:continue
        signature=(config['code'],country)
        if signature in seen:raise ValueError('Duplicate AMECO country/slice')
        seen.add(signature)
        if row['TITLE']!=config['providerTitle'] or row['UNIT']!=config['sourceUnit']:raise ValueError('AMECO definition/unit drift: '+row['CODE'])
        for year in range(1974,CONFIG['historicalCutoff']+1):
            token=row.get(str(year),'').strip()
            if token in ('','NA'):value=None
            else:
                value=float(token)
                if not math.isfinite(value):raise ValueError('Nonfinite AMECO observation')
            output[config['code']][country][str(year)]=value
    for config in configs:
        years=output[config['code']]['GRC']
        real=[y for y,v in years.items() if v is not None]
        if len(real)<15 or max(map(int,real),default=0)<2024:raise ValueError('Insufficient Greek AMECO history: '+config['code'])
    return output

def inventory(raw):
    rows=[]
    for file,row in archive_rows(raw):
        if row['CODE'].startswith('GRC.'):
            years=[]
            for y in range(1974,CONFIG['historicalCutoff']+1):
                token=row.get(str(y),'').strip()
                if token not in ('','NA'):
                    if not math.isfinite(float(token)):raise ValueError('Nonfinite inventory value')
                    years.append(y)
            rows.append({'sourceFile':file,'key':row['CODE'],'variable':row['CODE'].split('.')[-1],'title':row['TITLE'],'unit':row['UNIT'],'historicalYears':years,'selected':any(m['sourceFile']==file and row['CODE']=='GRC.'+m['slice']+'.'+m['variable'] for m in MANIFEST)})
    return {'release':CONFIG['release'],'archiveSha256':CONFIG['archiveSha256'],'historicalCutoff':CONFIG['historicalCutoff'],'rows':rows,'greekSourceRows':len(rows),'variableCodes':len({r['variable'] for r in rows}),'countsAreNotIndependentOrNetNewKPIs':True}

def metrics_from_receipt(receipt):
    if receipt['archiveSha256']!=CONFIG['archiveSha256'] or receipt['historicalCutoff']!=CONFIG['historicalCutoff']:raise ValueError('AMECO receipt release mismatch')
    metrics=[]
    for m in MANIFEST:
        values=receipt['observations'][m['code']]
        series={c:[[int(y),v] for y,v in sorted(values[c].items(),key=lambda p:int(p[0]))] for c in COUNTRIES}
        if any(y>CONFIG['historicalCutoff'] for rows in series.values() for y,v in rows):raise ValueError('Forecast-year leakage')
        greek=[p for p in series['GRC'] if p[1] is not None]
        if len(greek)<15 or greek[-1][0]<2024:raise ValueError('Insufficient Greek AMECO receipt history')
        flags={c:{str(y):'MODEL_ESTIMATE' for y,v in rows if v is not None} if m['variable']=='UBLGAPS' else {} for c,rows in series.items()}
        metrics.append({**m,'categories':[m['category']],'amecoSelectionId':m['variable'],'source':'AMECO','sourceName':'European Commission AMECO','provider':'European Commission, DG ECFIN; Eurostat and national sources','sourceUrl':SOURCE,'apiUrl':CONFIG['archiveUrl'],'metadataUrl':SOURCE,'accessMethod':'official bulk CSV archive','sourceVersion':CONFIG['release'],'sourceUpdatedAt':CONFIG['releaseDate'],'retrievedAt':receipt['retrievedAt'],'sha256':CONFIG['archiveSha256'],'rawReceiptSha256':receipt.get('receiptSha256'),'upstreamHashes':{'amecoArchive':CONFIG['archiveSha256']},'license':'CC BY 4.0 (EU-owned content; source exceptions apply)','termsUrl':TERMS,'sourceRightsBasis':'European Commission default reuse notice; retain credit and indicate transformations. No EU logos are reused.','attribution':'European Union / European Commission, DG ECFIN, AMECO, '+CONFIG['release']+'. Source: '+SOURCE+'. Exact slice '+m['slice']+'.'+m['variable']+'. Historical window limited to 1974–2024; no interpolation.','interpretation':WARNING,'transformation':'Exact country and AMECO slice, source units checked; 1974–2024 only. NA retained as null. No rescaling, currency conversion, interpolation or EU aggregation. Structural budget balance marked MODEL_ESTIMATE by Datacritus.','historicalCutoff':CONFIG['historicalCutoff'],'series':series,'flags':flags,'uncertainty':{c:{} for c in COUNTRIES},'uncertaintyLevel':None,'coverage':{'start':greek[0][0],'end':greek[-1][0],'observations':len(greek)},'subtopic':{'id':'ameco','title':{'en':'AMECO macroeconomic history','el':'Μακροοικονομική ιστορία AMECO'}}})
    return metrics

def collect_all(raw_dir,cached=False):
    raw_dir=Path(raw_dir);raw_dir.mkdir(parents=True,exist_ok=True);archive=raw_dir/'ameco-source.zip'
    if cached:raw=archive.read_bytes()
    else:
        error=None
        for attempt in range(3):
            try:
                request=urllib.request.Request(CONFIG['archiveUrl'],headers={'User-Agent':'Datacritus/1.0 (+https://www.datacritus.gr)'})
                with urllib.request.urlopen(request,timeout=60) as response:raw=response.read()
                if hashlib.sha256(raw).hexdigest()!=CONFIG['archiveSha256']:raise ValueError('Unreviewed AMECO release')
                break
            except Exception as exc:
                error=exc
                if attempt==2:raise RuntimeError('AMECO download failed; published snapshot retained') from error
                time.sleep(1+attempt)
        archive.write_bytes(raw)
    observations=parse_archive(raw)
    receipt={'archiveSha256':CONFIG['archiveSha256'],'historicalCutoff':CONFIG['historicalCutoff'],'retrievedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'observations':observations}
    path=raw_dir/'ameco-receipt.json';path.write_text(json.dumps(receipt,ensure_ascii=False,separators=(',',':')))
    receipt['receiptSha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    return metrics_from_receipt(receipt)
