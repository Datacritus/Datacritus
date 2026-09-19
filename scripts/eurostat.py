"""Decode Eurostat JSON-stat with explicit dimensions and retain status flags."""
import concurrent.futures, datetime as dt, hashlib, json, math, time
import urllib.parse, urllib.request

GEO={'EL':'GRC','EU27_2020':'EUU','DE':'DEU','FR':'FRA','ES':'ESP','PT':'PRT'}
CATALOG=[
 {'code':'ESTAT.GOV.DEBT','dataset':'gov_10dd_edpt1','title':{'en':'General government debt','el':'Χρέος γενικής κυβέρνησης'},'unit':'% of GDP','categories':['finance'],'params':{'unit':'PC_GDP','sector':'S13','na_item':'GD'},'definition':'Consolidated gross debt of general government (S13), at nominal value, as a percentage of GDP. Maastricht definition; distinct from central government debt.'},
 {'code':'ESTAT.GOV.BALANCE','dataset':'gov_10dd_edpt1','title':{'en':'Government surplus / deficit','el':'Πλεόνασμα / έλλειμμα γενικής κυβέρνησης'},'unit':'% of GDP','categories':['finance'],'params':{'unit':'PC_GDP','sector':'S13','na_item':'B9'},'definition':'General government net lending (+) or net borrowing (−), as a percentage of GDP, under ESA 2010 / the Excessive Deficit Procedure.'},
 {'code':'ESTAT.HOUSING.OVERBURDEN','dataset':'ilc_lvho07a','title':{'en':'Housing cost overburden','el':'Υπερβολική επιβάρυνση κόστους στέγασης'},'unit':'% of population','categories':['housing','wellbeing'],'params':{'unit':'PC','rskpovth':'TOTAL','age':'TOTAL','sex':'T'},'definition':'Share of people living in households where total housing costs, net of housing allowances, exceed 40% of total disposable household income, net of housing allowances. EU-SILC; all ages, both sexes, total poverty status.'},
 {'code':'ESTAT.CULTURE.EMPLOYMENT','dataset':'cult_emp_sex','title':{'en':'Cultural employment','el':'Πολιτιστική απασχόληση'},'unit':'% of employment','categories':['culture','business'],'params':{'unit':'PC_EMP','sex':'T'},'definition':'Employment in cultural economic activities and cultural occupations as a percentage of total employment. Both sexes; EU Labour Force Survey. Eurostat cultural employment definition applies; survey breaks and reliability flags are retained.'},
]

def parse_payload(payload):
    ids=payload['id'];sizes=payload['size'];dims=payload['dimension']
    geo_idx=ids.index('geo');time_idx=ids.index('time')
    for d,size in zip(ids,sizes):
        if d not in ('geo','time') and size!=1:raise ValueError(f'Unfiltered Eurostat dimension: {d}')
    axes=[]
    for d in ids:
        idx=dims[d]['category']['index']
        axes.append(idx if isinstance(idx,list) else [k for k,v in sorted(idx.items(),key=lambda kv:kv[1])])
    series={c:{} for c in GEO.values()};flags={c:{} for c in GEO.values()}
    values=payload.get('value',{});statuses=payload.get('status',{})
    values=dict(enumerate(values)) if isinstance(values,list) else values
    statuses=dict(enumerate(statuses)) if isinstance(statuses,list) else statuses
    for flat,value in values.items():
        n=int(flat);coords=[0]*len(sizes)
        for i in range(len(sizes)-1,-1,-1):coords[i]=n%sizes[i];n//=sizes[i]
        geo=axes[geo_idx][coords[geo_idx]];year=int(axes[time_idx][coords[time_idx]])
        if geo not in GEO or year<1974 or year>dt.datetime.now(dt.timezone.utc).year:continue
        if value is not None and (not isinstance(value,(float,int)) or not math.isfinite(value)):raise ValueError('Invalid Eurostat value')
        country=GEO[geo]
        if year in series[country]:raise ValueError('Duplicate Eurostat observation')
        series[country][year]=value
        flag=statuses.get(str(flat),statuses.get(int(flat)))
        if flag:flags[country][str(year)]=flag
    years=[int(y) for y in axes[time_idx] if int(y)>=1974]
    # Explicit nulls make gaps visible in the chart.
    return {c:[[y,points.get(y)] for y in years] for c,points in series.items()},flags

def collect_all(raw_dir):
    def collect(m):
        params={'lang':'en','freq':'A',**m['params']}
        url='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'+m['dataset']+'?'+urllib.parse.urlencode(params)
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url,timeout=55) as res:raw=res.read()
                payload=json.loads(raw)
                series,flags=parse_payload(payload)
                break
            except Exception:
                if attempt==2:raise
                time.sleep(attempt+1)
        (raw_dir/('eurostat-'+m['code']+'.json')).write_bytes(raw)
        greek=[p for p in series['GRC'] if p[1] is not None]
        if not greek:raise ValueError('Eurostat returned no Greek observations')
        print(f"Fetched {m['code']}: {len(greek)} Greece observations, latest {greek[-1]}",flush=True)
        return {**{k:v for k,v in m.items() if k not in ('params',)},'change':'pp','source':'Eurostat','sourceName':'Eurostat',
         'providerTitle':payload['label'],'provider':'Eurostat / national statistical authorities','series':series,'flags':flags,
         'sourceUrl':f"https://ec.europa.eu/eurostat/databrowser/view/{m['dataset']}/default/table?lang=en",
         'metadataUrl':url,'apiUrl':url,'retrievedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'sourceUpdatedAt':payload.get('updated'),
         'sha256':hashlib.sha256(raw).hexdigest(),'coverage':{'start':greek[0][0],'end':greek[-1][0],'observations':len(greek)}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:return list(ex.map(collect,CATALOG))
